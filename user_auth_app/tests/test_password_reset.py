import pytest
from django.urls import reverse
from user_auth_app.models import User

@pytest.mark.django_db
def test_password_reset_success(client):
    """Test successful password reset request."""
    User.objects.create_user(
        email='testuser@test.com',
        password='TestPassword123!',
        username='testuser@test.com',
        is_active=True
    )
    
    url = reverse('password_reset')
    data = {
        'email': 'testuser@test.com'
    }
    
    response = client.post(url, data, content_type='application/json')
    
    assert response.status_code == 200
    assert response.data['detail'] == 'An email has been sent to reset your password.'

@pytest.mark.django_db
def test_password_reset_nonexistent_user(client):
    """Test password reset for non-existent user."""
    url = reverse('password_reset')
    data = {
        'email': 'nonexistent@test.com'
    }
    
    response = client.post(url, data, content_type='application/json')
    
    assert response.status_code == 200
    assert response.data['detail'] == 'An email has been sent to reset your password.'

@pytest.mark.django_db
def test_password_reset_invalid_email(client):
    """Test password reset with invalid email format."""
    url = reverse('password_reset')
    data = {
        'email': 'invalid-email'
    }
    
    response = client.post(url, data, content_type='application/json')
    assert response.status_code == 400
    assert response.data['detail'] == 'Invalid email address'

@pytest.mark.django_db
def test_password_reset_missing_email(client):
    """Test password reset without email."""
    url = reverse('password_reset')
    data = {}
    
    response = client.post(url, data, content_type='application/json')
    assert response.status_code == 400
