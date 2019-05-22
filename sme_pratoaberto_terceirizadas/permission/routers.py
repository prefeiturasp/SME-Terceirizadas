from django.urls import path, include
from rest_framework import routers
from .api.viewsets import PermissionViewSets

router = routers.DefaultRouter()

router.register('profile', PermissionViewSets)

urlpatterns = [
    path('', include(router.urls))
]
