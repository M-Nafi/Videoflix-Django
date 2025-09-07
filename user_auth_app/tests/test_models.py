import pytest
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()

@pytest.mark.django_db
def test_create_user():
    """Test creating a regular user with username."""
    user = User.objects.create_user(
        email='test@test.com',
        password='TestPassword123!',
        username='test@test.com'
    )
    assert user.email == 'test@test.com'
    assert user.username == 'test@test.com'
    assert user.is_active is False
    assert user.is_staff is False
    assert user.is_superuser is False
    assert user.check_password('TestPassword123!')

@pytest.mark.django_db
def test_create_user_without_username():
    """Test creating a regular user without username (should be allowed)."""
    user = User.objects.create_user(
        email='test2@test.com',
        password='TestPassword123!'
    )
    assert user.email == 'test2@test.com'
    assert user.username is None
    assert user.is_active is False
    assert user.is_staff is False
    assert user.is_superuser is False
    assert user.check_password('TestPassword123!')

@pytest.mark.django_db
def test_create_superuser():
    """Test creating a superuser."""
    user = User.objects.create_superuser(
        email='admin@test.com',
        password='AdminPassword123!'
    )
    assert user.email == 'admin@test.com'
    assert user.is_active is True
    assert user.is_staff is True
    assert user.is_superuser is True
    assert user.check_password('AdminPassword123!')

@pytest.mark.django_db
def test_user_str_representation():
    """Test user string representation."""
    user = User.objects.create_user(
        email='test@test.com',
        password='TestPassword123!'
    )
    assert str(user) == 'test@test.com'

@pytest.mark.django_db
def test_create_user_without_email():
    """Test creating user without email raises error."""
    with pytest.raises(ValueError):
        User.objects.create_user(
            email='',
            password='TestPassword123!'
        )

@pytest.mark.django_db
def test_create_superuser_without_staff():
    """Test creating superuser without is_staff raises error."""
    with pytest.raises(ValueError):
        User.objects.create_superuser(
            email='admin@test.com',
            password='AdminPassword123!',
            is_staff=False
        )

@pytest.mark.django_db
def test_create_superuser_without_superuser():
    """Test creating superuser without is_superuser raises error."""
    with pytest.raises(ValueError):
        User.objects.create_superuser(
            email='admin@test.com',
            password='AdminPassword123!',
            is_superuser=False
        )

@pytest.mark.django_db
def test_email_normalization():
    """Test email normalization."""
    user = User.objects.create_user(
        email='Test@Example.COM',
        password='TestPassword123!'
    )
    assert user.email == 'Test@example.com'
