from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from accounts.models import User


class UserAdmin(BaseUserAdmin[User]):
    fieldsets = (
        (None, {"fields": ("identifier", "password")}),
        (_("Personal info"), {"fields": ("email", "first_name", "last_name")}),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("identifier", "email", "password1", "password2"),
            },
        ),
    )
    list_display = ("identifier", "email", "first_name", "last_name", "is_staff")
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    search_fields = ("identifier", "email", "first_name", "last_name")
    ordering = ("identifier",)
    readonly_fields = ()  # identifier is editable in this case


admin.site.register(User, UserAdmin)
