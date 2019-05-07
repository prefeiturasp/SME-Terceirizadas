from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.utils.translation import ugettext_lazy as _

from .models import User, Profile, Institution


class BaseUserAdmin(DjangoUserAdmin):
    """Define admin model for custom User model with no email field."""

    fieldsets = (
        (None, {
            'fields': ('email', 'password')
        }),
        (_('Personal info'), {
            'fields': ('name',)
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
    list_display = ('name', 'email', 'is_staff', 'is_active')
    search_fields = ('email', 'name')
    ordering = ('email',)


admin.site.register(Institution)
admin.site.register(User, BaseUserAdmin)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['title', 'institution', 'uuid']
    ordering = ['title', 'institution']
