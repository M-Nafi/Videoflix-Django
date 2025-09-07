import pytest
from django.urls import reverse
from rest_framework_simplejwt.tokens import RefreshToken
from user_auth_app.models import User

@pytest.mark.django_db
def test_logout_user_success(client):
    """Test successful user logout."""
    user = User.objects.create_user(
        email='testuser@test.com',
        password='TestPassword123!',
        username='testuser@test.com',
        is_active=True
    )
    
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    client.cookies['access_token'] = access_token
    client.cookies['refresh_token'] = str(refresh)
    
    url = reverse('logout')
    response = client.post(url)
    
    assert response.status_code == 200
    assert response.data['detail'] == 'Log-Out successfully!'
    
    assert 'access_token' in response.cookies
    assert response.cookies['access_token'].value == ''
    assert 'refresh_token' in response.cookies
    assert response.cookies['refresh_token'].value == ''

@pytest.mark.django_db
def test_logout_no_refresh_token(client):
    """Test logout without refresh token."""
    url = reverse('logout')
    response = client.post(url)
    
    assert response.status_code == 400
    assert response.data['detail'] == 'Refresh token not found'

@pytest.mark.django_db
def test_logout_invalid_refresh_token(client):
    """Test logout with invalid refresh token."""
    client.cookies['refresh_token'] = 'invalid_token'
    
    url = reverse('logout')
    response = client.post(url)
    
    assert response.status_code == 200
    assert response.data['detail'] == 'Log-Out successfully!'
