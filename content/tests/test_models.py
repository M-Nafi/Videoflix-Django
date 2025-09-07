import pytest
from content.models import Video

@pytest.mark.django_db
def test_create_video():
    """Test creating a video."""
    video = Video.objects.create(
        title='Test Video',
        description='Test Description',
        genre='action'
    )
    assert video.title == 'Test Video'
    assert video.description == 'Test Description'
    assert video.genre == 'action'
    assert video.upload_date is not None

@pytest.mark.django_db
def test_video_str_representation():
    """Test video string representation."""
    video = Video.objects.create(
        title='Test Video',
        description='Test Description',
        genre='action'
    )
    assert str(video) == 'Test Video'

@pytest.mark.django_db
def test_video_category_property():
    """Test video category property maps genre correctly."""
    test_cases = [
        ('action', 'Action'),
        ('comedy', 'Comedy'),
        ('drama', 'Drama'),
        ('sci_fi', 'Sci-Fi'),
        ('horror', 'Horror')
    ]
    
    for genre, expected_category in test_cases:
        video = Video.objects.create(
            title=f'{genre.title()} Video',
            description=f'Test {genre} video',
            genre=genre
        )
        assert video.category == expected_category

@pytest.mark.django_db
def test_video_genre_choices():
    """Test video genre choices validation."""
    valid_genres = [
        'action', 'comedy', 'drama', 'documentary', 'horror',
        'sci_fi', 'thriller', 'romance', 'animation', 'fantasy'
    ]
    
    for genre in valid_genres:
        video = Video.objects.create(
            title=f'Test {genre} Video',
            description=f'Test {genre} description',
            genre=genre
        )
        assert video.genre == genre

@pytest.mark.django_db
def test_video_fields_optional():
    """Test that optional fields can be None/blank."""
    video = Video.objects.create(
        title='Minimal Video',
        description='Minimal Description',
        genre='action'
    )
    assert not video.thumbnail or video.thumbnail.name == ''
    assert not video.video_480p or video.video_480p.name == ''
    assert not video.video_720p or video.video_720p.name == ''
    assert not video.video_1080p or video.video_1080p.name == ''
