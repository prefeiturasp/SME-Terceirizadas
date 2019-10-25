from django.contrib import admin

from .models import (Contato, LogSolicitacoesUsuario, TemplateMensagem)

admin.site.register(Contato)
admin.site.register(TemplateMensagem)
admin.site.register(LogSolicitacoesUsuario)
