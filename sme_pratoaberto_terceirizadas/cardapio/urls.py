from django.urls import path, include
from rest_framework import routers

from .api import viewsets

router = routers.DefaultRouter()
router.register("cardapios", viewsets.CardapioViewSet, 'Cardápios')
router.register("tipos-alimentacao", viewsets.TipoAlimentacaoViewSet, 'Tipos de Alimentação')
router.register("inverte-dia-cardapio", viewsets.InversaoCardapioViewSet, 'Inversão de dia de Cardápio')
router.register("suspensoes-alimentacao", viewsets.SuspensaoAlimentacaoViewSet, "Suspensão de alimentação")
router.register("alteracoes-cardapio", viewsets.AlteracoesCardapioViewSet, "Alterações de Cardápio")

urlpatterns = [
    path("", include(router.urls)),
]
