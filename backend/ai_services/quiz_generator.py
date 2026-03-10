"""
AI-powered quiz generation using Groq.
"""
from .groq_client import GroqClient
import json


class QuizGenerator:
    """
    Generates adaptive quizzes using Groq AI.
    """
    
    def __init__(self):
        self.client = GroqClient()
    
    def generate_adaptive_quiz(self, topic, difficulty='medium', num_questions=5, student_level=50.0):
        """
        Generate an adaptive quiz based on student's skill level.
        
        Args:
            topic: The topic for the quiz
            difficulty: Base difficulty level (easy, medium, hard)
            num_questions: Number of questions to generate
            student_level: Student's mastery level (0-100)
        
        Returns:
            list: List of generated questions
        """
        
        # Adjust difficulty based on student level
        if student_level < 30:
            adjusted_difficulty = 'easy'
        elif student_level < 70:
            adjusted_difficulty = 'medium'
        else:
            adjusted_difficulty = 'hard'
        
        prompt = f"""Generate {num_questions} multiple-choice questions about {topic}.
Difficulty level: {adjusted_difficulty}
Student mastery level: {student_level}%

Format each question as JSON with this structure:
{{
    "question_text": "The question",
    "options": {{"A": "option1", "B": "option2", "C": "option3", "D": "option4"}},
    "correct_answer": "A",
    "explanation": "Why this is correct",
    "difficulty": "{adjusted_difficulty}",
    "points": 10
}}

Return ONLY a JSON array of questions, no additional text."""

        messages = [
            {"role": "system", "content": "You are an expert educational content creator. Return ONLY valid JSON arrays with no additional text."},
            {"role": "user", "content": prompt}
        ]
        response = self.client.generate_response(messages, temperature=0.8, max_tokens=2048)
        
        try:
            # Parse the response
            questions = json.loads(response)
            if not isinstance(questions, list):
                questions = [questions]
            return questions
        except json.JSONDecodeError:
            # Fallback: create sample questions
            return self._generate_fallback_questions(topic, num_questions, adjusted_difficulty)
    
    def _generate_fallback_questions(self, topic, num_questions, difficulty):
        """Generate fallback questions if AI fails."""
        return [{
            "question_text": f"Sample question {i+1} about {topic}",
            "options": {
                "A": "Option A",
                "B": "Option B",
                "C": "Option C",
                "D": "Option D"
            },
            "correct_answer": "A",
            "explanation": "This is a sample explanation",
            "difficulty": difficulty,
            "points": 10
        } for i in range(num_questions)]
