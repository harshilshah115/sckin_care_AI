from django.urls import path

from .views import (
    ProductCategoryListView,
    ProductListView,
    ProductDetailView,
    FeaturedProductsView,
    PersonalizedProductsView,
    NaturalRemedyListView,
    NaturalRemedyDetailView
)

urlpatterns = [
    # Categories
    path('categories/', ProductCategoryListView.as_view(), name='category_list'),
    
    # Products
    path('', ProductListView.as_view(), name='product_list'),
    path('featured/', FeaturedProductsView.as_view(), name='featured_products'),
    path('personalized/', PersonalizedProductsView.as_view(), name='personalized_products'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product_detail'),
    
    # Natural Remedies
    path('remedies/', NaturalRemedyListView.as_view(), name='remedy_list'),
    path('remedies/<int:pk>/', NaturalRemedyDetailView.as_view(), name='remedy_detail'),
]
