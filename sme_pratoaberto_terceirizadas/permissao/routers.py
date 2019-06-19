from django.urls import path, include
from rest_framework import routers
from .api.viewsets import PermissaoViewSets

router = routers.DefaultRouter()

router.register('perfil', PermissaoViewSets)

urlpatterns = [
    path('', include(router.urls))
]
