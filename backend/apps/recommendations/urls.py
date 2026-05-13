from django.urls import path

from .views import (
    SavedProductListView,
    SavedProductDeleteView,
    SavedRemedyListView,
    SavedRemedyDeleteView,
    RoutineListCreateView,
    RoutineDetailView,
    RoutineGenerateView,
    RoutineLogListCreateView,
    TodayRoutineStatusView
)

urlpatterns = [
    # Saved Products
    path('saved/products/', SavedProductListView.as_view(), name='saved_products'),
    path('saved/products/<int:product_id>/', SavedProductDeleteView.as_view(), name='remove_saved_product'),
    
    # Saved Remedies
    path('saved/remedies/', SavedRemedyListView.as_view(), name='saved_remedies'),
    path('saved/remedies/<int:remedy_id>/', SavedRemedyDeleteView.as_view(), name='remove_saved_remedy'),
    
    # Routines
    path('routines/', RoutineListCreateView.as_view(), name='routine_list'),
    path('routines/generate/', RoutineGenerateView.as_view(), name='routine_generate'),
    path('routines/<int:pk>/', RoutineDetailView.as_view(), name='routine_detail'),
    path('routines/today/', TodayRoutineStatusView.as_view(), name='today_routine_status'),
    
    # Routine Logs
    path('routines/logs/', RoutineLogListCreateView.as_view(), name='routine_logs'),
]
