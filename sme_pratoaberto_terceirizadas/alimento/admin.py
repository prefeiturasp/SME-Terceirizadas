from django.contrib import admin
from .models import TipoRefeicao, Refeicao, Alimento, CardapioDia, StatusCardapio


@admin.register(Alimento)
class FoodAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'ativo']
    ordering = ['titulo']


admin.site.register(TipoRefeicao)
admin.site.register(Refeicao)
admin.site.register(CardapioDia)
admin.site.register(StatusCardapio)
