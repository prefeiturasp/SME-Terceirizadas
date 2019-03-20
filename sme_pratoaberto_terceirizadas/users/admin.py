from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model

from sme_pratoaberto_terceirizadas.users.forms import UserChangeForm, UserCreationForm

User = get_user_model()


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    fieldsets = (("User", {"fields": ("first_name",)}),) + auth_admin.UserAdmin.fieldsets
    list_display = ["username", "first_name", "is_superuser"]
    search_fields = ["first_name", "last_name", "functional_register"]
