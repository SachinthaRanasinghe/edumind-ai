"""
URL routing for learning app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    CourseViewSet,
    TopicViewSet,
    AssessmentViewSet,
    QuestionViewSet,
    StudentProgressView,
    QuizSubmitView,
)

router = DefaultRouter()
router.register(r'courses', CourseViewSet, basename='course')
router.register(r'topics', TopicViewSet, basename='topic')
router.register(r'assessments', AssessmentViewSet, basename='assessment')
router.register(r'questions', QuestionViewSet, basename='question')

app_name = 'learning'

urlpatterns = [
    path('', include(router.urls)),

    # Student progress
    path('progress/', StudentProgressView.as_view(), name='student-progress'),
    path('progress/<uuid:course_id>/', StudentProgressView.as_view(), name='student-progress-course'),

    # Quiz submission
    path('quiz/submit/', QuizSubmitView.as_view(), name='quiz-submit'),
]
