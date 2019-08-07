from django.urls import path, include
from rest_framework import routers

from .api import viewsets

router = routers.DefaultRouter()

router.register('escolas', viewsets.EscolaViewSet, basename='escolas')
router.register('escolas-simples', viewsets.EscolaSimplesViewSet, basename='escolas-simples')
router.register('periodos-escolares', viewsets.PeriodoEscolarViewSet, basename='periodos')
router.register('diretorias-regionais', viewsets.DiretoriaRegionalViewSet, basename='dres')
router.register('lotes', viewsets.LoteViewSet, basename='lotes')
router.register('tipos-gestao', viewsets.TipoGestaoViewSet, base_name="tipos-gestao")
router.register('subprefeituras', viewsets.SubprefeituraViewSet, base_name="subprefeituras")

urlpatterns = [
    path('', include(router.urls))
]
