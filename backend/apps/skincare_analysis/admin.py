from django.contrib import admin
from .models import SkinScan, Question


@admin.register(SkinScan)
class SkinScanAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'scan_type', 'skin_score', 'severity', 'created_at']
    list_filter = ['scan_type', 'severity', 'created_at']
    search_fields = ['user__email', 'analysis_text']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'category', 'question_short', 'is_helpful', 'created_at']
    list_filter = ['category', 'is_helpful', 'created_at']
    search_fields = ['user__email', 'question_text', 'answer_text']
    readonly_fields = ['created_at']
    ordering = ['-created_at']
    
    def question_short(self, obj):
        return obj.question_text[:50] + '...' if len(obj.question_text) > 50 else obj.question_text
    question_short.short_description = 'Question'
