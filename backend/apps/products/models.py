from django.db import models


class ProductCategory(models.Model):
    """Product categories (Cleanser, Moisturizer, etc.)"""
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    icon = models.CharField(max_length=50, blank=True)  # Material icon name
    
    class Meta:
        db_table = 'product_categories'
        verbose_name_plural = 'Product Categories'
    
    def __str__(self):
        return self.name


class Product(models.Model):
    """Skincare product model."""
    
    SKIN_TYPE_CHOICES = [
        ('all', 'All Skin Types'),
        ('dry', 'Dry'),
        ('oily', 'Oily'),
        ('combination', 'Combination'),
        ('sensitive', 'Sensitive'),
        ('acne_prone', 'Acne-Prone'),
    ]
    
    # Basic info
    name = models.CharField(max_length=200)
    brand = models.CharField(max_length=100)
    category = models.ForeignKey(ProductCategory, on_delete=models.CASCADE, related_name='products')
    description = models.TextField()
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='INR')
    
    # Details
    ingredients = models.JSONField(default=list)  # List of ingredients
    key_ingredients = models.JSONField(default=list)  # Highlighted ingredients
    skin_types = models.JSONField(default=list)  # Suitable skin types
    concerns = models.JSONField(default=list)  # Addressed concerns
    
    # Rating
    rating = models.FloatField(default=0.0)
    review_count = models.IntegerField(default=0)
    
    # Media
    image_url = models.URLField(blank=True)
    
    # Links
    affiliate_link = models.URLField(blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'products'
        ordering = ['-is_featured', '-rating']
    
    def __str__(self):
        return f"{self.brand} - {self.name}"


class NaturalRemedy(models.Model):
    """Natural/home remedy model."""
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    ingredients = models.JSONField(default=list)  # List of ingredients with quantities
    instructions = models.TextField()
    
    # Targeting
    concerns = models.JSONField(default=list)  # Skin concerns it addresses
    skin_types = models.JSONField(default=list)  # Suitable skin types
    
    # Usage
    frequency = models.CharField(max_length=100)  # e.g., "2-3 times per week"
    duration = models.CharField(max_length=100)  # e.g., "15-20 minutes"
    
    # Cautions
    cautions = models.TextField(blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'natural_remedies'
        verbose_name_plural = 'Natural Remedies'
    
    def __str__(self):
        return self.title
