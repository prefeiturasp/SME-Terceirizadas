from django.contrib import admin

from .models import (
    Fabricante,
    HomologacaoDoProduto,
    ImagemDoProduto,
    InformacaoNutricional,
    InformacoesNutricionaisDoProduto,
    Marca,
    Produto,
    NomeDeProdutoEdital,
    ProtocoloDeDietaEspecial,
    ReclamacaoDeProduto,
    RespostaAnaliseSensorial,
    SolicitacaoCadastroProdutoDieta,
    TipoDeInformacaoNutricional
)
from .forms import NomeDeProdutoEditalForm


class InformacoesNutricionaisDoProdutoInline(admin.TabularInline):
    model = InformacoesNutricionaisDoProduto
    extra = 1


class ImagemDoProdutoInline(admin.TabularInline):
    model = ImagemDoProduto
    extra = 1


@admin.register(Marca)
class MarcaModelAdmin(admin.ModelAdmin):
    search_fields = ('nome',)
    ordering = ('nome',)


@admin.register(Fabricante)
class FabricanteModelAdmin(admin.ModelAdmin):
    search_fields = ('nome',)
    ordering = ('nome',)


@admin.register(Produto)
class ProdutoModelAdmin(admin.ModelAdmin):
    inlines = [InformacoesNutricionaisDoProdutoInline, ImagemDoProdutoInline]
    list_display = ('nome', 'marca', 'fabricante')
    search_fields = ('nome', 'marca__nome', 'fabricante__nome')
    ordering = ('nome',)


@admin.register(NomeDeProdutoEdital)
class NomeDeProdutoEditalAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ativo')
    search_fields = ('nome',)
    list_filter = ('ativo',)
    readonly_fields = ('criado_por',)
    form = NomeDeProdutoEditalForm
    actions = ('ativar_produtos', 'inativar_produtos')

    def ativar_produtos(self, request, queryset):
        count = queryset.update(ativo=True)

        if count == 1:
            msg = '{} produto foi ativado.'  # noqa P103
        else:
            msg = '{} produtos foram ativados.'  # noqa P103

        self.message_user(request, msg.format(count))

    ativar_produtos.short_description = 'Marcar para ativar produtos'

    def inativar_produtos(self, request, queryset):
        count = queryset.update(ativo=False)

        if count == 1:
            msg = '{} produto foi inativado.'  # noqa P103
        else:
            msg = '{} produtos foram inativados.'  # noqa P103

        self.message_user(request, msg.format(count))

    inativar_produtos.short_description = 'Marcar para inativar produtos'

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ProtocoloDeDietaEspecial)
class ProtocoloDeDietaEspecialModelAdmin(admin.ModelAdmin):
    search_fields = ('nome',)
    ordering = ('nome',)


@admin.register(TipoDeInformacaoNutricional)
class TipoDeInformacaoNutricionalModelAdmin(admin.ModelAdmin):
    search_fields = ('nome',)
    ordering = ('nome',)


@admin.register(HomologacaoDoProduto)
class HomologacaoDoProdutoModelAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'produto', 'status', 'uuid')
    search_fields = ('produto__nome',)


@admin.register(InformacaoNutricional)
class InformacaoNutricionalModelAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'tipo_nutricional', 'medida')
    search_fields = ('nome',)
    list_filter = ('tipo_nutricional',)


admin.site.register(ReclamacaoDeProduto)
admin.site.register(RespostaAnaliseSensorial)
admin.site.register(SolicitacaoCadastroProdutoDieta)
