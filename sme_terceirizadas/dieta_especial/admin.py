from django.contrib import admin, messages
from django.shortcuts import redirect
from django.urls import path

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
from .tasks import processa_dietas_especiais_task


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


@admin.register(SolicitacaoDietaEspecial)
class SolicitacaoDietaEspecialAdmin(admin.ModelAdmin):
    list_display = ('id_externo', '__str__', 'status', 'ativo')
    list_display_links = ('__str__',)
    change_list_template = 'dieta_especial/change_list.html'

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('inativa_dietas/', self.admin_site.admin_view(self.inativa_dietas, cacheable=True)),
        ]
        return my_urls + urls

    def inativa_dietas(self, request):
        processa_dietas_especiais_task.delay()
        messages.add_message(
            request,
            messages.INFO,
            'Inativação de dietas disparada com sucesso. Dentro de instantes as dietas serão atualizadas.'
        )
        return redirect('admin:dieta_especial_solicitacaodietaespecial_changelist')


admin.site.register(SubstituicaoAlimento)
admin.site.register(TipoContagem)
