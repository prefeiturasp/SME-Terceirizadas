from calendar import monthrange

from django.db.models import QuerySet
from django.template.loader import render_to_string
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from xworkflows import InvalidTransitionError

from ...dados_comuns import constants
from ...dados_comuns.api.serializers import LogSolicitacoesUsuarioSerializer
from ...dados_comuns.models import LogSolicitacoesUsuario
from ...dados_comuns.permissions import (
    UsuarioCODAEGestaoAlimentacao,
    UsuarioDiretoriaRegional,
    UsuarioEscolaTercTotal,
    ViewSetActionPermissionMixin
)
from ...escola.api.permissions import PodeCriarAdministradoresDaCODAEGestaoAlimentacaoTerceirizada
from ...escola.models import Escola
from ...relatorios.utils import html_to_pdf_file
from ..models import (
    AnexoOcorrenciaMedicaoInicial,
    CategoriaMedicao,
    DiaSobremesaDoce,
    Medicao,
    SolicitacaoMedicaoInicial,
    TipoContagemAlimentacao,
    ValorMedicao
)
from ..utils import build_tabela_somatorio_body, build_tabelas_relatorio_medicao, tratar_valores
from .permissions import EhAdministradorMedicaoInicialOuGestaoAlimentacao
from .serializers import (
    AnexoOcorrenciaMedicaoInicialSerializer,
    CategoriaMedicaoSerializer,
    DiaSobremesaDoceSerializer,
    MedicaoSerializer,
    SolicitacaoMedicaoInicialDashboardSerializer,
    SolicitacaoMedicaoInicialSerializer,
    TipoContagemAlimentacaoSerializer,
    ValorMedicaoSerializer
)
from .serializers_create import (
    DiaSobremesaDoceCreateManySerializer,
    MedicaoCreateUpdateSerializer,
    SolicitacaoMedicaoInicialCreateSerializer
)


class DiaSobremesaDoceViewSet(ViewSetActionPermissionMixin, ModelViewSet):
    permission_action_classes = {
        'list': [EhAdministradorMedicaoInicialOuGestaoAlimentacao],
        'create': [PodeCriarAdministradoresDaCODAEGestaoAlimentacaoTerceirizada],
        'delete': [PodeCriarAdministradoresDaCODAEGestaoAlimentacaoTerceirizada]
    }
    queryset = DiaSobremesaDoce.objects.all()
    lookup_field = 'uuid'

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return DiaSobremesaDoceCreateManySerializer
        return DiaSobremesaDoceSerializer

    def get_queryset(self):
        queryset = DiaSobremesaDoce.objects.all()
        if 'mes' in self.request.query_params and 'ano' in self.request.query_params:
            queryset = queryset.filter(data__month=self.request.query_params.get('mes'),
                                       data__year=self.request.query_params.get('ano'))
        if 'escola_uuid' in self.request.query_params:
            escola = Escola.objects.get(uuid=self.request.query_params.get('escola_uuid'))
            queryset = queryset.filter(tipo_unidade=escola.tipo_unidade)
        return queryset

    def create(self, request, *args, **kwargs):
        try:
            return super(DiaSobremesaDoceViewSet, self).create(request, *args, **kwargs)
        except AssertionError as error:
            if str(error) == '`create()` did not return an object instance.':
                return Response(status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['GET'], url_path='lista-dias')
    def lista_dias(self, request):
        try:
            lista_dias = self.get_queryset().values_list('data', flat=True).distinct()
            return Response(lista_dias, status=status.HTTP_200_OK)
        except Escola.DoesNotExist as e:
            return Response({'detail': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class SolicitacaoMedicaoInicialViewSet(
        mixins.RetrieveModelMixin,
        mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.UpdateModelMixin,
        GenericViewSet):
    lookup_field = 'uuid'
    permission_classes = [UsuarioEscolaTercTotal | UsuarioDiretoriaRegional]
    queryset = SolicitacaoMedicaoInicial.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SolicitacaoMedicaoInicialCreateSerializer
        return SolicitacaoMedicaoInicialSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        escola_uuid = request.query_params.get('escola')
        mes = request.query_params.get('mes')
        ano = request.query_params.get('ano')

        queryset = queryset.filter(escola__uuid=escola_uuid, mes=mes, ano=ano)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @staticmethod
    def get_lista_status():
        return [
            SolicitacaoMedicaoInicial.workflow_class.MEDICAO_ENVIADA_PELA_UE,
            SolicitacaoMedicaoInicial.workflow_class.MEDICAO_CORRECAO_SOLICITADA,
            SolicitacaoMedicaoInicial.workflow_class.MEDICAO_CORRIGIDA_PELA_UE,
            SolicitacaoMedicaoInicial.workflow_class.MEDICAO_APROVADA_PELA_DRE,
            SolicitacaoMedicaoInicial.workflow_class.MEDICAO_CORRECAO_SOLICITADA_CODAE,
            SolicitacaoMedicaoInicial.workflow_class.MEDICAO_CORRIGIDA_PARA_CODAE,
            SolicitacaoMedicaoInicial.workflow_class.MEDICAO_APROVADA_PELA_CODAE,
            'TODOS_OS_LANCAMENTOS'
        ]

    def condicao_raw_query_por_usuario(self):
        usuario = self.request.user
        if usuario.tipo_usuario == 'diretoriaregional':
            return f'AND diretoria_regional_id = {self.request.user.vinculo_atual.object_id} '
        elif usuario.tipo_usuario == 'escola':
            return f'AND %(solicitacao_medicao_inicial)s.escola_id = {self.request.user.vinculo_atual.object_id} '
        return ''

    def condicao_por_usuario(self, queryset):
        usuario = self.request.user
        if usuario.tipo_usuario == 'diretoriaregional':
            return queryset.filter(escola__diretoria_regional=usuario.vinculo_atual.instituicao)
        elif usuario.tipo_usuario == 'escola':
            return queryset.filter(escola=usuario.vinculo_atual.instituicao)
        return queryset

    def dados_dashboard(self, request, query_set: QuerySet, kwargs: dict, use_raw=True) -> list:
        limit = int(request.query_params.get('limit', 10))
        offset = int(request.query_params.get('offset', 0))

        sumario = []
        for workflow in self.get_lista_status():
            todos_lancamentos = workflow == 'TODOS_OS_LANCAMENTOS'
            if use_raw:
                data = {'escola': Escola._meta.db_table,
                        'logs': LogSolicitacoesUsuario._meta.db_table,
                        'solicitacao_medicao_inicial': SolicitacaoMedicaoInicial._meta.db_table,
                        'status': workflow}
                raw_sql = ('SELECT %(solicitacao_medicao_inicial)s.* FROM %(solicitacao_medicao_inicial)s '
                           'JOIN (SELECT uuid_original, MAX(criado_em) AS log_criado_em FROM %(logs)s '
                           'GROUP BY uuid_original) '
                           'AS most_recent_log '
                           'ON %(solicitacao_medicao_inicial)s.uuid = most_recent_log.uuid_original '
                           'LEFT JOIN (SELECT id AS escola_id, diretoria_regional_id FROM %(escola)s) '
                           'AS escola_solicitacao_medicao '
                           'ON escola_solicitacao_medicao.escola_id = %(solicitacao_medicao_inicial)s.escola_id ')
                if todos_lancamentos:
                    raw_sql += ('WHERE NOT %(solicitacao_medicao_inicial)s.status = '
                                "'MEDICAO_EM_ABERTO_PARA_PREENCHIMENTO_UE' ")
                else:
                    raw_sql += "WHERE %(solicitacao_medicao_inicial)s.status = '%(status)s' "
                raw_sql += self.condicao_raw_query_por_usuario()
                raw_sql += 'ORDER BY log_criado_em DESC'
                qs = query_set.raw(raw_sql % data)
            else:
                qs = (query_set.filter(status=workflow) if not todos_lancamentos
                      else query_set.exclude(status='MEDICAO_EM_ABERTO_PARA_PREENCHIMENTO_UE'))
                qs = qs.filter(**kwargs)
                qs = self.condicao_por_usuario(qs)
                qs = sorted(qs.distinct().all(),
                            key=lambda x: x.log_mais_recente.criado_em
                            if x.log_mais_recente else '-criado_em', reverse=True)
            sumario.append({
                'status': workflow,
                'total': len(qs),
                'dados': SolicitacaoMedicaoInicialDashboardSerializer(
                    qs[offset:limit + offset],
                    context={'request': self.request, 'workflow': workflow}, many=True).data
            })
        if request.user.tipo_usuario == constants.TIPO_USUARIO_ESCOLA:
            status_medicao_corrigida = ['MEDICAO_CORRIGIDA_PELA_UE', 'MEDICAO_CORRIGIDA_PARA_CODAE']
            sumario_medicoes_corrigidas = [s for s in sumario if s['status'] == status_medicao_corrigida]
            total_medicao_corrigida = 0
            total_dados = []
            for s in sumario_medicoes_corrigidas:
                total_medicao_corrigida += s['total']
                total_dados += s['dados']
            sumario.insert(2, {
                'status': 'MEDICAO_CORRIGIDA',
                'total': total_medicao_corrigida,
                'dados': total_dados
            })
            sumario = [s for s in sumario if s['status'] not in status_medicao_corrigida]
        return sumario

    def formatar_filtros(self, query_params):
        kwargs = {}
        if query_params.get('mes_ano'):
            data_splitted = query_params.get('mes_ano').split('_')
            kwargs['mes'] = data_splitted[0]
            kwargs['ano'] = data_splitted[1]
        if query_params.getlist('lotes_selecionados[]'):
            kwargs['escola__lote__uuid__in'] = query_params.getlist('lotes_selecionados[]')
        if query_params.get('tipo_unidade'):
            kwargs['escola__tipo_unidade__uuid'] = query_params.get('tipo_unidade')
        if query_params.get('escola'):
            kwargs['escola__codigo_eol'] = query_params.get('escola').split(' - ')[0]
        if query_params.get('dre'):
            kwargs['escola__diretoria_regional__uuid'] = query_params.get('dre')
        return kwargs

    def assinatura_ue(self, solicitacao):
        log_enviado_ue = solicitacao.logs.filter(status_evento=55)
        assinatura_escola = None
        if log_enviado_ue:
            razao_social = solicitacao.rastro_terceirizada.razao_social if solicitacao.rastro_terceirizada else ''
            usuario_escola = log_enviado_ue.first().usuario
            data_enviado_ue = log_enviado_ue.first().criado_em.strftime('%d/%m/%Y às %H:%M')
            assinatura_escola = f"""Documento conferido e registrado eletronicamente por {usuario_escola.nome},
                                    {usuario_escola.cargo}, {usuario_escola.registro_funcional},
                                    {solicitacao.escola.nome} em {data_enviado_ue}. O registro eletrônico da Medição
                                    Inicial é comprovação e ateste do serviço prestado à Unidade Educacional,
                                    pela empresa {razao_social}."""
        return assinatura_escola

    def assinatura_dre(self, solicitacao):
        log_aprovado_dre = solicitacao.logs.filter(status_evento=66)
        assinatura_dre = None
        if log_aprovado_dre:
            usuario_dre = log_aprovado_dre.first().usuario
            data_aprovado_dre = log_aprovado_dre.first().criado_em.strftime('%d/%m/%Y às %H:%M')
            assinatura_dre = f"""Documento conferido e aprovado eletronicamente por {usuario_dre.nome},
                                 {usuario_dre.cargo}, {usuario_dre.registro_funcional},
                                 {usuario_dre.vinculo_atual.instituicao.nome} em {data_aprovado_dre}."""
        return assinatura_dre

    @action(detail=False, methods=['GET'], url_path='dashboard',
            permission_classes=[UsuarioEscolaTercTotal | UsuarioDiretoriaRegional | UsuarioCODAEGestaoAlimentacao])
    def dashboard(self, request):
        query_set = self.get_queryset()
        possui_filtros = len(request.query_params)
        kwargs = self.formatar_filtros(request.query_params)
        response = {'results': self.dados_dashboard(query_set=query_set,
                                                    request=request,
                                                    kwargs=kwargs,
                                                    use_raw=not possui_filtros)}
        return Response(response)

    @action(detail=False, methods=['GET'], url_path='meses-anos',
            permission_classes=[UsuarioEscolaTercTotal | UsuarioDiretoriaRegional | UsuarioCODAEGestaoAlimentacao])
    def meses_anos(self, request):
        query_set = self.condicao_por_usuario(self.get_queryset()).exclude(
            status=SolicitacaoMedicaoInicial.workflow_class.MEDICAO_EM_ABERTO_PARA_PREENCHIMENTO_UE)
        meses_anos = query_set.values_list('mes', 'ano')
        meses_anos_unicos = []
        for mes_ano in meses_anos:
            mes_ano_obj = {'mes': mes_ano[0], 'ano': mes_ano[1]}
            if mes_ano_obj not in meses_anos_unicos:
                meses_anos_unicos.append(mes_ano_obj)
        return Response({'results': sorted(meses_anos_unicos, key=lambda k: (k['ano'], k['mes']), reverse=True)},
                        status=status.HTTP_200_OK)

    @action(detail=True, methods=['GET'], url_path='relatorio-pdf')
    def relatorio_pdf(self, request, uuid):
        solicitacao = self.get_object()
        tabelas = build_tabelas_relatorio_medicao(solicitacao)
        tabela_observacoes = list(
            solicitacao.medicoes.filter(
                valores_medicao__nome_campo='observacoes'
            ).values_list(
                'valores_medicao__dia',
                'periodo_escolar__nome',
                'valores_medicao__categoria_medicao__nome',
                'valores_medicao__valor',
                'grupo__nome'
            ).order_by(
                'valores_medicao__dia',
                'periodo_escolar__nome',
                'valores_medicao__categoria_medicao__nome'))
        tabela_somatorio = build_tabela_somatorio_body(solicitacao)
        html_string = render_to_string(
            f'relatorio_solicitacao_medicao_por_escola.html',
            {
                'solicitacao': solicitacao,
                'responsaveis': solicitacao.responsaveis.all(),
                'assinatura_escola': self.assinatura_ue(solicitacao),
                'assinatura_dre': self.assinatura_dre(solicitacao),
                'quantidade_dias_mes': range(1, monthrange(int(solicitacao.ano), int(solicitacao.mes))[1] + 1),
                'tabelas': tabelas,
                'tabela_observacoes': tabela_observacoes,
                'tabela_somatorio': tabela_somatorio
            }
        )

        return html_to_pdf_file(html_string, f'relatorio_dieta_especial.pdf')

    @action(detail=False, methods=['GET'], url_path='periodos-grupos-medicao',
            permission_classes=[UsuarioDiretoriaRegional | UsuarioCODAEGestaoAlimentacao | UsuarioEscolaTercTotal])
    def periodos_grupos_medicao(self, request):
        uuid = request.query_params.get('uuid_solicitacao')
        solicitacao = SolicitacaoMedicaoInicial.objects.get(uuid=uuid)
        retorno = []
        for medicao in solicitacao.medicoes.all():
            nome = None
            if medicao.grupo and medicao.periodo_escolar:
                nome = f'{medicao.grupo.nome} - {medicao.periodo_escolar.nome}'
            elif medicao.grupo and not medicao.periodo_escolar:
                nome = f'{medicao.grupo.nome}'
            elif medicao.periodo_escolar:
                nome = medicao.periodo_escolar.nome
            retorno.append({
                'uuid_medicao_periodo_grupo': medicao.uuid,
                'nome_periodo_grupo': nome,
                'periodo_escolar': medicao.periodo_escolar.nome if medicao.periodo_escolar else None,
                'grupo': medicao.grupo.nome if medicao.grupo else None,
                'status': medicao.status.name,
                'logs': LogSolicitacoesUsuarioSerializer(medicao.logs.all(), many=True).data
            })
        ORDEM_PERIODOS_GRUPOS = {
            'MANHA': 1,
            'TARDE': 2,
            'INTEGRAL': 3,
            'NOITE': 4,
            'VESPERTINO': 5,
            'Programas e Projetos - MANHA': 6,
            'Programas e Projetos - TARDE': 7,
            'Solicitações de Alimentação': 8,
            'ETEC': 9
        }

        return Response({'results': sorted(retorno, key=lambda k: ORDEM_PERIODOS_GRUPOS[k['nome_periodo_grupo']])},
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['GET'], url_path='quantidades-alimentacoes-lancadas-periodo-grupo',
            permission_classes=[UsuarioEscolaTercTotal])
    def quantidades_alimentacoes_lancadas_periodo_grupo(self, request):
        usuario = self.request.user
        escola = usuario.vinculo_atual.instituicao
        uuid = request.query_params.get('uuid_solicitacao')
        solicitacao = SolicitacaoMedicaoInicial.objects.get(uuid=uuid)
        retorno = []
        campos_a_desconsiderar = ['matriculados', 'numero_de_alunos', 'frequencia', 'observacoes']
        for medicao in solicitacao.medicoes.all():
            valores = []
            for valor_medicao in medicao.valores_medicao.exclude(categoria_medicao__nome__icontains='DIETA'):
                tem_nome_campo = [valor for valor in valores if valor['nome_campo'] == valor_medicao.nome_campo]
                if valor_medicao.nome_campo not in campos_a_desconsiderar:
                    if tem_nome_campo:
                        valores = [valor for valor in valores if valor['nome_campo'] != valor_medicao.nome_campo]
                        valores.append({
                            'nome_campo': valor_medicao.nome_campo,
                            'valor': tem_nome_campo[0]['valor'] + int(valor_medicao.valor)
                        })
                    else:
                        valores.append({
                            'nome_campo': valor_medicao.nome_campo,
                            'valor': int(valor_medicao.valor),
                        })
            valores = tratar_valores(escola, valores)
            retorno.append({
                'nome_periodo_grupo': medicao.nome_periodo_grupo,
                'valores': valores,
                'valor_total': sum(v['valor'] for v in valores)
            })
        return Response({'results': retorno}, status=status.HTTP_200_OK)


class TipoContagemAlimentacaoViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = TipoContagemAlimentacao.objects.filter(ativo=True)
    serializer_class = TipoContagemAlimentacaoSerializer
    pagination_class = None


class CategoriaMedicaoViewSet(mixins.ListModelMixin, GenericViewSet):
    queryset = CategoriaMedicao.objects.filter(ativo=True)
    serializer_class = CategoriaMedicaoSerializer
    pagination_class = None


class ValorMedicaoViewSet(
        mixins.ListModelMixin,
        mixins.DestroyModelMixin,
        GenericViewSet):
    lookup_field = 'uuid'
    queryset = ValorMedicao.objects.all()
    serializer_class = ValorMedicaoSerializer
    pagination_class = None

    def get_queryset(self):
        queryset = ValorMedicao.objects.all()
        nome_periodo_escolar = self.request.query_params.get('nome_periodo_escolar', None)
        uuid_solicitacao_medicao = self.request.query_params.get('uuid_solicitacao_medicao', None)
        nome_grupo = self.request.query_params.get('nome_grupo', None)
        uuid_medicao_periodo_grupo = self.request.query_params.get('uuid_medicao_periodo_grupo', None)
        if nome_periodo_escolar:
            queryset = queryset.filter(medicao__periodo_escolar__nome=nome_periodo_escolar)
        if nome_grupo:
            queryset = queryset.filter(medicao__grupo__nome=nome_grupo)
        elif not uuid_medicao_periodo_grupo:
            queryset = queryset.filter(medicao__grupo__isnull=True)
        if uuid_solicitacao_medicao:
            queryset = queryset.filter(medicao__solicitacao_medicao_inicial__uuid=uuid_solicitacao_medicao)
        if uuid_medicao_periodo_grupo:
            queryset = queryset.filter(medicao__uuid=uuid_medicao_periodo_grupo)
        return queryset

    def destroy(self, request, *args, **kwargs):
        instance = ValorMedicao.objects.get(uuid=kwargs.get('uuid'))
        medicao = instance.medicao
        self.perform_destroy(instance)
        if not medicao.valores_medicao.all().exists():
            medicao.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class MedicaoViewSet(
        mixins.RetrieveModelMixin,
        mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.UpdateModelMixin,
        GenericViewSet):
    lookup_field = 'uuid'
    queryset = Medicao.objects.all()

    def get_serializer_class(self):
        if self.action == 'dre_aprova_medicao':
            return MedicaoSerializer
        return MedicaoCreateUpdateSerializer

    @action(detail=True, methods=['PATCH'], url_path='dre-aprova-medicao',
            permission_classes=[UsuarioDiretoriaRegional])
    def dre_aprova_medicao(self, request, uuid=None):
        medicao = self.get_object()
        solicitacao_medicao_inicial = medicao.solicitacao_medicao_inicial
        medicoes_aguardando_aprovacao = solicitacao_medicao_inicial.medicoes.exclude(uuid=medicao.uuid)
        medicoes_aguardando_aprovacao = medicoes_aguardando_aprovacao.filter(status=medicao.status)
        try:
            medicao.dre_aprova(user=request.user)
            if not medicoes_aguardando_aprovacao:
                solicitacao_medicao_inicial.dre_aprova(user=request.user)
            serializer = self.get_serializer(medicao)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['PATCH'], url_path='dre-pede-correcao-medicao',
            permission_classes=[UsuarioDiretoriaRegional])
    def dre_pede_correcao_medicao(self, request, uuid=None):
        medicao = self.get_object()
        justificativa = request.data.get('justificativa', None)
        uuids_valores_medicao_para_correcao = request.data.get('uuids_valores_medicao_para_correcao', None)
        try:
            ValorMedicao.objects.filter(uuid__in=uuids_valores_medicao_para_correcao).update(habilitado_correcao=True)
            medicao.dre_pede_correcao(user=request.user, justificativa=justificativa)
            serializer = self.get_serializer(medicao)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=status.HTTP_400_BAD_REQUEST)


class OcorrenciaViewSet(
        mixins.RetrieveModelMixin,
        mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.UpdateModelMixin,
        GenericViewSet):
    lookup_field = 'uuid'
    queryset = AnexoOcorrenciaMedicaoInicial.objects.all()

    def get_serializer_class(self):
        return AnexoOcorrenciaMedicaoInicialSerializer

    @action(detail=True, methods=['PATCH'], url_path='dre-pede-correcao-ocorrencia',)
    def dre_pede_correcao_ocorrencia(self, request, uuid=None):
        object = self.get_object()
        ocorrencias = object.solicitacao_medicao_inicial.anexos.all()
        justificativa = request.data.get('justificativa', None)
        try:
            for ocorrencia in ocorrencias:
                ocorrencia.dre_pede_correcao(user=request.user, justificativa=justificativa)
            serializer = self.get_serializer(ocorrencia.solicitacao_medicao_inicial.anexos.all(), many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=status.HTTP_400_BAD_REQUEST)
