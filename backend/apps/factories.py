"""
Factory Boy factories for all models.
Used in pytest tests for consistent test data generation.
"""

import factory
from django.contrib.auth import get_user_model
from apps.products.models import ProductCategory, Product
from apps.skincare_analysis.models import SkinScan
from apps.routines.models import Routine, RoutineStep

User = get_user_model()


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = User

    email = factory.Sequence(lambda n: f'testuser{n}@example.com')
    name = factory.Sequence(lambda n: f'Test User {n}')
    password = factory.PostGenerationMethodCall('set_password', 'testpass123')
    skin_type = 'combination'
    concerns = ['acne', 'hyperpigmentation']


class ProductCategoryFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ProductCategory

    name = factory.Sequence(lambda n: f'Category {n}')
    slug = factory.Sequence(lambda n: f'category-{n}')


class ProductFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Product

    name = factory.Sequence(lambda n: f'Product {n}')
    brand = 'Test Brand'
    category = factory.SubFactory(ProductCategoryFactory)
    description = factory.Faker('text', max_nb_chars=200)
    price = 499.00
    currency = 'INR'
    ingredients = ['Water', 'Glycerin', 'Niacinamide']
    key_ingredients = ['Niacinamide']
    skin_types = ['all']
    concerns = ['acne']
    rating = 4.5
    image_url = 'https://example.com/product.jpg'


class SkinScanFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SkinScan

    user = factory.SubFactory(UserFactory)
    image = factory.django.ImageField(color='blue')
    analysis_result = {
        'success': True,
        'skin_issues': [{'name': 'Acne', 'severity': 'moderate'}],
        'overall_score': 72,
    }


class RoutineFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Routine

    user = factory.SubFactory(UserFactory)
    name = 'My Morning Routine'
    time_of_day = 'morning'


class RoutineStepFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = RoutineStep

    routine = factory.SubFactory(RoutineFactory)
    step_type = 'cleanser'
    product_name = 'Gentle Cleanser'
    order = 0
