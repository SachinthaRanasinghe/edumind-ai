"""
URL routing for AI services.
"""
from django.urls import path
from .views import AITutorChatView

app_name = 'ai_services'

urlpatterns = [
    path('tutor/chat/', AITutorChatView.as_view(), name='tutor-chat'),
]
