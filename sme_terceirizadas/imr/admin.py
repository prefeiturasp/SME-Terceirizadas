from django.contrib import admin

from sme_terceirizadas.imr.models import (
    CategoriaOcorrencia,
    ObrigacaoPenalidade,
    TipoGravidade,
    TipoOcorrencia,
    TipoPenalidade,
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

    def save_model(self, request, obj, form, change):
        if not change:  # Apenas para novos registros
            obj.criado_por = request.user
        super().save_model(request, obj, form, change)


admin.site.register(TipoGravidade)
admin.site.register(ObrigacaoPenalidade)
admin.site.register(CategoriaOcorrencia)
