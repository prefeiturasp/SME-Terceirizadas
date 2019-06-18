from django.contrib import admin
from .models import InclusaoAlimentacao, DescricaoInclusaoAlimentacao, MotivoInclusaoAlimentacao, InclusaoAlimentacaoStatus, \
    DiaMotivoInclusaoAlimentacao


admin.site.register(InclusaoAlimentacao)
admin.site.register(DescricaoInclusaoAlimentacao)
admin.site.register(MotivoInclusaoAlimentacao)
admin.site.register(InclusaoAlimentacaoStatus)
admin.site.register(DiaMotivoInclusaoAlimentacao)
