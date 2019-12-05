from django.contrib import admin

from .models import (
    AlteracaoCardapio,
    Cardapio,
    GrupoSuspensaoAlimentacao,
    InversaoCardapio,
    MotivoAlteracaoCardapio,
    MotivoSuspensao,
    QuantidadePorPeriodoSuspensaoAlimentacao,
    SubstituicoesAlimentacaoNoPeriodoEscolar,
    SubstituicoesDoVinculoTipoAlimentacaoPeriodoTipoUE,
    SuspensaoAlimentacao,
    TipoAlimentacao,
    VinculoTipoAlimentacaoComPeriodoEscolarETipoUnidadeEscolar
)

admin.site.register(TipoAlimentacao)
admin.site.register(InversaoCardapio)
admin.site.register(MotivoAlteracaoCardapio)
admin.site.register(SubstituicoesAlimentacaoNoPeriodoEscolar)
admin.site.register(MotivoSuspensao)


class SubstituicoesVinculoInLine(admin.TabularInline):
    model = SubstituicoesDoVinculoTipoAlimentacaoPeriodoTipoUE
    extra = 1


@admin.register(VinculoTipoAlimentacaoComPeriodoEscolarETipoUnidadeEscolar)
class VinculoTipoAlimentacaoModelAdmin(admin.ModelAdmin):
    inlines = [SubstituicoesVinculoInLine]


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
    list_display = ['uuid', 'data_inicial', 'data_final', 'status']
    list_filter = ['status']


class SuspensaoAlimentacaoInline(admin.TabularInline):
    model = SuspensaoAlimentacao
    extra = 1


class QuantidadePorPeriodoSuspensaoAlimentacaoInline(admin.TabularInline):
    model = QuantidadePorPeriodoSuspensaoAlimentacao
    extra = 1


@admin.register(GrupoSuspensaoAlimentacao)
class GrupoSuspensaoAlimentacaoModelAdmin(admin.ModelAdmin):
    inlines = [SuspensaoAlimentacaoInline, QuantidadePorPeriodoSuspensaoAlimentacaoInline]
