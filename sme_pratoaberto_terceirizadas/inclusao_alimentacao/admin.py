from django.contrib import admin

from .models import (
    GrupoInclusaoAlimentacaoNormal, InclusaoAlimentacaoContinua,
    InclusaoAlimentacaoNormal, MotivoInclusaoContinua,
    MotivoInclusaoNormal, QuantidadePorPeriodo
)

admin.site.register(QuantidadePorPeriodo)
admin.site.register(MotivoInclusaoContinua)
admin.site.register(InclusaoAlimentacaoContinua)
admin.site.register(MotivoInclusaoNormal)
admin.site.register(InclusaoAlimentacaoNormal)
admin.site.register(GrupoInclusaoAlimentacaoNormal)
