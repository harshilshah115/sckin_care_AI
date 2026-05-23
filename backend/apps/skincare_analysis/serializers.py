from rest_framework import serializers
from .models import SkinScan, Question


def _truncate_text(text: str, max_length: int = 240) -> str:
    if not text:
        return ''
    normalized = ' '.join(str(text).split())
    if len(normalized) <= max_length:
        return normalized
    return f"{normalized[:max_length].rstrip()}..."


class SkinScanSerializer(serializers.ModelSerializer):
    """Serializer for skin scan results."""

    analysis_text_preview = serializers.SerializerMethodField()
    
    class Meta:
        model = SkinScan
        fields = [
            'id', 'image', 'scan_type', 'detected_issues', 'severity',
            'confidence_score', 'skin_score', 'metrics', 'analysis_text', 'analysis_text_preview',
            'recommendations',
            'ai_model_used', 'processing_time', 'created_at', 'updated_at'
        ]
        read_only_fields = [
            'id', 'detected_issues', 'severity', 'confidence_score', 'skin_score',
            'metrics', 'analysis_text', 'analysis_text_preview', 'recommendations',
            'ai_model_used', 'processing_time', 'created_at', 'updated_at'
        ]

    def get_analysis_text_preview(self, obj):
        return _truncate_text(obj.analysis_text)


class SkinScanCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating a new skin scan."""
    
    class Meta:
        model = SkinScan
        fields = ['image', 'scan_type']


class SkinScanListSerializer(serializers.ModelSerializer):
    """Serializer for listing skin scans (minimal data)."""

    analysis_text_preview = serializers.SerializerMethodField()
    
    class Meta:
        model = SkinScan
        fields = [
            'id', 'image', 'scan_type', 'detected_issues', 'skin_score', 'metrics',
            'severity', 'analysis_text_preview', 'created_at'
        ]

    def get_analysis_text_preview(self, obj):
        return _truncate_text(obj.analysis_text)


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for questions and answers."""
    
    class Meta:
        model = Question
        fields = [
            'id', 'question_text', 'category', 'answer_text', 'recommendations',
            'ai_model_used', 'processing_time', 'is_helpful', 'created_at'
        ]
        read_only_fields = [
            'id', 'answer_text', 'recommendations', 'ai_model_used',
            'processing_time', 'created_at'
        ]


class QuestionCreateSerializer(serializers.ModelSerializer):
    """Serializer for asking a new question."""
    
    class Meta:
        model = Question
        fields = ['question_text', 'category']


class QuestionFeedbackSerializer(serializers.ModelSerializer):
    """Serializer for providing feedback on an answer."""
    
    class Meta:
        model = Question
        fields = ['is_helpful']


class IngredientAnalysisSerializer(serializers.Serializer):
    """Serializer for ingredient analysis requests."""
    
    ingredients = serializers.ListField(
        child=serializers.CharField(max_length=200),
        min_length=1,
        max_length=100,
        help_text='List of ingredient names to analyze'
    )
    skin_type = serializers.ChoiceField(
        choices=['oily', 'dry', 'combination', 'normal', 'sensitive', 'unknown'],
        required=False,
        default='unknown'
    )
    concerns = serializers.ListField(
        child=serializers.CharField(max_length=100),
        required=False,
        default=list
    )
