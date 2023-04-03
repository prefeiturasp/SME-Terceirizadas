from django.urls import include, path
from rest_framework import routers

from .api import viewsets

router = routers.DefaultRouter()

router.register('terceirizadas', viewsets.TerceirizadaViewSet, basename='Terceirizadas')
router.register('empresas-nao-terceirizadas', viewsets.EmpresaNaoTerceirizadaViewSet, basename='empresas')
router.register('editais', viewsets.EditalViewSet, basename='Editais')
router.register('editais-contratos', viewsets.EditalContratosViewSet, basename='editais_e_contratos')
router.register('vinculos-terceirizadas', viewsets.VinculoTerceirizadaViewSet, basename='Vínculos - Terceirizadas')
router.register('emails-terceirizadas-modulos', viewsets.EmailTerceirizadaPorModuloViewSet,
                basename='emails-terceirizadas')
router.register('contratos', viewsets.ContratoViewSet, basename='Contratos')

urlpatterns = [
    path('', include(router.urls))
]
