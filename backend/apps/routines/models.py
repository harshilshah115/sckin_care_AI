import uuid
from django.db import models
from django.conf import settings


class Routine(models.Model):
    TIME_CHOICES = [
        ('morning', 'Morning'),
        ('evening', 'Evening'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_routines')
    name = models.CharField(max_length=200, default='My Skincare Routine')
    time_of_day = models.CharField(max_length=10, choices=TIME_CHOICES)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'routines'
        ordering = ['time_of_day', 'created_at']
        unique_together = [['user', 'time_of_day']]

    def __str__(self):
        return f"{self.user.email}'s {self.get_time_of_day_display()} Routine"


class RoutineStep(models.Model):
    STEP_TYPES = [
        ('cleanser', 'Cleanser'),
        ('toner', 'Toner'),
        ('serum', 'Serum'),
        ('moisturizer', 'Moisturizer'),
        ('sunscreen', 'Sunscreen'),
        ('eye_cream', 'Eye Cream'),
        ('treatment', 'Treatment'),
        ('exfoliator', 'Exfoliator'),
        ('mask', 'Mask'),
        ('other', 'Other'),
    ]

    routine = models.ForeignKey(Routine, on_delete=models.CASCADE, related_name='steps')
    product = models.ForeignKey('products.Product', on_delete=models.SET_NULL, null=True, blank=True, related_name='routine_steps')
    step_type = models.CharField(max_length=20, choices=STEP_TYPES)
    product_name = models.CharField(max_length=200, blank=True, help_text='Manual product name if no product linked')
    order = models.PositiveIntegerField(default=0)
    instructions = models.TextField(blank=True)
    duration_seconds = models.PositiveIntegerField(null=True, blank=True, help_text='How long to apply (e.g., 60s)')
    is_weather_dependent = models.BooleanField(default=False, help_text='Adjust based on weather conditions')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'routine_steps'
        ordering = ['routine', 'order']

    def __str__(self):
        return f"{self.get_step_type_display()} - {self.product_name or (self.product.name if self.product else 'N/A')}"


class RoutineReminder(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reminders')
    routine = models.ForeignKey(Routine, on_delete=models.CASCADE, related_name='reminders', null=True, blank=True)
    reminder_time = models.TimeField()
    days_of_week = models.JSONField(default=list, help_text='[0,1,2,3,4,5,6] where 0=Monday')
    is_enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'routine_reminders'
        ordering = ['reminder_time']

    def __str__(self):
        return f"Reminder for {self.user.email} at {self.reminder_time}"


class WeatherAdaptation(models.Model):
    WEATHER_CONDITIONS = [
        ('hot_humid', 'Hot & Humid'),
        ('hot_dry', 'Hot & Dry'),
        ('cold_humid', 'Cold & Humid'),
        ('cold_dry', 'Cold & Dry'),
        ('polluted', 'High Pollution'),
        ('sunny', 'Sunny/High UV'),
        ('rainy', 'Rainy'),
        ('normal', 'Normal/Mild'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='weather_adaptations')
    weather_condition = models.CharField(max_length=20, choices=WEATHER_CONDITIONS)
    routine = models.ForeignKey(Routine, on_delete=models.CASCADE, related_name='weather_adaptations')
    adjustment_notes = models.TextField(blank=True)
    add_steps = models.JSONField(default=list, help_text='Step types to add in this weather')
    remove_steps = models.JSONField(default=list, help_text='Step types to skip in this weather')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'weather_adaptations'
        unique_together = [['user', 'weather_condition']]

    def __str__(self):
        return f"{self.user.email} - {self.get_weather_condition_display()}"
