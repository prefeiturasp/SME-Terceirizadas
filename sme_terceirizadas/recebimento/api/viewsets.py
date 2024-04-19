from django_filters import rest_framework as filters
from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from ...dados_comuns.api.paginations import DefaultPagination
from ..models import FichaDeRecebimento, QuestaoConferencia, QuestoesPorProduto
from .filters import QuestoesPorProdutoFilter
from .permissions import (
    PermissaoParaCadastrarFichaRecebimento,
    PermissaoParaVisualizarQuestoesConferencia,
)
from .serializers.serializers import (
    QuestaoConferenciaSerializer,
    QuestaoConferenciaSimplesSerializer,
    QuestoesPorProdutoSerializer,
    QuestoesPorProdutoSimplesSerializer,
)
from .serializers.serializers_create import (
    FichaDeRecebimentoRascunhoSerializer,
    QuestoesPorProdutoCreateSerializer,
)


class QuestoesConferenciaModelViewSet(viewsets.ReadOnlyModelViewSet):
    lookup_field = "uuid"
    queryset = QuestaoConferencia.objects.order_by("posicao")
    permission_classes = (PermissaoParaVisualizarQuestoesConferencia,)
    serializer_class = QuestaoConferenciaSerializer

    def list(self, request, *args, **kwargs):
        qs = self.get_queryset()
        primarias = qs.filter(
            tipo_questao__contains=QuestaoConferencia.TIPO_QUESTAO_PRIMARIA
        )
        secundarias = qs.filter(
            tipo_questao__contains=QuestaoConferencia.TIPO_QUESTAO_SECUNDARIA
        )

        return Response(
            {
                "results": {
                    "primarias": QuestaoConferenciaSerializer(
                        primarias, many=True
                    ).data,
                    "secundarias": QuestaoConferenciaSerializer(
                        secundarias, many=True
                    ).data,
                }
            }
        )

    @action(detail=False, methods=["GET"], url_path="lista-simples-questoes")
    def lista_simples_questoes(self, request):
        questoes = self.get_queryset().order_by("questao").distinct("questao")
        serializer = QuestaoConferenciaSimplesSerializer(questoes, many=True).data
        response = {"results": serializer}
        return Response(response)


class QuestoesPorProdutoModelViewSet(viewsets.ModelViewSet):
    lookup_field = "uuid"
    queryset = QuestoesPorProduto.objects.all().order_by("-criado_em")
    permission_classes = (PermissaoParaVisualizarQuestoesConferencia,)
    serializer_class = QuestoesPorProdutoSerializer
    pagination_class = DefaultPagination
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = QuestoesPorProdutoFilter

    def get_serializer_class(self):
        return {
            "list": QuestoesPorProdutoSerializer,
            "retrieve": QuestoesPorProdutoSimplesSerializer,
        }.get(self.action, QuestoesPorProdutoCreateSerializer)


class FichaDeRecebimentoRascunhoViewSet(
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    lookup_field = "uuid"
    serializer_class = FichaDeRecebimentoRascunhoSerializer
    queryset = FichaDeRecebimento.objects.all().order_by("-criado_em")
    permission_classes = (PermissaoParaCadastrarFichaRecebimento,)
