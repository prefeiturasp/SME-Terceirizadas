from django.contrib import admin
from .models import TipoRefeicao, Refeicao, Alimento, CradapioDia, StatusCardapio


@admin.register(Alimento)
class FoodAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'ativo']
    ordering = ['titulo']


admin.site.register(TipoRefeicao)
admin.site.register(Refeicao)
admin.site.register(CradapioDia)
admin.site.register(StatusCardapio)
