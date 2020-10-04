from django.contrib import admin

from .models import (
    AlergiaIntolerancia,
    Alimento,
    Anexo,
    ClassificacaoDieta,
    MotivoNegacao,
    SolicitacaoDietaEspecial,
    SubstituicaoAlimento,
    TipoContagem,
)


@admin.register(Alimento)
class AlimentoAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)

admin.site.register(AlergiaIntolerancia)
admin.site.register(Anexo)
admin.site.register(ClassificacaoDieta)
admin.site.register(MotivoNegacao)
admin.site.register(SolicitacaoDietaEspecial)
admin.site.register(SubstituicaoAlimento)
admin.site.register(TipoContagem)
