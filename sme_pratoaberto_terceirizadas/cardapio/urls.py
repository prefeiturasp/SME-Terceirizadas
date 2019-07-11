from django.urls import path, include
from rest_framework import routers

from .api import viewsets

router = routers.DefaultRouter()
router.register("cardapio", viewsets.CardapioViewSet, 'Cardápio')
router.register("tipo-alimentacao", viewsets.TipoAlimentacaoViewSet, 'Tipo de Alimetação')
router.register("inverte-dia-cardapio", viewsets.InversaoCardapioViewSet, 'Inversão de dia de Cardápio')

urlpatterns = [
    path("", include(router.urls)),
]
