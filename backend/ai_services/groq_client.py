"""
Groq API client for LLM interactions.
"""
from groq import Groq
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class GroqClient:
    """Client for interacting with Groq API."""
    
    def __init__(self):
        self.api_key = settings.GROQ_API_KEY
        if not self.api_key:
            logger.warning("GROQ_API_KEY not set in settings")
        self.client = Groq(api_key=self.api_key) if self.api_key else None
    
    def generate_response(self, messages, model="llama3-8b-8192", temperature=0.7, max_tokens=1024):
        """
        Generate a response from Groq LLM.
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model to use (default: llama3-8b-8192)
            temperature: Randomness (0-2)
            max_tokens: Maximum response length
        
        Returns:
            str: Generated response
        """
        if not self.client:
            raise ValueError("Groq client not initialized. Check API key.")
        
        try:
            chat_completion = self.client.chat.completions.create(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return chat_completion.choices[0].message.content
        except Exception as e:
            logger.error(f"Error generating Groq response: {str(e)}")
            raise
    
    def generate_quiz_question(self, topic, difficulty="medium", question_type="multiple_choice"):
        """
        Generate a quiz question for a specific topic.
        
        Args:
            topic: Topic/subject for the question
            difficulty: easy, medium, or hard
            question_type: Type of question to generate
        
        Returns:
            dict: Question data
        """
        system_prompt = f"""You are an expert educational content creator. 
Generate a {difficulty} difficulty {question_type} question about {topic}.
Return ONLY a valid JSON object with this exact structure:
{{
    "question": "The question text",
    "options": ["Option A", "Option B", "Option C", "Option D"],
    "correct_answer": "The correct option",
    "explanation": "Why this is the correct answer"
}}"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Create a {difficulty} {question_type} question about {topic}"}
        ]
        
        response = self.generate_response(messages, temperature=0.8)
        
        # Parse JSON response
        import json
        try:
            question_data = json.loads(response)
            return question_data
        except json.JSONDecodeError:
            logger.error(f"Failed to parse question JSON: {response}")
            raise ValueError("Invalid question format from AI")
    
    def provide_tutoring_help(self, student_question, context=None):
        """
        Provide AI tutoring help for a student question.
        
        Args:
            student_question: The student's question
            context: Additional context (topic, previous messages, etc.)
        
        Returns:
            str: AI tutor response
        """
        system_prompt = """You are a patient and helpful AI tutor. Your goal is to:
1. Guide students to understand concepts, don't just give answers
2. Use Socratic method - ask leading questions
3. Provide hints and encouragement
4. Explain complex topics in simple terms
5. Use examples and analogies when helpful
6. Be supportive and positive"""
        
        messages = [{"role": "system", "content": system_prompt}]
        
        if context:
            messages.append({
                "role": "system",
                "content": f"Context: {context}"
            })
        
        messages.append({
            "role": "user",
            "content": student_question
        })
        
        return self.generate_response(messages, temperature=0.7, max_tokens=512)
    
    def grade_essay(self, essay_text, rubric, max_score=100):
        """
        Grade an essay using AI with a rubric.
        
        Args:
            essay_text: The essay to grade
            rubric: Grading criteria
            max_score: Maximum possible score
        
        Returns:
            dict: Grading results with score, feedback, strengths, weaknesses
        """
        system_prompt = f"""You are an expert essay grader. Grade the following essay based on this rubric:
{rubric}

Maximum score: {max_score}

Return ONLY a valid JSON object with this structure:
{{
    "score": <numeric score>,
    "percentage": <percentage score>,
    "strengths": ["strength 1", "strength 2", ...],
    "weaknesses": ["weakness 1", "weakness 2", ...],
    "suggestions": ["suggestion 1", "suggestion 2", ...],
    "overall_feedback": "General feedback summary"
}}"""
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Essay to grade:\n\n{essay_text}"}
        ]
        
        response = self.generate_response(messages, temperature=0.3, max_tokens=1024)
        
        # Parse JSON response
        import json
        try:
            grading_result = json.loads(response)
            return grading_result
        except json.JSONDecodeError:
            logger.error(f"Failed to parse grading JSON: {response}")
            raise ValueError("Invalid grading format from AI")


# Singleton instance
_groq_client = None

def get_groq_client():
    """Get or create Groq client singleton."""
    global _groq_client
    if _groq_client is None:
        _groq_client = GroqClient()
    return _groq_client
