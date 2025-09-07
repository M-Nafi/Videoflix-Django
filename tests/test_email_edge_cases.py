import pytest
from unittest.mock import patch, Mock, call
from django.urls import reverse
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework_simplejwt.tokens import RefreshToken
from user_auth_app.models import User
from user_auth_app.api.emails import send_verification_email, send_password_reset_email

@pytest.mark.django_db
class TestEmailFunctionality:
    """Test email sending functionality with mocks."""
    
    @patch('user_auth_app.api.emails.EmailMultiAlternatives')
    def test_send_verification_email(self, mock_email_class):
        """Test sending verification email."""
        mock_email_instance = Mock()
        mock_email_class.return_value = mock_email_instance
        
        email = 'test@test.com'
        uidb64 = 'test_uid'
        token = 'test_token'
        
        send_verification_email(email, uidb64, token)
        
        mock_email_class.assert_called_once()
        mock_email_instance.send.assert_called_once()
        
        call_args = mock_email_class.call_args
        assert email in call_args[1]['to']
        assert 'Confirm your email' in call_args[1]['subject']
    
    @patch('user_auth_app.api.emails.EmailMultiAlternatives')
    def test_send_password_reset_email(self, mock_email_class):
        """Test sending password reset email."""
        mock_email_instance = Mock()
        mock_email_class.return_value = mock_email_instance
        
        email = 'test@test.com'
        uidb64 = 'test_uid'
        token = 'test_token'
        
        send_password_reset_email(email, uidb64, token)
        
        mock_email_class.assert_called_once()
        mock_email_instance.send.assert_called_once()
        
        call_args = mock_email_class.call_args
        assert email in call_args[1]['to']
        assert 'Reset your password' in call_args[1]['subject']

    @patch('user_auth_app.api.emails.EmailMultiAlternatives')
    def test_email_sending_failure_handling(self, mock_email_class):
        """Test email sending failure handling."""
        mock_email_instance = Mock()
        mock_email_instance.send.side_effect = Exception("SMTP Error")
        mock_email_class.return_value = mock_email_instance
        
        email = 'test@test.com'
        uidb64 = 'test_uid'
        token = 'test_token'
        
        with pytest.raises(Exception):
            send_verification_email(email, uidb64, token)

    @patch('user_auth_app.api.emails.EmailMultiAlternatives')
    def test_email_content_validation(self, mock_email_class):
        """Test email content validation."""
        mock_email_instance = Mock()
        mock_email_class.return_value = mock_email_instance
        
        email = 'test@test.com'
        uidb64 = 'test_uid'
        token = 'test_token'
        
        send_verification_email(email, uidb64, token)
        
        call_args = mock_email_class.call_args
        body = call_args[1]['body']
        assert 'confirm your email' in body.lower()
        assert uidb64 in body
        assert token in body

    @patch('user_auth_app.api.emails.EmailMultiAlternatives')
    def test_password_reset_email_content(self, mock_email_class):
        """Test password reset email content."""
        mock_email_instance = Mock()
        mock_email_class.return_value = mock_email_instance
        
        email = 'test@test.com'
        uidb64 = 'test_uid'
        token = 'test_token'
        
        send_password_reset_email(email, uidb64, token)
        
        call_args = mock_email_class.call_args
        body = call_args[1]['body']
        assert 'password reset' in body.lower()
        assert uidb64 in body
        assert token in body

    @patch('user_auth_app.api.emails.EmailMultiAlternatives')
    def test_email_recipient_validation(self, mock_email_class):
        """Test email recipient validation."""
        mock_email_instance = Mock()
        mock_email_class.return_value = mock_email_instance
        
        email = 'valid@test.com'
        uidb64 = 'test_uid'
        token = 'test_token'
        
        send_verification_email(email, uidb64, token)
        
        call_args = mock_email_class.call_args
        assert call_args[1]['to'] == [email]

@pytest.mark.django_db
class TestAdditionalEdgeCases:
    """Test additional edge cases for models and functionality."""
    
    def test_video_model_string_representation_edge_cases(self):
        """Test video model with edge cases."""
        from content.models import Video
        
        long_title = 'A' * 200
        
        video = Video.objects.create(
            title=long_title,
            description='Test Description',
            genre='action'
        )
        
        assert video.title == long_title
        assert len(video.title) <= 255
        assert str(video) == long_title
    
    def test_genre_choices_completeness(self):
        """Test that all genre choices are properly handled."""
        from content.models import Video
        
        video = Video.objects.create(
            title='Sci-Fi Movie',
            description='A science fiction movie',
            genre='sci_fi'
        )
        
        assert video.genre == 'sci_fi'
        assert video.category == 'Sci-Fi'
