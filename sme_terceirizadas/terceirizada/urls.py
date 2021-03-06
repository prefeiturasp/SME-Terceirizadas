from django.urls import include, path
from rest_framework import routers

from .api import viewsets

router = routers.DefaultRouter()

router.register('terceirizadas', viewsets.TerceirizadaViewSet, basename='Terceirizadas')
router.register('editais', viewsets.EditalViewSet, basename='Editais')
router.register('editais-contratos', viewsets.EditalContratosViewSet, basename='editais_e_contratos')
router.register('vinculos-terceirizadas', viewsets.VinculoTerceirizadaViewSet, basename='Vínculos - Terceirizadas')

urlpatterns = [
    path('', include(router.urls))
]
