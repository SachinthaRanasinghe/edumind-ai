"""
Serializers for learning app.
"""
from rest_framework import serializers
from .models import (
    Course,
    CourseEnrollment,
    Topic,
    Assessment,
    Question,
    Submission,
    SubmissionAnswer,
    StudentSkillProfile,
)


class CourseSerializer(serializers.ModelSerializer):
    """Serializer for Course model."""
    teacher_name = serializers.CharField(source='teacher.user.get_full_name', read_only=True)
    enrolled_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Course
        fields = [
            'id', 'course_code', 'title', 'description', 'subject',
            'grade_level', 'teacher', 'teacher_name', 'is_active',
            'start_date', 'end_date', 'created_at', 'enrolled_count'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_enrolled_count(self, obj):
        return obj.enrollments.filter(status='active').count()


class TopicSerializer(serializers.ModelSerializer):
    """Serializer for Topic model."""
    
    class Meta:
        model = Topic
        fields = [
            'id', 'course', 'title', 'description', 'order_index',
            'prerequisites', 'estimated_duration', 'difficulty_level',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class QuestionSerializer(serializers.ModelSerializer):
    """Serializer for Question model."""
    
    class Meta:
        model = Question
        fields = [
            'id', 'assessment', 'question_type', 'question_text',
            'question_data', 'points', 'difficulty_level',
            'topic_tags', 'order_index'
        ]
        read_only_fields = ['id']


class AssessmentSerializer(serializers.ModelSerializer):
    """Serializer for Assessment model."""
    questions_count = serializers.SerializerMethodField()
    course_title = serializers.CharField(source='course.title', read_only=True)
    
    class Meta:
        model = Assessment
        fields = [
            'id', 'course', 'course_title', 'topic', 'title',
            'description', 'assessment_type', 'total_points',
            'passing_score', 'due_date', 'is_adaptive',
            'time_limit', 'questions_count', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_questions_count(self, obj):
        return obj.questions.count()


class SubmissionSerializer(serializers.ModelSerializer):
    """Serializer for Submission model."""
    student_name = serializers.CharField(source='student.user.get_full_name', read_only=True)
    assessment_title = serializers.CharField(source='assessment.title', read_only=True)
    
    class Meta:
        model = Submission
        fields = [
            'id', 'assessment', 'assessment_title', 'student',
            'student_name', 'submitted_at', 'score', 'max_score',
            'percentage', 'status', 'time_spent', 'attempt_number',
            'ai_graded', 'feedback'
        ]
        read_only_fields = ['id', 'submitted_at']


class StudentSkillProfileSerializer(serializers.ModelSerializer):
    """Serializer for StudentSkillProfile model."""
    topic_title = serializers.CharField(source='topic.title', read_only=True)
    course_title = serializers.CharField(source='course.title', read_only=True)
    
    class Meta:
        model = StudentSkillProfile
        fields = [
            'id', 'student', 'course', 'course_title', 'topic',
            'topic_title', 'mastery_level', 'attempts_count',
            'correct_count', 'last_practiced', 'next_review',
            'difficulty_preference', 'learning_speed'
        ]
        read_only_fields = ['id']
