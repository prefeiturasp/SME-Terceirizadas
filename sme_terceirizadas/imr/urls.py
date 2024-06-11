from django.urls import include, path
from rest_framework import routers

from .api import viewsets

router = routers.DefaultRouter()

router.register("periodos-de-visita", viewsets.PeriodoVisitaModelViewSet)
router.register(
    "rascunho-formulario-supervisao", viewsets.FormularioSupervisaoRascunhoModelViewSet
)
router.register(
    "formulario-supervisao", viewsets.FormularioSupervisaoModelViewSet
)
router.register("formulario-diretor", viewsets.FormularioDiretorModelViewSet)
router.register("utensilios-cozinha", viewsets.UtensilioCozinhaViewSet)
router.register("utensilios-mesa", viewsets.UtensilioMesaViewSet)
router.register("equipamentos", viewsets.EquipamentoViewSet)
router.register("mobiliarios", viewsets.MobiliarioViewSet)
router.register("reparos-e-adaptacoes", viewsets.ReparoEAdaptacaoViewSet)
router.register("insumos", viewsets.InsumoViewSet)

urlpatterns = [
    path("imr/", include(router.urls)),
]
