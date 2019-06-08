from django.urls import path, include
from rest_framework import routers
from .viewsets import CardapioViewSet

router = routers.DefaultRouter()

router.register('cardapio', CardapioViewSet, 'Cardapios')

urlpattern = [
    path('', include(router.urls))
]
