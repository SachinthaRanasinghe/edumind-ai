import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI } from '../services/api';
import toast from 'react-hot-toast';

export default function StudentDashboard() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [courses, setCourses] = useState([]);
  const [stats, setStats] = useState({
    enrolledCourses: 0,
    pendingAssignments: 0,
    averageScore: '--'
  });

  useEffect(() => {
    fetchUserData();
  }, []);

  const fetchUserData = async () => {
    try {
      const userData = await authAPI.getCurrentUser();
      setUser(userData);
      
      // Fetch courses
      const token = localStorage.getItem('access_token');
      const response = await fetch('http://localhost:8000/api/learning/courses/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (response.ok) {
        const data = await response.json();
        const courseList = data.results || data;
        setCourses(courseList);
        setStats({
          enrolledCourses: courseList.length,
          pendingAssignments: 0,
          averageScore: '--'
        });
      }
    } catch (error) {
      toast.error('Failed to load user data');
      navigate('/login');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await authAPI.logout();
      toast.success('Logged out successfully');
      navigate('/login');
    } catch (error) {
      toast.error('Logout failed');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Navigation */}
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <h1 className="text-2xl font-bold text-blue-600">EduMind AI</h1>
            <div className="flex items-center gap-4">
              <span className="text-gray-700">{user?.full_name}</span>
              <button
                onClick={handleLogout}
                className="px-4 py-2 text-sm text-gray-700 hover:text-red-600"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="mb-8">
          <h2 className="text-3xl font-bold text-gray-900">
            Welcome back, {user?.first_name}! 👋
          </h2>
          <p className="mt-2 text-gray-600">Here's your learning dashboard</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">Courses Enrolled</h3>
            <p className="mt-2 text-3xl font-bold text-blue-600">{stats.enrolledCourses}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">Assignments Pending</h3>
            <p className="mt-2 text-3xl font-bold text-orange-600">{stats.pendingAssignments}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">Average Score</h3>
            <p className="mt-2 text-3xl font-bold text-green-600">{stats.averageScore}</p>
          </div>
        </div>

        {/* My Courses */}
        {courses.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h3 className="text-xl font-bold text-gray-900 mb-4">My Courses</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {courses.map(course => (
                <div key={course.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition">
                  <h4 className="font-semibold text-lg text-gray-900">{course.title}</h4>
                  <p className="text-sm text-gray-600 mt-1">{course.course_code}</p>
                  <p className="text-sm text-gray-500 mt-2">{course.description}</p>
                  <div className="mt-3 flex gap-2">
                    <span className="px-2 py-1 bg-blue-100 text-blue-700 text-xs rounded">{course.subject}</span>
                    <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded">Grade {course.grade_level}</span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4">Quick Actions</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <button 
              onClick={() => navigate('/quiz')}
              className="p-4 border-2 border-blue-200 rounded-lg hover:bg-blue-50 hover:border-blue-400 transition text-left"
            >
              <div className="font-semibold text-blue-600">📝 Start Adaptive Quiz</div>
              <div className="text-sm text-gray-600">Practice with AI-generated questions</div>
            </button>
            <button 
              onClick={() => navigate('/ai-tutor')}
              className="p-4 border-2 border-purple-200 rounded-lg hover:bg-purple-50 hover:border-purple-400 transition text-left"
            >
              <div className="font-semibold text-purple-600">🤖 AI Tutor Chat</div>
              <div className="text-sm text-gray-600">Get help from your AI tutor</div>
            </button>
            <button 
              onClick={() => navigate('/progress')}
              className="p-4 border-2 border-green-200 rounded-lg hover:bg-green-50 hover:border-green-400 transition text-left"
            >
              <div className="font-semibold text-green-600">📊 View Progress</div>
              <div className="text-sm text-gray-600">Track your learning journey</div>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
