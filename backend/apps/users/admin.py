from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'name', 'skin_type', 'is_active', 'is_staff', 'created_at']
    list_filter = ['is_active', 'is_staff', 'skin_type', 'sensitivity']
    search_fields = ['email', 'name']
    ordering = ['-created_at']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name', 'phone', 'avatar')}),
        ('Skin Profile', {'fields': ('skin_type', 'sensitivity', 'concerns', 'allergies', 'age_group', 'climate')}),
        ('Preferences', {'fields': ('notifications_enabled', 'email_updates')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified', 'groups', 'user_permissions')}),
        ('Dates', {'fields': ('last_login',)}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'name', 'password1', 'password2'),
        }),
    )
