from django.urls import include, path
from rest_framework import routers

from .api import viewsets

router = routers.DefaultRouter()

router.register("periodos-de-visita", viewsets.PeriodoVisitaModelViewSet)


urlpatterns = [
    path("imr/", include(router.urls)),
]
