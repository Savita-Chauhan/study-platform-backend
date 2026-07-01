# backend/users/views.py

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .serializers import RegisterSerializer, UserProfileSerializer
from .models import CustomUser


class RegisterView(APIView):
    """
    POST /api/users/register/
    Naya user banata hai
    """
    permission_classes = [AllowAny]  # Bina login ke access ho

    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()

            # Register hote hi JWT token bhi do
            refresh = RefreshToken.for_user(user)

            return Response({
                'message': 'Account created successfully!',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                },
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                }
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """
    POST /api/users/login/
    Login karke JWT token deta hai
    """
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        # Username aur password check karo
        user = authenticate(username=username, password=password)

        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Login successful!',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'role': user.role,
                },
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                }
            }, status=status.HTTP_200_OK)

        return Response({
            'error': 'Invalid username or password!'
        }, status=status.HTTP_401_UNAUTHORIZED)


class LogoutView(APIView):
    """
    POST /api/users/logout/
    Refresh token blacklist karta hai
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            refresh_token = request.data.get('refresh')
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response({
                'message': 'Logged out successfully!'
            }, status=status.HTTP_200_OK)
        except Exception:
            return Response({
                'error': 'Something went wrong!'
            }, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(APIView):
    """
    GET  /api/users/profile/ — profile dekho
    PUT  /api/users/profile/ — profile update karo
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserProfileSerializer(
            request.user,
            data=request.data,
            partial=True  # Sirf jo fields bhejo wahi update ho
        )
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Profile updated!',
                'user': serializer.data
            })
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)