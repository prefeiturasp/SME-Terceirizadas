from django.contrib import admin

from .models import (KitLanche, ItemKitLanche, SolicitacaoKitLancheAvulsa,
                     MotivoSolicitacaoUnificada, SolicitacaoKitLancheUnificada,
                     EscolaQuantidade)

admin.site.register(KitLanche)
admin.site.register(ItemKitLanche)
admin.site.register(SolicitacaoKitLancheAvulsa)
admin.site.register(MotivoSolicitacaoUnificada)
admin.site.register(SolicitacaoKitLancheUnificada)
admin.site.register(EscolaQuantidade)
