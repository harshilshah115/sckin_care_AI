from django.contrib import admin
from .models import ProductCategory, Product, NaturalRemedy


@admin.register(ProductCategory)
class ProductCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'category', 'price', 'rating', 'is_active', 'is_featured']
    list_filter = ['category', 'is_active', 'is_featured']
    search_fields = ['name', 'brand', 'description']
    list_editable = ['is_active', 'is_featured']


@admin.register(NaturalRemedy)
class NaturalRemedyAdmin(admin.ModelAdmin):
    list_display = ['title', 'frequency', 'is_active']
    list_filter = ['is_active']
    search_fields = ['title', 'description']
