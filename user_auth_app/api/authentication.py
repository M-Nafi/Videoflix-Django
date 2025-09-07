from rest_framework_simplejwt.authentication import JWTAuthentication
from django.conf import settings

class CookieJWTAuthentication(JWTAuthentication):
    """
    JWT Authentication with cookie support.
    """
    
    def authenticate(self, request):
        """
        Authenticate a request using either a JWT in the Authorization header
        or in a cookie. Cookie name is read centrally from SIMPLE_JWT settings.
        """
        
        header = self.get_header(request)
        if header is None:
            jwt_settings = settings.SIMPLE_JWT
            cookie_name = jwt_settings.get('AUTH_COOKIE', 'access_token')
            raw_token = request.COOKIES.get(cookie_name)
            
            if raw_token is None:
                return None
                
            validated_token = self.get_validated_token(raw_token)
            return self.get_user(validated_token), validated_token
            
        return super().authenticate(request)
