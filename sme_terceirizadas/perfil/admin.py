from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _

from .models import Perfil, Usuario, Vinculo


class BaseUserAdmin(DjangoUserAdmin):
    """Define admin model for custom User model with no email field."""

    fieldsets = (
        (None, {
            'fields': ('email', 'tipo_email', 'password', 'cpf', 'registro_funcional', 'nome', 'crn_numero')
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
        'fields': ('email', 'password1', 'password2', 'cpf', 'registro_funcional', 'nome'),
    }),)
    list_display = ('email', 'nome', 'is_staff', 'is_active')
    search_fields = ('email', 'nome')
    ordering = ('email',)


admin.site.register(Usuario, BaseUserAdmin)
admin.site.register(Perfil)
admin.site.register(Vinculo)
