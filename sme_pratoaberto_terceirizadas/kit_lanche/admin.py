from django.contrib import admin

from .models import KitLanche, ItemKitLanche, SolicitacaoKitLancheAvulsa

admin.site.register(KitLanche)
admin.site.register(ItemKitLanche)
admin.site.register(SolicitacaoKitLancheAvulsa)
