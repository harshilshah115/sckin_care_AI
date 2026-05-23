"""
Barcode Scanner Service
Looks up products by barcode - local DB first, then Open Beauty Facts API.
"""

import os
import logging
import json
import requests
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


def lookup_product_by_barcode(barcode: str) -> Dict[str, Any]:
    """
    Look up a product by barcode.
    Checks local database first, then queries Open Beauty Facts.
    """
    from .models import Product, ProductCategory
    
    # 1. Check local database
    try:
        product = Product.objects.filter(barcode=barcode, is_active=True).select_related('category').first()
        if product:
            from .serializers import ProductSerializer
            return {
                'found': True,
                'source': 'local',
                'product': ProductSerializer(product).data,
            }
    except Exception as e:
        logger.warning(f'Local barcode lookup failed: {e}')
    
    # 2. Look up via Open Beauty Facts API
    try:
        result = _lookup_openbeautyfacts(barcode)
        if result.get('found'):
            return result
    except Exception as e:
        logger.warning(f'Open Beauty Facts lookup failed: {e}')
    
    return {
        'found': False,
        'source': None,
        'product': None,
        'error': 'Product not found for this barcode',
    }


def _lookup_openbeautyfacts(barcode: str) -> Dict[str, Any]:
    """Query Open Beauty Facts API for product by barcode."""
    url = f'https://world.openbeautyfacts.org/api/v2/product/{barcode}.json'
    
    response = requests.get(url, timeout=15, headers={
        'User-Agent': 'SckinCare/1.0 (skincare-assistant)',
    })
    
    if response.status_code != 200:
        return {'found': False, 'source': 'openbeautyfacts', 'product': None}
    
    data = response.json()
    
    if data.get('status') != 1 or not data.get('product'):
        return {'found': False, 'source': 'openbeautyfacts', 'product': None}
    
    product_data = data['product']
    
    # Parse Open Beauty Facts data into our format
    ingredients_list = []
    ingredients_text = product_data.get('ingredients_text', '')
    if ingredients_text:
        ingredients_list = [i.strip() for i in ingredients_text.split(',') if i.strip()]
    
    # If no ingredients_text, try structured ingredients
    if not ingredients_list:
        ingredients_raw = product_data.get('ingredients', [])
        ingredients_list = [i.get('text', '') for i in ingredients_raw if i.get('text')]
    
    product = {
        'name': product_data.get('product_name', 'Unknown Product'),
        'brand': product_data.get('brands', 'Unknown Brand'),
        'description': product_data.get('product_name', ''),
        'ingredients': ingredients_list,
        'image_url': product_data.get('image_url', product_data.get('image_front_url', '')),
        'barcode': barcode,
        'categories': product_data.get('categories', '').split(',') if product_data.get('categories') else [],
        'source': 'openbeautyfacts',
    }
    
    return {
        'found': True,
        'source': 'openbeautyfacts',
        'product': product,
    }
