from django.contrib import admin
from .models import DiretoriaRegional, PeriodoEscolar, Escola, GrupoEscolar


@admin.register(DiretoriaRegional)
class DiretoriaRegionalAdmin(admin.ModelAdmin):
    list_display = ['codigo']
    list_filter = ['codigo']


admin.site.register(Escola)
admin.site.register(PeriodoEscolar)
admin.site.register(GrupoEscolar)
