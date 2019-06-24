from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _

from .models import User, Perfil, Instituicao


class BaseUserAdmin(DjangoUserAdmin):
    """Define admin model for custom User model with no email field."""

    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        (_('Personal info'), {
            'fields': ('email', 'name')
        }),
        (_('Profile'), {
            'fields': ('profile',)
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
    list_display = ('email', 'name', 'is_staff', 'is_active')
    search_fields = ('email', 'name')
    ordering = ('email',)


admin.site.register(Instituicao)
admin.site.register(User, BaseUserAdmin)


@admin.register(Perfil)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['titulo', 'instituicao', 'uuid']
    ordering = ['titulo', 'instituicao']
