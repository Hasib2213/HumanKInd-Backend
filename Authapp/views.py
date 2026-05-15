from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import (
    UserRegistrationSerializer, UserLoginSerializer, 
    AdminLoginSerializer, AdminForgotPasswordSerializer, 
    AdminVerifyOTPSerializer, AdminResetPasswordSerializer
)
from .models import User, AdminOTP
import random
import string

# Google Login imports
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView

class RegistrationView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer

class LoginView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = UserLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data.get('email')
        password = serializer.validated_data.get('password')
        user = authenticate(email=email, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                }
            })
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = "http://localhost:3000/auth/callback" # Update this with your frontend callback URL
    client_class = OAuth2Client

class AdminLoginView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = AdminLoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
            }
        })

class AdminForgotPasswordView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = AdminForgotPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)
        
        # Generate 6-digit OTP
        otp_code = ''.join(random.choices(string.digits, k=6))
        AdminOTP.objects.create(user=user, otp_code=otp_code)
        
        # In a real app, send email here. For now, we'll return it in the response for testing.
        print(f"OTP for {email}: {otp_code}")
        
        return Response({"message": "OTP sent to your email.", "otp_test": otp_code}, status=status.HTTP_200_OK)

class AdminVerifyOTPView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = AdminVerifyOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        otp_code = serializer.validated_data['otp_code']
        
        otp_obj = AdminOTP.objects.filter(user__email=email, otp_code=otp_code, is_used=False).last()
        
        if not otp_obj or otp_obj.is_expired():
            return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)
        
        return Response({"message": "OTP verified successfully."}, status=status.HTTP_200_OK)

class AdminResetPasswordView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = AdminResetPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        otp_code = serializer.validated_data['otp_code']
        new_password = serializer.validated_data['new_password']
        
        otp_obj = AdminOTP.objects.filter(user__email=email, otp_code=otp_code, is_used=False).last()
        
        if not otp_obj or otp_obj.is_expired():
            return Response({"error": "Invalid or expired OTP."}, status=status.HTTP_400_BAD_REQUEST)
        
        user = otp_obj.user
        user.set_password(new_password)
        user.save()
        
        otp_obj.is_used = True
        otp_obj.save()
        
        return Response({"message": "Password reset successfully."}, status=status.HTTP_200_OK)
