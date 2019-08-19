from django.urls import path, include
from rest_framework import routers

from .api import viewsets

router = routers.DefaultRouter()
router.register("dre-pendentes-aprovacao", viewsets.DrePendentesAprovacaoViewSet, 'dre_pendentes_aprovacao')


urlpatterns = [
    path("", include(router.urls)),
]
