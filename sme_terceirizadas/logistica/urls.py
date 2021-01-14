from django.urls import include, path
from rest_framework import routers

from .api import viewsets
from .api.soup import views as soup_views

router = routers.DefaultRouter()

router.register('solicitacao-remessa', viewsets.SolicitacaoModelViewSet,
                basename='solicitacao-remessa')
router.register('solicitacao-remessa-envio', viewsets.SolicitacaoEnvioEmMassaModelViewSet,
                basename='solicitacao-remessa-envio')
router.register('solicitacao-remessa-cancelamento', viewsets.SolicitacaoCancelamentoModelViewSet,
                basename='solicitacao-remessa-cancelamento')
router.register('guias-da-requisicao', viewsets.GuiaDaRequisicaoModelViewSet, basename='guias-da-requisicao')
router.register('alimentos-da-guia', viewsets.AlimentoDaGuiaModelViewSet, basename='alimentos-da-guia')

urlpatterns = [
    path('', include(router.urls)),
    path('webserver/solicitacao-remessa/', soup_views.solicitacao_application),
]
