from django.urls import path, include
from rest_framework import routers

from .api import viewsets

router = routers.DefaultRouter()
router.register("dre-pendentes-aprovacao", viewsets.DrePendentesAprovacaoViewSet, 'dre_pendentes_aprovacao')
router.register("codae-solicitacoes", viewsets.CODAESolicitacoesViewSet, 'codae_solicitacoes')

urlpatterns = [
    path("", include(router.urls)),
]
