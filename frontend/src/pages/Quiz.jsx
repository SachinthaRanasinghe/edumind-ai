import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';

export default function Quiz() {
  const navigate = useNavigate();
  const [courses, setCourses] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [questions, setQuestions] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});
  const [showResults, setShowResults] = useState(false);
  
  useEffect(() => {
    fetchCourses();
  }, []);
  
  const fetchCourses = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/api/learning/courses/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        setCourses(data.results || data);
      } else {
        toast.error('Failed to load courses');
      }
    } catch (error) {
      toast.error('Error loading courses');
    } finally {
      setLoading(false);
    }
  };

  const startQuiz = async () => {
    if (!selectedCourse) {
      toast.error('Please select a course first');
      return;
    }
    
    try {
      setGenerating(true);
      toast.loading('Generating AI-powered quiz...', { id: 'quiz-gen' });
      
      const token = localStorage.getItem('access_token');
      const response = await fetch(`http://localhost:8000/api/learning/courses/${selectedCourse}/generate_quiz/`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          num_questions: 5,
          difficulty: 'medium'
        })
      });
      
      if (response.ok) {
        const data = await response.json();
        setQuestions(data.questions || []);
        setCurrentQuestion(0);
        setAnswers({});
        setShowResults(false);
        toast.success('Quiz generated successfully!', { id: 'quiz-gen' });
      } else {
        toast.error('Failed to generate quiz. Using demo questions...', { id: 'quiz-gen' });
        // Fallback to demo questions
        const mockQuestions = [
          {
            id: 1,
            question_text: "What is a variable in programming?",
            options: ["A container for storing data", "A type of loop", "A function", "An operator"],
            correct_answer: "A container for storing data"
          },
          {
            id: 2,
            question_text: "Which of these is a Python data type?",
            options: ["String", "Integer", "List", "All of the above"],
            correct_answer: "All of the above"
          },
          {
            id: 3,
            question_text: "What does 'for' loop do?",
            options: ["Repeats code", "Makes decisions", "Defines functions", "Imports libraries"],
            correct_answer: "Repeats code"
          }
        ];
        setQuestions(mockQuestions);
        setCurrentQuestion(0);
        setAnswers({});
        setShowResults(false);
      }
    } catch (error) {
      console.error('Quiz generation error:', error);
      toast.error('Error generating quiz', { id: 'quiz-gen' });
    } finally {
      setGenerating(false);
    }
  };

  const handleAnswer = (answer) => {
    setAnswers({ ...answers, [currentQuestion]: answer });
  };

  const nextQuestion = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
    } else {
      setShowResults(true);
    }
  };

  const calculateScore = () => {
    let correct = 0;
    questions.forEach((q, index) => {
      if (answers[index] === q.correct_answer) {
        correct++;
      }
    });
    return correct;
  };

  // Course selection screen
  if (!selectedCourse || questions.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-4xl mx-auto">
          <button
            onClick={() => navigate(-1)}
            className="mb-6 text-blue-600 hover:text-blue-700 font-medium"
          >
            ← Back to Dashboard
          </button>
          
          <h1 className="text-3xl font-bold mb-2">🎯 Adaptive Quiz</h1>
          <p className="text-gray-600 mb-8">Select a course to start an AI-generated quiz</p>
          
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Select a Course</h2>
            
            {loading ? (
              <div className="text-center py-8">
                <div className="text-lg text-gray-600">Loading courses...</div>
              </div>
            ) : courses.length === 0 ? (
              <div className="text-center py-8">
                <div className="text-lg text-gray-600">No courses available</div>
                <button
                  onClick={() => navigate(-1)}
                  className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  Go Back
                </button>
              </div>
            ) : (
              <>
                <div className="space-y-3 mb-6">
                  {courses.map((course) => (
                    <button
                      key={course.id}
                      onClick={() => setSelectedCourse(course.id)}
                      className={`w-full p-4 border-2 rounded-lg text-left transition ${
                        selectedCourse === course.id
                          ? 'border-blue-500 bg-blue-50'
                          : 'border-gray-200 hover:border-blue-300 hover:bg-blue-50'
                      }`}
                    >
                      <div className="font-semibold text-lg">{course.title}</div>
                      <div className="text-sm text-gray-600">{course.course_code} - {course.subject}</div>
                      <div className="text-xs text-gray-500 mt-1">{course.description}</div>
                    </button>
                  ))}
                </div>
                
                {selectedCourse && (
                  <button
                    onClick={startQuiz}
                    disabled={generating}
                    className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-semibold"
                  >
                    {generating ? 'Generating Quiz...' : '🚀 Start Adaptive Quiz'}
                  </button>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Results screen
  if (showResults) {
    const score = calculateScore();
    const percentage = (score / questions.length) * 100;
    
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow p-8 text-center">
            <h1 className="text-3xl font-bold mb-4">Quiz Complete! 🎉</h1>
            
            <div className="my-8">
              <div className="text-6xl font-bold text-blue-600 mb-2">{percentage.toFixed(0)}%</div>
              <div className="text-xl text-gray-600">
                {score} out of {questions.length} correct
              </div>
            </div>
            
            <div className="space-y-4 text-left mb-8">
              <h3 className="font-semibold text-lg">Review:</h3>
              {questions.map((q, index) => (
                <div key={index} className="p-4 border rounded-lg">
                  <p className="font-medium mb-2">Q{index + 1}: {q.question_text}</p>
                  <p className={`text-sm ${answers[index] === q.correct_answer ? 'text-green-600' : 'text-red-600'}`}>
                    Your answer: {answers[index] || 'Not answered'}
                  </p>
                  {answers[index] !== q.correct_answer && (
                    <p className="text-sm text-green-600">Correct answer: {q.correct_answer}</p>
                  )}
                </div>
              ))}
            </div>
            
            <div className="flex gap-4 justify-center">
              <button
                onClick={() => {
                  setQuestions([]);
                  setSelectedCourse(null);
                  setAnswers({});
                  setShowResults(false);
                  setCurrentQuestion(0);
                }}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Try Another Quiz
              </button>
              <button
                onClick={() => navigate(-1)}
                className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300"
              >
                Back to Dashboard
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Quiz taking screen
  const currentQ = questions[currentQuestion];
  
  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-6 flex justify-between items-center">
          <button
            onClick={() => navigate(-1)}
            className="text-blue-600 hover:text-blue-700 font-medium"
          >
            ← Exit Quiz
          </button>
          <div className="text-gray-600">
            Question {currentQuestion + 1} of {questions.length}
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow p-8">
          <div className="mb-4">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all"
                style={{ width: `${((currentQuestion + 1) / questions.length) * 100}%` }}
              ></div>
            </div>
          </div>
          
          <h2 className="text-2xl font-bold mb-6">{currentQ.question_text}</h2>
          
          <div className="space-y-3 mb-8">
            {currentQ.options && currentQ.options.map((option, index) => (
              <button
                key={index}
                onClick={() => handleAnswer(option)}
                className={`w-full p-4 border-2 rounded-lg text-left transition ${
                  answers[currentQuestion] === option
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-blue-300'
                }`}
              >
                {option}
              </button>
            ))}
          </div>
          
          <button
            onClick={nextQuestion}
            disabled={!answers[currentQuestion]}
            className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-semibold"
          >
            {currentQuestion === questions.length - 1 ? 'Finish Quiz' : 'Next Question →'}
          </button>
        </div>
      </div>
    </div>
  );
}
