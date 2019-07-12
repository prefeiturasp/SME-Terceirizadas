from django.urls import path, include
from rest_framework import routers
from .viewsets import KitLancheViewSet, SolicitacaoKitLancheViewSet, SolicitacaoUnificadaFormularioViewSet, \
    SolicitacaoUnificadaViewSet

router = routers.DefaultRouter()

router.register('kit-lanche', KitLancheViewSet, 'kit_lanche')
router.register('solicitar-kit-lanche', SolicitacaoKitLancheViewSet, 'solicitar_kit_lanche')
router.register('solicitacao-unificada', SolicitacaoUnificadaViewSet,
                'solicitacao_unificada')
router.register('solicitacao-unificada-formulario', SolicitacaoUnificadaFormularioViewSet,
                'solicitacao_unificada_formulario')

urlpatterns = [
    path('', include(router.urls))
]
