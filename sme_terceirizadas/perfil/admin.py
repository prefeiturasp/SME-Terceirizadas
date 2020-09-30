from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.core.management import call_command
from django.utils.translation import ugettext_lazy as _

from .models import Cargo, Perfil, Usuario, Vinculo


class BaseUserAdmin(DjangoUserAdmin):
    """Define admin model for custom User model with no email field."""

    fieldsets = (
        (None, {
            'fields': (
                'email', 'tipo_email', 'password', 'cpf',
                'registro_funcional', 'nome', 'cargo', 'crn_numero'
            )
        }),
        (_('Permissions'), {
            'fields': (
                'is_active', 'is_staff', 'is_superuser', 'groups',
                'user_permissions'
            )
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined')
        }),
    )
    add_fieldsets = ((None, {
        'classes': ('wide',),
        'fields': (
            'email', 'password1', 'password2', 'cpf', 'registro_funcional',
            'nome', 'cargo'
        ),
    }),)
    list_display = ('email', 'nome', 'is_staff', 'is_active')
    search_fields = ('email', 'nome')
    ordering = ('email',)
    actions = ('carga_dados',)

    def carga_dados(self, request, queryset):
        return call_command('carga_dados')


@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('nome', 'super_usuario', 'ativo')
    search_fields = ('nome',)

admin.site.register(Usuario, BaseUserAdmin)
admin.site.register(Vinculo)
admin.site.register(Cargo)
