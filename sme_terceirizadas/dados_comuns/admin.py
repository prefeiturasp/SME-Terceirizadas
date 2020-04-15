from django.contrib import admin

from .models import Contato, LogSolicitacoesUsuario, PerguntaFrequente, TemplateMensagem

admin.site.register(Contato)
admin.site.register(LogSolicitacoesUsuario)
admin.site.register(PerguntaFrequente)
admin.site.register(TemplateMensagem)
