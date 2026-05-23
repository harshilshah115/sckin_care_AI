from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import MultiPartParser, FormParser
import os
import logging

from .models import SkinScan, Question
from apps.history.models import ProgressPhoto
from .serializers import (
    SkinScanSerializer,
    SkinScanCreateSerializer,
    SkinScanListSerializer,
    QuestionSerializer,
    QuestionCreateSerializer,
    QuestionFeedbackSerializer,
    IngredientAnalysisSerializer
)
from .ai_service import analyze_skin_image, answer_skincare_question
from .ingredient_analyzer import analyze_ingredients

logger = logging.getLogger(__name__)


class SkinScanCreateView(APIView):
    """Create a new skin scan and get AI analysis."""
    
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    
    def post(self, request):
        serializer = SkinScanCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Save the scan first
            scan = serializer.save(user=request.user)
            
            # Get user profile for personalization
            user_profile = {
                'age': request.data.get('age') or None,
                'skin_type': request.data.get('skin_type') or request.user.skin_type,
                'sensitivity': request.user.sensitivity,
                'concerns': request.user.concerns,
                'allergies': request.user.allergies,
                'sleep_hours': request.data.get('sleep_hours') or None,
                'water_intake': request.data.get('water_intake') or None,
            }
            
            # Run AI analysis
            with scan.image.open('rb') as img_file:
                image_bytes = img_file.read()
            analysis = analyze_skin_image(scan.image.path, user_profile)
            
            # Check for errors
            if analysis.get('error'):
                # AI failed, but save scan with basic info
                friendly_message = analysis.get('friendly_message') or analysis.get('message', 'Unknown error')
                scan.analysis_text = f"Analysis temporarily unavailable: {friendly_message}"
                scan.ai_model_used = 'error'
                scan.processing_time = analysis.get('processing_time', 0)
                scan.save()
                
                return Response({
                    'message': 'Scan uploaded but AI analysis failed',
                    'scan': SkinScanSerializer(scan).data,
                    'error': analysis.get('message'),
                    'analysis_message': friendly_message,
                    'alerts': analysis.get('alerts', []),
                    'fallback': True
                }, status=status.HTTP_201_CREATED)
            
            # Check for doctor referral
            if analysis.get('refer_to_doctor'):
                scan.analysis_text = analysis.get('message', '')
                scan.severity = 'refer_to_doctor'
                scan.detected_issues = [{'name': analysis.get('detected_issue', 'Requires Assessment'), 'severity': 'refer_to_doctor'}]
                scan.metrics = analysis.get('metrics', {})
                scan.ai_model_used = analysis.get('ai_model_used', os.getenv('AI_MODEL', 'gemini-2.0-flash'))
                scan.processing_time = analysis.get('processing_time', 0)
                scan.save()
                
                return Response({
                    'message': 'Analysis complete - professional consultation recommended',
                    'scan': SkinScanSerializer(scan).data,
                    'refer_to_doctor': True,
                    'disclaimer': analysis.get('disclaimer', '')
                }, status=status.HTTP_201_CREATED)
            
            # Normal successful analysis
            scan.detected_issues = analysis.get('detected_issues', [])
            scan.severity = analysis.get('severity', 'unknown')
            scan.confidence_score = analysis.get('confidence_score', 0)
            scan.skin_score = analysis.get('skin_score', 0)
            scan.metrics = analysis.get('metrics', {})
            scan.analysis_text = analysis.get('analysis_text', '')
            scan.recommendations = analysis.get('recommendations', {})
            scan.ai_model_used = analysis.get('ai_model_used', os.getenv('AI_MODEL', 'gemini-2.0-flash'))
            scan.processing_time = analysis.get('processing_time', 0)
            scan.save()

            try:
                ProgressPhoto.objects.create(
                    user=request.user,
                    image=scan.image,
                    skin_score=scan.skin_score,
                    scan=scan
                )
            except Exception as error:
                logger.warning("Progress photo creation failed: %s", error)
            
            return Response({
                'message': 'Skin analysis completed successfully',
                'scan': SkinScanSerializer(scan).data,
                'disclaimer': analysis.get('disclaimer', ''),
                'severity_warning': analysis.get('severity_warning', '')
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SkinScanListView(generics.ListAPIView):
    """List all skin scans for the current user."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = SkinScanListSerializer
    
    def get_queryset(self):
        return SkinScan.objects.filter(user=self.request.user)


class SkinScanDetailView(generics.RetrieveDestroyAPIView):
    """Get or delete a specific skin scan."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = SkinScanSerializer
    
    def get_queryset(self):
        return SkinScan.objects.filter(user=self.request.user)


class QuestionCreateView(APIView):
    """Ask a skincare question and get AI answer."""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = QuestionCreateSerializer(data=request.data)
        if serializer.is_valid():
            # Save the question first
            question = serializer.save(user=request.user)
            
            # Get user profile for personalization
            user_profile = {
                'skin_type': request.user.skin_type,
                'sensitivity': request.user.sensitivity,
                'concerns': request.user.concerns,
            }
            
            # Get AI answer
            answer = answer_skincare_question(question.question_text, user_profile)
            
            # Check for errors
            if answer.get('error'):
                question.answer_text = f"I apologize, but I'm unable to provide an answer at this time. {answer.get('message', '')}"
                question.ai_model_used = 'error'
                question.processing_time = answer.get('processing_time', 0)
                question.save()
                
                return Response({
                    'message': 'Question saved but AI answer failed',
                    'question': QuestionSerializer(question).data,
                    'error': answer.get('message'),
                    'fallback': True
                }, status=status.HTTP_201_CREATED)
            
            # Check for safety redirect
            if answer.get('safety_redirect'):
                question.answer_text = answer.get('answer_text', '')
                question.ai_model_used = answer.get('ai_model_used', os.getenv('AI_MODEL', 'gemini-2.0-flash'))
                question.processing_time = answer.get('processing_time', 0)
                question.save()
                
                return Response({
                    'message': 'Question answered - please consult a professional',
                    'question': QuestionSerializer(question).data,
                    'disclaimer': answer.get('disclaimer', ''),
                    'safety_redirect': True
                }, status=status.HTTP_201_CREATED)
            
            # Normal successful answer
            question.answer_text = answer.get('answer_text', '')
            question.recommendations = answer.get('recommendations', {})
            question.ai_model_used = answer.get('ai_model_used', os.getenv('AI_MODEL', 'gemini-2.0-flash'))
            question.processing_time = answer.get('processing_time', 0)
            question.save()
            
            return Response({
                'message': 'Question answered successfully',
                'question': QuestionSerializer(question).data,
                'disclaimer': answer.get('disclaimer', '')
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class QuestionListView(generics.ListAPIView):
    """List all questions for the current user."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = QuestionSerializer
    
    def get_queryset(self):
        return Question.objects.filter(user=self.request.user)


class QuestionDetailView(generics.RetrieveDestroyAPIView):
    """Get or delete a specific question."""
    
    permission_classes = [IsAuthenticated]
    serializer_class = QuestionSerializer
    
    def get_queryset(self):
        return Question.objects.filter(user=self.request.user)


class QuestionFeedbackView(APIView):
    """Provide feedback on a question answer."""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request, pk):
        try:
            question = Question.objects.get(pk=pk, user=request.user)
        except Question.DoesNotExist:
            return Response({'error': 'Question not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = QuestionFeedbackSerializer(question, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({'message': 'Feedback recorded'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class IngredientAnalysisView(APIView):
    """Analyze product ingredients for safety and skin-type suitability."""
    
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = IngredientAnalysisSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        user_profile = {
            'skin_type': serializer.validated_data.get('skin_type') or getattr(user, 'skin_type', 'unknown'),
            'concerns': serializer.validated_data.get('concerns') or getattr(user, 'concerns', []),
            'allergies': getattr(user, 'allergies', 'None'),
            'sensitivity': getattr(user, 'sensitivity', None),
        }
        
        result = analyze_ingredients(
            ingredients=serializer.validated_data['ingredients'],
            user_profile=user_profile
        )
        
        return Response(result, status=status.HTTP_200_OK)


class AITestView(APIView):
    """Test AI service connection - No authentication required for testing."""
    
    permission_classes = []  # Public endpoint for testing
    
    def get(self, request):
        """Test AI connection and return status"""
        from .ai_service import test_ai_connection
        
        result = test_ai_connection()
        
        if result['success']:
            return Response(result, status=status.HTTP_200_OK)
        else:
            return Response(result, status=status.HTTP_503_SERVICE_UNAVAILABLE)


class AITestQuestionView(APIView):
    """Test AI question answering - No authentication required for testing."""
    
    permission_classes = []  # Public endpoint for testing
    
    def post(self, request):
        """Test asking a question to AI"""
        from .ai_service import answer_skincare_question
        
        question = request.data.get('question', 'What is the best way to clean oily skin?')
        
        user_profile = {
            'skin_type': request.data.get('skin_type', 'oily'),
            'sensitivity': request.data.get('sensitivity', 'normal'),
            'concerns': request.data.get('concerns', [])
        }
        
        result = answer_skincare_question(question, user_profile)
        
        if result.get('error'):
            return Response({
                'success': False,
                'message': 'AI test failed',
                'error': result.get('message'),
                'details': result
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'success': True,
            'message': 'AI question test successful',
            'question': question,
            'answer': result.get('answer_text', ''),
            'processing_time': result.get('processing_time', 0),
            'model_used': result.get('ai_model_used', ''),
            'full_response': result
        }, status=status.HTTP_200_OK)
    
    def get(self, request):
        """Show test form for browser access"""
        return Response({
            'message': 'AI Question Test Endpoint',
            'usage': 'Send POST request with JSON data',
            'example': {
                'question': 'How to treat acne?',
                'skin_type': 'oily',
                'sensitivity': 'normal',
                'concerns': ['acne', 'large_pores']
            },
            'note': 'All fields are optional. Default question will be used if not provided.'
        })

