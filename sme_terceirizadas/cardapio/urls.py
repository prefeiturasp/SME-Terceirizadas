from django.urls import include, path
from rest_framework import routers

from .api import viewsets

router = routers.DefaultRouter()
router.register('cardapios', viewsets.CardapioViewSet, 'Cardápios')
router.register('tipos-alimentacao', viewsets.TipoAlimentacaoViewSet, 'Tipos de Alimentação')
router.register('inversoes-dia-cardapio', viewsets.InversaoCardapioViewSet, 'Inversão de dia de Cardápio')
router.register('grupos-suspensoes-alimentacao', viewsets.GrupoSuspensaoAlimentacaoSerializerViewSet,
                'Grupos de suspensão de alimentação.')
router.register('alteracoes-cardapio', viewsets.AlteracoesCardapioViewSet, 'Alterações de Cardápio')
router.register('motivos-alteracao-cardapio', viewsets.MotivosAlteracaoCardapioViewSet,
                'Motivos de alteração de cardápio')
router.register('motivos-suspensao-cardapio', viewsets.MotivosSuspensaoCardapioViewSet,
                'Motivos de suspensão de cardápio')
router.register('alteracoes-cardapio-rascunho', viewsets.AlteracoesCardapioRascunhoViewSet,
                'Alterações de Cardápio Rascunho')
router.register('vinculos-tipo-alimentacao-u-e-periodo-escolar', viewsets.VinculoTipoAlimentacaoViewSet,
                'Vínculos de tipo de alimentação no periodo escolar e tipo de u.e')
urlpatterns = [
    path('', include(router.urls)),
]
