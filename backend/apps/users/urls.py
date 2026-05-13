from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView,
    LoginView,
    LogoutView,
    ProfileView,
    SkinProfileView,
    ChangePasswordView,
    DeleteAccountView
)

urlpatterns = [
    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Profile
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/skin/', SkinProfileView.as_view(), name='skin_profile'),
    path('profile/password/', ChangePasswordView.as_view(), name='change_password'),
    path('profile/delete/', DeleteAccountView.as_view(), name='delete_account'),
]
