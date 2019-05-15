from django.contrib import admin
from .models import RegionalDirector, SchoolPeriod, School


@admin.register(RegionalDirector)
class RegionalDirectorAdmin(admin.ModelAdmin):
    list_display = ['abbreviation']
    list_filter = ['abbreviation']


admin.site.register(School)
admin.site.register(SchoolPeriod)
