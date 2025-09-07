import pytest
from django.urls import reverse
from user_auth_app.models import User

@pytest.mark.django_db
def test_register_user_success(client):
    """Test successful user registration."""
    url = reverse('register')
    data = {
        'email': 'testuser@test.com',
        'password': 'TestPassword123!',
        'confirmed_password': 'TestPassword123!'
    }

    response = client.post(url, data, content_type='application/json')
    
    assert response.status_code == 201
    assert 'user' in response.data
    assert 'token' in response.data
    assert response.data['user']['email'] == 'testuser@test.com'
    
    user = User.objects.get(email='testuser@test.com')
    assert user.is_active is False
    assert user.username == 'testuser@test.com'

@pytest.mark.django_db
def test_register_user_with_existing_email(client):
    """Test registration with already existing email."""
    User.objects.create_user(
        email='testuser@test.com',
        password='TestPassword123!',
        username='testuser@test.com'
    )
    
    url = reverse('register')
    data = {
        'email': 'testuser@test.com',
        'password': 'TestPassword123!',
        'confirmed_password': 'TestPassword123!'
    }

    response = client.post(url, data, content_type='application/json')
    assert response.status_code == 400
    assert response.data['detail'] == 'Please check your entries and try again.'

@pytest.mark.django_db
def test_register_user_passwords_not_matching(client):
    """Test registration with non-matching passwords."""
    url = reverse('register')
    data = {
        'email': 'testuser@test.com',
        'password': 'TestPassword123!',
        'confirmed_password': 'DifferentPassword123!'
    }

    response = client.post(url, data, content_type='application/json')
    assert response.status_code == 400
    assert response.data['detail'] == 'Please check your entries and try again.'

@pytest.mark.django_db
def test_register_user_invalid_password(client):
    """Test registration with invalid password."""
    url = reverse('register')
    data = {
        'email': 'testuser@test.com',
        'password': '123',
        'confirmed_password': '123'
    }

    response = client.post(url, data, content_type='application/json')
    assert response.status_code == 400

@pytest.mark.django_db
def test_register_user_invalid_email(client):
    """Test registration with invalid email format."""
    url = reverse('register')
    data = {
        'email': 'invalid-email',
        'password': 'TestPassword123!',
        'confirmed_password': 'TestPassword123!'
    }

    response = client.post(url, data, content_type='application/json')
    assert response.status_code == 400

@pytest.mark.django_db
def test_register_user_missing_fields(client):
    """Test registration with missing required fields."""
    url = reverse('register')
    data = {
        'email': 'testuser@test.com',
    }

    response = client.post(url, data, content_type='application/json')
    assert response.status_code == 400
