import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.exceptions import ValidationError
from user_auth_app.api.serializers import (
    UserCreateSerializer, LoginSerializer, 
    PasswordResetSerializer, PasswordChangeSerializer
)
from user_auth_app.models import User

@pytest.mark.django_db
class TestUserCreateSerializer:
    """Test UserCreateSerializer validation and creation."""
    
    def test_valid_user_creation(self):
        """Test creating user with valid data."""
        data = {
            'email': 'test@test.com',
            'password': 'TestPassword123!',
            'confirmed_password': 'TestPassword123!'
        }
        
        serializer = UserCreateSerializer(data=data)
        assert serializer.is_valid()
        
        user = serializer.save()
        assert user.email == 'test@test.com'
        assert user.username == 'test@test.com'
        assert user.is_active is False
        assert user.check_password('TestPassword123!')
    
    def test_passwords_do_not_match(self):
        """Test validation when passwords don't match."""
        data = {
            'email': 'test@test.com',
            'password': 'TestPassword123!',
            'confirmed_password': 'DifferentPassword123!'
        }
        
        serializer = UserCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'non_field_errors' in serializer.errors
        assert 'Passwords do not match' in str(serializer.errors)
    
    def test_email_already_exists(self):
        """Test validation when email already exists."""
        User.objects.create_user(
            email='existing@test.com',
            password='Password123!'
        )
        
        data = {
            'email': 'existing@test.com',
            'password': 'TestPassword123!',
            'confirmed_password': 'TestPassword123!'
        }
        
        serializer = UserCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors
        error_text = str(serializer.errors['email'][0])
        assert 'already exists' in error_text.lower()
    
    def test_invalid_email_format(self):
        """Test validation with invalid email format."""
        data = {
            'email': 'invalid-email',
            'password': 'TestPassword123!',
            'confirmed_password': 'TestPassword123!'
        }
        
        serializer = UserCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors
    
    def test_weak_password(self):
        """Test validation with weak password."""
        data = {
            'email': 'test@test.com',
            'password': '123',
            'confirmed_password': '123'
        }
        
        serializer = UserCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'password' in serializer.errors
    
    def test_missing_required_fields(self):
        """Test validation with missing required fields."""
        data = {
            'email': 'test@test.com'
        }
        
        serializer = UserCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'password' in serializer.errors
        assert 'confirmed_password' in serializer.errors
    
    def test_empty_email(self):
        """Test validation with empty email."""
        data = {
            'email': '',
            'password': 'TestPassword123!',
            'confirmed_password': 'TestPassword123!'
        }
        
        serializer = UserCreateSerializer(data=data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors

@pytest.mark.django_db
class TestLoginSerializer:
    """Test LoginSerializer validation."""
    
    def test_valid_login(self):
        """Test login with valid credentials."""
        user = User.objects.create_user(
            email='test@test.com',
            password='TestPassword123!',
            is_active=True
        )
        
        data = {
            'email': 'test@test.com',
            'password': 'TestPassword123!'
        }
        
        serializer = LoginSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['user'] == user
    
    def test_invalid_credentials(self):
        """Test login with invalid credentials."""
        User.objects.create_user(
            email='test@test.com',
            password='TestPassword123!',
            is_active=True
        )
        
        data = {
            'email': 'test@test.com',
            'password': 'WrongPassword123!'
        }
        
        serializer = LoginSerializer(data=data)
        assert not serializer.is_valid()
        assert 'non_field_errors' in serializer.errors
        assert 'invalid' in str(serializer.errors['non_field_errors'][0]).lower()
    
    def test_nonexistent_user(self):
        """Test login with non-existent user."""
        data = {
            'email': 'nonexistent@test.com',
            'password': 'TestPassword123!'
        }
        
        serializer = LoginSerializer(data=data)
        assert not serializer.is_valid()
        assert 'non_field_errors' in serializer.errors
        assert 'invalid' in str(serializer.errors['non_field_errors'][0]).lower()
    
    def test_inactive_user(self):
        """Test login with inactive user."""
        User.objects.create_user(
            email='test@test.com',
            password='TestPassword123!',
            is_active=False
        )
        
        data = {
            'email': 'test@test.com',
            'password': 'TestPassword123!'
        }
        
        serializer = LoginSerializer(data=data)
        assert not serializer.is_valid()
        assert 'non_field_errors' in serializer.errors
        error_text = str(serializer.errors['non_field_errors'][0])
        assert 'invalid' in error_text.lower()
    
    def test_missing_email(self):
        """Test login without email."""
        data = {
            'password': 'TestPassword123!'
        }
        
        serializer = LoginSerializer(data=data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors
        assert 'required' in str(serializer.errors['email'][0]).lower()
    
    def test_missing_password(self):
        """Test login without password."""
        data = {
            'email': 'test@test.com'
        }
        
        serializer = LoginSerializer(data=data)
        assert not serializer.is_valid()
        assert 'password' in serializer.errors
        assert 'required' in str(serializer.errors['password'][0]).lower()
    
    def test_invalid_email_format(self):
        """Test login with invalid email format."""
        data = {
            'email': 'invalid-email',
            'password': 'TestPassword123!'
        }
        
        serializer = LoginSerializer(data=data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors
    
    def test_empty_credentials(self):
        """Test login with empty credentials."""
        data = {
            'email': '',
            'password': ''
        }
        
        serializer = LoginSerializer(data=data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors
        assert 'password' in serializer.errors

@pytest.mark.django_db
class TestPasswordResetSerializer:
    """Test PasswordResetSerializer validation."""
    
    def test_valid_password_reset(self):
        """Test password reset with valid email."""
        data = {
            'email': 'test@test.com'
        }
        
        serializer = PasswordResetSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['email'] == 'test@test.com'
    
    def test_invalid_email_format(self):
        """Test password reset with invalid email format."""
        data = {
            'email': 'invalid-email'
        }
        
        serializer = PasswordResetSerializer(data=data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors
    
    def test_missing_email(self):
        """Test password reset without email."""
        data = {}
        
        serializer = PasswordResetSerializer(data=data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors
    
    def test_empty_email(self):
        """Test password reset with empty email."""
        data = {
            'email': ''
        }
        
        serializer = PasswordResetSerializer(data=data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors

class TestPasswordChangeSerializer:
    """Test PasswordChangeSerializer validation."""
    
    def test_valid_password_change(self):
        """Test password change with valid data."""
        data = {
            'new_password': 'NewPassword123!',
            'confirm_password': 'NewPassword123!'
        }
        
        serializer = PasswordChangeSerializer(data=data)
        assert serializer.is_valid()
        assert serializer.validated_data['new_password'] == 'NewPassword123!'
    
    def test_passwords_do_not_match(self):
        """Test password change when passwords don't match."""
        data = {
            'new_password': 'NewPassword123!',
            'confirm_password': 'DifferentPassword123!'
        }
        
        serializer = PasswordChangeSerializer(data=data)
        assert not serializer.is_valid()
        assert 'non_field_errors' in serializer.errors
        assert 'Passwords do not match' in str(serializer.errors)
    
    def test_weak_new_password(self):
        """Test password change with weak password."""
        data = {
            'new_password': '123',
            'confirm_password': '123'
        }
        
        serializer = PasswordChangeSerializer(data=data)
        assert not serializer.is_valid()
        assert 'new_password' in serializer.errors
    
    def test_missing_new_password(self):
        """Test password change without new password."""
        data = {
            'confirm_password': 'NewPassword123!'
        }
        
        serializer = PasswordChangeSerializer(data=data)
        assert not serializer.is_valid()
        assert 'new_password' in serializer.errors
    
    def test_missing_confirm_password(self):
        """Test password change without confirm password."""
        data = {
            'new_password': 'NewPassword123!'
        }
        
        serializer = PasswordChangeSerializer(data=data)
        assert not serializer.is_valid()
        assert 'confirm_password' in serializer.errors
    
    def test_empty_passwords(self):
        """Test password change with empty passwords."""
        data = {
            'new_password': '',
            'confirm_password': ''
        }
        
        serializer = PasswordChangeSerializer(data=data)
        assert not serializer.is_valid()
        assert 'new_password' in serializer.errors
        assert 'confirm_password' in serializer.errors
