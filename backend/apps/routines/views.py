import logging
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import Routine, RoutineReminder, WeatherAdaptation
from .serializers import (
    RoutineSerializer,
    RoutineCreateSerializer,
    RoutineReminderSerializer,
    WeatherAdaptationSerializer,
)
from .services import get_weather, get_routine_adaptation

logger = logging.getLogger(__name__)


class RoutineListView(APIView):
    """List and create routines for the authenticated user."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        routines = Routine.objects.filter(user=request.user).prefetch_related('steps__product__category')
        serializer = RoutineSerializer(routines, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RoutineCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class RoutineDetailView(APIView):
    """Retrieve, update or delete a routine."""
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        return Routine.objects.filter(pk=pk, user=user).prefetch_related('steps__product__category').first()

    def get(self, request, pk):
        routine = self.get_object(pk, request.user)
        if not routine:
            return Response({'error': 'Routine not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = RoutineSerializer(routine)
        return Response(serializer.data)

    def put(self, request, pk):
        routine = self.get_object(pk, request.user)
        if not routine:
            return Response({'error': 'Routine not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = RoutineCreateSerializer(routine, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(RoutineSerializer(routine).data)

    def delete(self, request, pk):
        routine = self.get_object(pk, request.user)
        if not routine:
            return Response({'error': 'Routine not found'}, status=status.HTTP_404_NOT_FOUND)
        routine.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class WeatherRoutineView(APIView):
    """Get weather-adapted routine suggestions."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        city = request.query_params.get('city', 'Mumbai')
        lat = request.query_params.get('lat')
        lon = request.query_params.get('lon')

        weather = get_weather(city=city, lat=float(lat) if lat else None, lon=float(lon) if lon else None)
        adaptation = get_routine_adaptation(weather['condition'])

        # Check if user has saved weather adaptations
        saved_adaptation = WeatherAdaptation.objects.filter(
            user=request.user,
            weather_condition=weather['condition']
        ).first()

        # Get user's routine for the relevant time of day
        now_hour = __import__('datetime').datetime.now().hour
        time_of_day = 'morning' if now_hour < 17 else 'evening'
        routine = Routine.objects.filter(user=request.user, time_of_day=time_of_day).prefetch_related('steps__product__category').first()

        return Response({
            'weather': weather,
            'adaptation': adaptation,
            'saved_adaptation': WeatherAdaptationSerializer(saved_adaptation).data if saved_adaptation else None,
            'current_routine': RoutineSerializer(routine).data if routine else None,
            'time_of_day': time_of_day,
        })


class ReminderListView(APIView):
    """List and create reminders."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        reminders = RoutineReminder.objects.filter(user=request.user)
        serializer = RoutineReminderSerializer(reminders, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = RoutineReminderSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ReminderDetailView(APIView):
    """Update or delete a reminder."""
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        return RoutineReminder.objects.filter(pk=pk, user=user).first()

    def put(self, request, pk):
        reminder = self.get_object(pk, request.user)
        if not reminder:
            return Response({'error': 'Reminder not found'}, status=status.HTTP_404_NOT_FOUND)
        serializer = RoutineReminderSerializer(reminder, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        reminder = self.get_object(pk, request.user)
        if not reminder:
            return Response({'error': 'Reminder not found'}, status=status.HTTP_404_NOT_FOUND)
        reminder.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
