import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';
import { learningAPI } from '../services/api';

export default function Quiz() {
  const navigate = useNavigate();
  const [courses, setCourses] = useState([]);
  const [selectedCourse, setSelectedCourse] = useState(null);
  const [quizMeta, setQuizMeta] = useState(null); // { topic, student_mastery }
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [questions, setQuestions] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [answers, setAnswers] = useState({});   // { index: selected_option_string }
  const [showResults, setShowResults] = useState(false);
  const [serverResults, setServerResults] = useState(null); // from backend after submit
  const quizStartTime = useRef(null);

  useEffect(() => {
    fetchCourses();
  }, []);

  const fetchCourses = async () => {
    try {
      setLoading(true);
      const data = await learningAPI.getCourses();
      setCourses(data.results || data);
    } catch (error) {
      toast.error('Error loading courses');
    } finally {
      setLoading(false);
    }
  };

  // Normalise AI question: options can be object {A:..,B:..} or array
  const normaliseQuestion = (q) => {
    let options = q.options;
    if (options && !Array.isArray(options)) {
      options = Object.entries(options).map(([k, v]) => `${k}: ${v}`);
    }
    return { ...q, options: options || [] };
  };

  const startQuiz = async () => {
    if (!selectedCourse) {
      toast.error('Please select a course first');
      return;
    }
    const course = courses.find(c => c.id === selectedCourse);
    try {
      setGenerating(true);
      toast.loading('Generating AI-powered quiz...', { id: 'quiz-gen' });
      const data = await learningAPI.generateQuiz(selectedCourse, course?.title, 'medium', 5);
      const normalised = (data.questions || []).map(normaliseQuestion);
      setQuizMeta({ topic: data.topic, student_mastery: data.student_mastery });
      setQuestions(normalised);
      setCurrentQuestion(0);
      setAnswers({});
      setShowResults(false);
      setServerResults(null);
      quizStartTime.current = Date.now();
      toast.success('Quiz ready! Good luck 🚀', { id: 'quiz-gen' });
    } catch (error) {
      toast.error('Failed to generate quiz', { id: 'quiz-gen' });
    } finally {
      setGenerating(false);
    }
  };

  const handleAnswer = (option) => {
    setAnswers(prev => ({ ...prev, [currentQuestion]: option }));
  };

  const nextQuestion = () => {
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(prev => prev + 1);
    } else {
      submitQuiz();
    }
  };

  const submitQuiz = async () => {
    const timeSpent = quizStartTime.current
      ? Math.round((Date.now() - quizStartTime.current) / 1000)
      : 0;

    // Build answer payload
    const answerPayload = questions.map((q, index) => ({
      question_text: q.question_text,
      selected_option: answers[index] || '',
      correct_answer: q.correct_answer,
      options: q.options,
      explanation: q.explanation || '',
      difficulty: q.difficulty || 'medium',
      points: q.points || 10,
    }));

    try {
      setSubmitting(true);
      toast.loading('Submitting quiz...', { id: 'quiz-submit' });
      const result = await learningAPI.submitQuizAnswers({
        course_id: selectedCourse,
        topic: quizMeta?.topic || '',
        answers: answerPayload,
        time_spent: timeSpent,
      });
      setServerResults(result);
      toast.success('Quiz submitted!', { id: 'quiz-submit' });
    } catch (error) {
      // Even if server submit fails, show local results
      console.error('Submit error:', error);
      toast.error('Could not save to server — showing local results', { id: 'quiz-submit' });
      const localCorrect = questions.filter((q, i) =>
        (answers[i] || '').toLowerCase() === (q.correct_answer || '').toLowerCase()
      ).length;
      setServerResults({
        correct: localCorrect,
        total: questions.length,
        percentage: Math.round((localCorrect / questions.length) * 100),
        mastery_level: null,
        results: questions.map((q, i) => ({
          question_text: q.question_text,
          selected_option: answers[i] || 'Not answered',
          correct_answer: q.correct_answer,
          is_correct: (answers[i] || '').toLowerCase() === (q.correct_answer || '').toLowerCase(),
          explanation: q.explanation || '',
          points_earned: (answers[i] || '').toLowerCase() === (q.correct_answer || '').toLowerCase() ? (q.points || 10) : 0,
        })),
      });
    } finally {
      setSubmitting(false);
      setShowResults(true);
    }
  };

  const resetQuiz = () => {
    setQuestions([]);
    setSelectedCourse(null);
    setAnswers({});
    setShowResults(false);
    setServerResults(null);
    setCurrentQuestion(0);
    setQuizMeta(null);
  };

  // ── Course selection screen ──────────────────────────────────────────────
  if (!selectedCourse || questions.length === 0) {
    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-4xl mx-auto">
          <button onClick={() => navigate(-1)} className="mb-6 text-blue-600 hover:text-blue-700 font-medium">
            ← Back to Dashboard
          </button>
          <h1 className="text-3xl font-bold mb-2">🎯 Adaptive Quiz</h1>
          <p className="text-gray-600 mb-8">Select a course to start an AI-generated adaptive quiz</p>

          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-xl font-semibold mb-4">Select a Course</h2>
            {loading ? (
              <div className="text-center py-8 text-gray-600">Loading courses...</div>
            ) : courses.length === 0 ? (
              <div className="text-center py-8">
                <div className="text-gray-600">No courses available. Enroll in a course first.</div>
                <button onClick={() => navigate(-1)} className="mt-4 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
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
                      <div className="text-sm text-gray-600">{course.course_code} · {course.subject}</div>
                      {course.description && (
                        <div className="text-xs text-gray-500 mt-1 truncate">{course.description}</div>
                      )}
                    </button>
                  ))}
                </div>
                {selectedCourse && (
                  <button
                    onClick={startQuiz}
                    disabled={generating}
                    className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-semibold"
                  >
                    {generating ? '⏳ Generating Quiz...' : '🚀 Start Adaptive Quiz'}
                  </button>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    );
  }

  // ── Results screen ───────────────────────────────────────────────────────
  if (showResults && serverResults) {
    const { correct, total, percentage, mastery_level, results } = serverResults;
    const emoji = percentage >= 80 ? '🏆' : percentage >= 60 ? '👍' : '💪';
    const color = percentage >= 80 ? 'text-green-600' : percentage >= 60 ? 'text-yellow-600' : 'text-red-500';

    return (
      <div className="min-h-screen bg-gray-50 p-8">
        <div className="max-w-4xl mx-auto">
          <div className="bg-white rounded-lg shadow p-8">
            <h1 className="text-3xl font-bold mb-2 text-center">Quiz Complete! {emoji}</h1>
            {quizMeta?.topic && (
              <p className="text-center text-gray-500 mb-6">Topic: {quizMeta.topic}</p>
            )}

            {/* Score summary */}
            <div className="flex flex-col items-center my-6">
              <div className={`text-7xl font-bold ${color}`}>{percentage}%</div>
              <div className="text-xl text-gray-600 mt-2">{correct} / {total} correct</div>
              {mastery_level !== null && mastery_level !== undefined && (
                <div className="mt-4 px-4 py-2 bg-blue-50 rounded-full text-blue-700 text-sm font-medium">
                  🧠 Mastery level updated: {mastery_level.toFixed(1)}%
                </div>
              )}
            </div>

            {/* Per-question review */}
            <div className="space-y-4 mb-8">
              <h3 className="font-semibold text-lg">📋 Question Review</h3>
              {results.map((r, index) => (
                <div
                  key={index}
                  className={`p-4 border-2 rounded-lg ${r.is_correct ? 'border-green-200 bg-green-50' : 'border-red-200 bg-red-50'}`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <p className="font-medium text-gray-900">Q{index + 1}: {r.question_text}</p>
                    <span className={`text-xl flex-shrink-0 ${r.is_correct ? 'text-green-600' : 'text-red-500'}`}>
                      {r.is_correct ? '✅' : '❌'}
                    </span>
                  </div>
                  <p className={`text-sm mt-2 ${r.is_correct ? 'text-green-700' : 'text-red-700'}`}>
                    Your answer: <strong>{r.selected_option || 'Not answered'}</strong>
                  </p>
                  {!r.is_correct && (
                    <p className="text-sm text-green-700 mt-1">
                      Correct answer: <strong>{r.correct_answer}</strong>
                    </p>
                  )}
                  {r.explanation && (
                    <p className="text-sm text-gray-600 mt-2 italic">💡 {r.explanation}</p>
                  )}
                </div>
              ))}
            </div>

            <div className="flex gap-4 justify-center">
              <button
                onClick={resetQuiz}
                className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold"
              >
                Try Another Quiz
              </button>
              <button
                onClick={() => navigate('/progress')}
                className="px-6 py-3 bg-purple-600 text-white rounded-lg hover:bg-purple-700 font-semibold"
              >
                View Progress
              </button>
              <button
                onClick={() => navigate(-1)}
                className="px-6 py-3 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 font-semibold"
              >
                Dashboard
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // ── Quiz taking screen ───────────────────────────────────────────────────
  const currentQ = questions[currentQuestion];
  const isLast = currentQuestion === questions.length - 1;

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto">
        <div className="mb-6 flex justify-between items-center">
          <button onClick={() => navigate(-1)} className="text-blue-600 hover:text-blue-700 font-medium">
            ← Exit Quiz
          </button>
          <div className="text-gray-600 font-medium">
            Question {currentQuestion + 1} of {questions.length}
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-8">
          {/* Progress bar */}
          <div className="mb-6">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                style={{ width: `${((currentQuestion + 1) / questions.length) * 100}%` }}
              />
            </div>
          </div>

          {/* Difficulty badge */}
          {currentQ.difficulty && (
            <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold mb-4 ${
              currentQ.difficulty === 'easy' ? 'bg-green-100 text-green-700'
              : currentQ.difficulty === 'hard' ? 'bg-red-100 text-red-700'
              : 'bg-yellow-100 text-yellow-700'
            }`}>
              {currentQ.difficulty.charAt(0).toUpperCase() + currentQ.difficulty.slice(1)}
            </span>
          )}

          <h2 className="text-xl font-bold mb-6 text-gray-900">{currentQ.question_text}</h2>

          <div className="space-y-3 mb-8">
            {currentQ.options.map((option, index) => (
              <button
                key={index}
                onClick={() => handleAnswer(option)}
                className={`w-full p-4 border-2 rounded-lg text-left transition font-medium ${
                  answers[currentQuestion] === option
                    ? 'border-blue-500 bg-blue-50 text-blue-900'
                    : 'border-gray-200 hover:border-blue-300 hover:bg-blue-50 text-gray-800'
                }`}
              >
                {option}
              </button>
            ))}
          </div>

          <button
            onClick={nextQuestion}
            disabled={!answers[currentQuestion] || submitting}
            className="w-full px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed font-semibold transition"
          >
            {submitting ? '⏳ Submitting...' : isLast ? '✅ Finish & Submit' : 'Next Question →'}
          </button>
        </div>
      </div>
    </div>
  );
}
