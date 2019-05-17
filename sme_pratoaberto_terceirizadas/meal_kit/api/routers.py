from django.urls import path, include
from rest_framework import routers
from .viewsets import MealKitViewSet, OrderMealKitViewSet

router = routers.DefaultRouter()

router.register('kit-lanche', MealKitViewSet, basename='meal_kit')
router.register('solicitar-kit-lanche', OrderMealKitViewSet, basename='order_meal_kit')

urlpatterns = [
    path('', include(router.urls))
]
