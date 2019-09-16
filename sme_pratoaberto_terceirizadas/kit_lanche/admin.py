from django.contrib import admin

from .models import (
    EscolaQuantidade, ItemKitLanche, KitLanche, SolicitacaoKitLanche,
    SolicitacaoKitLancheAvulsa, SolicitacaoKitLancheUnificada
)

admin.site.register(KitLanche)
admin.site.register(ItemKitLanche)
admin.site.register(SolicitacaoKitLancheUnificada)
admin.site.register(EscolaQuantidade)
admin.site.register(SolicitacaoKitLanche)


@admin.register(SolicitacaoKitLancheAvulsa)
class SolicitacaoKitLancheAvulsaAdmin(admin.ModelAdmin):
    list_display = ['escola', 'status', 'solicitacao_kit_lanche']
    ordering = ['escola', 'status']
