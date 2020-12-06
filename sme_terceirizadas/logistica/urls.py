from django.urls import include, path
from rest_framework import routers

from .api import viewsets

router = routers.DefaultRouter()

router.register('solicitacao-remessa', viewsets.SolicitacaoModelViewSet,
                basename='solicitacao-remessa')
router.register('solicitacao-remessa-envio', viewsets.SolicitacaoEnvioEmMassaModelViewSet,
                basename='solicitacao-remessa-envio')
router.register('guias-da-requisicao', viewsets.GuiaDaRequisicaoModelViewSet, basename='guias-da-requisicao')
router.register('alimentos-da-guia', viewsets.AlimentoDaGuiaModelViewSet, basename='alimentos-da-guia')

urlpatterns = [
    path('', include(router.urls)),
]
