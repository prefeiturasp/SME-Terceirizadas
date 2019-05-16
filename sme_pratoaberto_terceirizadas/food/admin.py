from django.contrib import admin
from .models import MealType, Meal, Food, DayMenu, MenuStatus, MenuType


admin.site.register(MealType)
admin.site.register(Meal)
admin.site.register(Food)
admin.site.register(DayMenu)
admin.site.register(MenuStatus)
admin.site.register(MenuType)
