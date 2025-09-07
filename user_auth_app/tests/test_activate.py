import pytest
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework_simplejwt.tokens import RefreshToken
from user_auth_app.models import User

@pytest.mark.django_db
def test_activate_user_success(client):
    """Test successful user activation."""
    user = User.objects.create_user(
        email='testuser@test.com',
        password='TestPassword123!',
        username='testuser@test.com',
        is_active=False
    )
    
    refresh = RefreshToken.for_user(user)
    token = str(refresh.access_token)
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    
    url = reverse('activate', kwargs={'uidb64': uidb64, 'token': token})
    response = client.get(url)
    
    user.refresh_from_db()
    assert response.status_code == 200
    assert response.data['message'] == 'Account successfully activated.'
    assert user.is_active is True

@pytest.mark.django_db
def test_activate_user_already_active(client):
    """Test activation of already active user."""
    user = User.objects.create_user(
        email='testuser@test.com',
        password='TestPassword123!',
        username='testuser@test.com',
        is_active=True
    )
    
    refresh = RefreshToken.for_user(user)
    token = str(refresh.access_token)
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    
    url = reverse('activate', kwargs={'uidb64': uidb64, 'token': token})
    response = client.get(url)
    
    assert response.status_code == 200
    assert response.data['message'] == 'Account successfully activated.'

@pytest.mark.django_db
def test_activate_user_invalid_token(client):
    """Test activation with invalid token."""
    user = User.objects.create_user(
        email='testuser@test.com',
        password='TestPassword123!',
        username='testuser@test.com',
        is_active=False
    )
    
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    invalid_token = 'invalid_token'
    
    url = reverse('activate', kwargs={'uidb64': uidb64, 'token': invalid_token})
    response = client.get(url)
    
    user.refresh_from_db()
    assert response.status_code == 400
    assert response.data['message'] == 'Account activation failed.'
    assert user.is_active is False

@pytest.mark.django_db
def test_activate_user_invalid_uid(client):
    """Test activation with invalid user ID."""
    user = User.objects.create_user(
        email='testuser@test.com',
        password='TestPassword123!',
        username='testuser@test.com',
        is_active=False
    )
    
    refresh = RefreshToken.for_user(user)
    token = str(refresh.access_token)
    invalid_uidb64 = urlsafe_base64_encode(force_bytes(99999))
    
    url = reverse('activate', kwargs={'uidb64': invalid_uidb64, 'token': token})
    response = client.get(url)
    
    assert response.status_code == 400
    assert response.data['message'] == 'Account activation failed.'

@pytest.mark.django_db
def test_activate_user_token_for_different_user(client):
    """Test activation with token for different user."""
    user1 = User.objects.create_user(
        email='user1@test.com',
        password='TestPassword123!',
        username='user1@test.com',
        is_active=False
    )
    user2 = User.objects.create_user(
        email='user2@test.com',
        password='TestPassword123!',
        username='user2@test.com',
        is_active=False
    )
    
    refresh = RefreshToken.for_user(user2)
    token = str(refresh.access_token)
    uidb64 = urlsafe_base64_encode(force_bytes(user1.pk))
    
    url = reverse('activate', kwargs={'uidb64': uidb64, 'token': token})
    response = client.get(url)
    
    user1.refresh_from_db()
    assert response.status_code == 400
    assert response.data['message'] == 'Account activation failed.'
    assert user1.is_active is False
