import pytest
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from user_auth_app.models import User

@pytest.mark.django_db
def test_token_refresh_success(client):
    """Test successful token refresh."""
    user = User.objects.create_user(
        email='testuser@test.com',
        password='TestPassword123!',
        username='testuser@test.com',
        is_active=True
    )
    
    refresh = RefreshToken.for_user(user)
    client.cookies['refresh_token'] = str(refresh)
    
    url = reverse('token_refresh')
    response = client.post(url)
    
    assert response.status_code == 200
    assert response.data['detail'] == 'Token refreshed'
    assert 'access' in response.data
    
    assert 'access_token' in response.cookies

@pytest.mark.django_db
def test_token_refresh_no_token(client):
    """Test token refresh without refresh token."""
    url = reverse('token_refresh')
    response = client.post(url)
    
    assert response.status_code == 400
    assert response.data['detail'] == 'Refresh token not found'

@pytest.mark.django_db
def test_token_refresh_invalid_token(client):
    """Test token refresh with invalid token."""
    client.cookies['refresh_token'] = 'invalid_token'
    
    url = reverse('token_refresh')
    response = client.post(url)
    
    assert response.status_code == 401
    assert response.data['detail'] == 'Invalid refresh token'

@pytest.mark.django_db
def test_token_refresh_blacklisted_token(client):
    """Test token refresh with blacklisted token."""
    user = User.objects.create_user(
        email='testuser@test.com',
        password='TestPassword123!',
        username='testuser@test.com',
        is_active=True
    )
    
    refresh = RefreshToken.for_user(user)
    refresh.blacklist()
    
    client.cookies['refresh_token'] = str(refresh)
    
    url = reverse('token_refresh')
    response = client.post(url)
    
    assert response.status_code == 401
    assert response.data['detail'] == 'Invalid refresh token'
