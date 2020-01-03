from django.urls import include, path
from rest_framework import routers

from .api import viewsets
from .constants import (
    ENDPOINT_ALERGIAS_INTOLERANCIAS,
    ENDPOINT_CLASSIFICACOES_DIETA,
    ENDPOINT_MOTIVOS_NEGACAO,
    ENDPOINT_TIPOS_DIETA_ESPECIAL
)

router = routers.DefaultRouter()

router.register('solicitacoes-dieta-especial', viewsets.SolicitacaoDietaEspecialViewSet,
                basename='Solicitações de dieta especial')
router.register(ENDPOINT_ALERGIAS_INTOLERANCIAS, viewsets.AlergiaIntoleranciaViewSet,
                basename='Alergias/Intolerâncias alimentares')
router.register(ENDPOINT_CLASSIFICACOES_DIETA, viewsets.ClassificacaoDietaViewSet,
                basename='Classificação de dieta especial')
router.register(ENDPOINT_MOTIVOS_NEGACAO, viewsets.MotivoNegacaoViewSet,
                basename='Motivos de negação de dieta especial')
router.register(ENDPOINT_TIPOS_DIETA_ESPECIAL, viewsets.TipoDietaViewSet,
                basename='Tipos de dieta especial')

urlpatterns = [
    path('', include(router.urls))
]
