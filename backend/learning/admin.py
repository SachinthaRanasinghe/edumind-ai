"""
Admin configuration for learning app.
"""
from django.contrib import admin
from .models import (
    Course, CourseEnrollment, Topic, Assessment, Question,
    Submission, SubmissionAnswer, StudentSkillProfile,
    LearningSession, AITutorConversation, AITutorMessage
)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['course_code', 'title', 'subject', 'teacher', 'is_active']
    list_filter = ['subject', 'grade_level', 'is_active']
    search_fields = ['course_code', 'title', 'subject']


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['student', 'course', 'status', 'enrollment_date', 'final_grade']
    list_filter = ['status', 'enrollment_date']
    search_fields = ['student__student_id', 'course__course_code']


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'difficulty_level', 'order_index']
    list_filter = ['difficulty_level', 'course']
    search_fields = ['title', 'course__title']


@admin.register(Assessment)
class AssessmentAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'assessment_type', 'total_points', 'due_date']
    list_filter = ['assessment_type', 'is_adaptive', 'course']
    search_fields = ['title', 'course__title']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['question_text', 'question_type', 'difficulty_level', 'points']
    list_filter = ['question_type', 'difficulty_level']
    search_fields = ['question_text']


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['student', 'assessment', 'status', 'score', 'percentage', 'submitted_at']
    list_filter = ['status', 'ai_graded', 'submitted_at']
    search_fields = ['student__student_id', 'assessment__title']


@admin.register(SubmissionAnswer)
class SubmissionAnswerAdmin(admin.ModelAdmin):
    list_display = ['submission', 'question', 'is_correct', 'points_earned']
    list_filter = ['is_correct']


@admin.register(StudentSkillProfile)
class StudentSkillProfileAdmin(admin.ModelAdmin):
    list_display = ['student', 'topic', 'mastery_level', 'attempts_count', 'correct_count']
    list_filter = ['mastery_level']
    search_fields = ['student__student_id', 'topic__title']


@admin.register(LearningSession)
class LearningSessionAdmin(admin.ModelAdmin):
    list_display = ['student', 'session_type', 'started_at', 'duration', 'questions_attempted']
    list_filter = ['session_type', 'started_at']
    search_fields = ['student__student_id']


@admin.register(AITutorConversation)
class AITutorConversationAdmin(admin.ModelAdmin):
    list_display = ['student', 'topic', 'started_at', 'message_count']
    list_filter = ['started_at']
    search_fields = ['student__student_id']


@admin.register(AITutorMessage)
class AITutorMessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'role', 'message', 'created_at']
    list_filter = ['role', 'created_at']
