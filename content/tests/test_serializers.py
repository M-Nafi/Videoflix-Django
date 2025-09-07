import pytest
from unittest.mock import Mock, patch, PropertyMock
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import RequestFactory
from content.api.serializers import VideoUploadSerializer, VideoListSerializer
from content.models import Video

@pytest.mark.django_db
class TestVideoUploadSerializer:
    """Test VideoUploadSerializer validation and creation."""
    
    def test_valid_video_upload(self):
        """Test uploading video with valid data."""
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
        
        serializer = VideoUploadSerializer(data=data)
        assert serializer.is_valid()
        
        video = serializer.save()
        assert video.title == 'Test Video'
        assert video.description == 'Test Description'
        assert video.genre == 'action'
        assert video.original_file is not None
    
    def test_missing_title(self):
        """Test video upload without title."""
        video_file = SimpleUploadedFile(
            "test_video.mp4",
            b"fake video content",
            content_type="video/mp4"
        )
        
        data = {
            'description': 'Test Description',
            'genre': 'action',
            'original_file': video_file
        }
        
        serializer = VideoUploadSerializer(data=data)
        assert not serializer.is_valid()
        assert 'title' in serializer.errors
    
    def test_missing_description(self):
        """Test video upload without description."""
        video_file = SimpleUploadedFile(
            "test_video.mp4",
            b"fake video content",
            content_type="video/mp4"
        )
        
        data = {
            'title': 'Test Video',
            'genre': 'action',
            'original_file': video_file
        }
        
        serializer = VideoUploadSerializer(data=data)
        assert not serializer.is_valid()
        assert 'description' in serializer.errors
    
    def test_missing_genre(self):
        """Test video upload without genre."""
        video_file = SimpleUploadedFile(
            "test_video.mp4",
            b"fake video content",
            content_type="video/mp4"
        )
        
        data = {
            'title': 'Test Video',
            'description': 'Test Description',
            'original_file': video_file
        }
        
        serializer = VideoUploadSerializer(data=data)
        assert not serializer.is_valid()
        assert 'genre' in serializer.errors
    
    def test_missing_file(self):
        """Test video upload without file."""
        data = {
            'title': 'Test Video',
            'description': 'Test Description',
            'genre': 'action'
        }
        
        serializer = VideoUploadSerializer(data=data)
        assert not serializer.is_valid()
        assert 'original_file' in serializer.errors
    
    def test_invalid_genre(self):
        """Test video upload with invalid genre."""
        video_file = SimpleUploadedFile(
            "test_video.mp4",
            b"fake video content",
            content_type="video/mp4"
        )
        
        data = {
            'title': 'Test Video',
            'description': 'Test Description',
            'genre': 'invalid_genre',
            'original_file': video_file
        }
        
        serializer = VideoUploadSerializer(data=data)
        assert not serializer.is_valid()
        assert 'genre' in serializer.errors
    
    def test_empty_title(self):
        """Test video upload with empty title."""
        video_file = SimpleUploadedFile(
            "test_video.mp4",
            b"fake video content",
            content_type="video/mp4"
        )
        
        data = {
            'title': '',
            'description': 'Test Description',
            'genre': 'action',
            'original_file': video_file
        }
        
        serializer = VideoUploadSerializer(data=data)
        assert not serializer.is_valid()
        assert 'title' in serializer.errors
    
    def test_empty_description(self):
        """Test video upload with empty description."""
        video_file = SimpleUploadedFile(
            "test_video.mp4",
            b"fake video content",
            content_type="video/mp4"
        )
        
        data = {
            'title': 'Test Video',
            'description': '',
            'genre': 'action',
            'original_file': video_file
        }
        
        serializer = VideoUploadSerializer(data=data)
        assert not serializer.is_valid()
        assert 'description' in serializer.errors
    
    def test_very_long_title(self):
        """Test video upload with very long title."""
        video_file = SimpleUploadedFile(
            "test_video.mp4",
            b"fake video content",
            content_type="video/mp4"
        )
        
        long_title = 'A' * 300
        
        data = {
            'title': long_title,
            'description': 'Test Description',
            'genre': 'action',
            'original_file': video_file
        }
        
        serializer = VideoUploadSerializer(data=data)
        assert not serializer.is_valid()
        assert 'title' in serializer.errors

@pytest.mark.django_db
class TestVideoListSerializer:
    """Test VideoListSerializer."""
    
    def test_video_serialization_basic(self):
        """Test basic video serialization."""
        video = Video.objects.create(
            title='Test Video',
            description='Test Description',
            genre='action'
        )
        
        serializer = VideoListSerializer(video)
        data = serializer.data
        
        expected_fields = {'id', 'created_at', 'title', 'description', 'thumbnail_url', 'category'}
        assert set(data.keys()) == expected_fields
        
        assert data['title'] == 'Test Video'
        assert data['description'] == 'Test Description'
        assert data['category'] == 'Action'
        assert data['id'] == video.id
        assert data['created_at'] is not None
    
    def test_thumbnail_url_with_no_thumbnail(self):
        """Test thumbnail URL when no thumbnail is set."""
        video = Video.objects.create(
            title='Test Video',
            description='Test Description',
            genre='action'
        )
        
        serializer = VideoListSerializer(video)
        data = serializer.data
        
        assert data['thumbnail_url'] is None
    
    @patch('content.api.serializers.logger')
    def test_thumbnail_url_with_missing_file(self, mock_logger):
        """Test thumbnail URL when thumbnail file is missing."""
        video = Video.objects.create(
            title='Test Video',
            description='Test Description',
            genre='action'
        )
        
        mock_thumbnail = Mock()
        mock_thumbnail.__bool__ = Mock(return_value=True)
        
        url_property = PropertyMock(side_effect=ValueError("File not found"))
        type(mock_thumbnail).url = url_property
        
        video.thumbnail = mock_thumbnail
        
        serializer = VideoListSerializer(video)
        data = serializer.data
        
        assert data['thumbnail_url'] is None
        mock_logger.debug.assert_called_once()
    
    def test_thumbnail_url_with_request_context(self):
        """Test thumbnail URL generation with request context."""
        video = Video.objects.create(
            title='Test Video',
            description='Test Description',
            genre='action'
        )
        
        mock_thumbnail = Mock()
        mock_thumbnail.__bool__ = Mock(return_value=True)
        mock_thumbnail.url = '/media/thumbnails/test.jpg'
        video.thumbnail = mock_thumbnail
        
        factory = RequestFactory()
        request = factory.get('/')
        
        serializer = VideoListSerializer(video, context={'request': request})
        data = serializer.data
        
        assert data['thumbnail_url'] is not None
        assert 'testserver' in data['thumbnail_url']
        assert '/media/thumbnails/test.jpg' in data['thumbnail_url']
    
    def test_thumbnail_url_without_request_context(self):
        """Test thumbnail URL generation without request context."""
        video = Video.objects.create(
            title='Test Video',
            description='Test Description',
            genre='action'
        )
        
        mock_thumbnail = Mock()
        mock_thumbnail.url = '/media/thumbnails/test.jpg'
        mock_thumbnail.__bool__ = lambda self: True
        video.thumbnail = mock_thumbnail
        
        serializer = VideoListSerializer(video)
        data = serializer.data
        
        assert data['thumbnail_url'] == '/media/thumbnails/test.jpg'
    
    def test_category_mapping(self):
        """Test category mapping for different genres."""
        genre_category_mapping = [
            ('action', 'Action'),
            ('comedy', 'Comedy'),
            ('drama', 'Drama'),
            ('sci_fi', 'Sci-Fi'),
            ('horror', 'Horror'),
            ('documentary', 'Documentary'),
            ('thriller', 'Thriller'),
            ('romance', 'Romance'),
            ('animation', 'Animation'),
            ('fantasy', 'Fantasy'),
        ]
        
        for genre, expected_category in genre_category_mapping:
            video = Video.objects.create(
                title=f'Test {genre} Video',
                description='Test Description',
                genre=genre
            )
            
            serializer = VideoListSerializer(video)
            data = serializer.data
            
            assert data['category'] == expected_category
            video.delete()
    
    def test_created_at_field_mapping(self):
        """Test that created_at maps to upload_date."""
        video = Video.objects.create(
            title='Test Video',
            description='Test Description',
            genre='action'
        )
        
        serializer = VideoListSerializer(video)
        data = serializer.data
        
        assert data['created_at'] == video.upload_date.isoformat().replace('+00:00', 'Z')
    
    def test_multiple_videos_serialization(self):
        """Test serializing multiple videos."""
        video1 = Video.objects.create(
            title='Video 1',
            description='Description 1',
            genre='action'
        )
        video2 = Video.objects.create(
            title='Video 2',
            description='Description 2',
            genre='comedy'
        )
        
        videos = [video1, video2]
        serializer = VideoListSerializer(videos, many=True)
        data = serializer.data
        
        assert len(data) == 2
        assert data[0]['title'] == 'Video 1'
        assert data[0]['category'] == 'Action'
        assert data[1]['title'] == 'Video 2'
        assert data[1]['category'] == 'Comedy'
    
    def test_unicode_handling(self):
        """Test handling of Unicode characters in title and description."""
        video = Video.objects.create(
            title='测试视频 🎬',
            description='这是一个测试描述 with émojis 🎭',
            genre='drama'
        )
        
        serializer = VideoListSerializer(video)
        data = serializer.data
        
        assert data['title'] == '测试视频 🎬'
        assert data['description'] == '这是一个测试描述 with émojis 🎭'
        assert data['category'] == 'Drama'
