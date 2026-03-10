"""
Custom permissions for learning app.
"""
from rest_framework import permissions


class IsTeacherOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow teachers to create/edit courses.
    Students can only read.
    """
    
    def has_permission(self, request, view):
        # Read permissions are allowed to any authenticated user
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Write permissions only for teachers
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.user_type == 'teacher'
        )


class IsEnrolledStudent(permissions.BasePermission):
    """
    Permission to check if student is enrolled in the course.
    """
    
    def has_object_permission(self, request, view, obj):
        if request.user.user_type == 'teacher':
            return True
        
        if request.user.user_type == 'student':
            # Check if student is enrolled in the course
            if hasattr(obj, 'course'):
                return obj.course.enrolled_students.filter(id=request.user.id).exists()
            return obj.enrolled_students.filter(id=request.user.id).exists()
        
        return False


class IsCourseTeacher(permissions.BasePermission):
    """
    Permission to check if user is the teacher of the course.
    """
    
    def has_object_permission(self, request, view, obj):
        if request.user.user_type != 'teacher':
            return False
        
        if hasattr(obj, 'course'):
            return obj.course.teacher.user == request.user
        return obj.teacher.user == request.user
