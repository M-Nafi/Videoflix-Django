import pytest
import os
import tempfile
from django.urls import reverse
from django.test import override_settings
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from user_auth_app.models import User
from content.models import Video

@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.gettempdir())
def test_hls_manifest_success(client):
    """Test successful HLS manifest retrieval."""
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
    
    media_root = tempfile.gettempdir()
    video_filename = f'test_video_{video.id}.mp4'
    video_path = os.path.join(media_root, 'videos', video_filename)
    os.makedirs(os.path.dirname(video_path), exist_ok=True)
    
    with open(video_path, 'w') as f:
        f.write('dummy video content')
    
    video.original_file.name = f'videos/{video_filename}'
    video.save()
    
    basename = os.path.splitext(video_filename)[0]
    hls_dir = os.path.join(media_root, 'videos/hls/480p', basename)
    os.makedirs(hls_dir, exist_ok=True)
    
    manifest_path = os.path.join(hls_dir, 'index.m3u8')
    with open(manifest_path, 'w') as f:
        f.write('#EXTM3U\n#EXT-X-VERSION:3\n#EXT-X-TARGETDURATION:10\n')
    
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    api_client = APIClient()
    api_client.cookies['access_token'] = access_token
    
    url = reverse('hls-manifest', kwargs={'movie_id': video.id, 'resolution': '480p'})
    response = api_client.get(url)
    
    assert response.status_code == 200
    assert response['Content-Type'] == 'application/vnd.apple.mpegurl'

@pytest.mark.django_db
def test_hls_manifest_video_not_found(client):
    """Test HLS manifest for non-existent video."""
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
    
    url = reverse('hls-manifest', kwargs={'movie_id': 99999, 'resolution': '480p'})
    response = api_client.get(url)
    
    assert response.status_code == 404

@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.gettempdir())
def test_hls_manifest_file_not_found(client):
    """Test HLS manifest when manifest file doesn't exist."""
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
    
    media_root = tempfile.gettempdir()
    video_filename = f'test_video_{video.id}.mp4'
    video_path = os.path.join(media_root, 'videos', video_filename)
    os.makedirs(os.path.dirname(video_path), exist_ok=True)
    
    with open(video_path, 'w') as f:
        f.write('dummy video content')
    
    video.original_file.name = f'videos/{video_filename}'
    video.save()
    
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    api_client = APIClient()
    api_client.cookies['access_token'] = access_token
    
    url = reverse('hls-manifest', kwargs={'movie_id': video.id, 'resolution': '480p'})
    response = api_client.get(url)
    
    assert response.status_code == 404

@pytest.mark.django_db
def test_hls_manifest_unauthenticated(client):
    """Test HLS manifest access without authentication."""
    video = Video.objects.create(
        title='Test Video',
        description='Test Description',
        genre='action'
    )
    
    api_client = APIClient()
    url = reverse('hls-manifest', kwargs={'movie_id': video.id, 'resolution': '480p'})
    response = api_client.get(url)
    
    assert response.status_code == 401

@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.gettempdir())
def test_hls_manifest_different_resolutions(client):
    """Test HLS manifest for different resolutions."""
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
    
    media_root = tempfile.gettempdir()
    video_filename = f'test_video_{video.id}.mp4'
    video_path = os.path.join(media_root, 'videos', video_filename)
    os.makedirs(os.path.dirname(video_path), exist_ok=True)
    
    with open(video_path, 'w') as f:
        f.write('dummy video content')
    
    video.original_file.name = f'videos/{video_filename}'
    video.save()
    
    basename = os.path.splitext(video_filename)[0]
    resolutions = ['480p', '720p', '1080p']
    
    for resolution in resolutions:
        hls_dir = os.path.join(media_root, f'videos/hls/{resolution}', basename)
        os.makedirs(hls_dir, exist_ok=True)
        
        manifest_path = os.path.join(hls_dir, 'index.m3u8')
        with open(manifest_path, 'w') as f:
            f.write(f'#EXTM3U\n#EXT-X-VERSION:3\n#RESOLUTION:{resolution}\n')
    
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    api_client = APIClient()
    api_client.cookies['access_token'] = access_token
    
    for resolution in resolutions:
        url = reverse('hls-manifest', kwargs={'movie_id': video.id, 'resolution': resolution})
        response = api_client.get(url)
        
        assert response.status_code == 200
        assert response['Content-Type'] == 'application/vnd.apple.mpegurl'
