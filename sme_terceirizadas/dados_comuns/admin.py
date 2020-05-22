from django.contrib import admin

from .models import CategoriaPerguntaFrequente, Contato, LogSolicitacoesUsuario, PerguntaFrequente, TemplateMensagem

admin.site.register(CategoriaPerguntaFrequente)
admin.site.register(Contato)
admin.site.register(LogSolicitacoesUsuario)
admin.site.register(PerguntaFrequente)
admin.site.register(TemplateMensagem)
