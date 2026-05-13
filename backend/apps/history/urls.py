from django.urls import path

from .views import (
    ScanHistoryView,
    QuestionHistoryView,
    ProgressPhotoListView,
    MilestoneListView,
    ProgressSummaryView,
    ActivityTimelineView
)

urlpatterns = [
    # History
    path('scans/', ScanHistoryView.as_view(), name='scan_history'),
    path('questions/', QuestionHistoryView.as_view(), name='question_history'),
    
    # Progress
    path('progress/', ProgressSummaryView.as_view(), name='progress_summary'),
    path('progress/photos/', ProgressPhotoListView.as_view(), name='progress_photos'),
    
    # Milestones
    path('milestones/', MilestoneListView.as_view(), name='milestones'),
    
    # Timeline
    path('timeline/', ActivityTimelineView.as_view(), name='activity_timeline'),
]
