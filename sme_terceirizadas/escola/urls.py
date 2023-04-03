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
router.register('vinculos-codae-gestao-dieta-especial',
                viewsets.VinculoCODAEGestaoDietaEspecialViewSet,
                basename='vinculos-codae-gestao-dieta-especial')
router.register('vinculos-codae-gestao-produtos',
                viewsets.VinculoCODAEGestaoProdutosViewSet,
                basename='vinculos-codae-gestao-produtos')
router.register('vinculos-codae-supervisao-nutricao',
                viewsets.VinculoCODAESupervisaoNutricaoViewSet,
                basename='vinculos-codae-supervisao-nutricao')
router.register('faixas-etarias', viewsets.FaixaEtariaViewSet, basename='Faixas Etárias')
router.register('escola-quantidade-alunos-por-periodo-e-faixa-etaria',
                viewsets.EscolaQuantidadeAlunosPorPeriodoEFaixaViewSet,
                basename='escola-quantidade-alunos-por-periodo-e-faixa-etaria')
router.register('escolas-simples', viewsets.EscolaSimplesViewSet, basename='escolas-simples')
router.register('escolas-simplissima', viewsets.EscolaSimplissimaViewSet, basename='escolas-simplissima')
router.register('escolas-simplissima-com-dre', viewsets.EscolaSimplissimaComDREViewSet, basename='escolas-simplissima')
router.register('escolas-simplissima-com-dre-unpaginated', viewsets.EscolaSimplissimaComDREUnpaginatedViewSet,
                basename='escolas-simplissima-unpaginated')
router.register('periodos-escolares', viewsets.PeriodoEscolarViewSet, basename='periodos')
router.register('periodos-com-matriculados-por-ue', viewsets.PeriodosComMatriculadosPorUEViewSet,
                basename='periodos-com-matriculados')
router.register('diretorias-regionais', viewsets.DiretoriaRegionalViewSet, basename='dres')
router.register('diretorias-regionais-simplissima', viewsets.DiretoriaRegionalSimplissimaViewSet,
                basename='dres-simplissima')
router.register('lotes-simples', viewsets.LoteSimplesViewSet, basename='lotes-simples')
router.register('lotes', viewsets.LoteViewSet, basename='lotes')
router.register('tipos-gestao', viewsets.TipoGestaoViewSet, basename='tipos-gestao')
router.register('subprefeituras', viewsets.SubprefeituraViewSet, basename='subprefeituras')
router.register('codae', viewsets.CODAESimplesViewSet, basename='codae')
router.register('tipos-unidade-escolar', viewsets.TipoUnidadeEscolarViewSet, basename='tipos-unidade-escolar')
router.register('quantidade-alunos-por-periodo', viewsets.EscolaPeriodoEscolarViewSet,
                basename='quantidade-alunos-por-periodo')
router.register('alunos', viewsets.AlunoViewSet,
                basename='alunos')
router.register('matriculados-no-mes', viewsets.LogAlunosMatriculadosPeriodoEscolaViewSet,
                basename='matriculados-no-mes')
router.register('dias-calendario', viewsets.DiaCalendarioViewSet,
                basename='dias-calendario')
router.register('relatorio-alunos-matriculados', viewsets.RelatorioAlunosMatriculadosViewSet,
                basename='relatorio-alunos-matriculados')

urlpatterns = [
    path('', include(router.urls))
]
