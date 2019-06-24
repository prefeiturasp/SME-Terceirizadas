from django.contrib import admin

from sme_pratoaberto_terceirizadas.escola.models import TipoGestao, TipoUnidadeEscolar, SubPrefeitura, IdadeEscolar
from .models import DiretoriaRegional, PeriodoEscolar, Escola


@admin.register(DiretoriaRegional)
class DiretoriaRegionalAdmin(admin.ModelAdmin):
    list_display = ['nome']
    list_filter = ['nome']


admin.site.register(Escola)
admin.site.register(PeriodoEscolar)
admin.site.register(TipoGestao)
admin.site.register(TipoUnidadeEscolar)
admin.site.register(SubPrefeitura)
admin.site.register(IdadeEscolar)
