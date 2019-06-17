from django.contrib import admin
from .models import KitLanche, SolicitacaoKitLanche, SolicitacaoUnificada, SolicitacaoUnificadaFormulario, \
    SolicitacaoUnificadaMultiploEscola, RazaoSolicitacaoUnificada, StatusSolicitacaoUnificada


@admin.register(KitLanche)
class KitLancheAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ativo')
    ordering = ('nome', 'ativo')


@admin.register(SolicitacaoKitLanche)
class OrderMealKitAdmin(admin.ModelAdmin):
    list_display = ['localizacao', 'quantidade_estudantes', 'data_solicitacao', 'status']


admin.site.register(RazaoSolicitacaoUnificada)
admin.site.register(SolicitacaoUnificada)
admin.site.register(SolicitacaoUnificadaMultiploEscola)
admin.site.register(SolicitacaoUnificadaFormulario)
admin.site.register(StatusSolicitacaoUnificada)
