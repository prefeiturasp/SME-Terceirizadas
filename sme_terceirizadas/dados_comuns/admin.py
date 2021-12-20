from django.contrib import admin

from .models import (
    CategoriaPerguntaFrequente,
    Contato,
    Endereco,
    LogSolicitacoesUsuario,
    Notificacao,
    PerguntaFrequente,
    TemplateMensagem
)


@admin.register(Contato)
class ContatoAdmin(admin.ModelAdmin):
    list_display = ('email', 'nome', 'telefone', 'telefone2')
    search_fields = ('email', 'nome', 'telefone', 'telefone2')


admin.site.register(CategoriaPerguntaFrequente)
admin.site.register(Endereco)
admin.site.register(LogSolicitacoesUsuario)
admin.site.register(Notificacao)
admin.site.register(PerguntaFrequente)
admin.site.register(TemplateMensagem)
