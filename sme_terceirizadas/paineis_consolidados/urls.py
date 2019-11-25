from django.urls import include, path
from rest_framework import routers

from .api import viewsets

router = routers.DefaultRouter()
router.register('codae-solicitacoes', viewsets.CODAESolicitacoesViewSet, 'codae_solicitacoes')
router.register('escola-solicitacoes', viewsets.EscolaSolicitacoesViewSet, 'escola_solicitacoes')
router.register('escola-relatorio', viewsets.EscolaRelatorioViewSet, 'escola_relatorio')
router.register('diretoria-regional-solicitacoes', viewsets.DRESolicitacoesViewSet, 'dre_solicitacoes')
router.register('terceirizada-solicitacoes', viewsets.TerceirizadaSolicitacoesViewSet, 'terceirizada_solicitacoes')

urlpatterns = [
    path('', include(router.urls)),
]
