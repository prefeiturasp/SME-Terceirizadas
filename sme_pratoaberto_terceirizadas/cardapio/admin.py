from django.contrib import admin

from .models import TipoAlimentacao, Cardapio, InversaoCardapio, AlteracaoCardapio, SuspensaoAlimentacao
from .models import MotivoAlteracaoCardapio

admin.site.register(TipoAlimentacao)
admin.site.register(InversaoCardapio)
admin.site.register(AlteracaoCardapio)
admin.site.register(SuspensaoAlimentacao)
admin.site.register(MotivoAlteracaoCardapio)


@admin.register(Cardapio)
class CardapioAdmin(admin.ModelAdmin):
    list_display = ['data', 'criado_em', 'ativo']
    ordering = ['data', 'criado_em']
