from django.contrib import admin
from nested_inline.admin import NestedModelAdmin, NestedStackedInline

from .forms import CaixaAltaNomeForm
from .models import (
    Cronograma,
    EtapasDoCronograma,
    ImagemDoTipoDeEmbalagem,
    Laboratorio,
    LayoutDeEmbalagem,
    ProgramacaoDoRecebimentoDoCronograma,
    SolicitacaoAlteracaoCronograma,
    TipoDeEmbalagemDeLayout,
    TipoEmbalagemQld,
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


@admin.register(TipoEmbalagemQld)
class EmbalagemQldAdmin(admin.ModelAdmin):
    form = CaixaAltaNomeForm
    list_display = ('nome', 'abreviacao', 'criado_em')
    search_fields = ('nome',)
    readonly_fields = ('uuid',)


class EtapasAntigasInline(admin.StackedInline):
    model = SolicitacaoAlteracaoCronograma.etapas_antigas.through
    extra = 0  # Quantidade de linhas que serão exibidas.


class EtapasNovasInline(admin.StackedInline):
    model = SolicitacaoAlteracaoCronograma.etapas_novas.through
    extra = 0  # Quantidade de linhas que serão exibidas.


@admin.register(SolicitacaoAlteracaoCronograma)
class SolicitacaoAdmin(admin.ModelAdmin):
    inlines = [EtapasAntigasInline, EtapasNovasInline]


@admin.register(UnidadeMedida)
class UnidadeMedidaAdmin(admin.ModelAdmin):
    list_display = ('nome', 'abreviacao', 'criado_em')
    search_fields = ('nome', 'abreviacao')


class ImagemDoTipoDeEmbalagemInline(NestedStackedInline):
    model = ImagemDoTipoDeEmbalagem
    extra = 0
    fk_name = 'tipo_de_embalagem'
    show_change_link = True


class TipoEmbalagemLayoutInline(NestedStackedInline):
    model = TipoDeEmbalagemDeLayout
    extra = 0
    show_change_link = True
    readonly_fields = ('uuid',)
    fk_name = 'layout_de_embalagem'
    inlines = [ImagemDoTipoDeEmbalagemInline, ]


class LayoutDeEmbalagemAdmin(NestedModelAdmin):
    list_display = ('get_cronograma', 'get_produto', 'criado_em')
    search_fields = ('cronograma__numero', 'produto__nome')
    readonly_fields = ('uuid',)
    inlines = [TipoEmbalagemLayoutInline, ]

    def get_produto(self, obj):
        return obj.cronograma.produto.nome
    get_produto.short_description = 'Produto'

    def get_cronograma(self, obj):
        return obj.cronograma.numero
    get_cronograma.short_description = 'Cronograma'


admin.site.register(LayoutDeEmbalagem, LayoutDeEmbalagemAdmin)
admin.site.register(Cronograma)
admin.site.register(EtapasDoCronograma)
admin.site.register(ProgramacaoDoRecebimentoDoCronograma)
