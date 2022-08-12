from django.urls import include, path
from rest_framework import routers

from .api import viewsets

router = routers.DefaultRouter()

router.register('dias-sobremesa-doce', viewsets.DiaSobremesaDoceViewSet)
router.register('solicitacao-medicao-inicial', viewsets.SolicitacaoMedicaoInicialViewSet)
router.register('tipo-contagem-alimentacao', viewsets.TipoContagemAlimentacaoViewSet)

urlpatterns = [
    path('medicao-inicial/', include(router.urls))
]
