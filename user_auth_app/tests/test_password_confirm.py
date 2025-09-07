import pytest
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework_simplejwt.tokens import RefreshToken
from user_auth_app.models import User

@pytest.mark.django_db
def test_password_confirm_success(client):
    """Test successful password confirmation."""
    user = User.objects.create_user(
        email='testuser@test.com',
        password='OldPassword123!',
        username='testuser@test.com',
        is_active=True
    )
    
    refresh = RefreshToken.for_user(user)
    token = str(refresh.access_token)
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    
    url = reverse('password_confirm', kwargs={'uidb64': uidb64, 'token': token})
    data = {
        'new_password': 'NewPassword123!',
        'confirm_password': 'NewPassword123!'
    }
    
    response = client.post(url, data, content_type='application/json')
    
    assert response.status_code == 200
    assert response.data['detail'] == 'Your password has been successfully reset.'
    
    user.refresh_from_db()
    assert user.check_password('NewPassword123!')

@pytest.mark.django_db
def test_password_confirm_passwords_dont_match(client):
    """Test password confirmation with non-matching passwords."""
    user = User.objects.create_user(
        email='testuser@test.com',
        password='OldPassword123!',
        username='testuser@test.com',
        is_active=True
    )
    
    refresh = RefreshToken.for_user(user)
    token = str(refresh.access_token)
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    
    url = reverse('password_confirm', kwargs={'uidb64': uidb64, 'token': token})
    data = {
        'new_password': 'NewPassword123!',
        'confirm_password': 'DifferentPassword123!'
    }
    
    response = client.post(url, data, content_type='application/json')
    
    assert response.status_code == 400
    assert response.data['detail'] == 'Passwords do not match'

@pytest.mark.django_db
def test_password_confirm_invalid_token(client):
    """Test password confirmation with invalid token."""
    user = User.objects.create_user(
        email='testuser@test.com',
        password='OldPassword123!',
        username='testuser@test.com',
        is_active=True
    )
    
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    invalid_token = 'invalid_token'
    
    url = reverse('password_confirm', kwargs={'uidb64': uidb64, 'token': invalid_token})
    data = {
        'new_password': 'NewPassword123!',
        'confirm_password': 'NewPassword123!'
    }
    
    response = client.post(url, data, content_type='application/json')
    
    assert response.status_code == 400
    assert response.data['detail'] == 'Invalid token or user'

@pytest.mark.django_db
def test_password_confirm_invalid_uid(client):
    """Test password confirmation with invalid user ID."""
    user = User.objects.create_user(
        email='testuser@test.com',
        password='OldPassword123!',
        username='testuser@test.com',
        is_active=True
    )
    
    refresh = RefreshToken.for_user(user)
    token = str(refresh.access_token)
    invalid_uidb64 = urlsafe_base64_encode(force_bytes(99999))
    
    url = reverse('password_confirm', kwargs={'uidb64': invalid_uidb64, 'token': token})
    data = {
        'new_password': 'NewPassword123!',
        'confirm_password': 'NewPassword123!'
    }
    
    response = client.post(url, data, content_type='application/json')
    
    assert response.status_code == 400
    assert response.data['detail'] == 'Invalid token or user'

@pytest.mark.django_db
def test_password_confirm_weak_password(client):
    """Test password confirmation with weak password."""
    user = User.objects.create_user(
        email='testuser@test.com',
        password='OldPassword123!',
        username='testuser@test.com',
        is_active=True
    )
    
    refresh = RefreshToken.for_user(user)
    token = str(refresh.access_token)
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    
    url = reverse('password_confirm', kwargs={'uidb64': uidb64, 'token': token})
    data = {
        'new_password': '123',
        'confirm_password': '123'
    }
    
    response = client.post(url, data, content_type='application/json')
    
    assert response.status_code == 400
    assert response.data['detail'] == 'Passwords do not match'
