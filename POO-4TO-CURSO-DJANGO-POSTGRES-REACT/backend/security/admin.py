from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("email",)
    list_display = ("pkid", "id", "email", "username", "first_name", "last_name", "is_staff", "is_active")
    list_display_links = ("id", "email")
    list_filter = ("is_staff", "is_active")
    search_fields = ("email", "username", "first_name", "last_name")
    fieldsets = (
        (_("Credenciales"), {"fields": ("email", "password")}),
        (_("Photo"), {"fields": ("foto",)}),
        (_("Información personal"), {"fields": ("username", "first_name", "last_name")}),
        (_("Permisos"), {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        (_("Fechas importantes"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "username", "first_name", "last_name", "password1", "password2"),
        }),
    )
