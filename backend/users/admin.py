"""
Admin configuration for users app.
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Student, Teacher


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom admin for User model."""
    
    list_display = ['email', 'first_name', 'last_name', 'user_type', 'is_active', 'date_joined']
    list_filter = ['user_type', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['email', 'first_name', 'last_name']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'profile_picture', 'user_type')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_verified')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'user_type'),
        }),
    )


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Admin for Student model."""
    
    list_display = ['student_id', 'user', 'grade_level', 'current_gpa', 'enrollment_date']
    list_filter = ['grade_level', 'learning_style', 'enrollment_date']
    search_fields = ['student_id', 'user__email', 'user__first_name', 'user__last_name']
    raw_id_fields = ['user']


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    """Admin for Teacher model."""
    
    list_display = ['employee_id', 'user', 'department', 'hire_date']
    list_filter = ['department', 'hire_date']
    search_fields = ['employee_id', 'user__email', 'user__first_name', 'user__last_name']
    raw_id_fields = ['user']
