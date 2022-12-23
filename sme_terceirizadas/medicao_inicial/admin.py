from django.contrib import admin

from .models import (
    CategoriaMedicao,
    DiaSobremesaDoce,
    Medicao,
    SolicitacaoMedicaoInicial,
    TipoContagemAlimentacao,
    ValorMedicao
)

admin.site.register(CategoriaMedicao)
admin.site.register(DiaSobremesaDoce)
admin.site.register(Medicao)
admin.site.register(SolicitacaoMedicaoInicial)
admin.site.register(TipoContagemAlimentacao)
admin.site.register(ValorMedicao)
