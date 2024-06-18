from django.urls import include, path
from rest_framework import routers

from .api import viewsets

router = routers.DefaultRouter()
router.register(
    'controle-sobras',
    viewsets.ControleSobrasViewSet,
    'controle-sobras'
)
router.register(
    'controle-restos',
    viewsets.ControleRestosViewSet,
    'controle-restos'
)
router.register(
    "parametros-classificacao", 
    viewsets.ClassificacaoViewSet, 
    "Parâmetros de Classificação"
)
urlpatterns = [
    path("", include(router.urls)),
]
