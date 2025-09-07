from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from user_auth_app.views import redirect_to_admin
from user_auth_app.api.views import (
    RegisterView, ActivateView, LoginView, LogoutView,
    TokenRefreshView, PasswordResetView, PasswordConfirmView
)
import user_auth_app.api.urls as api_urls

urlpatterns = [
        
    path('', redirect_to_admin, name='root'),
    path('api/', redirect_to_admin, name='root'),
    path('admin/', admin.site.urls),
    path('django-rq/', include('django_rq.urls')),
    
    # Custom Auth Endpoints (matching specification)
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/activate/<uidb64>/<token>/', ActivateView.as_view(), name='activate'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/logout/', LogoutView.as_view(), name='logout'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/password_reset/', PasswordResetView.as_view(), name='password_reset'),
    path('api/password_confirm/<uidb64>/<token>/', PasswordConfirmView.as_view(), name='password_confirm'),
    path('api/', include('content.api.urls')),
   
    
    # User-Profil
    path('api/', include(api_urls)),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
