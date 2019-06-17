from django.contrib import admin
from .models import TipoRefeicao, Meal, Food, DayMenu, MenuStatus


@admin.register(Food)
class FoodAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active']
    ordering = ['title']


admin.site.register(TipoRefeicao)
admin.site.register(Meal)
admin.site.register(DayMenu)
admin.site.register(MenuStatus)
