from django.urls import include, path
from rest_framework import routers

from .api import viewsets

router = routers.DefaultRouter()
router.register('dre-pendentes-aprovacao', viewsets.DrePendentesAprovacaoViewSet, 'dre_pendentes_aprovacao')
router.register('codae-solicitacoes', viewsets.CODAESolicitacoesViewSet, 'codae_solicitacoes')
router.register('escola-solicitacoes', viewsets.EscolaSolicitacoesViewSet, 'escola_solicitacoes')
router.register('diretoria-regional-solicitacoes', viewsets.DRESolicitacoesViewSet, 'dre_solicitacoes')

urlpatterns = [
    path('', include(router.urls)),
]
