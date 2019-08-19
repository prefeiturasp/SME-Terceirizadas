from django.contrib import admin

from .models import (TemplateMensagem, Contato, Endereco, LogSolicitacoesUsuario)

admin.site.register(Contato)
admin.site.register(TemplateMensagem)
admin.site.register(Endereco)
admin.site.register(LogSolicitacoesUsuario)
