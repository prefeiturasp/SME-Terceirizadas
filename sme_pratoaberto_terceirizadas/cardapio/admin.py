from django.contrib import admin

from .models import (
    TipoAlimentacao, Cardapio, InversaoCardapio, AlteracaoCardapio, SuspensaoAlimentacao, MotivoAlteracaoCardapio,
    SubstituicoesAlimentacaoNoPeriodoEscolar
)

admin.site.register(TipoAlimentacao)
admin.site.register(InversaoCardapio)
admin.site.register(SuspensaoAlimentacao)
admin.site.register(MotivoAlteracaoCardapio)
admin.site.register(SubstituicoesAlimentacaoNoPeriodoEscolar)


@admin.register(Cardapio)
class CardapioAdmin(admin.ModelAdmin):
    list_display = ['data', 'criado_em', 'ativo']
    ordering = ['data', 'criado_em']


class SubstituicoesInLine(admin.TabularInline):
    model = SubstituicoesAlimentacaoNoPeriodoEscolar
    extra = 1


@admin.register(AlteracaoCardapio)
class AlteracaoCardapioModelAdmin(admin.ModelAdmin):

    inlines = [SubstituicoesInLine]


