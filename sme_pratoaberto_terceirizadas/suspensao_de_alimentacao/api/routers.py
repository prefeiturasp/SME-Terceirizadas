from django.urls import path, include
from rest_framework import routers
from .viewsets import SuspensaoDeAlimentacaoViewSet

router = routers.DefaultRouter()

router.register('suspensao-de-alimentacao', SuspensaoDeAlimentacaoViewSet, 'suspensao_de_alimentacao')


urlpatterns = [
    path('', include(router.urls))
]
