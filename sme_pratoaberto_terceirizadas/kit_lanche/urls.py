from django.urls import path, include
from rest_framework import routers

from .api import viewsets

router = routers.DefaultRouter()

router.register('motivos-solicitacao-unificada', viewsets.MotivoSolicitacaoUnificadaViewSet,
                basename='motivos-solicitacao-unificada')

router.register('kit-lanches', viewsets.KitLancheViewSet,
                basename='kit-lanches')

router.register('solicitacoes-kit-lanche-avulsa', viewsets.SolicitacaoKitLancheAvulsaViewSet,
                basename='solicitacao-kit-lanche-avulsa')

router.register('solicitacoes-kit-lanche-unificada', viewsets.SolicitacaoKitLancheUnificadaViewSet,
                basename='solicitacao-kit-lanche-unificada')

urlpatterns = [
    path('', include(router.urls))
]
