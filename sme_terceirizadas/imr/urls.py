from django.urls import include, path
from rest_framework import routers

from .api import viewsets

router = routers.DefaultRouter()

router.register("periodos-de-visita", viewsets.PeriodoVisitaModelViewSet)
router.register(
    "formulario-supervisao", viewsets.FormularioSupervisaoRascunhoModelViewSet
)
router.register("formulario-diretor", viewsets.FormularioDiretorModelViewSet)


urlpatterns = [
    path("imr/", include(router.urls)),
]
