from django.contrib import admin

from .forms import CaixaAltaNomeForm
from .models import (
    Cronograma,
    EmbalagemQld,
    EtapasDoCronograma,
    Laboratorio,
    ProgramacaoDoRecebimentoDoCronograma,
    SolicitacaoAlteracaoCronograma,
    UnidadeMedida
)


@admin.register(Laboratorio)
class Laboratoriodmin(admin.ModelAdmin):
    form = CaixaAltaNomeForm
    list_display = ('nome', 'cnpj', 'cidade', 'credenciado')
    ordering = ('-criado_em',)
    search_fields = ('nome',)
    list_filter = ('nome',)
    readonly_fields = ('uuid',)


@admin.register(EmbalagemQld)
class EmbalagemQldAdmin(admin.ModelAdmin):
    form = CaixaAltaNomeForm
    list_display = ('nome', 'abreviacao', 'criado_em')
    search_fields = ('nome',)
    readonly_fields = ('uuid',)


class EtapasAntigasInline(admin.StackedInline):
    model = SolicitacaoAlteracaoCronograma.etapas_antigas.through
    extra = 0  # Quantidade de linhas que serão exibidas.
    show_change_link = True


class EtapasNovasInline(admin.StackedInline):
    model = SolicitacaoAlteracaoCronograma.etapas_novas.through
    extra = 0  # Quantidade de linhas que serão exibidas.
    show_change_link = True


@admin.register(SolicitacaoAlteracaoCronograma)
class SolicitacaoAdmin(admin.ModelAdmin):
    inlines = [EtapasAntigasInline, EtapasNovasInline]


@admin.register(UnidadeMedida)
class UnidadeMedidaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'abreviacao', 'criado_em')
    search_fields = ('nome', 'abreviacao')


admin.site.register(Cronograma)
admin.site.register(EtapasDoCronograma)
admin.site.register(ProgramacaoDoRecebimentoDoCronograma)
