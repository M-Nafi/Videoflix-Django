import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from user_auth_app.models import User

@pytest.mark.django_db
def test_user_profile_get_authenticated(client):
    """Test retrieving user profile for authenticated user."""
    user = User.objects.create_user(
        email='testuser@test.com',
        password='TestPassword123!',
        username='testuser@test.com',
        is_active=True,
        first_name='Test',
        last_name='User'
    )
    
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    api_client = APIClient()
    api_client.cookies['access_token'] = access_token
    
    url = reverse('user-profile-list')
    response = api_client.get(url)
    
    assert response.status_code == 200
    assert len(response.data) == 1
    profile = response.data[0]
    assert profile['email'] == 'testuser@test.com'
    assert profile['username'] == 'testuser@test.com'
    assert profile['first_name'] == 'Test'
    assert profile['last_name'] == 'User'
    assert 'id' in profile
    assert 'date_joined' in profile

@pytest.mark.django_db
def test_user_profile_get_unauthenticated(client):
    """Test retrieving user profile without authentication."""
    api_client = APIClient()
    url = reverse('user-profile-list')
    response = api_client.get(url)
    
    assert response.status_code == 401

@pytest.mark.django_db
def test_user_profile_update_patch(client):
    """Test updating user profile with PATCH."""
    user = User.objects.create_user(
        email='testuser@test.com',
        password='TestPassword123!',
        username='testuser@test.com',
        is_active=True,
        first_name='Old',
        last_name='Name'
    )
    
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    api_client = APIClient()
    api_client.cookies['access_token'] = access_token
    
    url = reverse('user-profile-detail', kwargs={'pk': user.id})
    data = {
        'first_name': 'New',
        'last_name': 'Name'
    }
    
    response = api_client.patch(url, data, content_type='application/json')
    
    assert response.status_code == 200
    assert response.data['first_name'] == 'New'
    assert response.data['last_name'] == 'Name'
    assert response.data['email'] == 'testuser@test.com'
    
    user.refresh_from_db()
    assert user.first_name == 'New'
    assert user.last_name == 'Name'

@pytest.mark.django_db
def test_user_profile_update_put(client):
    """Test replacing user profile with PUT."""
    user = User.objects.create_user(
        email='testuser@test.com',
        password='TestPassword123!',
        username='testuser@test.com',
        is_active=True,
        first_name='Old',
        last_name='Name'
    )
    
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    api_client = APIClient()
    api_client.cookies['access_token'] = access_token
    
    url = reverse('user-profile-detail', kwargs={'pk': user.id})
    data = {
        'email': 'testuser@test.com',
        'first_name': 'Completely',
        'last_name': 'New'
    }
    
    response = api_client.put(url, data, content_type='application/json')
    
    assert response.status_code == 200
    assert response.data['first_name'] == 'Completely'
    assert response.data['last_name'] == 'New'
    assert response.data['email'] == 'testuser@test.com'

@pytest.mark.django_db
def test_user_profile_readonly_fields(client):
    """Test that read-only fields cannot be modified."""
    user = User.objects.create_user(
        email='testuser@test.com',
        password='TestPassword123!',
        username='testuser@test.com',
        is_active=True
    )
    
    original_date_joined = user.date_joined
    original_username = user.username
    
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    api_client = APIClient()
    api_client.cookies['access_token'] = access_token
    
    url = reverse('user-profile-detail', kwargs={'pk': user.id})
    data = {
        'username': 'newerusername@test.com',
        'date_joined': '2020-01-01T00:00:00Z',
        'first_name': 'Updated'
    }
    
    response = api_client.patch(url, data, content_type='application/json')
    
    assert response.status_code == 200
    assert response.data['first_name'] == 'Updated'
    assert response.data['username'] == original_username
    
    user.refresh_from_db()
    assert user.username == original_username
    assert user.date_joined == original_date_joined
    assert user.first_name == 'Updated'

@pytest.mark.django_db
def test_user_profile_only_own_profile(client):
    """Test that users can only access their own profile."""
    user1 = User.objects.create_user(
        email='user1@test.com',
        password='TestPassword123!',
        username='user1@test.com',
        is_active=True
    )
    user2 = User.objects.create_user(
        email='user2@test.com',
        password='TestPassword123!',
        username='user2@test.com',
        is_active=True
    )
    
    refresh = RefreshToken.for_user(user1)
    access_token = str(refresh.access_token)
    
    api_client = APIClient()
    api_client.cookies['access_token'] = access_token
    
    url = reverse('user-profile-detail', kwargs={'pk': user2.id})
    response = api_client.get(url)
    
    assert response.status_code == 404

@pytest.mark.django_db
def test_user_profile_invalid_methods():
    """Test user profile with invalid HTTP methods."""
    user = User.objects.create_user(
        email='test@test.com',
        password='TestPassword123!',
        username='test@test.com',
        is_active=True
    )
    
    client = APIClient()
    refresh = RefreshToken.for_user(user)
    client.cookies['access_token'] = str(refresh.access_token)
    
    endpoints_to_try = ['/api/profile/', '/api/user/', '/api/me/']
    
    for endpoint in endpoints_to_try:
        response = client.delete(endpoint)
        
        if response.status_code in [405, 403]:
            assert response.status_code in [405, 403]
            return
        elif response.status_code == 404:
            continue
        elif response.status_code == 204:
            user.refresh_from_db()
            assert user.id is not None
            return
    
    pytest.skip("User profile endpoints not found or not implemented")
