"""
Pytest conftest - shared fixtures for all test files.
"""

import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from apps.factories import UserFactory

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def authenticated_client(api_client, db):
    user = UserFactory()
    api_client.force_authenticate(user=user)
    return api_client, user


@pytest.fixture
def test_user():
    return UserFactory()
