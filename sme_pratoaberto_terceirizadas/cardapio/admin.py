from django.contrib import admin

from .models import TipoAlimentacao, Cardapio, InversaoCardapio, AlteracaoCardapio, SuspensaoAlimentacao

admin.site.register(TipoAlimentacao)
admin.site.register(Cardapio)
admin.site.register(InversaoCardapio)
admin.site.register(AlteracaoCardapio)
admin.site.register(SuspensaoAlimentacao)
