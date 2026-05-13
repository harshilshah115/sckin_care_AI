from django.db import models
from django.conf import settings


class ProgressPhoto(models.Model):
    """Photos for tracking skin progress over time."""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='progress_photos'
    )
    
    image = models.ImageField(upload_to='progress_photos/')
    skin_score = models.IntegerField(default=0)
    notes = models.TextField(blank=True)
    
    # Link to scan if created from a scan
    scan = models.ForeignKey(
        'skincare_analysis.SkinScan',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='progress_photo'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'progress_photos'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.created_at.date()}"


class Milestone(models.Model):
    """User milestones and achievements."""
    
    MILESTONE_TYPES = [
        ('scan_count', 'Scan Count'),
        ('streak', 'Routine Streak'),
        ('score', 'Skin Score'),
        ('improvement', 'Improvement'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='milestones'
    )
    
    milestone_type = models.CharField(max_length=20, choices=MILESTONE_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    value = models.IntegerField(default=0)  # e.g., scan count, score reached
    
    achieved_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'milestones'
        ordering = ['-achieved_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.title}"
