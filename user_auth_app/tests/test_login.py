import pytest
from django.urls import reverse
from user_auth_app.models import User

@pytest.mark.django_db
def test_login_user_success(client):
    """Test successful user login."""
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
    assert response.data['detail'] == 'Login successful'
    assert response.data['user']['id'] == user.id
    assert response.data['user']['username'] == 'testuser@test.com'
    
    assert 'access_token' in response.cookies
    assert 'refresh_token' in response.cookies
    assert response.cookies['access_token']['httponly']
    assert response.cookies['refresh_token']['httponly']

@pytest.mark.django_db
def test_login_inactive_user(client):
    """Test login with inactive user."""
    User.objects.create_user(
        email='testuser@test.com',
        password='TestPassword123!',
        username='testuser@test.com',
        is_active=False
    )
    
    url = reverse('login')
    data = {
        'email': 'testuser@test.com',
        'password': 'TestPassword123!'
    }
    
    response = client.post(url, data, content_type='application/json')
    assert response.status_code == 400
    assert response.data['detail'] == 'Please check your entries and try again.'

@pytest.mark.django_db
def test_login_invalid_password(client):
    """Test login with invalid password."""
    User.objects.create_user(
        email='testuser@test.com',
        password='TestPassword123!',
        username='testuser@test.com',
        is_active=True
    )
    
    url = reverse('login')
    data = {
        'email': 'testuser@test.com',
        'password': 'WrongPassword123!'
    }
    
    response = client.post(url, data, content_type='application/json')
    assert response.status_code == 400
    assert response.data['detail'] == 'Please check your entries and try again.'

@pytest.mark.django_db
def test_login_nonexistent_user(client):
    """Test login with non-existent user."""
    url = reverse('login')
    data = {
        'email': 'nonexistent@test.com',
        'password': 'TestPassword123!'
    }
    
    response = client.post(url, data, content_type='application/json')
    assert response.status_code == 400
    assert response.data['detail'] == 'Please check your entries and try again.'

@pytest.mark.django_db
def test_login_missing_email(client):
    """Test login with missing email."""
    url = reverse('login')
    data = {
        'password': 'TestPassword123!'
    }
    
    response = client.post(url, data, content_type='application/json')
    assert response.status_code == 400

@pytest.mark.django_db
def test_login_missing_password(client):
    """Test login with missing password."""
    url = reverse('login')
    data = {
        'email': 'testuser@test.com'
    }
    
    response = client.post(url, data, content_type='application/json')
    assert response.status_code == 400

@pytest.mark.django_db
def test_login_invalid_email_format(client):
    """Test login with invalid email format."""
    url = reverse('login')
    data = {
        'email': 'invalid-email',
        'password': 'TestPassword123!'
    }
    
    response = client.post(url, data, content_type='application/json')
    assert response.status_code == 400
