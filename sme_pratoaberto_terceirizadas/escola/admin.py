from django.contrib import admin

from .models import (
    Codae, DiretoriaRegional, Escola, FaixaIdadeEscolar, Lote,
    PeriodoEscolar, Subprefeitura, TipoGestao, TipoUnidadeEscolar
)

admin.site.register(DiretoriaRegional)
admin.site.register(FaixaIdadeEscolar)
admin.site.register(Lote)
admin.site.register(PeriodoEscolar)
admin.site.register(Subprefeitura)
admin.site.register(TipoGestao)
admin.site.register(TipoUnidadeEscolar)
admin.site.register(Codae)


@admin.register(Escola)
class EscolaAdmin(admin.ModelAdmin):
    list_display = ['codigo_eol', 'nome', 'diretoria_regional', 'tipo_gestao', 'tipo_unidade']
    ordering = ['codigo_eol', 'nome']
    search_fields = ['codigo_eol', 'nome']
