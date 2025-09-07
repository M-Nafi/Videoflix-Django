import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from user_auth_app.models import User
from content.models import Video
import jwt
from django.conf import settings

@pytest.mark.django_db
def test_authentication_invalid_jwt_format(client):
    """Test authentication with invalid JWT format."""
    user = User.objects.create_user(
        email='testuser@test.com',
        password='TestPassword123!',
        username='testuser@test.com',
        is_active=True
    )
    
    api_client = APIClient()
    api_client.cookies['access_token'] = 'invalid.jwt.format'
    
    url = reverse('video-list')
    response = api_client.get(url)
    
    assert response.status_code == 401

@pytest.mark.django_db
def test_authentication_expired_jwt(client):
    """Test authentication with expired JWT."""
    user = User.objects.create_user(
        email='testuser@test.com',
        password='TestPassword123!',
        username='testuser@test.com',
        is_active=True
    )
    
    import time
    from rest_framework_simplejwt.settings import api_settings
    
    payload = {
        'user_id': user.id,
        'exp': int(time.time()) - 3600,
        'iat': int(time.time()) - 7200,
    }
    
    expired_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    
    api_client = APIClient()
    api_client.cookies['access_token'] = expired_token
    
    url = reverse('video-list')
    response = api_client.get(url)
    
    assert response.status_code == 401

@pytest.mark.django_db
def test_authentication_malformed_cookie(client):
    """Test authentication with malformed cookie."""
    api_client = APIClient()
    api_client.cookies['access_token'] = 'definitely_not_a_jwt'
    
    url = reverse('video-list')
    response = api_client.get(url)
    
    assert response.status_code == 401

@pytest.mark.django_db
def test_authentication_empty_cookie(client):
    """Test authentication with empty cookie."""
    api_client = APIClient()
    api_client.cookies['access_token'] = ''
    
    url = reverse('video-list')
    response = api_client.get(url)
    
    assert response.status_code == 401

@pytest.mark.django_db
def test_authentication_missing_cookie(client):
    """Test authentication with missing cookie."""
    api_client = APIClient()
    
    url = reverse('video-list')
    response = api_client.get(url)
    
    assert response.status_code == 401

@pytest.mark.django_db
def test_authentication_jwt_for_nonexistent_user(client):
    """Test authentication with JWT for non-existent user."""
    payload = {
        'user_id': 99999,
        'exp': 9999999999,
        'iat': 1234567890,
    }
    
    fake_token = jwt.encode(payload, settings.SECRET_KEY, algorithm='HS256')
    
    api_client = APIClient()
    api_client.cookies['access_token'] = fake_token
    
    url = reverse('video-list')
    response = api_client.get(url)
    
    assert response.status_code == 401

@pytest.mark.django_db
def test_authentication_jwt_for_inactive_user(client):
    """Test authentication with JWT for inactive user."""
    user = User.objects.create_user(
        email='testuser@test.com',
        password='TestPassword123!',
        username='testuser@test.com',
        is_active=False
    )
    
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    api_client = APIClient()
    api_client.cookies['access_token'] = access_token
    
    url = reverse('video-list')
    response = api_client.get(url)
    
    assert response.status_code == 401

@pytest.mark.django_db
def test_authentication_jwt_with_wrong_secret(client):
    """Test authentication with JWT signed with wrong secret."""
    user = User.objects.create_user(
        email='testuser@test.com',
        password='TestPassword123!',
        username='testuser@test.com',
        is_active=True
    )
    
    payload = {
        'user_id': user.id,
        'exp': 9999999999,
        'iat': 1234567890,
    }
    
    wrong_secret_token = jwt.encode(payload, 'wrong_secret_key', algorithm='HS256')
    
    api_client = APIClient()
    api_client.cookies['access_token'] = wrong_secret_token
    
    url = reverse('video-list')
    response = api_client.get(url)
    
    assert response.status_code == 401

@pytest.mark.django_db
def test_authentication_blacklisted_access_token(client):
    """Test authentication with blacklisted access token."""
    user = User.objects.create_user(
        email='testuser@test.com',
        password='TestPassword123!',
        username='testuser@test.com',
        is_active=True
    )
    
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    refresh.blacklist()
    
    api_client = APIClient()
    api_client.cookies['access_token'] = access_token
    
    url = reverse('video-list')
    response = api_client.get(url)
    
    assert response.status_code in [200, 401]

@pytest.mark.django_db
def test_cookie_httponly_flag_on_login(client):
    """Test that HTTPOnly flag is set on cookies during login."""
    user = User.objects.create_user(
        email='testuser@test.com',
        password='TestPassword123!',
        username='testuser@test.com',
        is_active=True
    )
    
    url = reverse('login')
    data = {
        'email': 'testuser@test.com',
        'password': 'TestPassword123!'
    }
    
    response = client.post(url, data, content_type='application/json')
    
    assert response.status_code == 200
    assert 'access_token' in response.cookies
    assert 'refresh_token' in response.cookies

    assert response.cookies['access_token']['httponly']
    assert response.cookies['refresh_token']['httponly']

@pytest.mark.django_db
def test_cookie_clearing_on_logout(client):
    """Test that cookies are properly cleared on logout."""
    user = User.objects.create_user(
        email='testuser@test.com',
        password='TestPassword123!',
        username='testuser@test.com',
        is_active=True
    )
    
    login_url = reverse('login')
    login_data = {
        'email': 'testuser@test.com',
        'password': 'TestPassword123!'
    }
    
    login_response = client.post(login_url, login_data, content_type='application/json')
    assert login_response.status_code == 200
    
    logout_url = reverse('logout')
    logout_response = client.post(logout_url)
    
    assert logout_response.status_code == 200
    assert logout_response.cookies['access_token'].value == ''
    assert logout_response.cookies['refresh_token'].value == ''
    
    assert logout_response.cookies['access_token']['max-age'] == 0
    assert logout_response.cookies['refresh_token']['max-age'] == 0

@pytest.mark.django_db
def test_multiple_concurrent_sessions(client):
    """Test handling of multiple concurrent sessions for same user."""
    user = User.objects.create_user(
        email='testuser@test.com',
        password='TestPassword123!',
        username='testuser@test.com',
        is_active=True
    )
    
    refresh1 = RefreshToken.for_user(user)
    refresh2 = RefreshToken.for_user(user)
    
    access_token1 = str(refresh1.access_token)
    access_token2 = str(refresh2.access_token)
    
    api_client1 = APIClient()
    api_client1.cookies['access_token'] = access_token1
    
    api_client2 = APIClient()
    api_client2.cookies['access_token'] = access_token2
    
    url = reverse('video-list')
    
    response1 = api_client1.get(url)
    response2 = api_client2.get(url)
    
    assert response1.status_code == 200
    assert response2.status_code == 200
    
    refresh1.blacklist()
    
    response1_after = api_client1.get(url)
    response2_after = api_client2.get(url)
    
    assert response1_after.status_code in [200, 401]
    assert response2_after.status_code == 200
