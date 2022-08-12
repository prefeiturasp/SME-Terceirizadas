from django.contrib import admin

from .models import DiaSobremesaDoce, SolicitacaoMedicaoInicial, TipoContagemAlimentacao

admin.site.register(DiaSobremesaDoce)
admin.site.register(SolicitacaoMedicaoInicial)
admin.site.register(TipoContagemAlimentacao)
