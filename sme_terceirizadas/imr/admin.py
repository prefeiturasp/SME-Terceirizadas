from django import forms
from django.contrib import admin
from rangefilter.filters import DateRangeFilter

from sme_terceirizadas.dados_comuns.behaviors import PerfilDiretorSupervisao
from sme_terceirizadas.dados_comuns.utils import custom_titled_filter
from sme_terceirizadas.imr.models import (
    CategoriaOcorrencia,
    FormularioDiretor,
    FormularioOcorrenciasBase,
    FormularioSupervisao,
    ObrigacaoPenalidade,
    ParametrizacaoOcorrencia,
    PeriodoVisita,
    RespostaCampoNumerico,
    RespostaCampoTextoLongo,
    RespostaCampoTextoSimples,
    RespostaDatas,
    RespostaFaixaEtaria,
    RespostaPeriodo,
    RespostaSimNao,
    RespostaSimNaoNaoSeAplica,
    RespostaTipoAlimentacao,
    TipoGravidade,
    TipoOcorrencia,
    TipoPenalidade,
    TipoPerguntaParametrizacaoOcorrencia,
    TipoRespostaModelo,
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
        ("categoria__nome", custom_titled_filter("Categoria")),
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


class PerfisFilter(admin.SimpleListFilter):
    title = "Perfis"
    parameter_name = "perfis"

    def lookups(self, request, model_admin):
        return [("Diretor", "Diretor"), ("Supervisao", "Supervisao")]

    def queryset(self, request, queryset):
        if self.value() == "Tudo":
            return queryset.all()
        if self.value() in ["Diretor", "Supervisao"]:
            return queryset.filter(tipo_ocorrencia__perfis__icontains=self.value())


@admin.register(ParametrizacaoOcorrencia)
class ParametrizacaoAdmin(admin.ModelAdmin):
    list_display = ("edital", "titulo", "tipo_pergunta", "perfis")
    ordering = ("criado_em",)
    search_fields = ("edital", "titulo")
    list_filter = ("tipo_ocorrencia__edital", PerfisFilter)
    autocomplete_fields = ("tipo_ocorrencia",)

    def edital(self, obj):
        return obj.tipo_ocorrencia.edital.numero

    def perfis(self, obj):
        return obj.tipo_ocorrencia.perfis


class TipoFormularioFilter(admin.SimpleListFilter):
    title = "Tipo de formulário"
    parameter_name = "tipo_formulario"

    def lookups(self, request, model_admin):
        return [("Diretor", "Diretor"), ("Supervisao", "Supervisao")]

    def queryset(self, request, queryset):
        if self.value() == "Tudo":
            return queryset.all()
        elif self.value() == "Diretor":
            return queryset.filter(formulariodiretor__isnull=False)
        elif self.value() == "Supervisao":
            return queryset.filter(formulariosupervisao__isnull=False)


class FormularioSupervisaoInline(admin.StackedInline):
    model = FormularioSupervisao
    max_num = 1
    extra = 0
    autocomplete_fields = ("escola",)


class FormularioDiretorInline(admin.StackedInline):
    model = FormularioDiretor
    max_num = 1
    extra = 0


class RespostaSimNaoInline(admin.TabularInline):
    model = RespostaSimNao
    extra = 0


class RespostaCampoNumericoInline(admin.TabularInline):
    model = RespostaCampoNumerico
    extra = 0


class RespostaCampoTextoSimplesInline(admin.TabularInline):
    model = RespostaCampoTextoSimples
    extra = 0


class RespostaCampoTextoLongoInline(admin.TabularInline):
    model = RespostaCampoTextoLongo
    extra = 0


class RespostaDatasInline(admin.TabularInline):
    model = RespostaDatas
    extra = 0


class RespostaPeriodoInline(admin.TabularInline):
    model = RespostaPeriodo
    extra = 0


class RespostaFaixaEtariaInline(admin.TabularInline):
    model = RespostaFaixaEtaria
    extra = 0


class RespostaTipoAlimentacaoInline(admin.TabularInline):
    model = RespostaTipoAlimentacao
    extra = 0


class RespostaSimNaoNaoSeAplicaInline(admin.TabularInline):
    model = RespostaSimNaoNaoSeAplica
    extra = 0


@admin.register(FormularioOcorrenciasBase)
class FormularioOcorrenciasBaseAdmin(admin.ModelAdmin):
    inlines = [
        FormularioSupervisaoInline,
        FormularioDiretorInline,
        RespostaSimNaoInline,
        RespostaCampoNumericoInline,
        RespostaCampoTextoSimplesInline,
        RespostaCampoTextoLongoInline,
        RespostaDatasInline,
        RespostaPeriodoInline,
        RespostaFaixaEtariaInline,
        RespostaTipoAlimentacaoInline,
        RespostaSimNaoNaoSeAplicaInline,
    ]
    list_filter = (TipoFormularioFilter, ("data", DateRangeFilter))


@admin.register(FormularioDiretor)
class FormularioDiretorAdmin(admin.ModelAdmin):
    list_filter = (("formulario_base__data", DateRangeFilter),)


@admin.register(FormularioSupervisao)
class FormularioSupervisaoAdmin(admin.ModelAdmin):
    list_filter = (
        ("formulario_base__data", DateRangeFilter),
        "acompanhou_visita",
        "apresentou_ocorrencias",
    )


admin.site.register(TipoGravidade)
admin.site.register(ObrigacaoPenalidade)
admin.site.register(TipoPerguntaParametrizacaoOcorrencia)
admin.site.register(RespostaSimNao)
admin.site.register(RespostaCampoNumerico)
admin.site.register(RespostaCampoTextoSimples)
admin.site.register(RespostaCampoTextoLongo)
admin.site.register(RespostaDatas)
admin.site.register(RespostaPeriodo)
admin.site.register(RespostaFaixaEtaria)
admin.site.register(RespostaTipoAlimentacao)
admin.site.register(RespostaSimNaoNaoSeAplica)
admin.site.register(TipoRespostaModelo)
admin.site.register(PeriodoVisita)
