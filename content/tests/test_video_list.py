import pytest
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from user_auth_app.models import User
from content.models import Video

@pytest.mark.django_db
def test_video_list_authenticated_success(client):
    """Test video list retrieval for authenticated user."""
    user = User.objects.create_user(
        email='testuser@test.com',
        password='TestPassword123!',
        username='testuser@test.com',
        is_active=True
    )
    
    video1 = Video.objects.create(
        title='Test Video 1',
        description='Test Description 1',
        genre='action'
    )
    video2 = Video.objects.create(
        title='Test Video 2',
        description='Test Description 2',
        genre='comedy'
    )
    
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    api_client = APIClient()
    api_client.cookies['access_token'] = access_token
    
    url = reverse('video-list')
    response = api_client.get(url)
    
    assert response.status_code == 200
    assert isinstance(response.data, list)
    assert len(response.data) == 2
    
    for video in response.data:
        expected_fields = {'id', 'created_at', 'title', 'description', 'thumbnail_url', 'category'}
        assert set(video.keys()) == expected_fields
        assert video['title'] in ['Test Video 1', 'Test Video 2']

@pytest.mark.django_db
def test_video_list_unauthenticated_unauthorized(client):
    """Test video list retrieval for unauthenticated user."""
    Video.objects.create(
        title='Test Video',
        description='Test Description',
        genre='action'
    )
    
    api_client = APIClient()
    url = reverse('video-list')
    response = api_client.get(url)
    
    assert response.status_code == 401

@pytest.mark.django_db
def test_video_list_empty_list(client):
    """Test video list retrieval when no videos exist."""
    user = User.objects.create_user(
        email='testuser@test.com',
        password='TestPassword123!',
        username='testuser@test.com',
        is_active=True
    )
    
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    api_client = APIClient()
    api_client.cookies['access_token'] = access_token
    
    url = reverse('video-list')
    response = api_client.get(url)
    
    assert response.status_code == 200
    assert response.data == []

@pytest.mark.django_db
def test_video_list_ordering(client):
    """Test video list is ordered by upload_date descending."""
    user = User.objects.create_user(
        email='testuser@test.com',
        password='TestPassword123!',
        username='testuser@test.com',
        is_active=True
    )
    
    video1 = Video.objects.create(
        title='First Video',
        description='Description 1',
        genre='action'
    )
    video2 = Video.objects.create(
        title='Second Video',
        description='Description 2',
        genre='comedy'
    )
    
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    api_client = APIClient()
    api_client.cookies['access_token'] = access_token
    
    url = reverse('video-list')
    response = api_client.get(url)
    
    assert response.status_code == 200
    assert len(response.data) == 2
    assert response.data[0]['title'] == 'Second Video'
    assert response.data[1]['title'] == 'First Video'

@pytest.mark.django_db
def test_video_list_thumbnail_url_generation(client):
    """Test thumbnail URL generation in video list."""
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
    
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    api_client = APIClient()
    api_client.cookies['access_token'] = access_token
    
    url = reverse('video-list')
    response = api_client.get(url)
    
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['thumbnail_url'] is None

@pytest.mark.django_db
def test_video_list_multiple_genres(client):
    """Test video list with multiple video genres."""
    user = User.objects.create_user(
        email='testuser@test.com',
        password='TestPassword123!',
        username='testuser@test.com',
        is_active=True
    )
    
    genres = ['action', 'comedy', 'drama', 'horror', 'sci_fi']
    for i, genre in enumerate(genres):
        Video.objects.create(
            title=f'Video {i+1}',
            description=f'Description {i+1}',
            genre=genre
        )
    
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    api_client = APIClient()
    api_client.cookies['access_token'] = access_token
    
    url = reverse('video-list')
    response = api_client.get(url)
    
    assert response.status_code == 200
    assert len(response.data) == 5
    
    categories = [video['category'] for video in response.data]
    expected_categories = ['Action', 'Comedy', 'Drama', 'Horror', 'Sci-Fi']
    for category in expected_categories:
        assert category in categories
