from django.urls import include, path
from rest_framework import routers

from .api import viewsets

router = routers.DefaultRouter()

router.register('solicitacoes-remessas', viewsets.SolicitacaoModelViewSet,
                basename='solicitacoes-remessas')

urlpatterns = [
    path('', include(router.urls)),
]
