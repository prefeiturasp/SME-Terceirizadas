from django.urls import path, include
from rest_framework import routers
from .api.viewsets import SchoolViewSet

router = routers.DefaultRouter()

router.register('school', SchoolViewSet)

urlpatterns = [
    path('', include(router.urls))
]
