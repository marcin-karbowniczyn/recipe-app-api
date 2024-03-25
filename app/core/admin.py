""" Django Admin Customization """
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _  # Future-proof if we wanted to translate the project
from core import models


# BaseUserAdmin gives us some predefined auth, like requiring passwords and username.
# With ModelAdmin, we won't get the FieldError that expects username field on our User Model (we have email)
class UserAdmin(BaseUserAdmin):
    """ Define the admin pages for users """
    # The fields we specify need to match the fields we specified on our User Model (reminder for my future self)
    ordering = ['id']
    list_display = ['email', 'name']
    fieldsets = (
        (None, {'fields': ('email', 'password', 'name')}),
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        (_('Important dates'), {'fields': ('last_login',)})
    )
    readonly_fields = ['last_login']
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'name', 'is_active', 'is_staff', 'is_superuser')
        }),
    )


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Recipe)
