from django.contrib import admin

from .models import (
    AlteracaoCardapio,
    AlteracaoCardapioCEI,
    Cardapio,
    ComboDoVinculoTipoAlimentacaoPeriodoTipoUE,
    GrupoSuspensaoAlimentacao,
    HorarioDoComboDoTipoDeAlimentacaoPorUnidadeEscolar,
    InversaoCardapio,
    MotivoAlteracaoCardapio,
    MotivoSuspensao,
    QuantidadePorPeriodoSuspensaoAlimentacao,
    SubstituicaoAlimentacaoNoPeriodoEscolar,
    SubstituicaoAlimentacaoNoPeriodoEscolarCEI,
    SubstituicaoDoComboDoVinculoTipoAlimentacaoPeriodoTipoUE,
    SuspensaoAlimentacao,
    SuspensaoAlimentacaoDaCEI,
    TipoAlimentacao,
    VinculoTipoAlimentacaoComPeriodoEscolarETipoUnidadeEscolar
)

admin.site.register(TipoAlimentacao)
admin.site.register(InversaoCardapio)
admin.site.register(MotivoAlteracaoCardapio)
admin.site.register(SuspensaoAlimentacaoDaCEI)
admin.site.register(MotivoSuspensao)
admin.site.register(HorarioDoComboDoTipoDeAlimentacaoPorUnidadeEscolar)


class SubstituicaoComboInline(admin.TabularInline):
    model = SubstituicaoDoComboDoVinculoTipoAlimentacaoPeriodoTipoUE
    extra = 2


@admin.register(ComboDoVinculoTipoAlimentacaoPeriodoTipoUE)
class ComboDoVinculoTipoAlimentacaoPeriodoTipoUEModelAdmin(admin.ModelAdmin):
    inlines = [SubstituicaoComboInline]
    readonly_fields = ('vinculo',)


@admin.register(SubstituicaoAlimentacaoNoPeriodoEscolar)
class SubstituicaoAlimentacaoNoPeriodoEscolarModelAdmin(admin.ModelAdmin):
    readonly_fields = (
        'alteracao_cardapio',
        'periodo_escolar',
        'tipo_alimentacao_de',
        'tipo_alimentacao_para'
    )


class ComboVinculoLine(admin.TabularInline):
    model = ComboDoVinculoTipoAlimentacaoPeriodoTipoUE
    extra = 1


@admin.register(VinculoTipoAlimentacaoComPeriodoEscolarETipoUnidadeEscolar)
class VinculoTipoAlimentacaoModelAdmin(admin.ModelAdmin):
    inlines = [ComboVinculoLine]


@admin.register(Cardapio)
class CardapioAdmin(admin.ModelAdmin):
    list_display = ['data', 'criado_em', 'ativo']
    ordering = ['data', 'criado_em']


class SubstituicoesInLine(admin.TabularInline):
    model = SubstituicaoAlimentacaoNoPeriodoEscolar
    extra = 0
    readonly_fields = (
        'alteracao_cardapio',
        'periodo_escolar',
        'tipo_alimentacao_de',
        'tipo_alimentacao_para'
    )


@admin.register(AlteracaoCardapio)
class AlteracaoCardapioModelAdmin(admin.ModelAdmin):
    inlines = [SubstituicoesInLine]
    list_display = ('uuid', 'data_inicial', 'data_final', 'status')
    list_filter = ('status',)
    readonly_fields = ('escola',)


class SubstituicoesCEIInLine(admin.TabularInline):
    model = SubstituicaoAlimentacaoNoPeriodoEscolarCEI
    extra = 1


@admin.register(AlteracaoCardapioCEI)
class AlteracaoCardapioCEIModelAdmin(admin.ModelAdmin):
    inlines = [SubstituicoesCEIInLine]
    list_display = ['uuid', 'data', 'status']
    list_filter = ['status']


class SuspensaoAlimentacaoInline(admin.TabularInline):
    model = SuspensaoAlimentacao
    extra = 1


class QuantidadePorPeriodoSuspensaoAlimentacaoInline(admin.TabularInline):
    model = QuantidadePorPeriodoSuspensaoAlimentacao
    extra = 1


@admin.register(GrupoSuspensaoAlimentacao)
class GrupoSuspensaoAlimentacaoModelAdmin(admin.ModelAdmin):
    inlines = [
        SuspensaoAlimentacaoInline,
        QuantidadePorPeriodoSuspensaoAlimentacaoInline
    ]
