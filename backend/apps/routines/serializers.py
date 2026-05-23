from rest_framework import serializers
from .models import Routine, RoutineStep, RoutineReminder, WeatherAdaptation


class RoutineStepSerializer(serializers.ModelSerializer):
    product_name_display = serializers.SerializerMethodField()

    class Meta:
        model = RoutineStep
        fields = ['id', 'routine', 'product', 'step_type', 'product_name', 'product_name_display',
                  'order', 'instructions', 'duration_seconds', 'is_weather_dependent', 'created_at']
        read_only_fields = ['id', 'created_at']

    def get_product_name_display(self, obj):
        return obj.product.name if obj.product else obj.product_name


class RoutineSerializer(serializers.ModelSerializer):
    steps = RoutineStepSerializer(many=True, read_only=True)
    time_of_day_display = serializers.SerializerMethodField()

    class Meta:
        model = Routine
        fields = ['id', 'user', 'name', 'time_of_day', 'time_of_day_display',
                  'is_active', 'steps', 'created_at', 'updated_at']
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']

    def get_time_of_day_display(self, obj):
        return obj.get_time_of_day_display()


class RoutineCreateSerializer(serializers.ModelSerializer):
    steps = RoutineStepSerializer(many=True, required=False)

    class Meta:
        model = Routine
        fields = ['name', 'time_of_day', 'steps']

    def create(self, validated_data):
        steps_data = validated_data.pop('steps', [])
        routine = Routine.objects.create(**validated_data)
        for order, step_data in enumerate(steps_data):
            RoutineStep.objects.create(routine=routine, order=order, **step_data)
        return routine


class RoutineStepCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoutineStep
        fields = ['product', 'step_type', 'product_name', 'order', 'instructions', 'duration_seconds', 'is_weather_dependent']


class RoutineReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoutineReminder
        fields = ['id', 'user', 'routine', 'reminder_time', 'days_of_week', 'is_enabled', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']


class WeatherAdaptationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WeatherAdaptation
        fields = ['id', 'user', 'weather_condition', 'routine', 'adjustment_notes', 'add_steps', 'remove_steps', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
