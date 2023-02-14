from django.urls import include, path
from rest_framework import routers

from .api import viewsets

router = routers.DefaultRouter()

router.register('cronogramas', viewsets.CronogramaModelViewSet)
router.register('laboratorios', viewsets.LaboratorioModelViewSet)
router.register('embalagens', viewsets.EmbalagemQldModelViewSet)

router.register('solicitacao-de-alteracao-de-cronograma', viewsets.SolicitacaoDeAlteracaoCronogramaViewSet,
                basename='solicitacao-de-alteracao-de-cronograma')


urlpatterns = [
    path('', include(router.urls))
]
