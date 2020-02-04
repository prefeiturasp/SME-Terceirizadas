from django.db.models import Sum
from django.forms import ValidationError
from rest_framework import generics, mixins, serializers
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.viewsets import GenericViewSet
from xworkflows import InvalidTransitionError

from ...dados_comuns import constants
from ...paineis_consolidados.api.constants import FILTRO_CODIGO_EOL_ALUNO
from ...relatorios.relatorios import relatorio_dieta_especial
from ..forms import NegaDietaEspecialForm, SolicitacoesAtivasInativasPorAlunoForm
from ..models import (
    AlergiaIntolerancia,
    Alimento,
    ClassificacaoDieta,
    MotivoNegacao,
    SolicitacaoDietaEspecial,
    SolicitacoesDietaEspecialAtivasInativasPorAluno
)
from .serializers import (
    AlergiaIntoleranciaSerializer,
    AlimentoSerializer,
    ClassificacaoDietaSerializer,
    MotivoNegacaoSerializer,
    SolicitacaoDietaEspecialAutorizarSerializer,
    SolicitacaoDietaEspecialCreateSerializer,
    SolicitacaoDietaEspecialSerializer,
    SolicitacoesAtivasInativasPorAlunoSerializer
)
from .serializers_create import SolicitacaoDietaEspecialCreateSerializer


class SolicitacaoDietaEspecialViewSet(mixins.RetrieveModelMixin,
                                      mixins.ListModelMixin,
                                      mixins.CreateModelMixin,
                                      GenericViewSet):
    lookup_field = 'uuid'
    queryset = SolicitacaoDietaEspecial.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SolicitacaoDietaEspecialCreateSerializer
        elif self.action == 'autorizar':
            return SolicitacaoDietaEspecialAutorizarSerializer
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

    @action(detail=True, methods=['patch'])
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


    @action(detail=True, methods=['patch'], url_path=constants.ESCOLA_SOLICITA_INATIVACAO)
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

    @action(detail=True, methods=['patch'], url_path=constants.CODAE_AUTORIZA_INATIVACAO)
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

    @action(detail=True, methods=['patch'], url_path=constants.CODAE_NEGA_INATIVACAO)
    def codae_nega_inativacao(self, request, uuid=None):
        solicitacao_dieta_especial = self.get_object()
        justificativa = request.data.get('justificativa_negacao', '')
        try:
            solicitacao_dieta_especial.codae_nega_inativacao(user=request.user, justificativa=justificativa)
            serializer = self.get_serializer(solicitacao_dieta_especial)
            return Response(serializer.data)
        except InvalidTransitionError as e:
            return Response(dict(detail=f'Erro de transição de estado: {e}'), status=HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def negar(self, request, uuid=None):
        solicitacao = self.get_object()
        form = NegaDietaEspecialForm(request.data, instance=solicitacao)

        if not form.is_valid():
            return Response(form.errors)

        solicitacao.codae_nega(user=request.user)

        return Response({'mensagem': 'Solicitação de Dieta Especial Negada'})

    @action(detail=True, methods=['post'])
    def tomar_ciencia(self, request, uuid=None):
        solicitacao = self.get_object()

        solicitacao.terceirizada_toma_ciencia(user=request.user)

        return Response({'mensagem': 'Ciente da solicitação de dieta especial'})

    @action(detail=True, url_path=constants.RELATORIO,
            methods=['get'], permission_classes=[AllowAny])
    def relatorio(self, request, uuid=None):
        return relatorio_dieta_especial(request, solicitacao=self.get_object())

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
    queryset = Alimento.objects.all()
    serializer_class = AlimentoSerializer
    pagination_class = None
