from django.urls import include, path
from rest_framework import routers

from .api import viewsets

router = routers.DefaultRouter()

router.register('solicitacoes-dieta-especial', viewsets.SolicitacaoDietaEspecialViewSet,
                basename='Solicitações de dieta especial')

urlpatterns = [
    path('', include(router.urls))
]
