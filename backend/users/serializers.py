"""
Serializers for user-related models.
"""
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Student, Teacher


class UserSerializer(serializers.ModelSerializer):
    """Serializer for the User model."""
    
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'email', 'user_type', 'first_name', 'last_name',
            'full_name', 'profile_picture', 'is_active', 'is_verified',
            'date_joined', 'last_login'
        ]
        read_only_fields = ['id', 'date_joined', 'last_login']
    
    def get_full_name(self, obj):
        return obj.get_full_name()


class StudentSerializer(serializers.ModelSerializer):
    """Serializer for the Student model."""
    
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Student
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class TeacherSerializer(serializers.ModelSerializer):
    """Serializer for the Teacher model."""
    
    user = UserSerializer(read_only=True)
    
    class Meta:
        model = Teacher
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration."""
    
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True, required=True)
    
    class Meta:
        model = User
        fields = [
            'email', 'password', 'password_confirm', 'user_type',
            'first_name', 'last_name'
        ]
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user


class StudentRegistrationSerializer(serializers.Serializer):
    """Serializer for student registration with profile."""
    
    # User fields
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    
    # Student fields
    student_id = serializers.CharField(max_length=50)
    grade_level = serializers.IntegerField(required=False)
    date_of_birth = serializers.DateField(required=False)
    parent_email = serializers.EmailField(required=False)
    learning_style = serializers.ChoiceField(choices=Student.LEARNING_STYLE_CHOICES, required=False)
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        # Extract student-specific fields
        student_data = {
            'student_id': validated_data.pop('student_id'),
            'grade_level': validated_data.pop('grade_level', None),
            'date_of_birth': validated_data.pop('date_of_birth', None),
            'parent_email': validated_data.pop('parent_email', None),
            'learning_style': validated_data.pop('learning_style', None),
        }
        
        # Remove password_confirm
        validated_data.pop('password_confirm')
        
        # Create user
        user = User.objects.create_user(
            user_type='student',
            **validated_data
        )
        
        # Create student profile
        student = Student.objects.create(user=user, **student_data)
        
        return student


class TeacherRegistrationSerializer(serializers.Serializer):
    """Serializer for teacher registration with profile."""
    
    # User fields
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    first_name = serializers.CharField(max_length=100)
    last_name = serializers.CharField(max_length=100)
    
    # Teacher fields
    employee_id = serializers.CharField(max_length=50)
    department = serializers.CharField(max_length=100, required=False)
    specialization = serializers.ListField(child=serializers.CharField(), required=False)
    hire_date = serializers.DateField(required=False)
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        # Extract teacher-specific fields
        teacher_data = {
            'employee_id': validated_data.pop('employee_id'),
            'department': validated_data.pop('department', None),
            'specialization': validated_data.pop('specialization', []),
            'hire_date': validated_data.pop('hire_date', None),
        }
        
        # Remove password_confirm
        validated_data.pop('password_confirm')
        
        # Create user
        user = User.objects.create_user(
            user_type='teacher',
            **validated_data
        )
        
        # Create teacher profile
        teacher = Teacher.objects.create(user=user, **teacher_data)
        
        return teacher
