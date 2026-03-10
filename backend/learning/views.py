"""
Views for learning app - Phase 1 MVP.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from .models import (
    Course,
    CourseEnrollment,
    Topic,
    Assessment,
    Question,
    Submission,
    StudentSkillProfile,
)
from .serializers import (
    CourseSerializer,
    TopicSerializer,
    AssessmentSerializer,
    QuestionSerializer,
)
from .permissions import IsTeacherOrReadOnly, IsEnrolledStudent
from ai_services.quiz_generator import QuizGenerator
from ai_services.mastery_tracker import MasteryTracker


class CourseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Course CRUD operations.
    """
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        if user.user_type == 'student':
            # Students see only enrolled courses
            return Course.objects.filter(enrollments__student__user=user)
        elif user.user_type == 'teacher':
            # Teachers see their own courses
            return Course.objects.filter(teacher__user=user)
        return Course.objects.all()
    
    @action(detail=True, methods=['post'])
    def enroll(self, request, pk=None):
        """Enroll a student in a course."""
        course = self.get_object()
        if request.user.user_type != 'student':
            return Response(
                {'error': 'Only students can enroll in courses'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        enrollment, created = CourseEnrollment.objects.get_or_create(
            student=request.user.student,
            course=course
        )
        
        if created:
            return Response({'message': 'Enrolled successfully'})
        return Response({'message': 'Already enrolled'})
    
    @action(detail=True, methods=['post'])
    def generate_quiz(self, request, pk=None):
        """Generate AI-powered adaptive quiz for a course."""
        course = self.get_object()
        
        if request.user.user_type != 'student':
            return Response(
                {'error': 'Only students can generate quizzes'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        student = request.user.student
        topic = request.data.get('topic', course.title)
        difficulty = request.data.get('difficulty', 'medium')
        num_questions = int(request.data.get('num_questions', 5))
        
        # Get student's skill profile for adaptive difficulty
        skill_profiles = StudentSkillProfile.objects.filter(
            student=student,
            course=course
        )
        
        avg_mastery = 50.0
        if skill_profiles.exists():
            from django.db.models import Avg
            avg_mastery = skill_profiles.aggregate(Avg('mastery_level'))['mastery_level__avg'] or 50.0
        
        # Generate quiz using AI
        quiz_generator = QuizGenerator()
        questions = quiz_generator.generate_adaptive_quiz(
            topic=topic,
            difficulty=difficulty,
            num_questions=num_questions,
            student_level=float(avg_mastery)
        )
        
        return Response({
            'course_id': str(course.id),
            'course_code': course.course_code,
            'topic': topic,
            'questions': questions,
            'adaptive': True,
            'student_mastery': float(avg_mastery)
        })


class TopicViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Topic management.
    """
    queryset = Topic.objects.all()
    serializer_class = TopicSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        course_id = self.request.query_params.get('course')
        if course_id:
            return Topic.objects.filter(course_id=course_id)
        return Topic.objects.all()


class AssessmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Assessment management.
    """
    queryset = Assessment.objects.all()
    serializer_class = AssessmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        course_id = self.request.query_params.get('course')
        
        queryset = Assessment.objects.all()
        if course_id:
            queryset = queryset.filter(course_id=course_id)
        
        if user.user_type == 'student':
            # Students see assessments from enrolled courses
            queryset = queryset.filter(course__enrollments__student__user=user)
        
        return queryset
    
    @action(detail=True, methods=['get'])
    def generate_quiz(self, request, pk=None):
        """Generate AI-powered adaptive quiz for an assessment."""
        assessment = self.get_object()
        
        if request.user.user_type != 'student':
            return Response(
                {'error': 'Only students can generate quizzes'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        student = request.user.student
        difficulty = request.query_params.get('difficulty', 'medium')
        num_questions = int(request.query_params.get('num_questions', 5))
        
        # Get student's skill profile for adaptive difficulty
        skill_profile = StudentSkillProfile.objects.filter(
            student=student,
            course=assessment.course
        ).first()
        
        # Generate quiz using AI
        quiz_generator = QuizGenerator()
        questions = quiz_generator.generate_adaptive_quiz(
            topic=assessment.topic.title if assessment.topic else assessment.title,
            difficulty=difficulty,
            num_questions=num_questions,
            student_level=skill_profile.mastery_level if skill_profile else 50.0
        )
        
        return Response({
            'assessment_id': str(assessment.id),
            'questions': questions,
            'adaptive': True
        })


class QuestionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Question management.
    """
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacherOrReadOnly]
    
    def get_queryset(self):
        assessment_id = self.request.query_params.get('assessment')
        if assessment_id:
            return Question.objects.filter(assessment_id=assessment_id)
        return Question.objects.all()


class StudentProgressView(APIView):
    """
    Get student progress for a course or overall.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, course_id=None):
        if request.user.user_type != 'student':
            return Response(
                {'error': 'Only students can view progress'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        student = request.user.student
        
        if course_id:
            # Get progress for specific course
            skills = StudentSkillProfile.objects.filter(
                student=student,
                course_id=course_id
            )
        else:
            # Get overall progress
            skills = StudentSkillProfile.objects.filter(student=student)
        
        progress_data = []
        for skill in skills:
            progress_data.append({
                'topic': skill.topic.title,
                'course': skill.course.title,
                'mastery_level': float(skill.mastery_level),
                'attempts': skill.attempts_count,
                'correct': skill.correct_count,
                'last_practiced': skill.last_practiced,
            })
        
        return Response({
            'student': student.user.get_full_name(),
            'progress': progress_data
        })
