from rest_framework import serializers
from .models import ProgressPhoto, Milestone
from apps.skincare_analysis.serializers import SkinScanListSerializer


class ProgressPhotoSerializer(serializers.ModelSerializer):
    scan = SkinScanListSerializer(read_only=True)
    
    class Meta:
        model = ProgressPhoto
        fields = ['id', 'image', 'skin_score', 'notes', 'scan', 'created_at']
        read_only_fields = ['id', 'created_at']


class MilestoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Milestone
        fields = ['id', 'milestone_type', 'title', 'description', 'value', 'achieved_at']
        read_only_fields = ['id', 'achieved_at']


class ProgressSummarySerializer(serializers.Serializer):
    """Summary of user's skin progress."""
    
    current_score = serializers.IntegerField()
    score_change = serializers.IntegerField()
    total_scans = serializers.IntegerField()
    days_tracked = serializers.IntegerField()
    score_history = serializers.ListField()
