"""
Student mastery tracking and adaptive difficulty engine.
"""
from datetime import timedelta
from django.utils import timezone
from learning.models import StudentSkillProfile


class MasteryTracker:
    """
    Tracks student mastery and determines adaptive difficulty.
    """
    
    @staticmethod
    def update_mastery(student, topic, is_correct, time_taken):
        """
        Update student's mastery level for a topic.
        
        Uses a weighted algorithm:
        - Recent performance weighs more
        - Time taken affects learning speed
        - Spaced repetition scheduling
        """
        profile, created = StudentSkillProfile.objects.get_or_create(
            student=student,
            course=topic.course,
            topic=topic,
            defaults={'mastery_level': 0.0}
        )
        
        # Update attempts
        profile.attempts_count += 1
        if is_correct:
            profile.correct_count += 1
        
        # Calculate new mastery level
        success_rate = (profile.correct_count / profile.attempts_count) * 100
        
        # Weighted update: 70% current mastery, 30% new performance
        if is_correct:
            delta = (100 - float(profile.mastery_level)) * 0.3
        else:
            delta = -float(profile.mastery_level) * 0.2
        
        new_mastery = float(profile.mastery_level) + delta
        profile.mastery_level = max(0, min(100, new_mastery))
        
        # Update timestamps
        profile.last_practiced = timezone.now()
        
        # Spaced repetition: schedule next review based on mastery
        if profile.mastery_level >= 80:
            days = 7  # Review weekly if mastered
        elif profile.mastery_level >= 50:
            days = 3  # Review every 3 days
        else:
            days = 1  # Review daily if struggling
        
        profile.next_review = timezone.now() + timedelta(days=days)
        
        # Calculate learning speed (questions per hour)
        if time_taken > 0:
            questions_per_hour = 3600 / time_taken
            if profile.learning_speed:
                # Weighted average
                profile.learning_speed = (float(profile.learning_speed) * 0.7 + questions_per_hour * 0.3)
            else:
                profile.learning_speed = questions_per_hour
        
        profile.save()
        
        return profile
    
    @staticmethod
    def get_recommended_difficulty(student, topic):
        """
        Get recommended difficulty level for a student on a topic.
        """
        try:
            profile = StudentSkillProfile.objects.get(
                student=student,
                topic=topic
            )
            
            mastery = float(profile.mastery_level)
            if mastery < 30:
                return 'easy'
            elif mastery < 70:
                return 'medium'
            else:
                return 'hard'
        except StudentSkillProfile.DoesNotExist:
            return 'easy'  # Start with easy for new topics
    
    @staticmethod
    def get_weak_topics(student, course, limit=5):
        """
        Get topics where student needs more practice.
        """
        return StudentSkillProfile.objects.filter(
            student=student,
            course=course,
            mastery_level__lt=70
        ).order_by('mastery_level')[:limit]
    
    @staticmethod
    def get_topics_for_review(student, course):
        """
        Get topics that are due for spaced repetition review.
        """
        return StudentSkillProfile.objects.filter(
            student=student,
            course=course,
            next_review__lte=timezone.now()
        ).order_by('next_review')
