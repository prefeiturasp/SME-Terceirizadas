from django.contrib import admin
from .models import DiretorRegional, PeriodoEscolar, Escola, SchoolGroup


@admin.register(DiretorRegional)
class RegionalDirectorAdmin(admin.ModelAdmin):
    list_display = ['abbreviation']
    list_filter = ['abbreviation']


admin.site.register(Escola)
admin.site.register(PeriodoEscolar)
admin.site.register(SchoolGroup)
