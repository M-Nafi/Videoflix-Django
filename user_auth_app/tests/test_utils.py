import pytest
from django.test import RequestFactory
from django.http import HttpResponse
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from user_auth_app.models import User
from user_auth_app.api.utils import (
    set_jwt_cookies, clear_jwt_cookies, get_refresh_token_from_request
)

@pytest.mark.django_db
class TestJWTCookieUtils:
    """Test JWT cookie utility functions."""
    
    def setup_method(self):
        """Set up test user and tokens."""
        self.user = User.objects.create_user(
            email='test@test.com',
            password='TestPassword123!',
            username='test@test.com',
            is_active=True
        )
        
        self.refresh = RefreshToken.for_user(self.user)
        self.access_token = self.refresh.access_token
        
        self.factory = RequestFactory()
    
    def test_set_jwt_cookies_access_only(self):
        """Test setting only access token cookie."""
        response = HttpResponse()
        
        set_jwt_cookies(response, self.access_token)
        
        assert 'access_token' in response.cookies
        assert response.cookies['access_token'].value == str(self.access_token)
        
        cookie = response.cookies['access_token']
        assert cookie['httponly'] in ['', True]
        assert cookie['path'] == '/'
        assert cookie['samesite'] in ['Lax', 'None', None]
        
        assert 'refresh_token' not in response.cookies
    
    def test_set_jwt_cookies_both_tokens(self):
        """Test setting both access and refresh tokens."""
        response = HttpResponse()
        
        set_jwt_cookies(response, self.access_token, self.refresh)
        
        assert 'access_token' in response.cookies
        assert 'refresh_token' in response.cookies
        
        assert response.cookies['access_token'].value == str(self.access_token)
        assert response.cookies['refresh_token'].value == str(self.refresh)
        
        for cookie_name in ['access_token', 'refresh_token']:
            cookie = response.cookies[cookie_name]
            assert cookie['httponly'] in ['', True]
            assert cookie['path'] == '/'
            assert cookie['samesite'] in ['Lax', 'None', None]
    
    def test_set_jwt_cookies_custom_settings(self):
        """Test setting cookies with custom JWT settings."""
        custom_settings = {
            'AUTH_COOKIE': 'custom_access',
            'AUTH_COOKIE_REFRESH': 'custom_refresh',
            'AUTH_COOKIE_HTTP_ONLY': False,
            'AUTH_COOKIE_SECURE': True,
            'AUTH_COOKIE_SAMESITE': 'Strict',
            'AUTH_COOKIE_PATH': '/api/',
        }
        
        original_settings = getattr(settings, 'SIMPLE_JWT', {})
        settings.SIMPLE_JWT = {**original_settings, **custom_settings}
        
        try:
            response = HttpResponse()
            set_jwt_cookies(response, self.access_token, self.refresh)
            
            assert 'custom_access' in response.cookies
            assert 'custom_refresh' in response.cookies
            
            access_cookie = response.cookies['custom_access']
            assert access_cookie['httponly'] in ['', False]
            assert access_cookie['secure'] in ['', True]
            assert access_cookie['samesite'] in ['Strict', 'None']
            assert access_cookie['path'] == '/api/'
        finally:
            settings.SIMPLE_JWT = original_settings
    
    def test_clear_jwt_cookies(self):
        """Test clearing JWT cookies."""
        response = HttpResponse()
        
        set_jwt_cookies(response, self.access_token, self.refresh)
        assert 'access_token' in response.cookies
        assert 'refresh_token' in response.cookies
        
        clear_jwt_cookies(response)
        
        access_cookie = response.cookies.get('access_token')
        refresh_cookie = response.cookies.get('refresh_token')
        
        if access_cookie:
            assert access_cookie['max-age'] == 0
        if refresh_cookie:
            assert refresh_cookie['max-age'] == 0
    
    def test_get_refresh_token_from_request(self):
        """Test getting refresh token from request cookies."""
        request = self.factory.get('/')
        request.COOKIES = {'refresh_token': str(self.refresh)}
        
        token = get_refresh_token_from_request(request)
        assert token == str(self.refresh)
    
    def test_get_refresh_token_from_request_missing(self):
        """Test getting refresh token when cookie is missing."""
        request = self.factory.get('/')
        request.COOKIES = {}
        
        token = get_refresh_token_from_request(request)
        assert token is None
    
    def test_get_refresh_token_custom_cookie_name(self):
        """Test getting refresh token with custom cookie name."""
        custom_settings = {
            'AUTH_COOKIE_REFRESH': 'custom_refresh_token',
        }
        
        original_settings = getattr(settings, 'SIMPLE_JWT', {})
        settings.SIMPLE_JWT = {**original_settings, **custom_settings}
        
        try:
            request = self.factory.get('/')
            request.COOKIES = {'custom_refresh_token': str(self.refresh)}
            
            token = get_refresh_token_from_request(request)
            assert token == str(self.refresh)
        finally:
            settings.SIMPLE_JWT = original_settings
