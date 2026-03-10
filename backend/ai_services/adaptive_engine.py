"""
Adaptive learning engine for personalizing student experience.
"""
from learning.models import StudentSkillProfile, Question
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class AdaptiveLearningEngine:
    """Engine for adaptive learning and personalized content delivery."""
    
    def __init__(self):
        self.mastery_threshold = settings.EDUMIND_SETTINGS['ADAPTIVE_LEARNING']['MASTERY_THRESHOLD']
        self.min_attempts = settings.EDUMIND_SETTINGS['ADAPTIVE_LEARNING']['MIN_ATTEMPTS_FOR_MASTERY']
        self.sr_intervals = settings.EDUMIND_SETTINGS['ADAPTIVE_LEARNING']['SPACED_REPETITION_INTERVALS']
    
    def calculate_mastery_level(self, correct_count, total_attempts):
        """
        Calculate mastery level based on performance.
        
        Args:
            correct_count: Number of correct answers
            total_attempts: Total number of attempts
        
        Returns:
            float: Mastery percentage (0-100)
        """
        if total_attempts == 0:
            return 0.0
        
        # Basic accuracy calculation with diminishing returns for repetition
        accuracy = (correct_count / total_attempts) * 100
        
        # Apply confidence factor based on number of attempts
        confidence_factor = min(1.0, total_attempts / self.min_attempts)
        
        mastery = accuracy * confidence_factor
        return round(mastery, 2)
    
    def get_next_difficulty(self, student_profile):
        """
        Determine the next difficulty level for a student.
        
        Args:
            student_profile: StudentSkillProfile instance
        
        Returns:
            str: Difficulty level (easy, medium, hard)
        """
        mastery = student_profile.mastery_level
        
        if mastery >= 80:
            return 'hard'
        elif mastery >= 50:
            return 'medium'
        else:
            return 'easy'
    
    def calculate_next_review_date(self, current_mastery, review_count):
        """
        Calculate when the topic should be reviewed next (spaced repetition).
        
        Args:
            current_mastery: Current mastery level (0-100)
            review_count: Number of times reviewed
        
        Returns:
            datetime: Next review date
        """
        if current_mastery < 50:
            # Low mastery - review soon
            interval_days = self.sr_intervals[0]
        elif current_mastery < 80:
            # Medium mastery - moderate interval
            interval_index = min(review_count, len(self.sr_intervals) - 1)
            interval_days = self.sr_intervals[interval_index]
        else:
            # High mastery - longer interval
            interval_index = min(review_count + 1, len(self.sr_intervals) - 1)
            interval_days = self.sr_intervals[interval_index]
        
        return timezone.now() + timedelta(days=interval_days)
    
    def select_adaptive_questions(self, student, topic, count=10):
        """
        Select questions adaptively based on student's skill level.
        
        Args:
            student: Student instance
            topic: Topic instance
            count: Number of questions to select
        
        Returns:
            QuerySet: Selected questions
        """
        # Get student's skill profile for this topic
        try:
            skill_profile = StudentSkillProfile.objects.get(
                student=student,
                topic=topic
            )
            difficulty = self.get_next_difficulty(skill_profile)
        except StudentSkillProfile.DoesNotExist:
            # New topic - start with easy questions
            difficulty = 'easy'
        
        # Get questions for the topic
        questions = Question.objects.filter(
            topic_tags__contains=[str(topic.id)],
            difficulty_level=difficulty
        ).order_by('?')[:count]
        
        # If not enough questions at this difficulty, mix in adjacent difficulties
        if questions.count() < count:
            remaining = count - questions.count()
            if difficulty == 'easy':
                extra = Question.objects.filter(
                    topic_tags__contains=[str(topic.id)],
                    difficulty_level='medium'
                ).order_by('?')[:remaining]
            elif difficulty == 'hard':
                extra = Question.objects.filter(
                    topic_tags__contains=[str(topic.id)],
                    difficulty_level='medium'
                ).order_by('?')[:remaining]
            else:  # medium
                extra = Question.objects.filter(
                    topic_tags__contains=[str(topic.id)]
                ).exclude(difficulty_level='medium').order_by('?')[:remaining]
            
            questions = list(questions) + list(extra)
        
        return questions
    
    def update_skill_profile(self, student, topic, course, is_correct, time_spent=None):
        """
        Update student's skill profile after answering a question.
        
        Args:
            student: Student instance
            topic: Topic instance
            course: Course instance
            is_correct: Whether the answer was correct
            time_spent: Time spent on question (optional)
        """
        profile, created = StudentSkillProfile.objects.get_or_create(
            student=student,
            topic=topic,
            course=course,
            defaults={
                'mastery_level': 0.0,
                'attempts_count': 0,
                'correct_count': 0
            }
        )
        
        # Update counts
        profile.attempts_count += 1
        if is_correct:
            profile.correct_count += 1
        
        # Recalculate mastery
        profile.mastery_level = self.calculate_mastery_level(
            profile.correct_count,
            profile.attempts_count
        )
        
        # Update timestamps
        profile.last_practiced = timezone.now()
        profile.next_review = self.calculate_next_review_date(
            profile.mastery_level,
            profile.attempts_count
        )
        
        # Calculate learning speed if time_spent provided
        if time_spent:
            # Questions per hour
            profile.learning_speed = 3600 / time_spent if time_spent > 0 else None
        
        profile.save()
        
        logger.info(f"Updated skill profile for {student} on {topic}: Mastery={profile.mastery_level}%")
        
        return profile
    
    def get_recommended_topics(self, student, course, limit=5):
        """
        Get recommended topics for a student based on their progress.
        
        Args:
            student: Student instance
            course: Course instance
            limit: Maximum number of topics to return
        
        Returns:
            list: Recommended topics with reasons
        """
        recommendations = []
        
        # Get all skill profiles for this student in this course
        profiles = StudentSkillProfile.objects.filter(
            student=student,
            course=course
        ).select_related('topic')
        
        # Topics due for review (spaced repetition)
        due_for_review = profiles.filter(
            next_review__lte=timezone.now()
        ).order_by('next_review')[:limit]
        
        for profile in due_for_review:
            recommendations.append({
                'topic': profile.topic,
                'reason': 'Due for review (Spaced Repetition)',
                'mastery': profile.mastery_level,
                'priority': 'high'
            })
        
        # Topics with low mastery
        if len(recommendations) < limit:
            low_mastery = profiles.filter(
                mastery_level__lt=50
            ).exclude(
                id__in=[r['topic'].id for r in recommendations]
            ).order_by('mastery_level')[:limit - len(recommendations)]
            
            for profile in low_mastery:
                recommendations.append({
                    'topic': profile.topic,
                    'reason': 'Needs improvement',
                    'mastery': profile.mastery_level,
                    'priority': 'medium'
                })
        
        return recommendations


# Singleton instance
_adaptive_engine = None

def get_adaptive_engine():
    """Get or create adaptive engine singleton."""
    global _adaptive_engine
    if _adaptive_engine is None:
        _adaptive_engine = AdaptiveLearningEngine()
    return _adaptive_engine
