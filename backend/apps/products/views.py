from rest_framework import generics, filters
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.db.models import Q

from .models import ProductCategory, Product, NaturalRemedy
from .serializers import (
    ProductCategorySerializer,
    ProductSerializer,
    ProductListSerializer,
    NaturalRemedySerializer
)


class ProductCategoryListView(generics.ListAPIView):
    """List all product categories."""
    
    permission_classes = [AllowAny]
    queryset = ProductCategory.objects.all()
    serializer_class = ProductCategorySerializer


class ProductListView(generics.ListAPIView):
    """List products with filtering."""
    
    permission_classes = [AllowAny]
    serializer_class = ProductListSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'brand', 'description']
    ordering_fields = ['price', 'rating', 'created_at']
    
    def get_queryset(self):
        queryset = Product.objects.filter(is_active=True)
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category__slug=category)
        
        # Filter by skin type
        skin_type = self.request.query_params.get('skin_type')
        if skin_type:
            queryset = queryset.filter(skin_types__contains=[skin_type])
        
        # Filter by concern
        concern = self.request.query_params.get('concern')
        if concern:
            queryset = queryset.filter(concerns__contains=[concern])
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
        
        return queryset


class ProductDetailView(generics.RetrieveAPIView):
    """Get product details."""
    
    permission_classes = [AllowAny]
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer


class FeaturedProductsView(generics.ListAPIView):
    """List featured products."""
    
    permission_classes = [AllowAny]
    serializer_class = ProductListSerializer
    
    def get_queryset(self):
        return Product.objects.filter(is_active=True, is_featured=True)[:10]


class PersonalizedProductsView(APIView):
    """Get personalized product recommendations based on user profile."""
    
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        
        # Build query based on user's skin profile
        queryset = Product.objects.filter(is_active=True)
        
        if user.skin_type:
            queryset = queryset.filter(
                Q(skin_types__contains=[user.skin_type]) | 
                Q(skin_types__contains=['all'])
            )
        
        if user.concerns:
            # Match any of user's concerns
            for concern in user.concerns:
                queryset = queryset.filter(concerns__contains=[concern])
        
        # Calculate match score (simplified)
        products = ProductListSerializer(queryset[:20], many=True).data
        
        # Add match score to each product
        for product in products:
            match_score = 70  # Base score
            if user.skin_type and user.skin_type in product.get('skin_types', []):
                match_score += 15
            if user.concerns:
                matched_concerns = set(user.concerns) & set(product.get('concerns', []))
                match_score += len(matched_concerns) * 5
            product['match_score'] = min(match_score, 100)
        
        # Sort by match score
        products.sort(key=lambda x: x['match_score'], reverse=True)
        
        return Response(products)


class NaturalRemedyListView(generics.ListAPIView):
    """List natural remedies."""
    
    permission_classes = [AllowAny]
    serializer_class = NaturalRemedySerializer
    
    def get_queryset(self):
        queryset = NaturalRemedy.objects.filter(is_active=True)
        
        # Filter by concern
        concern = self.request.query_params.get('concern')
        if concern:
            queryset = queryset.filter(concerns__contains=[concern])
        
        # Filter by skin type
        skin_type = self.request.query_params.get('skin_type')
        if skin_type:
            queryset = queryset.filter(skin_types__contains=[skin_type])
        
        return queryset


class NaturalRemedyDetailView(generics.RetrieveAPIView):
    """Get natural remedy details."""
    
    permission_classes = [AllowAny]
    queryset = NaturalRemedy.objects.filter(is_active=True)
    serializer_class = NaturalRemedySerializer
