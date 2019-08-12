from django.urls import path, include
from rest_framework import routers

from .api import viewsets

router = routers.DefaultRouter()

router.register('terceirizadas', viewsets.TerceirizadaViewSet, basename='Terceirizadas')
router.register('editais', viewsets.EditalViewSet, basename='Editais')
router.register('editais-contratos', viewsets.EditalContratosViewSet, basename='editais_e_contratos')

urlpatterns = [
    path('', include(router.urls))
]
