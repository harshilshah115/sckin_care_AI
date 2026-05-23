from django.urls import path
from .views import (
    RoutineListView,
    RoutineDetailView,
    WeatherRoutineView,
    ReminderListView,
    ReminderDetailView,
)

urlpatterns = [
    # Routines
    path('', RoutineListView.as_view(), name='routine_list'),
    path('<int:pk>/', RoutineDetailView.as_view(), name='routine_detail'),
    
    # Weather
    path('weather/', WeatherRoutineView.as_view(), name='weather_routine'),
    
    # Reminders
    path('reminders/', ReminderListView.as_view(), name='reminder_list'),
    path('reminders/<int:pk>/', ReminderDetailView.as_view(), name='reminder_detail'),
]
