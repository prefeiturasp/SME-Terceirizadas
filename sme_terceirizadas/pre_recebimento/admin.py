from django.contrib import admin

from .models import (
    ContatoLaboratorio,
    Cronograma,
    EtapasDoCronograma,
    Laboratorio,
    ProgramacaoDoRecebimentoDoCronograma
)


class ContatoInline(admin.StackedInline):
    model = ContatoLaboratorio
    extra = 1
    show_change_link = True


@admin.register(Laboratorio)
class Laboratoriodmin(admin.ModelAdmin):
    list_display = ('nome', 'cnpj', 'cidade', 'credenciado')
    ordering = ('-criado_em',)
    search_fields = ('nome',)
    list_filter = ('nome',)
    readonly_fields = ('uuid',)
    inlines = [ContatoInline]


admin.site.register(Cronograma)
admin.site.register(EtapasDoCronograma)
admin.site.register(ProgramacaoDoRecebimentoDoCronograma)
