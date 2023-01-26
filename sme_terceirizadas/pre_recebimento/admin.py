from django.contrib import admin

from .forms import CaixaAltaNomeForm
from .models import (
    AlteracaoCronogramaEtapa,
    Cronograma,
    EmbalagemQld,
    EtapasDoCronograma,
    Laboratorio,
    ProgramacaoDoRecebimentoDoCronograma,
    SolicitacaoAlteracaoCronograma
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


class AlteracaoCronogramaEtapaInline(admin.StackedInline):
    model = SolicitacaoAlteracaoCronograma.etapas.through
    extra = 0  # Quantidade de linhas que serão exibidas.
    show_change_link = True


@admin.register(SolicitacaoAlteracaoCronograma)
class SolicitacaoAdmin(admin.ModelAdmin):
    inlines = [AlteracaoCronogramaEtapaInline]


@admin.register(AlteracaoCronogramaEtapa)
class AlteracaoCronogramaEtapaAdmin(admin.ModelAdmin):
    readonly_fields = [
        'etapa'
    ]

    def has_add_permission(self, request) -> bool:
        return False


admin.site.register(Cronograma)
admin.site.register(EtapasDoCronograma)
admin.site.register(ProgramacaoDoRecebimentoDoCronograma)
