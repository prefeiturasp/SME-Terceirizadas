from django.urls import include, path
from rest_framework import routers

from .api import viewsets

router = routers.DefaultRouter()
router.register('dados-contrato-safi', viewsets.DadosContratoSAFIViewSet, basename='Dados Contrato SAFI')

urlpatterns = [
    path('', include(router.urls)),
]
