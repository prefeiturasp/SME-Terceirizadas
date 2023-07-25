
from django.core.exceptions import ObjectDoesNotExist
from django.db import transaction
from django.db.models import QuerySet
from django_filters import rest_framework as filters
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_401_UNAUTHORIZED, HTTP_406_NOT_ACCEPTABLE
from xworkflows.base import InvalidTransitionError

from sme_terceirizadas.dados_comuns.constants import ADMINISTRADOR_EMPRESA
from sme_terceirizadas.dados_comuns.fluxo_status import CronogramaWorkflow
from sme_terceirizadas.dados_comuns.permissions import (
    PermissaoParaAnalisarDilogSolicitacaoAlteracaoCronograma,
    PermissaoParaAnalisarDinutreSolicitacaoAlteracaoCronograma,
    PermissaoParaAssinarCronogramaUsuarioDilog,
    PermissaoParaAssinarCronogramaUsuarioDinutre,
    PermissaoParaAssinarCronogramaUsuarioFornecedor,
    PermissaoParaCadastrarLaboratorio,
    PermissaoParaCadastrarVisualizarEmbalagem,
    PermissaoParaCadastrarVisualizarUnidadesMedida,
    PermissaoParaCriarCronograma,
    PermissaoParaCriarSolicitacoesAlteracaoCronograma,
    PermissaoParaDarCienciaAlteracaoCronograma,
    PermissaoParaDashboardCronograma,
    PermissaoParaListarDashboardSolicitacaoAlteracaoCronograma,
    PermissaoParaVisualizarCronograma,
    PermissaoParaVisualizarSolicitacoesAlteracaoCronograma,
    ViewSetActionPermissionMixin
)
from sme_terceirizadas.pre_recebimento.api.filters import (
    CronogramaFilter,
    EmbalagensQldFilter,
    LaboratorioFilter,
    SolicitacaoAlteracaoCronogramaFilter,
    UnidadeMedidaFilter
)
from sme_terceirizadas.pre_recebimento.api.paginations import (
    CronogramaPagination,
    EmbalagemQldPagination,
    LaboratorioPagination
)
from sme_terceirizadas.pre_recebimento.api.serializers.serializer_create import (
    CronogramaCreateSerializer,
    EmbalagemQldCreateSerializer,
    LaboratorioCreateSerializer,
    SolicitacaoDeAlteracaoCronogramaCreateSerializer,
    UnidadeMedidaCreateSerializer
)
from sme_terceirizadas.pre_recebimento.api.serializers.serializers import (
    CronogramaComLogSerializer,
    CronogramaRascunhosSerializer,
    CronogramaSerializer,
    EmbalagemQldSerializer,
    LaboratorioSerializer,
    LaboratorioSimplesFiltroSerializer,
    NomeEAbreviacaoUnidadeMedidaSerializer,
    PainelCronogramaSerializer,
    PainelSolicitacaoAlteracaoCronogramaSerializer,
    SolicitacaoAlteracaoCronogramaCompletoSerializer,
    SolicitacaoAlteracaoCronogramaSerializer,
    UnidadeMedidaSerialzer
)
from sme_terceirizadas.pre_recebimento.models import (
    Cronograma,
    EmbalagemQld,
    EtapasDoCronograma,
    Laboratorio,
    SolicitacaoAlteracaoCronograma,
    UnidadeMedida
)
from sme_terceirizadas.pre_recebimento.utils import (
    ServiceDashboardSolicitacaoAlteracaoCronogramaProfiles,
    UnidadeMedidaPagination
)

from ...dados_comuns.models import LogSolicitacoesUsuario
from ...relatorios.relatorios import get_pdf_cronograma


class CronogramaModelViewSet(ViewSetActionPermissionMixin, viewsets.ModelViewSet):
    lookup_field = 'uuid'
    queryset = Cronograma.objects.all()
    serializer_class = CronogramaSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = CronogramaFilter
    pagination_class = CronogramaPagination
    permission_classes = (PermissaoParaVisualizarCronograma,)
    permission_action_classes = {
        'create': [PermissaoParaCriarCronograma],
        'delete': [PermissaoParaCriarCronograma]
    }

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return CronogramaSerializer
        else:
            return CronogramaCreateSerializer

    def get_queryset(self):
        return Cronograma.objects.all().order_by('-criado_em')

    def get_lista_status(self):
        lista_status = [
            Cronograma.workflow_class.ASSINADO_FORNECEDOR,
            Cronograma.workflow_class.ASSINADO_DINUTRE,
            Cronograma.workflow_class.ASSINADO_CODAE,
        ]

        return lista_status

    def get_default_sql(self, workflow, query_set, use_raw):
        if use_raw:
            data = {'logs': LogSolicitacoesUsuario._meta.db_table,
                    'cronograma': Cronograma._meta.db_table,
                    'status': workflow}
            raw_sql = ('SELECT %(cronograma)s.* FROM %(cronograma)s '
                       'JOIN (SELECT uuid_original, MAX(criado_em) AS log_criado_em FROM %(logs)s '
                       'GROUP BY uuid_original) '
                       'AS most_recent_log '
                       'ON %(cronograma)s.uuid = most_recent_log.uuid_original '
                       "WHERE %(cronograma)s.status = '%(status)s' ")
            raw_sql += 'ORDER BY log_criado_em DESC'

            return query_set.raw(raw_sql % data)
        else:
            qs = sorted(query_set.filter(status=workflow).distinct().all(),
                        key=lambda x: x.log_mais_recente.criado_em
                        if x.log_mais_recente else '-criado_em', reverse=True)
            return qs

    def dados_dashboard(self, request, query_set: QuerySet, use_raw) -> list:
        limit = int(request.query_params.get('limit', 10))
        offset = int(request.query_params.get('offset', 0))
        status = request.query_params.get('status', None)
        sumario = []
        if status:
            qs = self.get_default_sql(workflow=status, query_set=query_set, use_raw=use_raw)
            sumario.append({
                'status': status,
                'total': len(qs),
                'dados': PainelCronogramaSerializer(
                    qs[offset:limit + offset],
                    context={'request': self.request, 'workflow': status}, many=True).data
            })
        else:
            for workflow in self.get_lista_status():
                qs = self.get_default_sql(workflow=workflow, query_set=query_set, use_raw=use_raw)
                sumario.append({
                    'status': workflow,
                    'dados': PainelCronogramaSerializer(
                        qs[:6],
                        context={'request': self.request, 'workflow': workflow}, many=True).data
                })

        return sumario

    @action(detail=False, methods=['GET'],
            url_path='dashboard', permission_classes=(PermissaoParaDashboardCronograma,))
    def dashboard(self, request):
        query_set = self.get_queryset()
        response = {'results': self.dados_dashboard(query_set=query_set, request=request, use_raw=False)}
        return Response(response)

    @action(detail=False, methods=['GET'],
            url_path='dashboard-com-filtro', permission_classes=(PermissaoParaDashboardCronograma,))
    def dashboard_com_filtro(self, request):
        query_set = self.get_queryset()
        numero_cronograma = request.query_params.get('numero_cronograma', None)
        produto = request.query_params.get('nome_produto', None)
        fornecedor = request.query_params.get('nome_fornecedor', None)

        if numero_cronograma:
            query_set = query_set.filter(numero__icontains=numero_cronograma)
        if produto:
            query_set = query_set.filter(produto__nome__icontains=produto)
        if fornecedor:
            query_set = query_set.filter(empresa__razao_social__icontains=fornecedor)

        response = {'results': self.dados_dashboard(query_set=query_set, request=request, use_raw=False)}
        return Response(response)

    def list(self, request, *args, **kwargs):
        vinculo = self.request.user.vinculo_atual
        queryset = self.filter_queryset(self.get_queryset())
        queryset = queryset.order_by('-alterado_em').distinct()

        if vinculo.perfil.nome == ADMINISTRADOR_EMPRESA and vinculo.instituicao.eh_fornecedor:
            queryset = queryset.filter(empresa=vinculo.instituicao)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            response = self.get_paginated_response(
                serializer.data
            )
            return response

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, url_path='opcoes-etapas')
    def etapas(self, _):
        return Response(EtapasDoCronograma.etapas_to_json())

    @action(detail=False, methods=['GET'], url_path='rascunhos')
    def rascunhos(self, _):
        queryset = self.get_queryset().filter(status__in=[CronogramaWorkflow.RASCUNHO])
        response = {'results': CronogramaRascunhosSerializer(queryset, many=True).data}
        return Response(response)

    @transaction.atomic
    @action(detail=True, permission_classes=(PermissaoParaAssinarCronogramaUsuarioFornecedor,),
            methods=['patch'], url_path='fornecedor-assina-cronograma')
    def fornecedor_assina(self, request, uuid=None):
        usuario = request.user

        if not usuario.verificar_autenticidade(request.data.get('password')):
            return Response(
                dict(detail=f'Assinatura do cronograma não foi validada. Verifique sua senha.'),
                status=HTTP_401_UNAUTHORIZED
            )

        try:
            cronograma = Cronograma.objects.get(uuid=uuid)
            cronograma.fornecedor_assina(user=usuario, )
            serializer = CronogramaSerializer(cronograma)
            return Response(serializer.data)

        except ObjectDoesNotExist as e:
            return Response(dict(detail=f'Cronograma informado não é valido: {e}'), status=HTTP_406_NOT_ACCEPTABLE)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @transaction.atomic
    @action(detail=True, permission_classes=(PermissaoParaAssinarCronogramaUsuarioDinutre,),
            methods=['patch'], url_path='dinutre-assina')
    def dinutre_assina(self, request, uuid):
        usuario = request.user

        if not usuario.verificar_autenticidade(request.data.get('password')):
            return Response(
                dict(detail=f'Assinatura do cronograma não foi validada. Verifique sua senha.'),
                status=HTTP_401_UNAUTHORIZED
            )

        try:
            cronograma = Cronograma.objects.get(uuid=uuid)
            cronograma.dinutre_assina(user=usuario)
            serializer = CronogramaSerializer(cronograma)
            return Response(serializer.data)

        except ObjectDoesNotExist as e:
            return Response(dict(detail=f'Cronograma informado não é valido: {e}'), status=HTTP_406_NOT_ACCEPTABLE)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @transaction.atomic
    @action(detail=True, permission_classes=(PermissaoParaAssinarCronogramaUsuarioDilog,),
            methods=['patch'], url_path='codae-assina')
    def codae_assina(self, request, uuid):
        usuario = request.user

        if not usuario.verificar_autenticidade(request.data.get('password')):
            return Response(
                dict(detail=f'Assinatura do cronograma não foi validada. Verifique sua senha.'),
                status=HTTP_401_UNAUTHORIZED
            )

        try:
            cronograma = Cronograma.objects.get(uuid=uuid)
            cronograma.codae_assina(user=usuario)
            serializer = CronogramaSerializer(cronograma)
            return Response(serializer.data)

        except ObjectDoesNotExist as e:
            return Response(dict(detail=f'Cronograma informado não é valido: {e}'), status=HTTP_406_NOT_ACCEPTABLE)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['GET'], url_path='gerar-pdf-cronograma')
    def gerar_pdf_cronograma(self, request, uuid=None):
        cronograma = self.get_object()

        return get_pdf_cronograma(request, cronograma)

    @action(detail=True, methods=['GET'], url_path='detalhar-com-log')
    def detalhar_com_log(self, request, uuid=None):
        cronograma = self.get_object()
        response = CronogramaComLogSerializer(cronograma, many=False).data
        return Response(response)


class LaboratorioModelViewSet(ViewSetActionPermissionMixin, viewsets.ModelViewSet):
    lookup_field = 'uuid'
    queryset = Laboratorio.objects.all().order_by('-criado_em')
    serializer_class = LaboratorioSerializer
    pagination_class = LaboratorioPagination
    filterset_class = LaboratorioFilter
    filter_backends = (filters.DjangoFilterBackend,)
    permission_classes = (PermissaoParaCadastrarLaboratorio,)
    permission_action_classes = {
        'create': [PermissaoParaCadastrarLaboratorio],
        'delete': [PermissaoParaCadastrarLaboratorio]
    }

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return LaboratorioSerializer
        else:
            return LaboratorioCreateSerializer

    @action(detail=False, methods=['GET'], url_path='lista-nomes-laboratorios')
    def lista_nomes_laboratorios(self, request):
        queryset = Laboratorio.objects.all()
        response = {'results': [q.nome for q in queryset]}
        return Response(response)

    @action(detail=False, methods=['GET'], url_path='lista-laboratorios')
    def lista_laboratorios_para_filtros(self, request):
        laboratorios = self.get_queryset()
        serializer = LaboratorioSimplesFiltroSerializer(laboratorios, many=True).data
        response = {'results': serializer}
        return Response(response)


class EmbalagemQldModelViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    queryset = EmbalagemQld.objects.all().order_by('-criado_em')
    serializer_class = EmbalagemQldSerializer
    permission_classes = (PermissaoParaCadastrarVisualizarEmbalagem,)
    pagination_class = EmbalagemQldPagination
    filterset_class = EmbalagensQldFilter
    filter_backends = (filters.DjangoFilterBackend,)

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return EmbalagemQldSerializer
        else:
            return EmbalagemQldCreateSerializer

    @action(detail=False, methods=['GET'], url_path='lista-nomes-embalagens')
    def lista_nomes_embalagens(self, request):
        queryset = EmbalagemQld.objects.all().values_list('nome', flat=True)
        response = {'results': queryset}
        return Response(response)

    @action(detail=False, methods=['GET'], url_path='lista-abreviacao-embalagens')
    def lista_abreviacoes_embalagens(self, request):
        queryset = EmbalagemQld.objects.all().values_list('abreviacao', flat=True)
        response = {'results': queryset}
        return Response(response)


class SolicitacaoDeAlteracaoCronogramaViewSet(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    filter_backends = (filters.DjangoFilterBackend, )
    pagination_class = CronogramaPagination
    permission_classes = (IsAuthenticated,)
    filterset_class = SolicitacaoAlteracaoCronogramaFilter

    def get_queryset(self):
        user = self.request.user
        if user.eh_fornecedor:
            return SolicitacaoAlteracaoCronograma.objects.filter(
                cronograma__empresa=user.vinculo_atual.instituicao
            ).order_by('-criado_em')
        return SolicitacaoAlteracaoCronograma.objects.all().order_by('-criado_em')

    def get_serializer_class(self):
        serializer_classes_map = {
            'list': SolicitacaoAlteracaoCronogramaSerializer,
            'retrieve': SolicitacaoAlteracaoCronogramaCompletoSerializer,
        }
        return serializer_classes_map.get(self.action, SolicitacaoDeAlteracaoCronogramaCreateSerializer)

    def get_permissions(self):
        permission_classes_map = {
            'list': (PermissaoParaVisualizarSolicitacoesAlteracaoCronograma,),
            'retrieve': (PermissaoParaVisualizarSolicitacoesAlteracaoCronograma,),
            'create': (PermissaoParaCriarSolicitacoesAlteracaoCronograma,),
        }
        action_permissions = permission_classes_map.get(self.action, [])
        self.permission_classes = (*self.permission_classes, *action_permissions)
        return super(SolicitacaoDeAlteracaoCronogramaViewSet, self).get_permissions()

    def _dados_dashboard(self, request, filtros=None):
        limit = int(request.query_params.get('limit', 10)) if 'limit' in request.query_params else 6
        offset = int(request.query_params.get('offset', 0)) if 'offset' in request.query_params else 0
        status = request.query_params.get('status', None)
        dados_dashboard = []
        lista_status = [
            status] if status else ServiceDashboardSolicitacaoAlteracaoCronogramaProfiles.get_dashboard_status(
            self.request.user)
        dados_dashboard = [{'status': status, 'dados':
                            SolicitacaoAlteracaoCronograma.objects.filtrar_por_status(status,
                                                                                      filtros, offset, limit + offset)}
                           for status in lista_status]
        if status:
            dados_dashboard[0]['total'] = SolicitacaoAlteracaoCronograma.objects.filtrar_por_status(
                status, filtros).count()
        return dados_dashboard

    @action(detail=False, methods=['GET'],
            url_path='dashboard', permission_classes=(PermissaoParaListarDashboardSolicitacaoAlteracaoCronograma,))
    def dashboard(self, request):
        serialized_data = PainelSolicitacaoAlteracaoCronogramaSerializer(self._dados_dashboard(request), many=True).data
        return Response({'results': serialized_data})

    @action(detail=False, methods=['GET'],
            url_path='dashboard-com-filtro', permission_classes=(
        PermissaoParaListarDashboardSolicitacaoAlteracaoCronograma,))
    def dashboard_com_filtro(self, request):
        filtros = request.query_params
        serialized_data = PainelSolicitacaoAlteracaoCronogramaSerializer(self._dados_dashboard(
            request, filtros), many=True).data
        return Response({'results': serialized_data})

    @transaction.atomic
    @action(detail=True, permission_classes=(PermissaoParaDarCienciaAlteracaoCronograma,),
            methods=['patch'], url_path='cronograma-ciente')
    def cronograma_ciente(self, request, uuid):
        usuario = request.user
        justificativa = request.data.get('justificativa_cronograma')
        try:
            solicitacao_cronograma = SolicitacaoAlteracaoCronograma.objects.get(uuid=uuid)
            solicitacao_cronograma.cronograma_ciente(user=usuario, justificativa=justificativa)
            solicitacao_cronograma.save()
            serializer = SolicitacaoAlteracaoCronogramaSerializer(solicitacao_cronograma)
            return Response(serializer.data)

        except ObjectDoesNotExist as e:
            return Response(dict(detail=f'Solicitação Cronograma informado não é valido: {e}'),
                            status=HTTP_406_NOT_ACCEPTABLE)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @transaction.atomic
    @action(detail=True, permission_classes=(PermissaoParaAnalisarDinutreSolicitacaoAlteracaoCronograma,),
            methods=['patch'], url_path='analise-dinutre')
    def analise_dinutre(self, request, uuid):
        usuario = request.user
        aprovado = request.data.get(('aprovado'), 'aprovado')
        try:
            solicitacao_cronograma = SolicitacaoAlteracaoCronograma.objects.get(uuid=uuid)
            if aprovado is True:
                solicitacao_cronograma.dinutre_aprova(user=usuario)
            elif aprovado is False:
                justificativa = request.data.get('justificativa_dinutre')
                solicitacao_cronograma.dinutre_reprova(user=usuario, justificativa=justificativa)
            else:
                raise ValidationError(f'Parametro aprovado deve ser true ou false.')
            solicitacao_cronograma.save()
            serializer = SolicitacaoAlteracaoCronogramaSerializer(solicitacao_cronograma)
            return Response(serializer.data)

        except ObjectDoesNotExist as e:
            return Response(dict(detail=f'Solicitação Cronograma informado não é valido: {e}'),
                            status=HTTP_406_NOT_ACCEPTABLE)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @transaction.atomic
    @action(detail=True, permission_classes=(PermissaoParaAnalisarDilogSolicitacaoAlteracaoCronograma,),
            methods=['patch'], url_path='analise-dilog')
    def analise_dilog(self, request, uuid):
        usuario = request.user
        aprovado = request.data.get(('aprovado'), 'aprovado')
        try:
            solicitacao_cronograma = SolicitacaoAlteracaoCronograma.objects.get(uuid=uuid)
            if aprovado is True:
                solicitacao_cronograma.dilog_aprova(user=usuario)
            elif aprovado is False:
                justificativa = request.data.get('justificativa_dilog')
                solicitacao_cronograma.dilog_reprova(user=usuario, justificativa=justificativa)
            else:
                raise ValidationError(f'Parametro aprovado deve ser true ou false.')
            solicitacao_cronograma.save()
            solicitacao_cronograma.cronograma.finaliza_solicitacao_alteracao(user=usuario)
            serializer = SolicitacaoAlteracaoCronogramaSerializer(solicitacao_cronograma)
            return Response(serializer.data)

        except ObjectDoesNotExist as e:
            return Response(dict(detail=f'Solicitação Cronograma informado não é valido: {e}'),
                            status=HTTP_406_NOT_ACCEPTABLE)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)


class UnidadeMedidaViewset(viewsets.ModelViewSet):
    lookup_field = 'uuid'
    queryset = UnidadeMedida.objects.all().order_by('-criado_em')
    permission_classes = (PermissaoParaCadastrarVisualizarUnidadesMedida,)
    pagination_class = UnidadeMedidaPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = UnidadeMedidaFilter

    def get_serializer_class(self):
        if self.action in ['retrieve', 'list']:
            return UnidadeMedidaSerialzer
        return UnidadeMedidaCreateSerializer

    @action(detail=False, methods=['GET'], url_path='lista-nomes-abreviacoes')
    def listar_nomes_abreviacoes(self, request):
        unidades_medida = self.get_queryset()
        serializer = NomeEAbreviacaoUnidadeMedidaSerializer(unidades_medida, many=True)
        response = {'results': serializer.data}
        return Response(response)
