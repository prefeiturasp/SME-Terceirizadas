from django.contrib import admin

from .models import (
    GrupoInclusaoAlimentacaoNormal,
    InclusaoAlimentacaoContinua,
    InclusaoAlimentacaoDaCEI,
    InclusaoAlimentacaoNormal,
    InclusaoDeAlimentacaoCEMEI,
    MotivoInclusaoContinua,
    MotivoInclusaoNormal,
    QuantidadeDeAlunosPorFaixaEtariaDaInclusaoDeAlimentacaoDaCEI,
    QuantidadePorPeriodo
)

admin.site.register(QuantidadePorPeriodo)
admin.site.register(MotivoInclusaoContinua)
admin.site.register(InclusaoAlimentacaoContinua)
admin.site.register(MotivoInclusaoNormal)
admin.site.register(InclusaoAlimentacaoNormal)
admin.site.register(GrupoInclusaoAlimentacaoNormal)
admin.site.register(InclusaoAlimentacaoDaCEI)
admin.site.register(InclusaoDeAlimentacaoCEMEI)
admin.site.register(QuantidadeDeAlunosPorFaixaEtariaDaInclusaoDeAlimentacaoDaCEI)
