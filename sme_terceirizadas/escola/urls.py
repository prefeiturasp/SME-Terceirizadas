from django.urls import include, path
from rest_framework import routers

from .api import viewsets

router = routers.DefaultRouter()

router.register('vinculos-escolas', viewsets.VinculoEscolaViewSet, basename='vinculos-escolas')
router.register('vinculos-diretorias-regionais', viewsets.VinculoDiretoriaRegionalViewSet,
                basename='vinculos-diretorias-regionais')
router.register('vinculos-codae-gestao-alimentacao-terceirizada',
                viewsets.VinculoCODAEGestaoAlimentacaoTerceirizadaViewSet,
                basename='vinculos-codae-gestao-alimentacao-terceirizada')
router.register('escolas-simples', viewsets.EscolaSimplesViewSet, basename='escolas-simples')
router.register('escolas-simplissima', viewsets.EscolaSimplissimaViewSet, basename='escolas-simplissima')
router.register('periodos-escolares', viewsets.PeriodoEscolarViewSet, basename='periodos')
router.register('diretorias-regionais', viewsets.DiretoriaRegionalViewSet, basename='dres')
router.register('diretorias-regionais-simplissima', viewsets.DiretoriaRegionalSimplissimaViewSet,
                basename='dres-simplissima')
router.register('lotes', viewsets.LoteViewSet, basename='lotes')
router.register('tipos-gestao', viewsets.TipoGestaoViewSet, basename='tipos-gestao')
router.register('subprefeituras', viewsets.SubprefeituraViewSet, basename='subprefeituras')
router.register('codae', viewsets.CODAESimplesViewSet, basename='codae')
router.register('tipos-unidade-escolar', viewsets.TipoUnidadeEscolarViewSet, basename='tipos-unidade-escolar')
router.register('quantidade-alunos-por-periodo', viewsets.EscolaPeriodoEscolarViewSet,
                base_name='quantidade-alunos-por-periodo')

urlpatterns = [
    path('', include(router.urls))
]
