from django.urls import path, include
from rest_framework import routers

from .api import viewsets

router = routers.DefaultRouter()
router.register("alteracao_cardapio", viewsets.AlteracaoCardapioViewSet)
router.register("marcelo", viewsets.MarceloViewSet, basename='marcelo')
router.register("idade", viewsets.IdadeEscolarViewSet)


urlpatterns = [
    path("", include(router.urls)),
]
