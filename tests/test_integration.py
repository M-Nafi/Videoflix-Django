import pytest
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from user_auth_app.models import User
from content.models import Video

@pytest.mark.integration
@pytest.mark.django_db
def test_full_user_registration_flow(client):
    """Test complete user registration and activation flow."""
    register_url = reverse('register')
    register_data = {
        'email': 'testuser@test.com',
        'password': 'TestPassword123!',
        'confirmed_password': 'TestPassword123!'
    }
    
    register_response = client.post(register_url, register_data, content_type='application/json')
    assert register_response.status_code == 201
    
    user = User.objects.get(email='testuser@test.com')
    assert user.is_active is False
    
    refresh = RefreshToken.for_user(user)
    token = str(refresh.access_token)
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    
    activate_url = reverse('activate', kwargs={'uidb64': uidb64, 'token': token})
    activate_response = client.get(activate_url)
    assert activate_response.status_code == 200
    
    user.refresh_from_db()
    assert user.is_active is True
    
    login_url = reverse('login')
    login_data = {
        'email': 'testuser@test.com',
        'password': 'TestPassword123!'
    }
    
    login_response = client.post(login_url, login_data, content_type='application/json')
    assert login_response.status_code == 200
    assert 'access_token' in login_response.cookies

@pytest.mark.integration
@pytest.mark.django_db
def test_full_authentication_and_video_access_flow(client):
    """Test complete authentication and video access flow."""
    user = User.objects.create_user(
        email='testuser@test.com',
        password='TestPassword123!',
        username='testuser@test.com',
        is_active=True
    )
    
    video = Video.objects.create(
        title='Test Video',
        description='Test Description',
        genre='action'
    )
    
    login_url = reverse('login')
    login_data = {
        'email': 'testuser@test.com',
        'password': 'TestPassword123!'
    }
    
    login_response = client.post(login_url, login_data, content_type='application/json')
    assert login_response.status_code == 200
    
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    api_client = APIClient()
    api_client.cookies['access_token'] = access_token
    
    video_list_url = reverse('video-list')
    video_response = api_client.get(video_list_url)
    
    assert video_response.status_code == 200
    assert len(video_response.data) == 1
    assert video_response.data[0]['title'] == 'Test Video'

@pytest.mark.integration
@pytest.mark.django_db
def test_password_reset_flow(client):
    """Test complete password reset flow."""
    user = User.objects.create_user(
        email='testuser@test.com',
        password='OldPassword123!',
        username='testuser@test.com',
        is_active=True
    )
    
    reset_url = reverse('password_reset')
    reset_data = {
        'email': 'testuser@test.com'
    }
    
    reset_response = client.post(reset_url, reset_data, content_type='application/json')
    assert reset_response.status_code == 200
    
    refresh = RefreshToken.for_user(user)
    token = str(refresh.access_token)
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    
    confirm_url = reverse('password_confirm', kwargs={'uidb64': uidb64, 'token': token})
    confirm_data = {
        'new_password': 'NewPassword123!',
        'confirm_password': 'NewPassword123!'
    }
    
    confirm_response = client.post(confirm_url, confirm_data, content_type='application/json')
    assert confirm_response.status_code == 200
    
    user.refresh_from_db()
    assert user.check_password('NewPassword123!')
    
    login_url = reverse('login')
    login_data = {
        'email': 'testuser@test.com',
        'password': 'NewPassword123!'
    }
    
    login_response = client.post(login_url, login_data, content_type='application/json')
    assert login_response.status_code == 200

@pytest.mark.integration
@pytest.mark.django_db
def test_token_refresh_flow(client):
    """Test token refresh flow."""
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
    
    refresh_url = reverse('token_refresh')
    refresh_response = client.post(refresh_url)
    
    assert refresh_response.status_code == 200
    assert 'access' in refresh_response.data
    assert 'access_token' in refresh_response.cookies

@pytest.mark.integration
@pytest.mark.django_db
def test_logout_flow(client):
    """Test logout flow."""
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

@pytest.mark.integration
@pytest.mark.django_db  
def test_unauthorized_access_scenarios(client):
    """Test various unauthorized access scenarios."""
    video = Video.objects.create(
        title='Test Video',
        description='Test Description',
        genre='action'
    )
    
    api_client = APIClient()
    
    protected_urls = [
        reverse('video-list'),
        reverse('hls-manifest', kwargs={'movie_id': video.id, 'resolution': '480p'}),
        reverse('hls-segment', kwargs={'movie_id': video.id, 'resolution': '480p', 'segment': '000.ts'}),
    ]
    
    for url in protected_urls:
        response = api_client.get(url)
        assert response.status_code == 401
