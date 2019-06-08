from django.urls import path, include
from rest_framework import routers
from .viewsets import MealKitViewSet, OrderMealKitViewSet

router = routers.DefaultRouter()

router.register('kit-lanche', MealKitViewSet, 'meal_kit')
router.register('solicitar-kit-lanche', OrderMealKitViewSet, 'solicitar_kit_lanche')

urlpatterns = [
    path('', include(router.urls))
]
