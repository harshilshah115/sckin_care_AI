from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg
from datetime import timedelta
from django.utils import timezone

from .models import ProgressPhoto, Milestone
from .serializers import ProgressPhotoSerializer, MilestoneSerializer
from apps.skincare_analysis.models import SkinScan, Question
from apps.skincare_analysis.serializers import SkinScanListSerializer, QuestionSerializer


class ScanHistoryView(generics.ListAPIView):
    """List user's scan history."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = SkinScanListSerializer
    
    def get_queryset(self):
        return SkinScan.objects.filter(user=self.request.user)


class QuestionHistoryView(generics.ListAPIView):
    """List user's question history."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = QuestionSerializer
    
    def get_queryset(self):
        return Question.objects.filter(user=self.request.user)


class ProgressPhotoListView(generics.ListCreateAPIView):
    """List and add progress photos."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = ProgressPhotoSerializer
    
    def get_queryset(self):
        return ProgressPhoto.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MilestoneListView(generics.ListAPIView):
    """List user's milestones."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = MilestoneSerializer
    
    def get_queryset(self):
        return Milestone.objects.filter(user=self.request.user)


class ProgressSummaryView(APIView):
    """Get comprehensive progress summary."""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Get scan data
        scans = SkinScan.objects.filter(user=user).order_by('created_at')
        total_scans = scans.count()
        
        # Calculate score history
        score_history = []
        for scan in scans:
            score_history.append({
                'date': scan.created_at.strftime('%b %d'),
                'score': scan.skin_score
            })
        
        # Current and first scores
        current_score = scans.last().skin_score if scans.exists() else 0
        first_score = scans.first().skin_score if scans.exists() else 0
        score_change = current_score - first_score
        
        # Days tracked (from first scan to now)
        if scans.exists():
            first_scan_date = scans.first().created_at.date()
            days_tracked = (timezone.now().date() - first_scan_date).days + 1
        else:
            days_tracked = 0
        
        # Get questions count
        total_questions = Question.objects.filter(user=user).count()
        
        # Get recent milestones
        milestones = Milestone.objects.filter(user=user)[:5]
        
        # Calculate improvement areas
        improvements = []
        if scans.count() >= 2:
            first_scan = scans.first()
            last_scan = scans.last()
            
            # Compare detected issues
            def get_issue_name(item):
                if isinstance(item, dict):
                    return item.get('name', '')
                elif isinstance(item, str):
                    return item
                return str(item) if item else ''

            first_issues = set(get_issue_name(i) for i in first_scan.detected_issues)
            last_issues = set(get_issue_name(i) for i in last_scan.detected_issues)

            resolved = first_issues - last_issues
            for issue in resolved:
                improvements.append({
                    'label': issue,
                    'improvement': 100
                })
        
        return Response({
            'current_score': current_score,
            'score_change': score_change,
            'total_scans': total_scans,
            'total_questions': total_questions,
            'days_tracked': days_tracked,
            'score_history': score_history[-10:],  # Last 10 entries
            'milestones': MilestoneSerializer(milestones, many=True).data,
            'improvements': improvements
        })


class ActivityTimelineView(APIView):
    """Get user's activity timeline."""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        try:
            limit = int(request.query_params.get('limit', 20))
        except (ValueError, TypeError):
            limit = 20
        limit = max(1, min(limit, 100))
        
        # Get recent scans
        scans = SkinScan.objects.filter(user=user).order_by('-created_at')[:limit]
        
        # Get recent questions
        questions = Question.objects.filter(user=user).order_by('-created_at')[:limit]
        
        # Combine and sort by date
        activities = []
        
        for scan in scans:
            activities.append({
                'type': 'scan',
                'id': scan.id,
                'title': f'{scan.scan_type.replace("_", " ").title()}',
                'subtitle': f'Score: {scan.skin_score}',
                'date': scan.created_at,
                'data': {
                    'image': scan.image.url if scan.image else None,
                    'score': scan.skin_score,
                    'issues': scan.detected_issues[:3]
                }
            })
        
        for question in questions:
            activities.append({
                'type': 'question',
                'id': question.id,
                'title': question.question_text[:50] + '...' if len(question.question_text) > 50 else question.question_text,
                'subtitle': question.category,
                'date': question.created_at,
                'data': {
                    'answer_preview': question.answer_text[:100] + '...' if len(question.answer_text) > 100 else question.answer_text
                }
            })
        
        # Sort by date
        activities.sort(key=lambda x: x['date'], reverse=True)
        
        return Response(activities[:limit])
