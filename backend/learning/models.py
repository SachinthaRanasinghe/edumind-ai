"""
Models for adaptive learning system.
"""
from django.db import models
from django.utils import timezone
from users.models import Student, Teacher
import uuid


class Course(models.Model):
    """Course model."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course_code = models.CharField(max_length=20, unique=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    subject = models.CharField(max_length=100)
    grade_level = models.IntegerField(null=True, blank=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='courses')
    
    is_active = models.BooleanField(default=True)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'courses'
        indexes = [
            models.Index(fields=['teacher']),
            models.Index(fields=['subject']),
        ]
    
    def __str__(self):
        return f"{self.course_code} - {self.title}"


class CourseEnrollment(models.Model):
    """Student enrollment in courses."""
    
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
        ('failed', 'Failed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    
    enrollment_date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    final_grade = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'course_enrollments'
        unique_together = ['student', 'course']
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['course']),
        ]
    
    def __str__(self):
        return f"{self.student} enrolled in {self.course}"


class Topic(models.Model):
    """Course topics/modules."""
    
    DIFFICULTY_CHOICES = [
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='topics')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order_index = models.IntegerField()
    
    prerequisites = models.JSONField(default=list, blank=True)  # List of topic IDs
    estimated_duration = models.IntegerField(null=True, blank=True, help_text="Duration in minutes")
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='beginner')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'topics'
        ordering = ['order_index']
        indexes = [
            models.Index(fields=['course']),
        ]
    
    def __str__(self):
        return f"{self.course.course_code} - {self.title}"


class Assessment(models.Model):
    """Assessments/quizzes for courses."""
    
    ASSESSMENT_TYPE_CHOICES = [
        ('quiz', 'Quiz'),
        ('assignment', 'Assignment'),
        ('exam', 'Exam'),
        ('essay', 'Essay'),
        ('project', 'Project'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assessments')
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, related_name='assessments')
    
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    assessment_type = models.CharField(max_length=20, choices=ASSESSMENT_TYPE_CHOICES)
    
    total_points = models.DecimalField(max_digits=6, decimal_places=2)
    passing_score = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    due_date = models.DateTimeField(null=True, blank=True)
    
    is_adaptive = models.BooleanField(default=False)
    time_limit = models.IntegerField(null=True, blank=True, help_text="Time limit in minutes")
    
    created_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='created_assessments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'assessments'
        indexes = [
            models.Index(fields=['course']),
            models.Index(fields=['assessment_type']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.assessment_type})"


class Question(models.Model):
    """Questions for assessments."""
    
    QUESTION_TYPE_CHOICES = [
        ('multiple_choice', 'Multiple Choice'),
        ('true_false', 'True/False'),
        ('short_answer', 'Short Answer'),
        ('essay', 'Essay'),
        ('coding', 'Coding'),
    ]
    
    DIFFICULTY_CHOICES = [
        ('easy', 'Easy'),
        ('medium', 'Medium'),
        ('hard', 'Hard'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='questions')
    
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES)
    question_text = models.TextField()
    question_data = models.JSONField(help_text="Stores options, correct answers, etc.")
    
    points = models.DecimalField(max_digits=6, decimal_places=2)
    difficulty_level = models.CharField(max_length=20, choices=DIFFICULTY_CHOICES, default='medium')
    topic_tags = models.JSONField(default=list, blank=True)
    order_index = models.IntegerField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'questions'
        ordering = ['order_index']
        indexes = [
            models.Index(fields=['assessment']),
            models.Index(fields=['difficulty_level']),
        ]
    
    def __str__(self):
        return f"{self.question_type}: {self.question_text[:50]}..."


class Submission(models.Model):
    """Student submissions for assessments."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('graded', 'Graded'),
        ('in_review', 'In Review'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assessment = models.ForeignKey(Assessment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='submissions')
    
    submitted_at = models.DateTimeField(default=timezone.now)
    score = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    max_score = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    time_spent = models.IntegerField(null=True, blank=True, help_text="Time spent in seconds")
    attempt_number = models.IntegerField(default=1)
    
    ai_graded = models.BooleanField(default=False)
    graded_by = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, blank=True, related_name='graded_submissions')
    graded_at = models.DateTimeField(null=True, blank=True)
    feedback = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'submissions'
        indexes = [
            models.Index(fields=['assessment']),
            models.Index(fields=['student']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.student} - {self.assessment} (Attempt {self.attempt_number})"


class SubmissionAnswer(models.Model):
    """Individual answers within a submission."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='student_answers')
    
    answer_data = models.JSONField(help_text="Stores student's answer")
    is_correct = models.BooleanField(null=True, blank=True)
    points_earned = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    ai_feedback = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'submission_answers'
        indexes = [
            models.Index(fields=['submission']),
        ]
    
    def __str__(self):
        return f"Answer to {self.question.id}"


class StudentSkillProfile(models.Model):
    """Tracks student mastery of topics."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='skill_profiles')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='skill_profiles')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE, related_name='skill_profiles')
    
    mastery_level = models.DecimalField(max_digits=4, decimal_places=2, default=0.0,
                                       help_text="Mastery percentage (0-100)")
    attempts_count = models.IntegerField(default=0)
    correct_count = models.IntegerField(default=0)
    
    last_practiced = models.DateTimeField(null=True, blank=True)
    next_review = models.DateTimeField(null=True, blank=True, help_text="For spaced repetition")
    
    difficulty_preference = models.CharField(max_length=20, null=True, blank=True)
    learning_speed = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True,
                                        help_text="Questions per hour")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'student_skill_profiles'
        unique_together = ['student', 'course', 'topic']
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['mastery_level']),
        ]
    
    def __str__(self):
        return f"{self.student} - {self.topic} (Mastery: {self.mastery_level}%)"


class LearningSession(models.Model):
    """Tracks individual learning sessions."""
    
    SESSION_TYPE_CHOICES = [
        ('quiz', 'Quiz'),
        ('study', 'Study'),
        ('ai_tutor', 'AI Tutor'),
        ('practice', 'Practice'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='learning_sessions')
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='sessions')
    
    session_type = models.CharField(max_length=50, choices=SESSION_TYPE_CHOICES)
    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True, help_text="Duration in seconds")
    
    questions_attempted = models.IntegerField(default=0)
    questions_correct = models.IntegerField(default=0)
    topics_covered = models.JSONField(default=list, blank=True)
    session_data = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'learning_sessions'
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['started_at']),
        ]
    
    def __str__(self):
        return f"{self.student} - {self.session_type} on {self.started_at}"


class AITutorConversation(models.Model):
    """AI tutor conversation sessions."""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='ai_conversations')
    session = models.ForeignKey(LearningSession, on_delete=models.SET_NULL, null=True, blank=True, related_name='conversations')
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL, null=True, blank=True, related_name='conversations')
    
    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True, blank=True)
    message_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_tutor_conversations'
        indexes = [
            models.Index(fields=['student']),
        ]
    
    def __str__(self):
        return f"Conversation {self.id} - {self.student}"


class AITutorMessage(models.Model):
    """Messages in AI tutor conversations."""
    
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('ai', 'AI'),
        ('system', 'System'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    conversation = models.ForeignKey(AITutorConversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    message = models.TextField()
    metadata = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'ai_tutor_messages'
        indexes = [
            models.Index(fields=['conversation']),
        ]
    
    def __str__(self):
        return f"{self.role}: {self.message[:50]}..."


class StudentAnswer(models.Model):
    """
    Records student answers for questions.
    """
    ANSWER_STATUS = [
        ('correct', 'Correct'),
        ('incorrect', 'Incorrect'),
        ('partial', 'Partially Correct'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='student_answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    submission = models.ForeignKey(Submission, on_delete=models.CASCADE, related_name='student_answers', null=True, blank=True)
    
    # Answer data
    answer_text = models.TextField(blank=True)
    selected_option = models.CharField(max_length=1, blank=True)  # A, B, C, D for MCQ
    
    # Grading
    is_correct = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=ANSWER_STATUS, default='incorrect')
    points_earned = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)
    
    # AI Feedback
    ai_feedback = models.TextField(blank=True)
    hints_used = models.IntegerField(default=0)
    
    # Timing
    time_taken_seconds = models.IntegerField(default=0)
    answered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'student_answers'
        ordering = ['-answered_at']
        indexes = [
            models.Index(fields=['student']),
            models.Index(fields=['question']),
        ]
    
    def __str__(self):
        return f"{self.student} - Q{self.question.id} ({self.status})"
