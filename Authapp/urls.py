from django.urls import path
from .views import (
    RegistrationView, LoginView, GoogleLogin,
    AdminLoginView, AdminForgotPasswordView, AdminVerifyOTPView, AdminResetPasswordView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('google/', GoogleLogin.as_view(), name='google_login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Admin Auth Endpoints
    path('admin/login/', AdminLoginView.as_view(), name='admin_login'),
    path('admin/forgot-password/', AdminForgotPasswordView.as_view(), name='admin_forgot_password'),
    path('admin/verify-otp/', AdminVerifyOTPView.as_view(), name='admin_verify_otp'),
    path('admin/reset-password/', AdminResetPasswordView.as_view(), name='admin_reset_password'),
]
