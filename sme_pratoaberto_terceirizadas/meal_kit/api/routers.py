from django.urls import path, include
from rest_framework import routers
from .viewsets import MealKitViewSet, OrderMealKitViewSet, SolicitacaoUnificadaFormularioViewSet, \
    SolicitacaoUnificadaViewSet

router = routers.DefaultRouter()

router.register('kit-lanche', MealKitViewSet, 'meal_kit')
router.register('solicitar-kit-lanche', OrderMealKitViewSet, 'solicitar_kit_lanche')
router.register('solicitacao-unificada', SolicitacaoUnificadaViewSet,
                'solicitacao_unificada')
router.register('solicitacao-unificada-formulario', SolicitacaoUnificadaFormularioViewSet,
                'solicitacao_unificada_formulario')
router.register('kit-lanche', MealKitViewSet, 'meal_kit')
router.register('solicitar-kit-lanche', OrderMealKitViewSet, 'solicitar_kit_lanche')


urlpatterns = [
    path('', include(router.urls))
]
