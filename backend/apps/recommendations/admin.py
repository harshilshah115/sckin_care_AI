from django.contrib import admin
from .models import SavedProduct, SavedRemedy, SkincareRoutine, RoutineLog


@admin.register(SavedProduct)
class SavedProductAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email', 'product__name']


@admin.register(SavedRemedy)
class SavedRemedyAdmin(admin.ModelAdmin):
    list_display = ['user', 'remedy', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email', 'remedy__title']


@admin.register(SkincareRoutine)
class SkincareRoutineAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'routine_type', 'is_active', 'created_at']
    list_filter = ['routine_type', 'is_active']
    search_fields = ['user__email', 'name']


@admin.register(RoutineLog)
class RoutineLogAdmin(admin.ModelAdmin):
    list_display = ['user', 'routine_type', 'completed_at']
    list_filter = ['routine_type', 'completed_at']
    search_fields = ['user__email']
