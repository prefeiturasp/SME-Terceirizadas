from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _

from .models import (GrupoPerfil, Perfil, PerfilPermissao, Permissao, Usuario)


class BaseUserAdmin(DjangoUserAdmin):
    """Define admin model for custom User model with no email field."""

    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        (_('Personal info'), {
            'fields': ('nome', 'registro_funcional', 'cpf')
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined')
        }),
    )
    add_fieldsets = ((None, {
        'classes': ('wide',),
        'fields': ('email', 'password1', 'password2'),
    }),)
    list_display = ('email', 'nome', 'is_staff', 'is_active')
    search_fields = ('email', 'nome')
    ordering = ('email',)


admin.site.register(Usuario, BaseUserAdmin)
admin.site.register(Perfil)
admin.site.register(GrupoPerfil)
admin.site.register(Permissao)
admin.site.register(PerfilPermissao)
