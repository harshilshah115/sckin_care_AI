from rest_framework import serializers
from .models import ProductCategory, Product, NaturalRemedy


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = ['id', 'name', 'slug', 'description', 'icon']


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'brand', 'category', 'category_name', 'description',
            'price', 'currency', 'ingredients', 'key_ingredients',
            'skin_types', 'concerns', 'rating', 'review_count',
            'image_url', 'affiliate_link', 'is_featured'
        ]


class ProductListSerializer(serializers.ModelSerializer):
    """Minimal serializer for product lists."""
    category_name = serializers.CharField(source='category.name', read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'brand', 'category_name', 'price', 'currency',
            'key_ingredients', 'skin_types', 'rating', 'review_count', 'image_url'
        ]


class NaturalRemedySerializer(serializers.ModelSerializer):
    class Meta:
        model = NaturalRemedy
        fields = [
            'id', 'title', 'description', 'ingredients', 'instructions',
            'concerns', 'skin_types', 'frequency', 'duration', 'cautions'
        ]
