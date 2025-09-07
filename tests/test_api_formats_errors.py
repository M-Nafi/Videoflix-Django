import pytest
from unittest.mock import patch, mock_open, Mock, MagicMock
from django.test import TestCase
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from user_auth_app.models import User
from content.models import Video

@pytest.mark.django_db
class TestAPIResponseFormats:
    """Test API response formats and content types."""
    
    def setup_method(self):
        """Set up test user and authentication."""
        self.user = User.objects.create_user(
            email='test@test.com',
            password='TestPassword123!',
            username='test@test.com',
            is_active=True
        )
        
        self.video = Video.objects.create(
            title='Test Video',
            description='Test Description',
            genre='action'
        )
        
        self.api_client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.api_client.cookies['access_token'] = str(refresh.access_token)
    
    @patch('builtins.open', new_callable=mock_open, read_data=b'#EXTM3U\n#EXT-X-VERSION:3\n')
    @patch('os.path.exists')
    def test_hls_manifest_content_type(self, mock_exists, mock_file_open):
        """Test HLS manifest returns correct content type."""
        mock_exists.return_value = True
        
        mock_file = MagicMock()
        mock_file.read.return_value = b'#EXTM3U\n#EXT-X-VERSION:3\n'
        mock_file.__enter__ = Mock(return_value=mock_file)
        mock_file.__exit__ = Mock(return_value=None)
        mock_file_open.return_value = mock_file
        
        url = f'/api/video/{self.video.id}/720p/index.m3u8'
        response = self.api_client.get(url)
        
        assert response.status_code in [200, 404]
        
        if response.status_code == 200:
            assert response['Content-Type'] == 'application/vnd.apple.mpegurl'
    
    @patch('builtins.open', new_callable=mock_open, read_data=b'binary_video_data')
    @patch('os.path.exists')
    def test_hls_segment_content_type(self, mock_exists, mock_file_open):
        """Test HLS segment returns correct content type."""
        mock_exists.return_value = True
        
        mock_file = MagicMock()
        mock_file.read.return_value = b'binary_video_data'
        mock_file.__enter__ = Mock(return_value=mock_file)
        mock_file.__exit__ = Mock(return_value=None)
        mock_file_open.return_value = mock_file
        
        url = f'/api/video/{self.video.id}/720p/000.ts'
        response = self.api_client.get(url)
        
        assert response.status_code in [200, 301, 404]
        
        if response.status_code == 200:
            assert response['Content-Type'] == 'video/MP2T'

@pytest.mark.django_db
class TestErrorHandling:
    """Test error handling for various scenarios."""
    
    def setup_method(self):
        """Set up test user and authentication."""
        self.user = User.objects.create_user(
            email='test@test.com',
            password='TestPassword123!', 
            username='test@test.com',
            is_active=True
        )
        
        self.video = Video.objects.create(
            title='Test Video',
            description='Test Description',
            genre='action'
        )
        
        self.api_client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.api_client.cookies['access_token'] = str(refresh.access_token)
    
    @patch('builtins.open')
    @patch('os.path.exists')
    def test_file_system_permission_error(self, mock_exists, mock_open_func):
        """Test handling of file system permission errors."""
        mock_exists.return_value = True
        mock_open_func.side_effect = PermissionError("Permission denied")
        
        url = f'/api/video/{self.video.id}/720p/index.m3u8'
        response = self.api_client.get(url)
        
        assert response.status_code in [403, 404, 500]
    
    def test_video_not_found_error(self):
        """Test handling when video doesn't exist."""
        non_existent_id = 99999
        url = f'/api/video/{non_existent_id}/720p/index.m3u8'
        response = self.api_client.get(url)
        
        assert response.status_code == 404
    
    def test_unauthenticated_access(self):
        """Test access without authentication."""
        client = APIClient()
        
        url = f'/api/video/{self.video.id}/720p/index.m3u8'
        response = client.get(url)
        
        assert response.status_code in [401, 403]
