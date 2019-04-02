from django.contrib import admin
from .models import RegionalDirector


@admin.register(RegionalDirector)
class RegionalDirectorAdmin(admin.ModelAdmin):
    list_display = ['abbreviation']
    list_filter = ['abbreviation']

# Register your models here.
