from django.contrib import admin

from .forms import CaixaAltaNomeForm
from .models import Cronograma, EmbalagemQld, EtapasDoCronograma, Laboratorio, ProgramacaoDoRecebimentoDoCronograma


@admin.register(Laboratorio)
class Laboratoriodmin(admin.ModelAdmin):
    form = CaixaAltaNomeForm
    list_display = ('nome', 'cnpj', 'cidade', 'credenciado')
    ordering = ('-criado_em',)
    search_fields = ('nome',)
    list_filter = ('nome',)
    readonly_fields = ('uuid',)


@admin.register(EmbalagemQld)
class EmbalagemQldAdmin(admin.ModelAdmin):
    form = CaixaAltaNomeForm
    list_display = ('nome', 'abreviacao', 'criado_em')
    search_fields = ('nome',)
    readonly_fields = ('uuid',)


admin.site.register(Cronograma)
admin.site.register(EtapasDoCronograma)
admin.site.register(ProgramacaoDoRecebimentoDoCronograma)
