from django.contrib import admin

from .models import (
    Aluno,
    Codae,
    DiretoriaRegional,
    Escola,
    EscolaPeriodoEscolar,
    FaixaIdadeEscolar,
    LogAlteracaoQuantidadeAlunosPorEscolaEPeriodoEscolar,
    Lote,
    PeriodoEscolar,
    Responsavel,
    Subprefeitura,
    TipoGestao,
    TipoUnidadeEscolar
)

admin.site.register(Aluno)
admin.site.register(DiretoriaRegional)
admin.site.register(FaixaIdadeEscolar)
admin.site.register(Lote)
admin.site.register(PeriodoEscolar)
admin.site.register(Subprefeitura)
admin.site.register(TipoGestao)
admin.site.register(TipoUnidadeEscolar)
admin.site.register(Codae)


class EscolaPeriodoEscolarAdmin(admin.ModelAdmin):
    search_fields = ['escola__nome', 'periodo_escolar__nome']


admin.site.register(EscolaPeriodoEscolar, EscolaPeriodoEscolarAdmin)
admin.site.register(LogAlteracaoQuantidadeAlunosPorEscolaEPeriodoEscolar)
admin.site.register(Responsavel)


@admin.register(Escola)
class EscolaAdmin(admin.ModelAdmin):
    list_display = ['codigo_eol', 'nome', 'diretoria_regional', 'tipo_gestao', 'tipo_unidade']
    ordering = ['codigo_eol', 'nome']
    search_fields = ['codigo_eol', 'nome']
