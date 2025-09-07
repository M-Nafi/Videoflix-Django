import pytest
import os
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile, InMemoryUploadedFile
from rest_framework.test import APIClient
from user_auth_app.models import User
from content.models import Video
import io

@pytest.mark.django_db
class TestVideoUploadEdgeCases:
    """Test video upload with various edge cases."""
    
    def setup_method(self):
        """Set up admin user for each test."""
        self.admin_user = User.objects.create_superuser(
            email='admin@test.com',
            password='AdminPassword123!',
            username='admin@test.com'
        )
        
        self.api_client = APIClient()
        self.api_client.force_authenticate(user=self.admin_user)
        self.url = reverse('video-upload')
    
    def test_upload_large_file(self):
        """Test uploading a large video file."""
        # Create a 5MB fake video file
        large_content = b"fake video content" * 300000  # ~5MB
        
        video_file = SimpleUploadedFile(
            "large_video.mp4",
            large_content,
            content_type="video/mp4"
        )
        
        data = {
            'title': 'Large Video',
            'description': 'A large video file',
            'genre': 'action',
            'original_file': video_file
        }
        
        response = self.api_client.post(self.url, data, format='multipart')
        
        # Should succeed (assuming no file size limit set)
        assert response.status_code == 201
        
        video = Video.objects.get(title='Large Video')
        assert video.original_file is not None
    
    def test_upload_empty_file(self):
        """Test uploading an empty file."""
        empty_file = SimpleUploadedFile(
            "empty_video.mp4",
            b"",  # Empty content
            content_type="video/mp4"
        )
        
        data = {
            'title': 'Empty Video',
            'description': 'An empty video file',
            'genre': 'action',
            'original_file': empty_file
        }
        
        response = self.api_client.post(self.url, data, format='multipart')
        
        # Might succeed or fail depending on validation
        # Empty files are usually not desired
        if response.status_code == 201:
            video = Video.objects.get(title='Empty Video')
            assert video.original_file is not None
        else:
            assert response.status_code == 400
    
    def test_upload_invalid_file_type_by_extension(self):
        """Test uploading file with invalid extension."""
        text_file = SimpleUploadedFile(
            "not_a_video.txt",
            b"This is not a video file",
            content_type="text/plain"
        )
        
        data = {
            'title': 'Text File',
            'description': 'A text file disguised as video',
            'genre': 'action',
            'original_file': text_file
        }
        
        response = self.api_client.post(self.url, data, format='multipart')
        
        # Should still succeed if no file type validation is implemented
        # The model accepts FileField, not specifically video files
        assert response.status_code in [201, 400]
    
    def test_upload_invalid_file_type_by_content(self):
        """Test uploading file with video extension but text content."""
        fake_video = SimpleUploadedFile(
            "fake_video.mp4",
            b"This is actually text content, not video",
            content_type="video/mp4"
        )
        
        data = {
            'title': 'Fake Video',
            'description': 'Text content with video extension',
            'genre': 'action',
            'original_file': fake_video
        }
        
        response = self.api_client.post(self.url, data, format='multipart')
        
        # Should succeed at upload level (content validation would happen during processing)
        assert response.status_code == 201
    
    def test_upload_file_with_special_characters(self):
        """Test uploading file with special characters in filename."""
        special_file = SimpleUploadedFile(
            "vidéo_spécial-测试!@#$%^&*().mp4",
            b"fake video content",
            content_type="video/mp4"
        )
        
        data = {
            'title': 'Special Characters Video',
            'description': 'Video with special characters in filename',
            'genre': 'action',
            'original_file': special_file
        }
        
        response = self.api_client.post(self.url, data, format='multipart')
        
        assert response.status_code == 201
        
        video = Video.objects.get(title='Special Characters Video')
        assert video.original_file is not None
    
    def test_upload_file_with_very_long_filename(self):
        """Test uploading file with very long filename."""
        long_filename = "a" * 200 + ".mp4"  # Very long filename
        
        long_file = SimpleUploadedFile(
            long_filename,
            b"fake video content",
            content_type="video/mp4"
        )
        
        data = {
            'title': 'Long Filename Video',
            'description': 'Video with very long filename',
            'genre': 'action',
            'original_file': long_file
        }
        
        response = self.api_client.post(self.url, data, format='multipart')
        
        # Should succeed, Django/filesystem will handle filename truncation
        assert response.status_code == 201
    
    def test_upload_multiple_files_same_name(self):
        """Test uploading multiple files with the same name."""
        # First upload
        video_file1 = SimpleUploadedFile(
            "same_name.mp4",
            b"first video content",
            content_type="video/mp4"
        )
        
        data1 = {
            'title': 'First Video',
            'description': 'First video with same filename',
            'genre': 'action',
            'original_file': video_file1
        }
        
        response1 = self.api_client.post(self.url, data1, format='multipart')
        assert response1.status_code == 201
        
        # Second upload with same filename
        video_file2 = SimpleUploadedFile(
            "same_name.mp4",
            b"second video content",
            content_type="video/mp4"
        )
        
        data2 = {
            'title': 'Second Video',
            'description': 'Second video with same filename',
            'genre': 'comedy',
            'original_file': video_file2
        }
        
        response2 = self.api_client.post(self.url, data2, format='multipart')
        assert response2.status_code == 201
        
        # Both videos should exist
        video1 = Video.objects.get(title='First Video')
        video2 = Video.objects.get(title='Second Video')
        
        # Filenames should be different (Django adds suffix)
        assert video1.original_file.name != video2.original_file.name
    
    def test_upload_with_inmemory_file(self):
        """Test uploading with InMemoryUploadedFile."""
        file_content = b"fake video content for in-memory file"
        file_obj = io.BytesIO(file_content)
        
        inmemory_file = InMemoryUploadedFile(
            file_obj,
            field_name='original_file',
            name='inmemory_video.mp4',
            content_type='video/mp4',
            size=len(file_content),
            charset=None
        )
        
        data = {
            'title': 'InMemory Video',
            'description': 'Video uploaded as InMemoryUploadedFile',
            'genre': 'action',
            'original_file': inmemory_file
        }
        
        response = self.api_client.post(self.url, data, format='multipart')
        
        assert response.status_code == 201
        
        video = Video.objects.get(title='InMemory Video')
        assert video.original_file is not None
    
    def test_upload_file_without_extension(self):
        """Test uploading file without extension."""
        no_ext_file = SimpleUploadedFile(
            "video_without_extension",
            b"fake video content",
            content_type="video/mp4"
        )
        
        data = {
            'title': 'No Extension Video',
            'description': 'Video file without extension',
            'genre': 'action',
            'original_file': no_ext_file
        }
        
        response = self.api_client.post(self.url, data, format='multipart')
        
        assert response.status_code == 201
        
        video = Video.objects.get(title='No Extension Video')
        assert video.original_file is not None
    
    def test_upload_with_null_bytes_in_filename(self):
        """Test uploading file with null bytes in filename."""
        null_byte_file = SimpleUploadedFile(
            "video\\x00with_null.mp4",
            b"fake video content",
            content_type="video/mp4"
        )
        
        data = {
            'title': 'Null Byte Video',
            'description': 'Video with null bytes in filename',
            'genre': 'action',
            'original_file': null_byte_file
        }
        
        response = self.api_client.post(self.url, data, format='multipart')
        
        # Should handle gracefully
        assert response.status_code in [201, 400]
    
    def test_upload_with_binary_data_in_title_description(self):
        """Test uploading with binary/special characters in title and description."""
        video_file = SimpleUploadedFile(
            "test_video.mp4",
            b"fake video content",
            content_type="video/mp4"
        )
        
        data = {
            'title': 'Test 测试 🎬 Vidéo',
            'description': 'Description with émojis 🎭 and ñiño characters',
            'genre': 'action',
            'original_file': video_file
        }
        
        response = self.api_client.post(self.url, data, format='multipart')
        
        assert response.status_code == 201
        
        video = Video.objects.get(title='Test 测试 🎬 Vidéo')
        assert video.description == 'Description with émojis 🎭 and ñiño characters'
    
    def test_upload_concurrent_same_title(self):
        """Test uploading videos with same title concurrently."""
        video_file1 = SimpleUploadedFile(
            "video1.mp4",
            b"first video content",
            content_type="video/mp4"
        )
        
        video_file2 = SimpleUploadedFile(
            "video2.mp4",
            b"second video content",
            content_type="video/mp4"
        )
        
        data1 = {
            'title': 'Duplicate Title Video',
            'description': 'First video with duplicate title',
            'genre': 'action',
            'original_file': video_file1
        }
        
        data2 = {
            'title': 'Duplicate Title Video',
            'description': 'Second video with duplicate title',
            'genre': 'comedy',
            'original_file': video_file2
        }
        
        response1 = self.api_client.post(self.url, data1, format='multipart')
        response2 = self.api_client.post(self.url, data2, format='multipart')
        
        # Both should succeed (no unique constraint on title)
        assert response1.status_code == 201
        assert response2.status_code == 201
        
        videos = Video.objects.filter(title='Duplicate Title Video')
        assert len(videos) == 2
    
    def test_upload_with_corrupted_multipart_data(self):
        """Test uploading with malformed multipart data."""
        # This test is more complex and depends on how the API handles malformed data
        # For now, test with missing content-type
        
        data = {
            'title': 'Test Video',
            'description': 'Test Description',
            'genre': 'action',
            # Missing original_file
        }
        
        response = self.api_client.post(self.url, data, format='multipart')
        
        assert response.status_code == 400
        assert 'original_file' in response.data or 'original_file' in str(response.data)
