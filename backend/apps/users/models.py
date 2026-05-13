from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models


class UserManager(BaseUserManager):
    """Custom user manager for email-based authentication."""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """Custom User model with skin profile fields."""
    
    SKIN_TYPE_CHOICES = [
        ('dry', 'Dry'),
        ('oily', 'Oily'),
        ('combination', 'Combination'),
        ('normal', 'Normal'),
        ('sensitive', 'Sensitive'),
    ]
    
    SENSITIVITY_CHOICES = [
        ('low', 'Low'),
        ('normal', 'Normal'),
        ('high', 'High'),
    ]
    
    AGE_GROUP_CHOICES = [
        ('under-18', 'Under 18'),
        ('18-24', '18-24'),
        ('25-34', '25-34'),
        ('35-44', '35-44'),
        ('45-54', '45-54'),
        ('55+', '55+'),
    ]
    
    # Basic fields
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=150)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    
    # Skin profile fields
    skin_type = models.CharField(max_length=20, choices=SKIN_TYPE_CHOICES, blank=True)
    sensitivity = models.CharField(max_length=20, choices=SENSITIVITY_CHOICES, default='normal')
    concerns = models.JSONField(default=list, blank=True)  # List of skin concerns
    allergies = models.TextField(blank=True)  # Known allergies
    age_group = models.CharField(max_length=20, choices=AGE_GROUP_CHOICES, blank=True)
    climate = models.CharField(max_length=50, blank=True)  # User's climate/region
    
    # Preferences
    notifications_enabled = models.BooleanField(default=True)
    email_updates = models.BooleanField(default=False)
    
    # Status fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.email
    
    def get_full_name(self):
        return self.name
    
    def get_short_name(self):
        return self.name.split()[0] if self.name else self.email
