from django.contrib import admin

from .models import (
    AlimentacaoLancamentoEspecial,
    CategoriaMedicao,
    DiaSobremesaDoce,
    GrupoMedicao,
    Medicao,
    PermissaoLancamentoEspecial,
    SolicitacaoMedicaoInicial,
    TipoContagemAlimentacao,
    ValorMedicao
)

admin.site.register(AlimentacaoLancamentoEspecial)
admin.site.register(CategoriaMedicao)
admin.site.register(DiaSobremesaDoce)
admin.site.register(GrupoMedicao)
admin.site.register(TipoContagemAlimentacao)
admin.site.register(ValorMedicao)


@admin.register(SolicitacaoMedicaoInicial)
class SolicitacaoMedicaoInicialAdmin(admin.ModelAdmin):
    list_display = ('id_externo', 'escola', 'mes', 'ano', 'criado_em')
    search_fields = ('escola__nome', 'escola__codigo_eol')
    list_filter = ('mes', 'ano')


@admin.register(Medicao)
class MedicaoAdmin(admin.ModelAdmin):
    list_display = ('get_escola', 'get_mes', 'get_ano', 'periodo_escolar', 'grupo', 'get_uuid_sol_medicao', 'criado_em')
    search_fields = ('solicitacao_medicao_inicial__escola__nome', 'solicitacao_medicao_inicial__escola__codigo_eol')
    list_filter = (
        'periodo_escolar__nome',
        'grupo',
        'solicitacao_medicao_inicial__mes',
        'solicitacao_medicao_inicial__ano'
    )

    @admin.display(description='Solicitação Medição Inicial')
    def get_uuid_sol_medicao(self, obj):
        return obj.solicitacao_medicao_inicial.id_externo

    @admin.display(description='Escola')
    def get_escola(self, obj):
        return f'{obj.solicitacao_medicao_inicial.escola.codigo_eol}: {obj.solicitacao_medicao_inicial.escola.nome}'

    @admin.display(description='Mês')
    def get_mes(self, obj):
        return obj.solicitacao_medicao_inicial.mes

    @admin.display(description='Ano')
    def get_ano(self, obj):
        return obj.solicitacao_medicao_inicial.ano


@admin.register(PermissaoLancamentoEspecial)
class PermissaoLancamentoEspecialAdmin(admin.ModelAdmin):
    list_display = ('id_externo', 'escola', 'periodo_escolar', 'data_inicial', 'data_final',
                    'diretoria_regional', 'get_alimentacoes_lancamento_especial')
    search_fields = ('escola__nome', 'escola__codigo_eol')

    @admin.display(description='Alimentações Lançamento Especial')
    def get_alimentacoes_lancamento_especial(self, obj):
        return [ali.nome for ali in obj.alimentacoes_lancamento_especial.all()]
