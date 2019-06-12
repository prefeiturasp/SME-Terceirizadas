from django.contrib import admin

from sme_pratoaberto_terceirizadas.alimentacao.models import Gestao, Edital, Tipo, Categoria, Cardapio, \
    InverterDiaCardapio


@admin.register(Gestao)
class GestaoAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'descricao', 'ativo']
    ordering = ['titulo', 'ativo']


@admin.register(Edital)
class EditalAdmin(admin.ModelAdmin):
    list_display = ['numero', 'descricao', 'ativo']
    ordering = ['numero', 'ativo']


@admin.register(Tipo)
class TipoAdmin(admin.ModelAdmin):
    list_display = ['codigo', 'titulo', 'descricao', 'ativo']
    ordering = ['titulo', 'ativo']


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'descricao', 'ativo']
    ordering = ['titulo', 'ativo']


@admin.register(Cardapio)
class CardapioAdmin(admin.ModelAdmin):
    list_display = ['data', 'tipo', 'categoria', 'criado_por', 'edital', 'ultima_atualizacao', 'descricao',
                    'atualizado_por']
    ordering = ['data', 'tipo', 'categoria', 'edital', 'ultima_atualizacao']


@admin.register(InverterDiaCardapio)
class InverterDiaCardapioAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'escola', 'data_de', 'data_para', 'status']
    ordering = ['data_de', 'data_para']
