from django.contrib import admin

from .models import (
    AlergiaIntolerancia,
    Alimento,
    Anexo,
    ClassificacaoDieta,
    MotivoAlteracaoUE,
    MotivoNegacao,
    SolicitacaoDietaEspecial,
    SubstituicaoAlimento,
    TipoContagem
)


@admin.register(AlergiaIntolerancia)
class AlergiaIntoleranciaAdmin(admin.ModelAdmin):
    list_display = ('descricao',)
    search_fields = ('descricao',)
    ordering = ('descricao',)


@admin.register(Alimento)
class AlimentoAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    search_fields = ('nome',)
    ordering = ('nome',)


admin.site.register(Anexo)
admin.site.register(ClassificacaoDieta)
admin.site.register(MotivoAlteracaoUE)
admin.site.register(MotivoNegacao)
admin.site.register(SolicitacaoDietaEspecial)
admin.site.register(SubstituicaoAlimento)
admin.site.register(TipoContagem)
