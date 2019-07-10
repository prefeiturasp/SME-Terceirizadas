from django.urls import path, include
from rest_framework import routers

from .api import viewsets

router = routers.DefaultRouter()

router.register('motivo-inclusao-continua', viewsets.MotivoInclusaoContinuaViewSet,
                basename='motivo-inclusao-continua')
router.register('motivo-inclusao-normal', viewsets.MotivoInclusaoNormalViewSet,
                basename='motivo-inclusao-normal')
router.register('inclusao-alimentacao-normal', viewsets.InclusaoAlimentacaoNormalViewSet,
                basename='inclusao-alimentacao-normal')
router.register('grupo-inclusao-alimentacao-normal', viewsets.GrupoInclusaoAlimentacaoNormalViewSet,
                basename='grupo-inclusao-alimentacao-normal')

urlpatterns = [
    path('', include(router.urls))
]
