from django.contrib import admin

from .models import (Contato, Endereco, LogSolicitacoesUsuario, TemplateMensagem)

admin.site.register(Contato)
admin.site.register(TemplateMensagem)
admin.site.register(Endereco)
admin.site.register(LogSolicitacoesUsuario)
