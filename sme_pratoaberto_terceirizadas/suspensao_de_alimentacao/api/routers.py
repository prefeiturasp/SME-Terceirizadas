from django.urls import path, include
from rest_framework import routers
from .viewsets import SuspensaoDeAlimentacaoViewSet

router = routers.DefaultRouter()

router.register('suspensao-de-alimentacao', SuspensaoDeAlimentacaoViewSet, 'Suspensão de Alimentação')


urlpatterns = [
    path('', include(router.urls))
]
