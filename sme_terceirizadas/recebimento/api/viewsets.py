from rest_framework import mixins, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from sme_terceirizadas.dados_comuns.permissions import (
    PermissaoParaVisualizarQuestoesConferencia,
)

from ..models import QuestaoConferencia, QuestoesPorProduto
from .serializers.serializers import (
    QuestaoConferenciaSerializer,
    QuestaoConferenciaSimplesSerializer,
)
from .serializers.serializers_create import QuestoesPorProdutoCreateSerializer


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
        questoes = self.get_queryset()
        serializer = QuestaoConferenciaSimplesSerializer(questoes, many=True).data
        response = {"results": serializer}
        return Response(response)


class QuestoesPorProdutoModelViewSet(mixins.CreateModelMixin, viewsets.GenericViewSet):
    lookup_field = "uuid"
    queryset = QuestoesPorProduto.objects.all()
    permission_classes = (PermissaoParaVisualizarQuestoesConferencia,)
    serializer_class = QuestoesPorProdutoCreateSerializer
