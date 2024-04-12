from django import forms
from django.contrib import admin

from sme_terceirizadas.dados_comuns.behaviors import PerfilDiretorSupervisao
from sme_terceirizadas.imr.models import (
    CategoriaOcorrencia,
    ObrigacaoPenalidade,
    ParametrizacaoOcorrencia,
    Relatorio,
    RespostaSimNao,
    RespostaTipoAlimentacao,
    TipoGravidade,
    TipoOcorrencia,
    TipoPenalidade,
    TipoPerguntaParametrizacaoOcorrencia,
)


class ObrigacaoPenalidadeInline(admin.StackedInline):
    model = ObrigacaoPenalidade
    extra = 1  # Quantidade de linhas que serão exibidas.
    show_change_link = True


@admin.register(TipoPenalidade)
class TipoPenalidadeAdmin(admin.ModelAdmin):
    list_display = (
        "edital",
        "numero_clausula",
        "gravidade",
        "status",
    )
    ordering = ("criado_em",)
    search_fields = ("numero_clausula",)
    list_filter = (
        "edital",
        "gravidade",
        "status",
    )
    readonly_fields = ("uuid", "criado_em", "criado_por", "alterado_em")
    autocomplete_fields = ("edital",)
    inlines = [ObrigacaoPenalidadeInline]

    def save_model(self, request, obj, form, change):
        if not change:  # Apenas para novos registros
            obj.criado_por = request.user
        super().save_model(request, obj, form, change)


class PerfisMultipleChoiceForm(forms.ModelForm):
    perfis = forms.MultipleChoiceField(choices=PerfilDiretorSupervisao.PERFIS)


@admin.register(TipoOcorrencia)
class TipoOcorrenciaAdmin(admin.ModelAdmin):
    list_display = (
        "edital",
        "categoria",
        "titulo",
        "penalidade",
        "pontuacao",
        "perfis",
        "status",
    )
    ordering = ("criado_em",)
    search_fields = ("titulo",)
    list_filter = (
        "edital",
        "categoria",
        "status",
    )
    readonly_fields = ("uuid", "criado_em", "criado_por", "alterado_em")
    autocomplete_fields = ("edital", "penalidade")
    form = PerfisMultipleChoiceForm

    def save_model(self, request, obj, form, change):
        if not change:  # Apenas para novos registros
            obj.criado_por = request.user
        super().save_model(request, obj, form, change)


@admin.register(CategoriaOcorrencia)
class CategoriaOcorrenciaAdmin(admin.ModelAdmin):
    form = PerfisMultipleChoiceForm


@admin.register(ParametrizacaoOcorrencia)
class ParametrizacaoAdmin(admin.ModelAdmin):
    list_display = (
        "get_edital",
        "titulo",
        "tipo_pergunta",
    )
    ordering = ("criado_em",)
    search_fields = ("get_edital", "titulo")
    list_filter = ("tipo_ocorrencia__edital",)
    autocomplete_fields = ("tipo_ocorrencia",)

    def get_edital(self, obj):
        return obj.tipo_ocorrencia.edital.numero


admin.site.register(TipoGravidade)
admin.site.register(ObrigacaoPenalidade)
admin.site.register(TipoPerguntaParametrizacaoOcorrencia)
admin.site.register(RespostaSimNao)
admin.site.register(RespostaTipoAlimentacao)
admin.site.register(Relatorio)
