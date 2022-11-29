from django.urls import include, path
from rest_framework import routers

from .api import viewsets

router = routers.DefaultRouter()

router.register('cronogramas', viewsets.CronogramaModelViewSet)
router.register('laboratorios', viewsets.LaboratorioModelViewSet)
router.register('embalagens', viewsets.EmbalagemQldModelViewSet)

urlpatterns = [
    path('', include(router.urls))
]
