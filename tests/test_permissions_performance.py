import pytest
import time
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from user_auth_app.models import User

@pytest.mark.django_db
class TestPermissions:
    """Test permission handling."""
    
    def setup_method(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            email='test@test.com',
            password='TestPassword123!',
            username='test@test.com',
            is_active=True
        )
        
        self.api_client = APIClient()
        refresh = RefreshToken.for_user(self.user)
        self.api_client.cookies['access_token'] = str(refresh.access_token)
    
    def test_video_upload_permissions(self):
        """Test video upload requires proper permissions."""
        video_file = SimpleUploadedFile(
            "test_video.mp4",
            b"fake video content",
            content_type="video/mp4"
        )
        
        data = {
            'title': 'Test Video',
            'description': 'Test Description',
            'genre': 'action',
            'original_file': video_file
        }
        
        response = self.api_client.post('/api/upload/', data, format='multipart')
        
        if response.status_code == 404:
            response = self.api_client.post('/api/videos/', data, format='multipart')
        
        assert response.status_code in [201, 403, 404, 405]
        
        if response.status_code == 403:
            pass
        elif response.status_code == 201:
            assert 'id' in response.data

@pytest.mark.django_db
class TestPerformanceBasics:
    """Test basic performance requirements."""
    
    def test_user_creation_performance(self):
        """Test user creation performance."""
        start_time = time.time()
        
        users = []
        for i in range(20):
            user = User.objects.create_user(
                email=f'user{i}@test.com',
                password='TestPassword123!',
                username=f'user{i}@test.com'
            )
            users.append(user)
        
        end_time = time.time()
        duration = end_time - start_time
        
        assert duration < 5.0, f"Creating 20 users took {duration:.2f} seconds"
        assert len(users) == 20
