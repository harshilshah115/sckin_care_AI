"""
Tests for the Products app endpoints.
"""

import pytest
from django.urls import reverse
from apps.factories import ProductFactory, ProductCategoryFactory


class TestProductList:
    """Tests for the product list endpoint."""
    
    @pytest.mark.django_db
    def test_list_products_success(self, api_client):
        ProductFactory.create_batch(3)
        url = reverse('product_list')
        response = api_client.get(url)
        assert response.status_code == 200
        assert len(response.data['results']) == 3
    
    @pytest.mark.django_db
    def test_list_products_empty(self, api_client):
        url = reverse('product_list')
        response = api_client.get(url)
        assert response.status_code == 200
        assert len(response.data['results']) == 0
    
    @pytest.mark.django_db
    def test_list_products_filter_by_category(self, api_client):
        cat_a = ProductCategoryFactory(slug='cleansers')
        cat_b = ProductCategoryFactory(slug='moisturizers')
        ProductFactory.create_batch(2, category=cat_a)
        ProductFactory.create_batch(1, category=cat_b)
        
        url = reverse('product_list')
        response = api_client.get(url, {'category': 'cleansers'})
        assert response.status_code == 200
        assert len(response.data['results']) == 2
    
    @pytest.mark.django_db
    def test_list_products_pagination(self, api_client):
        ProductFactory.create_batch(25)
        url = reverse('product_list')
        response = api_client.get(url)
        assert response.status_code == 200
        assert 'count' in response.data
        assert response.data['count'] == 25
        assert len(response.data['results']) == 10


class TestProductDetail:
    """Tests for the product detail endpoint."""
    
    @pytest.mark.django_db
    def test_get_product_detail(self, api_client):
        product = ProductFactory()
        url = reverse('product_detail', args=[product.pk])
        response = api_client.get(url)
        assert response.status_code == 200
        assert response.data['name'] == product.name
        assert response.data['brand'] == product.brand
    
    @pytest.mark.django_db
    def test_get_product_detail_not_found(self, api_client):
        url = reverse('product_detail', args=[99999])
        response = api_client.get(url)
        assert response.status_code == 404


class TestFeaturedProducts:
    """Tests for the featured products endpoint."""
    
    @pytest.mark.django_db
    def test_featured_products_ordered_by_rating(self, api_client):
        ProductFactory(is_featured=True, rating=4.0)
        ProductFactory(is_featured=True, rating=5.0)
        ProductFactory(is_featured=True, rating=3.0)
        
        url = reverse('featured_products')
        response = api_client.get(url)
        assert response.status_code == 200
        ratings = [p['rating'] for p in response.data['results']]
        assert ratings == sorted(ratings, reverse=True)
    
    @pytest.mark.django_db
    def test_featured_products_returns_only_featured(self, api_client):
        ProductFactory(is_featured=True)
        ProductFactory(is_featured=False)
        
        url = reverse('featured_products')
        response = api_client.get(url)
        assert response.status_code == 200
        assert len(response.data['results']) == 1


class TestBarcodeLookup:
    """Tests for the barcode lookup endpoint."""
    
    def test_barcode_requires_auth(self, api_client):
        url = reverse('product_barcode')
        response = api_client.get(url, {'barcode': '8901234567890'})
        assert response.status_code == 401
    
    @pytest.mark.django_db
    def test_barcode_invalid_input(self, authenticated_client):
        client, _ = authenticated_client
        url = reverse('product_barcode')
        response = client.get(url, {'barcode': 'abc'})
        assert response.status_code == 400
    
    @pytest.mark.django_db
    def test_barcode_not_found(self, authenticated_client):
        client, _ = authenticated_client
        url = reverse('product_barcode')
        response = client.get(url, {'barcode': '0000000000000'})
        assert response.status_code == 200
        assert response.data['found'] is False
