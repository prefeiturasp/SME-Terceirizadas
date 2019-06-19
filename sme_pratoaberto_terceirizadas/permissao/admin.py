from django.contrib import admin
from .models import Permissao, PerfilPermissao


@admin.register(Permissao)
class PermissaoAdmin(admin.ModelAdmin):
    list_display = ['titulo']


@admin.register(PerfilPermissao)
class PerfilPermissaoAdmin(admin.ModelAdmin):
    list_display = ['perfil', 'permissao', 'acao']
