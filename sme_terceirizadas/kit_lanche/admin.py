from django.contrib import admin

from .models import (
    EscolaQuantidade,
    ItemKitLanche,
    KitLanche,
    SolicitacaoKitLanche,
    SolicitacaoKitLancheAvulsa,
    SolicitacaoKitLancheUnificada
)

admin.site.register(KitLanche)
admin.site.register(ItemKitLanche)
admin.site.register(SolicitacaoKitLancheUnificada)
admin.site.register(EscolaQuantidade)


@admin.register(SolicitacaoKitLancheAvulsa)
class SolicitacaoKitLancheAvulsaAdmin(admin.ModelAdmin):
    list_display = ['escola', 'status', 'solicitacao_kit_lanche']
    ordering = ['escola', 'status']


@admin.register(SolicitacaoKitLanche)
class SolicitacaoKitLancheAdmin(admin.ModelAdmin):
    list_display = ['criado_em', 'data']
