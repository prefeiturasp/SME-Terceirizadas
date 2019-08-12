from django.contrib import admin

from .models import (
    TipoAlimentacao, Cardapio, InversaoCardapio,
    MotivoAlteracaoCardapio, AlteracaoCardapio,
    SubstituicoesAlimentacaoNoPeriodoEscolar, GrupoSuspensaoAlimentacao,
    SuspensaoAlimentacao, QuantidadePorPeriodoSuspensaoAlimentacao,
    MotivoSuspensao)

admin.site.register(TipoAlimentacao)
admin.site.register(InversaoCardapio)
admin.site.register(MotivoAlteracaoCardapio)
admin.site.register(SubstituicoesAlimentacaoNoPeriodoEscolar)
admin.site.register(MotivoSuspensao)


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


class SuspensaoAlimentacaoInline(admin.TabularInline):
    model = SuspensaoAlimentacao
    extra = 1


class QuantidadePorPeriodoSuspensaoAlimentacaoInline(admin.TabularInline):
    model = QuantidadePorPeriodoSuspensaoAlimentacao
    extra = 1


@admin.register(GrupoSuspensaoAlimentacao)
class GrupoSuspensaoAlimentacaoModelAdmin(admin.ModelAdmin):
    inlines = [SuspensaoAlimentacaoInline, QuantidadePorPeriodoSuspensaoAlimentacaoInline]
