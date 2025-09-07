from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_bytes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, status
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken, AccessToken, TokenError
from core import settings
from .serializers import (
    UserSerializer, UserCreateSerializer, 
    LoginSerializer, PasswordResetSerializer, PasswordChangeSerializer
)
from .emails import send_verification_email, send_password_reset_email
from .utils import set_jwt_cookies, clear_jwt_cookies, get_refresh_token_from_request

User = get_user_model()


class UserProfileViewSet(viewsets.ModelViewSet):
    """Retrieve and update the authenticated user's profile."""
    
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_queryset(self):
        return User.objects.filter(id=self.request.user.id)


class RegisterView(APIView):
    """Handle user registration and send activation email."""
    
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            refresh = RefreshToken.for_user(user)
            activation_token = str(refresh.access_token)
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            
            send_verification_email(user.email, uidb64, activation_token)
            
            return Response({
                "user": {
                    "id": user.id,
                    "email": user.email
                },
                "token": activation_token
            }, status=status.HTTP_201_CREATED)
        
        return Response(
            {"detail": "Please check your entries and try again."},
            status=status.HTTP_400_BAD_REQUEST
        )


class ActivateView(APIView):
    """Activate user account using token from email."""
    
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
            access_token = AccessToken(token)

            if str(user.pk) != str(access_token['user_id']):
                raise Exception

            if not user.is_active:
                user.is_active = True
                user.save()
                return Response(
                    {"message": "Account successfully activated."},
                    status=status.HTTP_200_OK
                )
            
            return Response(
                {"message": "Account successfully activated."},
                status=status.HTTP_200_OK
            )
            
        except Exception:
            return Response(
                {"message": "Account activation failed."},
                status=status.HTTP_400_BAD_REQUEST
            )
    
class LoginView(APIView):
    """Handle user login and set JWT tokens in cookies."""
    
    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"detail": "Please check your entries and try again."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        access_token = refresh.access_token
        
        response = Response({
            "detail": "Login successful",
            "user": {
                "id": user.id,
                "username": user.email
            }
        }, status=status.HTTP_200_OK)
        
        set_jwt_cookies(response, access_token, refresh)
        
        return response
        
class TokenRefreshView(APIView):
    """Refresh JWT access token using refresh token from cookies."""
    
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = get_refresh_token_from_request(request)
        
        if not refresh_token:
            return Response(
                {"detail": "Refresh token not found"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            refresh = RefreshToken(refresh_token)
            new_access_token = refresh.access_token
        except TokenError:
            return Response(
                {"detail": "Invalid refresh token"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        response = Response({
            "detail": "Token refreshed",
            "access": str(new_access_token)
        }, status=status.HTTP_200_OK)
        
        set_jwt_cookies(response, new_access_token)
        
        return response
                
class LogoutView(APIView):
    """Log out user by clearing JWT cookies and blacklisting refresh token."""
    
    permission_classes = [AllowAny]

    def post(self, request):
        refresh_token = get_refresh_token_from_request(request)
        
        if not refresh_token:
            return Response(
                {"detail": "Refresh token not found"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            RefreshToken(refresh_token).blacklist()
        except Exception:
            pass
        
        response = Response({
            "detail": "Log-Out successfully!"
        }, status=status.HTTP_200_OK)
        
        clear_jwt_cookies(response)
        
        return response

class PasswordResetView(APIView):
    """Handle password reset requests by sending email with reset link."""
    
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                user = User.objects.get(email=email)
                
                refresh = RefreshToken.for_user(user)
                token = str(refresh.access_token)
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                
                send_password_reset_email(user.email, uidb64, token)
                
            except User.DoesNotExist:
                pass
            
            return Response(
                {"detail": "An email has been sent to reset your password."},
                status=status.HTTP_200_OK
            )
        
        return Response(
            {"detail": "Invalid email address"},
            status=status.HTTP_400_BAD_REQUEST
        )


class PasswordConfirmView(APIView):
    """Handle password reset confirmation and update user password."""
    
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        serializer = PasswordChangeSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(
                {"detail": "Passwords do not match"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
            access_token = AccessToken(token)
            
            if str(user.pk) != str(access_token['user_id']):
                raise Exception
                
        except Exception:
            return Response(
                {"detail": "Invalid token or user"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        return Response(
            {"detail": "Your password has been successfully reset."},
            status=status.HTTP_200_OK
        )
