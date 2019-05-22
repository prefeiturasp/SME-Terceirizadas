from django.urls import path, include
from rest_framework import routers

from .api import viewsets

router = routers.DefaultRouter()
router.register("/alteracao", viewsets.AlteracaoCardapioViewSet)

urlpatterns = [
    path(r"cardapio", include(router.urls)),
]
