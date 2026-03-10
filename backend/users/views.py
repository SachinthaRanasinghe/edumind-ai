"""
Views for user authentication and management.
"""
from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .models import User, Student, Teacher
from .serializers import (
    UserSerializer,
    StudentSerializer,
    TeacherSerializer,
    StudentRegistrationSerializer,
    TeacherRegistrationSerializer,
)


class StudentRegistrationView(generics.CreateAPIView):
    """Register a new student account."""
    
    permission_classes = [permissions.AllowAny]
    serializer_class = StudentRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        student = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(student.user)
        
        return Response({
            'message': 'Student registration successful',
            'student': StudentSerializer(student).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class TeacherRegistrationView(generics.CreateAPIView):
    """Register a new teacher account."""
    
    permission_classes = [permissions.AllowAny]
    serializer_class = TeacherRegistrationSerializer
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        teacher = serializer.save()
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(teacher.user)
        
        return Response({
            'message': 'Teacher registration successful',
            'teacher': TeacherSerializer(teacher).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        }, status=status.HTTP_201_CREATED)


class CurrentUserView(APIView):
    """Get current authenticated user's profile."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        user_data = UserSerializer(user).data
        
        # Add profile data based on user type
        if user.user_type == 'student':
            try:
                student = user.student_profile
                user_data['profile'] = StudentSerializer(student).data
            except Student.DoesNotExist:
                user_data['profile'] = None
        elif user.user_type == 'teacher':
            try:
                teacher = user.teacher_profile
                user_data['profile'] = TeacherSerializer(teacher).data
            except Teacher.DoesNotExist:
                user_data['profile'] = None
        
        return Response(user_data)


class UserProfileUpdateView(generics.UpdateAPIView):
    """Update current user's profile."""
    
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserSerializer
    
    def get_object(self):
        return self.request.user


class StudentProfileUpdateView(generics.UpdateAPIView):
    """Update student profile."""
    
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = StudentSerializer
    
    def get_object(self):
        return self.request.user.student_profile


class TeacherProfileUpdateView(generics.UpdateAPIView):
    """Update teacher profile."""
    
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = TeacherSerializer
    
    def get_object(self):
        return self.request.user.teacher_profile


class LogoutView(APIView):
    """Logout by blacklisting the refresh token."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if not refresh_token:
                return Response(
                    {'error': 'Refresh token is required'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            token = RefreshToken(refresh_token)
            token.blacklist()
            
            return Response({'message': 'Logout successful'}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response(
                {'error': 'Invalid token'},
                status=status.HTTP_400_BAD_REQUEST
            )
