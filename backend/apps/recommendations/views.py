from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction

from .models import SavedProduct, SavedRemedy, SkincareRoutine, RoutineLog
from .serializers import (
    SavedProductSerializer,
    SavedRemedySerializer,
    SkincareRoutineSerializer,
    RoutineLogSerializer
)
from apps.products.models import Product, NaturalRemedy
from apps.skincare_analysis.models import SkinScan, Question
from apps.skincare_analysis.ai_service import generate_personalized_routine


# Saved Products Views
class SavedProductListView(generics.ListCreateAPIView):
    """List and save products."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = SavedProductSerializer
    
    def get_queryset(self):
        return SavedProduct.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SavedProductDeleteView(APIView):
    """Remove a saved product."""
    
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, product_id):
        try:
            saved = SavedProduct.objects.get(user=request.user, product_id=product_id)
            saved.delete()
            return Response({'message': 'Product removed from saved'}, status=status.HTTP_204_NO_CONTENT)
        except SavedProduct.DoesNotExist:
            return Response({'error': 'Product not found in saved'}, status=status.HTTP_404_NOT_FOUND)


# Saved Remedies Views
class SavedRemedyListView(generics.ListCreateAPIView):
    """List and save remedies."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = SavedRemedySerializer
    
    def get_queryset(self):
        return SavedRemedy.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class SavedRemedyDeleteView(APIView):
    """Remove a saved remedy."""
    
    permission_classes = [IsAuthenticated]
    
    def delete(self, request, remedy_id):
        try:
            saved = SavedRemedy.objects.get(user=request.user, remedy_id=remedy_id)
            saved.delete()
            return Response({'message': 'Remedy removed from saved'}, status=status.HTTP_204_NO_CONTENT)
        except SavedRemedy.DoesNotExist:
            return Response({'error': 'Remedy not found in saved'}, status=status.HTTP_404_NOT_FOUND)


# Routine Views
class RoutineListCreateView(generics.ListCreateAPIView):
    """List and create skincare routines."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = SkincareRoutineSerializer
    
    def get_queryset(self):
        queryset = SkincareRoutine.objects.filter(user=self.request.user)
        routine_type = self.request.query_params.get('type')
        if routine_type:
            queryset = queryset.filter(routine_type=routine_type)
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class RoutineDetailView(generics.RetrieveUpdateDestroyAPIView):
    """Get, update, or delete a routine."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = SkincareRoutineSerializer
    
    def get_queryset(self):
        return SkincareRoutine.objects.filter(user=self.request.user)


def _normalize_steps(steps):
    normalized = []
    for idx, item in enumerate(steps or [], start=1):
        if not isinstance(item, dict):
            continue
        step_no = item.get('step') or idx
        normalized.append({
            'step': step_no,
            'step_name': item.get('name') or item.get('step_name') or f"Step {step_no}",
            'product_type': item.get('product_type', ''),
            'instructions': item.get('instructions', ''),
            'duration': item.get('duration', ''),
            'key_ingredients': item.get('key_ingredients', [])
        })
    return normalized


def _normalize_weekly_treatments(treatments):
    normalized = []
    for idx, item in enumerate(treatments or [], start=1):
        if not isinstance(item, dict):
            continue
        normalized.append({
            'step': idx,
            'name': item.get('name', f"Weekly Step {idx}"),
            'frequency': item.get('frequency', ''),
            'day': item.get('day', ''),
            'description': item.get('description', '')
        })
    return normalized


def _build_scan_summary(scan):
    if not scan:
        return None
    issues = [issue.get('name') for issue in scan.detected_issues if issue.get('name')]
    issues_text = ', '.join(issues) if issues else 'No major issues noted'
    analysis_snippet = (scan.analysis_text or '').strip()
    if len(analysis_snippet) > 280:
        analysis_snippet = f"{analysis_snippet[:277]}..."
    return (
        f"Scan type: {scan.scan_type}. Issues: {issues_text}. "
        f"Severity: {scan.severity}. Skin score: {scan.skin_score}. "
        f"Notes: {analysis_snippet or 'None'}"
    )


def _build_question_summary(question):
    if not question:
        return None
    answer_snippet = (question.answer_text or '').strip()
    if len(answer_snippet) > 280:
        answer_snippet = f"{answer_snippet[:277]}..."
    return (
        f"Q: {question.question_text}. "
        f"Category: {question.category}. "
        f"A: {answer_snippet or 'No answer text'}"
    )


class RoutineGenerateView(APIView):
    """Generate an AI routine plan based on user history and profile."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        days = request.data.get('days')
        custom_days = request.data.get('custom_days')

        plan_days = None
        if isinstance(days, str) and days.lower() == 'custom':
            try:
                plan_days = int(custom_days)
            except (TypeError, ValueError):
                return Response(
                    {'error': 'Invalid custom_days value'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        else:
            try:
                plan_days = int(days)
            except (TypeError, ValueError):
                return Response(
                    {'error': 'Invalid days value'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        if not plan_days or plan_days < 7 or plan_days > 90:
            return Response(
                {'error': 'Plan length must be between 7 and 90 days'},
                status=status.HTTP_400_BAD_REQUEST
            )

        has_scan = SkinScan.objects.filter(user=request.user).exists()
        has_question = Question.objects.filter(user=request.user).exists()

        if not (has_scan or has_question):
            return Response(
                {
                    'needs_ai': True,
                    'message': (
                        'You have not used AI yet, so we cannot build a routine. '
                        'Please create a routine with AI first.'
                    )
                },
                status=status.HTTP_200_OK
            )

        latest_scan = SkinScan.objects.filter(user=request.user).order_by('-created_at').first()
        latest_question = Question.objects.filter(user=request.user).order_by('-created_at').first()

        skin_profile = {
            'skin_type': request.user.skin_type or 'normal',
            'concerns': request.user.concerns or [],
            'sensitivity': request.user.sensitivity,
            'allergies': request.user.allergies,
            'age_group': request.user.age_group,
            'plan_days': plan_days,
            'scan_summary': _build_scan_summary(latest_scan),
            'question_summary': _build_question_summary(latest_question)
        }

        routine_result = generate_personalized_routine(skin_profile)
        if routine_result.get('error'):
            return Response(
                {
                    'error': routine_result.get('message', 'Routine generation failed')
                },
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )

        morning_steps = _normalize_steps(routine_result.get('morning_routine', []))
        night_steps = _normalize_steps(routine_result.get('night_routine', []))
        weekly_steps = _normalize_weekly_treatments(routine_result.get('weekly_treatments', []))

        routine_name = f"AI Routine ({plan_days} days)"
        routine_description = "Generated from AI using your recent scans and questions."

        with transaction.atomic():
            morning_routine = SkincareRoutine.objects.create(
                user=request.user,
                name=routine_name,
                routine_type='morning',
                description=routine_description,
                steps=morning_steps,
                frequency=f"Daily for {plan_days} days"
            )
            night_routine = SkincareRoutine.objects.create(
                user=request.user,
                name=routine_name,
                routine_type='night',
                description=routine_description,
                steps=night_steps,
                frequency=f"Daily for {plan_days} days"
            )

            weekly_routine = None
            if weekly_steps:
                weekly_routine = SkincareRoutine.objects.create(
                    user=request.user,
                    name=f"AI Weekly Treatments ({plan_days} days)",
                    routine_type='weekly',
                    description=routine_description,
                    steps=weekly_steps,
                    frequency=f"Weekly for {plan_days} days"
                )

        return Response(
            {
                'needs_ai': False,
                'message': 'Routine generated successfully',
                'plan_days': plan_days,
                'routines': {
                    'morning': SkincareRoutineSerializer(morning_routine).data,
                    'night': SkincareRoutineSerializer(night_routine).data,
                    'weekly': SkincareRoutineSerializer(weekly_routine).data if weekly_routine else None
                }
            },
            status=status.HTTP_201_CREATED
        )


# Routine Logging Views
class RoutineLogListCreateView(generics.ListCreateAPIView):
    """List and create routine logs."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = RoutineLogSerializer
    
    def get_queryset(self):
        queryset = RoutineLog.objects.filter(user=self.request.user)
        
        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(completed_at__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(completed_at__date__lte=end_date)
        
        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TodayRoutineStatusView(APIView):
    """Get today's routine completion status."""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        from datetime import date
        
        today_logs = RoutineLog.objects.filter(
            user=request.user,
            completed_at__date=date.today()
        )
        
        morning_done = today_logs.filter(routine_type='morning').exists()
        night_done = today_logs.filter(routine_type='night').exists()
        
        # Get user's routines
        routines = SkincareRoutine.objects.filter(user=request.user, is_active=True)
        
        return Response({
            'date': date.today().isoformat(),
            'morning': {
                'completed': morning_done,
                'routine': SkincareRoutineSerializer(
                    routines.filter(routine_type='morning').first()
                ).data if routines.filter(routine_type='morning').exists() else None
            },
            'night': {
                'completed': night_done,
                'routine': SkincareRoutineSerializer(
                    routines.filter(routine_type='night').first()
                ).data if routines.filter(routine_type='night').exists() else None
            }
        })
