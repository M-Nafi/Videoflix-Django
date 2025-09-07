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
def test_hls_segment_success(client):
    """Test successful HLS segment retrieval."""
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
    
    segment_filename = '000.ts'
    segment_path = os.path.join(hls_dir, segment_filename)
    with open(segment_path, 'wb') as f:
        f.write(b'dummy segment content')
    
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    api_client = APIClient()
    api_client.cookies['access_token'] = access_token
    
    url = reverse('hls-segment', kwargs={
        'movie_id': video.id,
        'resolution': '480p',
        'segment': segment_filename
    })
    response = api_client.get(url)
    
    assert response.status_code == 200
    assert response['Content-Type'] == 'video/MP2T'

@pytest.mark.django_db
def test_hls_segment_video_not_found(client):
    """Test HLS segment for non-existent video."""
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
    
    url = reverse('hls-segment', kwargs={
        'movie_id': 99999,
        'resolution': '480p',
        'segment': '000.ts'
    })
    response = api_client.get(url)
    
    assert response.status_code == 404

@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.gettempdir())
def test_hls_segment_file_not_found(client):
    """Test HLS segment when segment file doesn't exist."""
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
    
    url = reverse('hls-segment', kwargs={
        'movie_id': video.id,
        'resolution': '480p',
        'segment': 'nonexistent.ts'
    })
    response = api_client.get(url)
    
    assert response.status_code == 404

@pytest.mark.django_db
def test_hls_segment_unauthenticated(client):
    """Test HLS segment access without authentication."""
    video = Video.objects.create(
        title='Test Video',
        description='Test Description',
        genre='action'
    )
    
    api_client = APIClient()
    url = reverse('hls-segment', kwargs={
        'movie_id': video.id,
        'resolution': '480p',
        'segment': '000.ts'
    })
    response = api_client.get(url)
    
    assert response.status_code == 401

@pytest.mark.django_db
@override_settings(MEDIA_ROOT=tempfile.gettempdir())
def test_hls_segment_multiple_segments(client):
    """Test HLS segments for multiple files."""
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
    
    segment_files = ['000.ts', '001.ts', '002.ts']
    for segment_file in segment_files:
        segment_path = os.path.join(hls_dir, segment_file)
        with open(segment_path, 'wb') as f:
            f.write(f'dummy segment content for {segment_file}'.encode())
    
    refresh = RefreshToken.for_user(user)
    access_token = str(refresh.access_token)
    
    api_client = APIClient()
    api_client.cookies['access_token'] = access_token
    
    for segment_file in segment_files:
        url = reverse('hls-segment', kwargs={
            'movie_id': video.id,
            'resolution': '480p',
            'segment': segment_file
        })
        response = api_client.get(url)
        
        assert response.status_code == 200
        assert response['Content-Type'] == 'video/MP2T'
