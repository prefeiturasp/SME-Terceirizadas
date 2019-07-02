from django.contrib import admin

from .models import TipoAlimentacao, Cardapio, InversaoCardapio, AlteracaoCardapio

admin.site.register(TipoAlimentacao)
admin.site.register(Cardapio)
admin.site.register(InversaoCardapio)
admin.site.register(AlteracaoCardapio)
