from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from django.core.mail import send_mail
from django.conf import settings
import uuid

from .models import User
from .serializers import (
    UserSerializer, LoginSerializer, RegisterSerializer, 
    ForgotPasswordSerializer, ResetPasswordSerializer
)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        
        # Login the user
        login(request, user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'access': token.key,
                'refresh': token.key  # In a real app, you'd use JWT refresh tokens
            }
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        
        # Login the user after registration
        login(request, user)
        
        return Response({
            'user': UserSerializer(user).data,
            'tokens': {
                'access': token.key,
                'refresh': token.key
            },
            'requiresEmailVerification': not user.email_verified
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def logout_view(request):
    # For logout, we don't need authentication since we're just clearing the session
    logout(request)
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([AllowAny])
def refresh_token_view(request):
    # In a real implementation, you'd validate the refresh token
    # For now, we'll just return a new token
    if request.user.is_authenticated:
        token, created = Token.objects.get_or_create(user=request.user)
        return Response({
            'access': token.key
        })
    
    return Response({'error': 'Invalid refresh token'}, status=status.HTTP_401_UNAUTHORIZED)


@api_view(['POST'])
@permission_classes([AllowAny])
def forgot_password_view(request):
    serializer = ForgotPasswordSerializer(data=request.data)
    if serializer.is_valid():
        email = serializer.validated_data['email']
        try:
            user = User.objects.get(email=email)
            # In a real app, you'd generate a secure token and send an email
            # For now, we'll just return success
            return Response(status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            # Don't reveal if email exists or not
            return Response(status=status.HTTP_204_NO_CONTENT)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def reset_password_view(request):
    serializer = ResetPasswordSerializer(data=request.data)
    if serializer.is_valid():
        # In a real app, you'd validate the token and reset the password
        # For now, we'll just return success
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile_view(request):
    serializer = UserSerializer(request.user)
    return Response(serializer.data)