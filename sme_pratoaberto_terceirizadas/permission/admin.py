from django.contrib import admin
from .models import Permission, ProfilePermission


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    list_display = ['title']


@admin.register(ProfilePermission)
class ProfilePermissionAdmin(admin.ModelAdmin):
    list_display = ['profile', 'permission', 'verbs']
