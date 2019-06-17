from django.urls import path, include
from rest_framework import routers
from .api.viewsets import EscolaViewSet

router = routers.DefaultRouter()

router.register('escola', EscolaViewSet)

urlpatterns = [
    path('', include(router.urls))
]
