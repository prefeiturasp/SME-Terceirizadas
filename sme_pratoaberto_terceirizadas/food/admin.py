from django.contrib import admin
from .models import MealType, Meal, Food, DayMenu, MenuStatus, MenuType


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active']
    ordering = ['title']


admin.site.register(MealType)
admin.site.register(Meal)
admin.site.register(DayMenu)
admin.site.register(MenuStatus)
admin.site.register(MenuType)
