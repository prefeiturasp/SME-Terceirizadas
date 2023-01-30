from django.contrib import admin

from .models import (
    CategoriaMedicao,
    DiaSobremesaDoce,
    GrupoMedicao,
    Medicao,
    SolicitacaoMedicaoInicial,
    TipoContagemAlimentacao,
    ValorMedicao
)

admin.site.register(CategoriaMedicao)
admin.site.register(DiaSobremesaDoce)
admin.site.register(GrupoMedicao)
admin.site.register(Medicao)
admin.site.register(TipoContagemAlimentacao)
admin.site.register(ValorMedicao)


@admin.register(SolicitacaoMedicaoInicial)
class SolicitacaoMedicaoInicialAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'criado_em')
