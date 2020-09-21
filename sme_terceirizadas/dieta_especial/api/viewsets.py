from django.db import transaction
from django.db.models import Case, CharField, Count, Q, Sum, Value, When
from django.forms import ValidationError
from rest_framework import generics, mixins, serializers
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.viewsets import GenericViewSet
from xworkflows import InvalidTransitionError

from ...dados_comuns import constants
from ...dados_comuns.permissions import (
    PermissaoParaRecuperarDietaEspecial,
    UsuarioCODAEDietaEspecial,
    UsuarioEscola,
    UsuarioTerceirizada
)
from ...paineis_consolidados.api.constants import FILTRO_CODIGO_EOL_ALUNO
from ...relatorios.relatorios import (
    relatorio_dieta_especial,
    relatorio_dieta_especial_protocolo,
    relatorio_quantitativo_diag_dieta_especial,
    relatorio_quantitativo_solic_dieta_especial
)
from ..forms import (
    NegaDietaEspecialForm,
    RelatorioQuantitativoSolicDietaEspForm,
    SolicitacoesAtivasInativasPorAlunoForm
)
from ..models import (
    AlergiaIntolerancia,
    Alimento,
    ClassificacaoDieta,
    MotivoNegacao,
    SolicitacaoDietaEspecial,
    SolicitacoesDietaEspecialAtivasInativasPorAluno
)
from ..utils import RelatorioPagination
from .serializers import (
    AlergiaIntoleranciaSerializer,
    AlimentoSerializer,
    ClassificacaoDietaSerializer,
    MotivoNegacaoSerializer,
    RelatorioQuantitativoSolicDietaEspSerializer,
    SolicitacaoDietaEspecialAutorizarSerializer,
    SolicitacaoDietaEspecialSerializer,
    SolicitacaoDietaEspecialUpdateSerializer,
    SolicitacoesAtivasInativasPorAlunoSerializer
)
from .serializers_create import SolicitacaoDietaEspecialCreateSerializer


class SolicitacaoDietaEspecialViewSet(mixins.RetrieveModelMixin,
                                      mixins.ListModelMixin,
                                      mixins.CreateModelMixin,
                                      mixins.UpdateModelMixin,
                                      GenericViewSet):
    lookup_field = 'uuid'
    permission_classes = (IsAuthenticated,)
    queryset = SolicitacaoDietaEspecial.objects.all()

    def get_permissions(self):  # noqa C901
        if self.action == 'list':
            self.permission_classes = (IsAdminUser,)
        elif self.action == 'update':
            self.permission_classes = (IsAdminUser, UsuarioCODAEDietaEspecial)
        elif self.action == 'retrieve':
            self.permission_classes = (IsAuthenticated, PermissaoParaRecuperarDietaEspecial)
        elif self.action == 'create':
            self.permission_classes = (UsuarioEscola,)
        return super(SolicitacaoDietaEspecialViewSet, self).get_permissions()

    def get_serializer_class(self):  # noqa C901
        if self.action == 'create':
            return SolicitacaoDietaEspecialCreateSerializer
        elif self.action == 'autorizar':
            return SolicitacaoDietaEspecialAutorizarSerializer
        elif self.action in ['update', 'partial_update']:
            return SolicitacaoDietaEspecialUpdateSerializer
        elif self.action in ['relatorio_quantitativo_solic_dieta_esp', 'relatorio_quantitativo_diag_dieta_esp']:
            return RelatorioQuantitativoSolicDietaEspSerializer
        return SolicitacaoDietaEspecialSerializer

    @action(detail=False, methods=['get'], url_path=f'solicitacoes-aluno/{FILTRO_CODIGO_EOL_ALUNO}')
    def solicitacoes_vigentes(self, request, codigo_eol_aluno=None):
        solicitacoes = SolicitacaoDietaEspecial.objects.filter(
            aluno__codigo_eol=codigo_eol_aluno
        ).exclude(
            status=SolicitacaoDietaEspecial.workflow_class.CODAE_A_AUTORIZAR
        )
        page = self.paginate_queryset(solicitacoes)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @transaction.atomic  # noqa C901
    @action(detail=True, methods=['patch'], permission_classes=(UsuarioCODAEDietaEspecial,))  # noqa: C901
    def autorizar(self, request, uuid=None):
        solicitacao = self.get_object()
        if solicitacao.aluno.possui_dieta_especial_ativa:
            solicitacao.aluno.inativar_dieta_especial()
        serializer = self.get_serializer()
        try:
            serializer.update(solicitacao, request.data)
            solicitacao.codae_autoriza(user=request.user)
            return Response({'detail': 'Autorização de dieta especial realizada com sucesso'})
        except InvalidTransitionError as e:
            return Response({'detail': f'Erro na transição de estado {e}'}, status=HTTP_400_BAD_REQUEST)
        except serializers.ValidationError as e:
            return Response({'detail': f'Dados inválidos {e}'}, status=HTTP_400_BAD_REQUEST)

    @action(detail=True,
            methods=['patch'],
            url_path=constants.ESCOLA_SOLICITA_INATIVACAO,
            permission_classes=(UsuarioEscola,))
    def escola_solicita_inativacao(self, request, uuid=None):
        solicitacao_dieta_especial = self.get_object()
        justificativa = request.data.get('justificativa', '')
        try:
            solicitacao_dieta_especial.cria_anexos_inativacao(request.data.get('anexos'))
            solicitacao_dieta_especial.inicia_fluxo_inativacao(user=request.user, justificativa=justificativa)
            serializer = self.get_serializer(solicitacao_dieta_especial)
            return Response(serializer.data)
        except AssertionError as e:
            return Response(dict(detail=str(e)), status=HTTP_400_BAD_REQUEST)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True,
            methods=['patch'],
            url_path=constants.CODAE_AUTORIZA_INATIVACAO,
            permission_classes=(UsuarioCODAEDietaEspecial,))
    def codae_autoriza_inativacao(self, request, uuid=None):
        solicitacao_dieta_especial = self.get_object()
        try:
            solicitacao_dieta_especial.codae_autoriza_inativacao(user=request.user)
            solicitacao_dieta_especial.ativo = False
            solicitacao_dieta_especial.save()
            serializer = self.get_serializer(solicitacao_dieta_especial)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True,
            methods=['patch'],
            url_path=constants.CODAE_NEGA_INATIVACAO,
            permission_classes=(UsuarioCODAEDietaEspecial,))
    def codae_nega_inativacao(self, request, uuid=None):
        solicitacao_dieta_especial = self.get_object()
        justificativa = request.data.get('justificativa_negacao', '')
        try:
            solicitacao_dieta_especial.codae_nega_inativacao(user=request.user, justificativa=justificativa)
            serializer = self.get_serializer(solicitacao_dieta_especial)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True,
            methods=['patch'],
            url_path=constants.TERCEIRIZADA_TOMOU_CIENCIA_INATIVACAO,
            permission_classes=(UsuarioTerceirizada,))
    def terceirizada_toma_ciencia_inativacao(self, request, uuid=None):
        solicitacao_dieta_especial = self.get_object()
        try:
            solicitacao_dieta_especial.terceirizada_toma_ciencia_inativacao(user=request.user)
            serializer = self.get_serializer(solicitacao_dieta_especial)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], permission_classes=(UsuarioCODAEDietaEspecial,))
    def negar(self, request, uuid=None):
        solicitacao = self.get_object()
        form = NegaDietaEspecialForm(request.data, instance=solicitacao)

        if not form.is_valid():
            return Response(form.errors)

        solicitacao.codae_nega(user=request.user)

        return Response({'mensagem': 'Solicitação de Dieta Especial Negada'})

    @action(detail=True, methods=['post'], permission_classes=(UsuarioTerceirizada,))
    def tomar_ciencia(self, request, uuid=None):
        solicitacao = self.get_object()
        try:
            solicitacao.terceirizada_toma_ciencia(user=request.user)
            return Response({'mensagem': 'Ciente da solicitação de dieta especial'})
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, url_path=constants.RELATORIO,
            methods=['get'], permission_classes=[AllowAny])
    def relatorio(self, request, uuid=None):
        return relatorio_dieta_especial(request, solicitacao=self.get_object())

    @action(detail=True, url_path=constants.PROTOCOLO,
            methods=['get'], permission_classes=[AllowAny])
    def protocolo(self, request, uuid=None):
        return relatorio_dieta_especial_protocolo(request, solicitacao=self.get_object())

    @action(detail=True, methods=['post'], url_path=constants.ESCOLA_CANCELA_DIETA_ESPECIAL)
    def escola_cancela_solicitacao(self, request, uuid=None):
        justificativa = request.data.get('justificativa', '')
        solicitacao = self.get_object()
        try:
            solicitacao.cancelar_pedido(user=request.user, justificativa=justificativa)
            serializer = self.get_serializer(solicitacao)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    def get_queryset_relatorio_quantitativo_solic_dieta_esp(self, form, campos):  # noqa C901
        user = self.request.user
        qs = self.get_queryset()

        if user.tipo_usuario == 'escola':
            qs = qs.filter(aluno__escola=user.vinculo_atual.instituicao)
        elif form.cleaned_data['escola']:
            qs = qs.filter(aluno__escola__in=form.cleaned_data['escola'])
        elif user.tipo_usuario == 'diretoriaregional':
            qs = qs.filter(aluno__escola__diretoria_regional=user.vinculo_atual.instituicao)
        elif form.cleaned_data['dre']:
            qs = qs.filter(aluno__escola__diretoria_regional__in=form.cleaned_data['dre'])

        if form.cleaned_data['data_inicial']:
            qs = qs.filter(criado_em__date__gte=form.cleaned_data['data_inicial'])
        if form.cleaned_data['data_final']:
            qs = qs.filter(criado_em__date__lte=form.cleaned_data['data_final'])
        if form.cleaned_data['diagnostico']:
            qs = qs.filter(alergias_intolerancias__in=form.cleaned_data['diagnostico'])

        STATUS_PENDENTE = ['CODAE_A_AUTORIZAR']
        STATUS_ATIVA = ['CODAE_AUTORIZADO', 'TERCEIRIZADA_TOMOU_CIENCIA', 'ESCOLA_SOLICITOU_INATIVACAO',
                        'CODAE_NEGOU_INATIVACAO']
        STATUS_INATIVA = ['CODAE_AUTORIZOU_INATIVACAO', 'TERCEIRIZADA_TOMOU_CIENCIA_INATIVACAO',
                          'TERMINADA_AUTOMATICAMENTE_SISTEMA']

        when_data = {
            'ativas': When(status__in=STATUS_ATIVA, then=Value('Ativa')),
            'inativas': When(status__in=STATUS_INATIVA, then=Value('Inativa')),
            'pendentes': When(status__in=STATUS_PENDENTE, then=Value('Pendente'))
        }

        if form.cleaned_data['status'] == '':
            whens = when_data.values()
        else:
            whens = [when_data[form.cleaned_data['status']]]

        qs = qs.annotate(
            status_simples=Case(
                *whens,
                default=Value('Outros'),
                output_field=CharField()
            )
        ).exclude(status_simples='Outros').values(*campos).annotate(
            qtde_ativas=Count('status_simples', filter=Q(status_simples='Ativa')),
            qtde_inativas=Count('status_simples', filter=Q(status_simples='Inativa')),
            qtde_pendentes=Count('status_simples', filter=Q(status_simples='Pendente'))
        ).order_by(*campos)

        return qs

    def get_campos_relatorio_quantitativo_solic_dieta_esp(self, filtros):
        campos = ['aluno__escola__diretoria_regional__nome']
        if len(filtros['escola']) > 0:
            campos.append('aluno__escola__nome')
        return campos

    def get_campos_relatorio_quantitativo_diag_dieta_esp(self, filtros):
        user = self.request.user
        campos = []
        if user.tipo_usuario != 'diretoriaregional' and len(filtros['escola']) == 0:
            campos.append('aluno__escola__diretoria_regional__nome')
        else:
            if user.tipo_usuario != 'diretoriaregional':
                campos.append('aluno__escola__diretoria_regional__nome')
        if len(filtros['escola']) > 0:
            campos.append('aluno__escola__nome')
        campos.append('alergias_intolerancias__descricao')
        campos.append('aluno__data_nascimento__year')

        return campos

    @action(detail=False, methods=['POST'], url_path='relatorio-quantitativo-solic-dieta-esp')
    def relatorio_quantitativo_solic_dieta_esp(self, request):
        form = RelatorioQuantitativoSolicDietaEspForm(self.request.data)
        if not form.is_valid():
            raise ValidationError(form.errors)

        campos = self.get_campos_relatorio_quantitativo_solic_dieta_esp(form.cleaned_data)
        qs = self.get_queryset_relatorio_quantitativo_solic_dieta_esp(form, campos)

        self.pagination_class = RelatorioPagination
        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page if page is not None else qs, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['POST'], url_path='relatorio-quantitativo-diag-dieta-esp')
    def relatorio_quantitativo_diag_dieta_esp(self, request):
        form = RelatorioQuantitativoSolicDietaEspForm(self.request.data)
        if not form.is_valid():
            raise ValidationError(form.errors)

        campos = self.get_campos_relatorio_quantitativo_diag_dieta_esp(form.cleaned_data)
        qs = self.get_queryset_relatorio_quantitativo_solic_dieta_esp(form, campos)

        self.pagination_class = RelatorioPagination
        page = self.paginate_queryset(qs)
        serializer = self.get_serializer(page if page is not None else qs, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=False, methods=['POST'], url_path='imprime-relatorio-quantitativo-solic-dieta-esp')
    def imprime_relatorio_quantitativo_solic_dieta_esp(self, request):
        form = RelatorioQuantitativoSolicDietaEspForm(self.request.data)
        if not form.is_valid():
            raise ValidationError(form.errors)

        campos = self.get_campos_relatorio_quantitativo_solic_dieta_esp(form.cleaned_data)
        qs = self.get_queryset_relatorio_quantitativo_solic_dieta_esp(form, campos)
        user = self.request.user

        return relatorio_quantitativo_solic_dieta_especial(campos, form.cleaned_data, qs, user)

    @action(detail=False, methods=['POST'], url_path='imprime-relatorio-quantitativo-diag-dieta-esp')
    def imprime_relatorio_quantitativo_diag_dieta_esp(self, request):
        form = RelatorioQuantitativoSolicDietaEspForm(self.request.data)
        if not form.is_valid():
            raise ValidationError(form.errors)

        campos = self.get_campos_relatorio_quantitativo_diag_dieta_esp(form.cleaned_data)
        qs = self.get_queryset_relatorio_quantitativo_solic_dieta_esp(form, campos)
        user = self.request.user

        return relatorio_quantitativo_diag_dieta_especial(campos, form.cleaned_data, qs, user)


class SolicitacoesAtivasInativasPorAlunoView(generics.ListAPIView):
    serializer_class = SolicitacoesAtivasInativasPorAlunoSerializer
    pagination_class = PageNumberPagination

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        agregado = queryset.aggregate(Sum('ativas'), Sum('inativas'))

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            # TODO: Ver se tem como remover o UnorderedObjectListWarning
            # que acontece por passarmos mais dados do que apenas o serializer.data
            return self.get_paginated_response({
                'total_ativas': agregado['ativas__sum'],
                'total_inativas': agregado['inativas__sum'],
                'solicitacoes': serializer.data
            })

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'total_ativas': agregado['ativas__sum'],
            'total_inativas': agregado['inativas__sum'],
            'solicitacoes': serializer.data
        })

    def get_queryset(self):  # noqa C901
        form = SolicitacoesAtivasInativasPorAlunoForm(self.request.GET)
        if not form.is_valid():
            raise ValidationError(form.errors)

        qs = SolicitacoesDietaEspecialAtivasInativasPorAluno.objects.all()

        user = self.request.user

        if user.tipo_usuario == 'escola':
            qs = qs.filter(aluno__escola=user.vinculo_atual.instituicao)
        elif form.cleaned_data['escola']:
            qs = qs.filter(aluno__escola=form.cleaned_data['escola'])
        elif user.tipo_usuario == 'diretoriaregional':
            qs = qs.filter(aluno__escola__diretoria_regional=user.vinculo_atual.instituicao)
        elif form.cleaned_data['dre']:
            qs = qs.filter(aluno__escola__diretoria_regional=form.cleaned_data['dre'])

        if form.cleaned_data['codigo_eol']:
            codigo_eol = f"{int(form.cleaned_data['codigo_eol']):06d}"
            qs = qs.filter(aluno__codigo_eol=codigo_eol)
        elif form.cleaned_data['nome_aluno']:
            qs = qs.filter(aluno__nome__icontains=form.cleaned_data['nome_aluno'])

        if self.request.user.tipo_usuario == 'dieta_especial':
            return qs.order_by('aluno__escola__diretoria_regional__nome', 'aluno__escola__nome', 'aluno__nome')
        elif self.request.user.tipo_usuario == 'diretoriaregional':
            return qs.order_by('aluno__escola__nome', 'aluno__nome')
        return qs.order_by('aluno__nome')


class AlergiaIntoleranciaViewSet(mixins.ListModelMixin,
                                 mixins.RetrieveModelMixin,
                                 GenericViewSet):
    queryset = AlergiaIntolerancia.objects.all()
    serializer_class = AlergiaIntoleranciaSerializer
    pagination_class = None


class ClassificacaoDietaViewSet(mixins.ListModelMixin,
                                mixins.RetrieveModelMixin,
                                GenericViewSet):
    queryset = ClassificacaoDieta.objects.all()
    serializer_class = ClassificacaoDietaSerializer
    pagination_class = None


class MotivoNegacaoViewSet(mixins.ListModelMixin,
                           mixins.RetrieveModelMixin,
                           GenericViewSet):
    queryset = MotivoNegacao.objects.all()
    serializer_class = MotivoNegacaoSerializer
    pagination_class = None


class AlimentoViewSet(mixins.ListModelMixin,
                      mixins.RetrieveModelMixin,
                      GenericViewSet):
    queryset = Alimento.objects.all().order_by('nome')
    serializer_class = AlimentoSerializer
    pagination_class = None
