from django.contrib import admin
from .models import MealKit


@admin.register(MealKit)
class MealKitAdmin(admin.ModelAdmin):
    list_display = ('name',)
