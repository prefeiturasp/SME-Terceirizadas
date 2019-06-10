from django.urls import path, include
from rest_framework import routers
from .viewsets import CardapioViewSet, InverterDiaCardapioViewSet

router = routers.DefaultRouter()

router.register('cardapio', CardapioViewSet, 'Cardapios')
router.register('inverter-dia-cardapio', InverterDiaCardapioViewSet, 'Inverter dia de Cardápio')

urlpattern = [
    path('', include(router.urls))
]
