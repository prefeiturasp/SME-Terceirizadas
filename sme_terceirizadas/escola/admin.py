from django.contrib import admin

from .models import (
    Aluno,
    Codae,
    DiretoriaRegional,
    Escola,
    EscolaPeriodoEscolar,
    FaixaIdadeEscolar,
    LogAlteracaoQuantidadeAlunosPorEscolaEPeriodoEscolar,
    LogRotinaDiariaAlunos,
    Lote,
    PeriodoEscolar,
    Responsavel,
    Subprefeitura,
    TipoGestao,
    TipoUnidadeEscolar
)


class EscolaPeriodoEscolarAdmin(admin.ModelAdmin):
    search_fields = ('escola__nome', 'periodo_escolar__nome')


@admin.register(Escola)
class EscolaAdmin(admin.ModelAdmin):
    list_display = (
        'codigo_eol',
        'codigo_codae',
        'nome',
        'diretoria_regional',
        'tipo_gestao',
        'tipo_unidade',
        'enviar_email_por_produto',
    )
    search_fields = (
        'codigo_eol',
        'codigo_codae',
        'nome',
        'diretoria_regional__nome',
        'tipo_unidade__iniciais',
    )
    list_filter = (
        'enviar_email_por_produto',
        'diretoria_regional',
        'tipo_gestao',
        'tipo_unidade',
    )
    ordering = ('codigo_eol', 'nome')
    actions = ('marcar_para_receber_email', 'marcar_para_nao_receber_email')

    def marcar_para_receber_email(self, request, queryset):
        count = queryset.update(enviar_email_por_produto=True)

        if count == 1:
            msg = '{} escola foi marcada para receber e-mail dos produtos.'  # noqa P103
        else:
            msg = '{} escolas foram marcadas para receber e-mail dos produtos.'  # noqa P103

        self.message_user(request, msg.format(count))

    marcar_para_receber_email.short_description = 'Marcar para receber e-mail dos produtos'

    def marcar_para_nao_receber_email(self, request, queryset):
        count = queryset.update(enviar_email_por_produto=False)

        if count == 1:
            msg = '{} escola foi marcada para não receber e-mail dos produtos.'  # noqa P103
        else:
            msg = '{} escolas foram marcadas para não receber e-mail dos produtos.'  # noqa P103

        self.message_user(request, msg.format(count))

    marcar_para_nao_receber_email.short_description = 'Marcar para não receber e-mail dos produtos'


@admin.register(Lote)
class LoteAdmin(admin.ModelAdmin):
    list_display = ('iniciais', '__str__')
    list_display_links = ('__str__',)
    search_fields = ('iniciais', 'nome', 'diretoria_regional__nome')


@admin.register(DiretoriaRegional)
class DiretoriaRegionalAdmin(admin.ModelAdmin):
    list_display = ('iniciais', '__str__')
    list_display_links = ('__str__',)
    search_fields = ('codigo_eol', 'nome')


@admin.register(Aluno)
class AlunoAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'escola')
    search_fields = ('nome', 'escola__nome', 'codigo_eol', 'escola__codigo_eol')


admin.site.register(Codae)
admin.site.register(EscolaPeriodoEscolar, EscolaPeriodoEscolarAdmin)
admin.site.register(FaixaIdadeEscolar)
admin.site.register(LogAlteracaoQuantidadeAlunosPorEscolaEPeriodoEscolar)
admin.site.register(LogRotinaDiariaAlunos)
admin.site.register(PeriodoEscolar)
admin.site.register(Responsavel)
admin.site.register(Subprefeitura)
admin.site.register(TipoGestao)
admin.site.register(TipoUnidadeEscolar)
