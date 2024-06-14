from django.urls import include, path
from rest_framework import routers

from .api import viewsets

router = routers.DefaultRouter()
router.register(
    "classificacao", 
    viewsets.ClassificacaoViewSet, 
    "Parâmetros de Classificação"
)
urlpatterns = [
    path("", include(router.urls)),
]
