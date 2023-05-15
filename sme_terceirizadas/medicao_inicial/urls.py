from django.urls import include, path
from rest_framework import routers

from .api import viewsets

router = routers.DefaultRouter()

router.register('categorias-medicao', viewsets.CategoriaMedicaoViewSet)
router.register('dias-sobremesa-doce', viewsets.DiaSobremesaDoceViewSet)
router.register('medicao', viewsets.MedicaoViewSet)
router.register('solicitacao-medicao-inicial', viewsets.SolicitacaoMedicaoInicialViewSet)
router.register('tipo-contagem-alimentacao', viewsets.TipoContagemAlimentacaoViewSet)
router.register('valores-medicao', viewsets.ValorMedicaoViewSet)
router.register('ocorrencia', viewsets.OcorrenciaViewSet)

urlpatterns = [
    path('medicao-inicial/', include(router.urls))
]
