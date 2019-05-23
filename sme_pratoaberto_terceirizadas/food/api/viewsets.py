from rest_framework import viewsets

from sme_pratoaberto_terceirizadas.food.api.serializers import MealSerializer
from sme_pratoaberto_terceirizadas.food.models import Meal


class MealViewSet(viewsets.ModelViewSet):
    queryset = Meal.objects.all()
    serializer_class = MealSerializer
