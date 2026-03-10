"""
Views for learning app - Phase 1 MVP.
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
import logging

from .models import (
    Course,
    CourseEnrollment,
    Topic,
    Assessment,
    Question,
    Submission,
    StudentAnswer,
    StudentSkillProfile,
    LearningSession,
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

logger = logging.getLogger(__name__)


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


class QuizSubmitView(APIView):
    """
    Submit answers for an AI-generated adaptive quiz.
    Records StudentAnswers, updates mastery, returns feedback.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if request.user.user_type != 'student':
            return Response(
                {'error': 'Only students can submit quiz answers'},
                status=status.HTTP_403_FORBIDDEN
            )

        student = request.user.student
        course_id = request.data.get('course_id')
        topic_name = request.data.get('topic', '')
        answers = request.data.get('answers', [])  # [{question_text, selected_option, correct_answer, options, explanation, difficulty}]
        time_spent = request.data.get('time_spent', 0)  # total seconds

        if not course_id or not answers:
            return Response(
                {'error': 'course_id and answers are required'},
                status=status.HTTP_400_BAD_REQUEST
            )

        course = get_object_or_404(Course, id=course_id)

        # Get or create topic for mastery tracking
        topic = Topic.objects.filter(course=course, title__icontains=topic_name).first()
        if not topic:
            # Create a dynamic topic entry if not found
            topic, _ = Topic.objects.get_or_create(
                course=course,
                title=topic_name or course.title,
                defaults={'order_index': 0, 'difficulty_level': 'beginner'}
            )

        # Track the learning session
        session = LearningSession.objects.create(
            student=student,
            course=course,
            session_type='quiz',
            started_at=timezone.now() - timezone.timedelta(seconds=time_spent),
            ended_at=timezone.now(),
            duration=time_spent,
            questions_attempted=len(answers),
        )

        # Grade each answer & update mastery
        results = []
        total_correct = 0
        total_points = 0
        earned_points = 0
        avg_time_per_q = time_spent / len(answers) if answers else 0

        for ans in answers:
            question_text = ans.get('question_text', '')
            selected = ans.get('selected_option', '')
            correct = ans.get('correct_answer', '')
            explanation = ans.get('explanation', '')
            difficulty = ans.get('difficulty', 'medium')
            points = float(ans.get('points', 10))

            is_correct = selected.strip().lower() == correct.strip().lower()
            pts_earned = points if is_correct else 0

            if is_correct:
                total_correct += 1
            total_points += points
            earned_points += pts_earned

            # Record StudentAnswer (for history & analytics)
            StudentAnswer.objects.create(
                student=student,
                question=Question.objects.filter(
                    assessment__course=course,
                    question_text=question_text
                ).first() or _get_or_create_ai_question(course, topic, question_text, ans, difficulty, points),
                answer_text=selected,
                selected_option=selected[:1] if selected else '',
                is_correct=is_correct,
                status='correct' if is_correct else 'incorrect',
                points_earned=pts_earned,
                ai_feedback=explanation,
                time_taken_seconds=int(avg_time_per_q),
            )

            # Update mastery via MasteryTracker
            MasteryTracker.update_mastery(
                student=student,
                topic=topic,
                is_correct=is_correct,
                time_taken=int(avg_time_per_q),
            )

            results.append({
                'question_text': question_text,
                'selected_option': selected,
                'correct_answer': correct,
                'is_correct': is_correct,
                'points_earned': pts_earned,
                'explanation': explanation,
            })

        # Update session stats
        session.questions_correct = total_correct
        session.topics_covered = [topic.title]
        session.save()

        # Get updated mastery
        skill_profile = StudentSkillProfile.objects.filter(
            student=student, topic=topic, course=course
        ).first()

        percentage = (earned_points / total_points * 100) if total_points > 0 else 0

        return Response({
            'score': earned_points,
            'max_score': total_points,
            'percentage': round(percentage, 1),
            'correct': total_correct,
            'total': len(answers),
            'mastery_level': float(skill_profile.mastery_level) if skill_profile else 0,
            'next_review': skill_profile.next_review if skill_profile else None,
            'results': results,
        }, status=status.HTTP_200_OK)


def _get_or_create_ai_question(course, topic, question_text, ans_data, difficulty, points):
    """
    Find or create a Question record for AI-generated questions
    so StudentAnswer always has a valid FK.
    """
    # Find or create a generic AI-quiz assessment for this course
    assessment, _ = Assessment.objects.get_or_create(
        course=course,
        title=f'AI Adaptive Quiz - {course.course_code}',
        defaults={
            'assessment_type': 'quiz',
            'total_points': 100,
            'is_adaptive': True,
            'topic': topic,
        }
    )
    question, _ = Question.objects.get_or_create(
        assessment=assessment,
        question_text=question_text,
        defaults={
            'question_type': 'multiple_choice',
            'question_data': {
                'options': ans_data.get('options', {}),
                'correct_answer': ans_data.get('correct_answer', ''),
                'explanation': ans_data.get('explanation', ''),
            },
            'points': points,
            'difficulty_level': difficulty,
        }
    )
    return question


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
