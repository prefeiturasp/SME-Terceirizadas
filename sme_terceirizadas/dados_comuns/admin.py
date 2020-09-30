from django.contrib import admin

from .models import (
    CategoriaPerguntaFrequente,
    Contato,
    Endereco,
    LogSolicitacoesUsuario,
    PerguntaFrequente,
    TemplateMensagem
)


@admin.register(Contato)
class ContatoAdmin(admin.ModelAdmin):
    list_display = ('telefone', 'telefone2', 'email')
    search_fields = ('telefone', 'telefone2', 'email')


admin.site.register(CategoriaPerguntaFrequente)
admin.site.register(Endereco)
admin.site.register(LogSolicitacoesUsuario)
admin.site.register(PerguntaFrequente)
admin.site.register(TemplateMensagem)
