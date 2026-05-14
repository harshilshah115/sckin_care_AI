from django.db import models
from django.conf import settings


class SkinScan(models.Model):
    """Model for storing skin scan/analysis results."""
    
    SCAN_TYPE_CHOICES = [
        ('full_face', 'Full Face Scan'),
        ('spot', 'Spot Analysis'),
        ('forehead', 'Forehead'),
        ('cheeks', 'Cheeks'),
        ('chin', 'Chin'),
        ('nose', 'Nose'),
    ]
    
    SEVERITY_CHOICES = [
        ('none', 'None'),
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='skin_scans'
    )
    
    # Scan details
    image = models.ImageField(upload_to='skin_scans/')
    scan_type = models.CharField(max_length=20, choices=SCAN_TYPE_CHOICES, default='full_face')
    
    # Analysis results
    detected_issues = models.JSONField(default=list)  # List of detected skin issues
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default='none')
    confidence_score = models.FloatField(default=0.0)  # AI confidence 0-100
    skin_score = models.IntegerField(default=0)  # Overall skin health score 0-100
    metrics = models.JSONField(default=dict)  # Per-metric scores like oiliness, hydration, pores
    
    # Detailed analysis
    analysis_text = models.TextField(blank=True)  # Full AI analysis
    recommendations = models.JSONField(default=dict)  # AI recommendations
    
    # Metadata
    ai_model_used = models.CharField(max_length=50, blank=True)  # Which AI was used
    processing_time = models.FloatField(default=0.0)  # Time taken in seconds
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'skin_scans'
        ordering = ['-created_at']
        verbose_name = 'Skin Scan'
        verbose_name_plural = 'Skin Scans'
    
    def __str__(self):
        return f"Scan {self.id} - {self.user.email} - {self.created_at.strftime('%Y-%m-%d')}"


class Question(models.Model):
    """Model for storing user questions and AI answers."""
    
    CATEGORY_CHOICES = [
        ('routine', 'Skincare Routine'),
        ('product', 'Product Recommendation'),
        ('concern', 'Skin Concern'),
        ('ingredient', 'Ingredients'),
        ('general', 'General'),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='questions'
    )
    
    # Question details
    question_text = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    
    # Answer details
    answer_text = models.TextField(blank=True)
    recommendations = models.JSONField(default=dict)  # Products, remedies etc.
    
    # Metadata
    ai_model_used = models.CharField(max_length=50, blank=True)
    processing_time = models.FloatField(default=0.0)
    
    # User feedback
    is_helpful = models.BooleanField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'questions'
        ordering = ['-created_at']
        verbose_name = 'Question'
        verbose_name_plural = 'Questions'
    
    def __str__(self):
        return f"Q: {self.question_text[:50]}..."
