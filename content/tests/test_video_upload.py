import pytest
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from user_auth_app.models import User
from content.models import Video

@pytest.mark.django_db
def test_video_upload_success_admin(client):
    """Test successful video upload by admin user."""
    admin_user = User.objects.create_superuser(
        email='admin@test.com',
        password='AdminPassword123!',
        username='admin@test.com'
    )
    
    video_file = SimpleUploadedFile(
        "test_video.mp4",
        b"fake video content",
        content_type="video/mp4"
    )
    
    api_client = APIClient()
    api_client.force_authenticate(user=admin_user)
    
    url = reverse('video-upload')
    data = {
        'title': 'Test Video',
        'description': 'Test Description',
        'genre': 'action',
        'original_file': video_file
    }
    
    response = api_client.post(url, data, format='multipart')
    
    assert response.status_code == 201
    assert response.data['detail'] == 'Video uploaded successfully. Processing started in background.'
    
    video = Video.objects.get(title='Test Video')
    assert video.description == 'Test Description'
    assert video.genre == 'action'

@pytest.mark.django_db
def test_video_upload_unauthorized_regular_user(client):
    """Test video upload by regular user (should fail)."""
    user = User.objects.create_user(
        email='user@test.com',
        password='UserPassword123!',
        username='user@test.com',
        is_active=True
    )
    
    video_file = SimpleUploadedFile(
        "test_video.mp4",
        b"fake video content",
        content_type="video/mp4"
    )
    
    api_client = APIClient()
    api_client.force_authenticate(user=user)
    
    url = reverse('video-upload')
    data = {
        'title': 'Test Video',
        'description': 'Test Description',
        'genre': 'action',
        'original_file': video_file
    }
    
    response = api_client.post(url, data, format='multipart')
    
    assert response.status_code == 403

@pytest.mark.django_db
def test_video_upload_unauthenticated(client):
    """Test video upload without authentication."""
    video_file = SimpleUploadedFile(
        "test_video.mp4",
        b"fake video content",
        content_type="video/mp4"
    )
    
    api_client = APIClient()
    
    url = reverse('video-upload')
    data = {
        'title': 'Test Video',
        'description': 'Test Description',
        'genre': 'action',
        'original_file': video_file
    }
    
    response = api_client.post(url, data, format='multipart')
    
    assert response.status_code == 403

@pytest.mark.django_db
def test_video_upload_missing_fields(client):
    """Test video upload with missing required fields."""
    admin_user = User.objects.create_superuser(
        email='admin@test.com',
        password='AdminPassword123!',
        username='admin@test.com'
    )
    
    api_client = APIClient()
    api_client.force_authenticate(user=admin_user)
    
    url = reverse('video-upload')
    data = {
        'title': 'Test Video',
    }
    
    response = api_client.post(url, data, format='multipart')
    
    assert response.status_code == 400

@pytest.mark.django_db
def test_video_upload_invalid_genre(client):
    """Test video upload with invalid genre."""
    admin_user = User.objects.create_superuser(
        email='admin@test.com',
        password='AdminPassword123!',
        username='admin@test.com'
    )
    
    video_file = SimpleUploadedFile(
        "test_video.mp4",
        b"fake video content",
        content_type="video/mp4"
    )
    
    api_client = APIClient()
    api_client.force_authenticate(user=admin_user)
    
    url = reverse('video-upload')
    data = {
        'title': 'Test Video',
        'description': 'Test Description',
        'genre': 'invalid_genre',
        'original_file': video_file
    }
    
    response = api_client.post(url, data, format='multipart')
    
    assert response.status_code == 400

@pytest.mark.django_db
def test_video_upload_no_file(client):
    """Test video upload without file."""
    admin_user = User.objects.create_superuser(
        email='admin@test.com',
        password='AdminPassword123!',
        username='admin@test.com'
    )
    
    api_client = APIClient()
    api_client.force_authenticate(user=admin_user)
    
    url = reverse('video-upload')
    data = {
        'title': 'Test Video',
        'description': 'Test Description',
        'genre': 'action'
    }
    
    response = api_client.post(url, data, format='multipart')
    
    assert response.status_code == 400
