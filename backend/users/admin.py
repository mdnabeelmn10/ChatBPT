from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User

class UserAdmin(BaseUserAdmin):
    # Add 'tier' to the fieldsets used when editing users
    fieldsets = BaseUserAdmin.fieldsets + (
        (_('Custom Fields'), {'fields': ('tier',)}),
    )

    # Add 'tier' to the fields shown when creating a user
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        (_('Custom Fields'), {'fields': ('tier',)}),
    )

    # Show 'tier' in the admin user list
    list_display = ('username', 'email', 'tier', 'is_staff', 'is_superuser')
    list_filter = ('tier', 'is_staff', 'is_superuser', 'is_active')

# Register the customized admin
admin.site.register(User, UserAdmin)
