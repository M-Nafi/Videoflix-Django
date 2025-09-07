import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

User = get_user_model()

@pytest.fixture
def api_client():
    """Provide APIClient instance."""
    return APIClient()

@pytest.fixture
def user():
    """Create a regular user."""
    return User.objects.create_user(
        email='testuser@test.com',
        password='TestPassword123!',
        username='testuser@test.com',
        is_active=True
    )

@pytest.fixture
def admin_user():
    """Create an admin user."""
    return User.objects.create_superuser(
        email='admin@test.com',
        password='AdminPassword123!',
        username='admin@test.com'
    )

@pytest.fixture
def inactive_user():
    """Create an inactive user."""
    return User.objects.create_user(
        email='inactive@test.com',
        password='TestPassword123!',
        username='inactive@test.com',
        is_active=False
    )

@pytest.fixture
def authenticated_client(api_client, user):
    """Provide authenticated APIClient."""
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    api_client.cookies['access_token'] = access_token
    return api_client

@pytest.fixture
def admin_authenticated_client(api_client, admin_user):
    """Provide admin authenticated APIClient."""
    api_client.force_authenticate(user=admin_user)
    return api_client
