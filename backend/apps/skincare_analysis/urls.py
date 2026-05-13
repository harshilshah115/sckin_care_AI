from django.urls import path

from .views import (
    SkinScanCreateView,
    SkinScanListView,
    SkinScanDetailView,
    QuestionCreateView,
    QuestionListView,
    QuestionDetailView,
    QuestionFeedbackView,
    AITestView,
    AITestQuestionView
)

urlpatterns = [
    # AI Test Endpoints (No Auth Required)
    path('test/', AITestView.as_view(), name='ai_test'),
    path('test/question/', AITestQuestionView.as_view(), name='ai_test_question'),
    
    # Skin Scans
    path('', SkinScanCreateView.as_view(), name='scan_create'),
    path('list/', SkinScanListView.as_view(), name='scan_list'),
    path('<int:pk>/', SkinScanDetailView.as_view(), name='scan_detail'),
    
    # Questions
    path('ask/', QuestionCreateView.as_view(), name='question_create'),
    path('questions/', QuestionListView.as_view(), name='question_list'),
    path('questions/<int:pk>/', QuestionDetailView.as_view(), name='question_detail'),
    path('questions/<int:pk>/feedback/', QuestionFeedbackView.as_view(), name='question_feedback'),
]
