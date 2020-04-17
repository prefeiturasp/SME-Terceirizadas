from django.urls import include, path
from rest_framework import routers

from .api import viewsets

router = routers.DefaultRouter()

router.register('produtos', viewsets.ProdutoViewSet, 'Produtos')

urlpatterns = [
    path('', include(router.urls)),
]
