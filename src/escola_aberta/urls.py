from django.urls import include, path
from rest_framework import routers

from .api import viewsets

router = routers.DefaultRouter()

router.register("escola-aberta", viewsets.EscolaAbertaViewSet, basename="escola-aberta")

urlpatterns = [path("", include(router.urls))]
