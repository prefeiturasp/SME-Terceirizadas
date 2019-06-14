from django.contrib import admin
from .models import DiretorRegional, PeriodoEscolar, Escola, GrupoEscolar


@admin.register(DiretorRegional)
class RegionalDirectorAdmin(admin.ModelAdmin):
    list_display = ['codigo']
    list_filter = ['codigo']


admin.site.register(Escola)
admin.site.register(PeriodoEscolar)
admin.site.register(GrupoEscolar)
