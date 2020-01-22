from rest_framework import generics, mixins
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST
from rest_framework.viewsets import GenericViewSet
from xworkflows import InvalidTransitionError

from ...dados_comuns import constants
from ...dados_comuns.utils import convert_base64_to_contentfile
from ...paineis_consolidados.api.constants import FILTRO_CODIGO_EOL_ALUNO
from ...relatorios.relatorios import relatorio_dieta_especial
from ..forms import AutorizaDietaEspecialForm, NegaDietaEspecialForm
from ..models import (
    AlergiaIntolerancia,
    Anexo,
    ClassificacaoDieta,
    MotivoNegacao,
    SolicitacaoDietaEspecial,
    SolicitacoesDietaEspecialAtivasInativasPorAluno,
    TipoDieta
)
from .serializers import (
    AlergiaIntoleranciaSerializer,
    ClassificacaoDietaSerializer,
    MotivoNegacaoSerializer,
    SolicitacaoDietaEspecialCreateSerializer,
    SolicitacaoDietaEspecialSerializer,
    SolicitacoesAtivasInativasPorAlunoSerializer,
    TipoDietaSerializer
)


class SolicitacaoDietaEspecialViewSet(mixins.RetrieveModelMixin,
                                      mixins.ListModelMixin,
                                      mixins.CreateModelMixin,
                                      GenericViewSet):
    lookup_field = 'uuid'
    queryset = SolicitacaoDietaEspecial.objects.all()

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return SolicitacaoDietaEspecialCreateSerializer
        return SolicitacaoDietaEspecialSerializer

    @action(detail=False, methods=['get'], url_path=f'solicitacoes-aluno/{FILTRO_CODIGO_EOL_ALUNO}')
    def solicitacoes_vigentes(self, request, codigo_eol_aluno=None):
        solicitacoes = SolicitacaoDietaEspecial.objects.filter(
            aluno__codigo_eol=codigo_eol_aluno,
            status=SolicitacaoDietaEspecial.workflow_class.CODAE_AUTORIZADO
        )
        page = self.paginate_queryset(solicitacoes)
        serializer = self.get_serializer(page, many=True)
        return self.get_paginated_response(serializer.data)

    @action(detail=True, methods=['post'])
    def autorizar(self, request, uuid=None):
        solicitacao = self.get_object()
        form = AutorizaDietaEspecialForm(request.data, instance=solicitacao)

        if not form.is_valid():
            return Response(form.errors)

        form.save()

        for p in request.data['protocolos']:
            data = convert_base64_to_contentfile(p.get('base64'))
            Anexo.objects.create(
                solicitacao_dieta_especial=solicitacao, arquivo=data, nome=p.get('nome', ''), eh_laudo_medico=False
            )

        solicitacao.codae_autoriza(user=request.user)

        solicitacao.save()

        return Response({'mensagem': 'Autorização de dieta especial realizada com sucesso'})

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
    queryset = SolicitacoesDietaEspecialAtivasInativasPorAluno.objects.all()
    serializer_class = SolicitacoesAtivasInativasPorAlunoSerializer


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


class TipoDietaViewSet(mixins.ListModelMixin,
                       mixins.RetrieveModelMixin,
                       GenericViewSet):
    queryset = TipoDieta.objects.all()
    serializer_class = TipoDietaSerializer
    pagination_class = None
