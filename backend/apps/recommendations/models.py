from django.db import models
from django.conf import settings


class SavedProduct(models.Model):
    """User's saved/bookmarked products."""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_products'
    )
    product = models.ForeignKey(
        'products.Product',
        on_delete=models.CASCADE,
        related_name='saved_by'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'saved_products'
        unique_together = ['user', 'product']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.product.name}"


class SavedRemedy(models.Model):
    """User's saved natural remedies."""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='saved_remedies'
    )
    remedy = models.ForeignKey(
        'products.NaturalRemedy',
        on_delete=models.CASCADE,
        related_name='saved_by'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'saved_remedies'
        unique_together = ['user', 'remedy']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.remedy.title}"


class SkincareRoutine(models.Model):
    """User's saved skincare routines."""
    
    ROUTINE_TYPE_CHOICES = [
        ('morning', 'Morning'),
        ('night', 'Night'),
        ('weekly', 'Weekly'),
        ('custom', 'Custom'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='routines'
    )
    
    name = models.CharField(max_length=100)
    routine_type = models.CharField(max_length=20, choices=ROUTINE_TYPE_CHOICES)
    description = models.TextField(blank=True)
    
    # Steps stored as JSON
    steps = models.JSONField(default=list)
    # Example: [{"order": 1, "name": "Cleanser", "product_id": 1, "duration": "1 min", "notes": "..."}]
    
    # Frequency for weekly/custom
    frequency = models.CharField(max_length=100, blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'skincare_routines'
        ordering = ['routine_type', '-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.name}"


class RoutineLog(models.Model):
    """Log of completed routines for tracking."""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='routine_logs'
    )
    routine = models.ForeignKey(
        SkincareRoutine,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='logs'
    )
    
    routine_type = models.CharField(max_length=20)  # morning/night
    completed_steps = models.JSONField(default=list)
    notes = models.TextField(blank=True)
    
    completed_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'routine_logs'
        ordering = ['-completed_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.routine_type} - {self.completed_at.date()}"
