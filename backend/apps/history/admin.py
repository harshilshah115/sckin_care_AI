from django.contrib import admin
from .models import ProgressPhoto, Milestone


@admin.register(ProgressPhoto)
class ProgressPhotoAdmin(admin.ModelAdmin):
    list_display = ['user', 'skin_score', 'created_at']
    list_filter = ['created_at']
    search_fields = ['user__email']


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ['user', 'milestone_type', 'title', 'value', 'achieved_at']
    list_filter = ['milestone_type', 'achieved_at']
    search_fields = ['user__email', 'title']
