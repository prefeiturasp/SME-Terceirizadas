from django.contrib import admin, messages
from django.shortcuts import redirect
from rangefilter.filters import DateRangeFilter

from .models import (
    Aluno,
    AlunosMatriculadosPeriodoEscola,
    Codae,
    DiaCalendario,
    DiretoriaRegional,
    Escola,
    EscolaPeriodoEscolar,
    FaixaIdadeEscolar,
    LogAlteracaoQuantidadeAlunosPorEscolaEPeriodoEscolar,
    LogAlunosMatriculadosPeriodoEscola,
    LogRotinaDiariaAlunos,
    Lote,
    PeriodoEscolar,
    PlanilhaEscolaDeParaCodigoEolCodigoCoade,
    Responsavel,
    Subprefeitura,
    TipoGestao,
    TipoUnidadeEscolar
)
from .tasks import atualiza_codigo_codae_das_escolas_task


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
        'subprefeitura',
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


@admin.register(PlanilhaEscolaDeParaCodigoEolCodigoCoade)
class PlanilhaEscolaDeParaCodigoEolCodigoCoadeAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'criado_em', 'codigos_codae_vinculados')
    actions = ('vincular_codigos_codae_da_planilha', )

    def vincular_codigos_codae_da_planilha(self, request, queryset):
        if len(queryset) > 1:
            self.message_user(request, 'Escolha somente uma planilha.', messages.ERROR)
            return

        arquivo = queryset.first()
        atualiza_codigo_codae_das_escolas_task.delay(path_planilha=arquivo.planilha.path, id_planilha=arquivo.id)

        messages.add_message(
            request,
            messages.INFO,
            'Atualização de códigos codae das escolas disparada. Este procedimento pode demorar alguns minutos..'
        )
        return redirect('admin:escola_planilhaescoladeparacodigoeolcodigocoade_changelist')
    vincular_codigos_codae_da_planilha.short_description = 'Executar atualização dos códigos codae das escolas'


@admin.register(AlunosMatriculadosPeriodoEscola)
class AlunosMatriculadosPeriodoEscolaAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'alterado_em', 'tipo_turma')
    search_fields = ('escola__nome', 'periodo_escolar__nome')
    list_filter = ('alterado_em', 'tipo_turma')


@admin.register(LogAlunosMatriculadosPeriodoEscola)
class LogAlunosMatriculadosPeriodoEscolaAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'criado_em', 'tipo_turma')
    search_fields = ('escola__nome', 'periodo_escolar__nome')
    list_filter = (('criado_em', DateRangeFilter), 'tipo_turma')


@admin.register(DiaCalendario)
class DiaCalendarioAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'data', 'dia_letivo')
    search_fields = ('escola__nome',)
    list_filter = (('data', DateRangeFilter),)


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
