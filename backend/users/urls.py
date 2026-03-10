"""
URL routing for users app.
"""
from django.urls import path
from .views import (
    StudentRegistrationView,
    TeacherRegistrationView,
    CurrentUserView,
    UserProfileUpdateView,
    StudentProfileUpdateView,
    TeacherProfileUpdateView,
    LogoutView,
)

app_name = 'users'

urlpatterns = [
    # Registration
    path('register/student/', StudentRegistrationView.as_view(), name='student-register'),
    path('register/teacher/', TeacherRegistrationView.as_view(), name='teacher-register'),
    
    # Profile
    path('me/', CurrentUserView.as_view(), name='current-user'),
    path('profile/update/', UserProfileUpdateView.as_view(), name='profile-update'),
    path('profile/student/update/', StudentProfileUpdateView.as_view(), name='student-profile-update'),
    path('profile/teacher/update/', TeacherProfileUpdateView.as_view(), name='teacher-profile-update'),
    
    # Logout
    path('logout/', LogoutView.as_view(), name='logout'),
]
