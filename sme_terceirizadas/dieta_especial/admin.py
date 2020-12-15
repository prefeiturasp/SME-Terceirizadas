from django.contrib import admin, messages
from django.shortcuts import redirect
from django.urls import path

from sme_terceirizadas.dados_comuns.constants import COORDENADOR_LOGISTICA
from sme_terceirizadas.escola.models import Codae

from .forms import AlimentoProprioForm
from .models import (
    AlergiaIntolerancia,
    Alimento,
    AlimentoProprio,
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


@admin.register(AlimentoProprio)
class AlimentoProprioAdmin(admin.ModelAdmin):
    list_display = ('nome', 'marca', 'outras_informacoes', 'ativo')
    search_fields = ('nome', 'marca__nome', 'outras_informacoes')
    list_filter = ('ativo',)
    ordering = ('nome',)
    readonly_fields = ('tipo',)
    form = AlimentoProprioForm
    actions = ('inativar_alimentos',)

    def inativar_alimentos(self, request, queryset):
        count = queryset.update(ativo=False)

        if count == 1:
            msg = '{} alimento próprio foi inativado.'  # noqa P103
        else:
            msg = '{} alimentos próprios foram inativados.'  # noqa P103

        self.message_user(request, msg.format(count))

    inativar_alimentos.short_description = 'Marcar para inativar alimentos'

    def has_module_permission(self, request, obj=None):
        usuario = request.user
        if usuario:
            if not usuario.is_anonymous:
                return (
                    not usuario.is_anonymous and
                    usuario.vinculo_atual and
                    isinstance(usuario.vinculo_atual.instituicao, Codae) and
                    usuario.vinculo_atual.perfil.nome in [COORDENADOR_LOGISTICA] or
                    usuario.email == 'admin@admin.com'
                )
        return False

    def has_delete_permission(self, request, obj=None):
        return False


admin.site.register(Anexo)
admin.site.register(ClassificacaoDieta)
admin.site.register(MotivoAlteracaoUE)
admin.site.register(MotivoNegacao)


@admin.register(SolicitacaoDietaEspecial)
class SolicitacaoDietaEspecialAdmin(admin.ModelAdmin):
    list_display = ('id_externo', '__str__', 'status', 'ativo')
    list_display_links = ('__str__',)
    readonly_fields = ('aluno',)
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
