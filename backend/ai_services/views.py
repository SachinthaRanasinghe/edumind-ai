"""
AI Services Views - AI Tutor Chat endpoint.
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .groq_client import GroqClient


class AITutorChatView(APIView):
    """
    AI Tutor Chat endpoint using Groq.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Send a message to the AI tutor and get a response.
        """
        message = request.data.get('message')
        topic = request.data.get('topic', '')
        context = request.data.get('context', '')
        
        if not message:
            return Response(
                {'error': 'Message is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Build the tutor prompt
        system_prompt = f"""You are a helpful and patient AI tutor specializing in {topic if topic else 'various subjects'}.
Your role is to:
1. Help students understand concepts, not just give answers
2. Provide hints and guidance rather than direct solutions
3. Ask clarifying questions to assess understanding
4. Encourage critical thinking
5. Be supportive and encouraging

Context: {context if context else 'General tutoring session'}

Respond in a friendly, educational manner."""

        full_prompt = f"{system_prompt}\n\nStudent: {message}\n\nTutor:"
        
        # Get AI response
        client = GroqClient()
        response = client.chat(full_prompt)
        
        return Response({
            'response': response,
            'topic': topic,
        })
