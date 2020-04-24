from django.contrib import admin

from .models import (
    Fabricante,
    HomologacaoDoProduto,
    ImagemDoProduto,
    InformacaoNutricional,
    InformacoesNutricionaisDoProduto,
    Marca,
    Produto,
    ProtocoloDeDietaEspecial,
    TipoDeInformacaoNutricional
)

admin.site.register(Fabricante)
admin.site.register(InformacaoNutricional)
admin.site.register(Marca)
admin.site.register(ProtocoloDeDietaEspecial)
admin.site.register(TipoDeInformacaoNutricional)
admin.site.register(HomologacaoDoProduto)


class InformacoesNutricionaisDoProdutoInline(admin.TabularInline):
    model = InformacoesNutricionaisDoProduto
    extra = 1


class ImagemDoProdutoInline(admin.TabularInline):
    model = ImagemDoProduto
    extra = 1


@admin.register(Produto)
class ProdutoModelAdmin(admin.ModelAdmin):
    inlines = [InformacoesNutricionaisDoProdutoInline, ImagemDoProdutoInline]
