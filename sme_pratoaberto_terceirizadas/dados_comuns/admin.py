from django.contrib import admin

from .models import (TemplateMensagem, Contato, Endereco)

admin.site.register(Contato)
admin.site.register(TemplateMensagem)
admin.site.register(Endereco)
