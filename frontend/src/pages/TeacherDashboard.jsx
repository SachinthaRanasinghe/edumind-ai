import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { authAPI } from '../services/api';
import toast from 'react-hot-toast';

export default function TeacherDashboard() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [courses, setCourses] = useState([]);
  const [stats, setStats] = useState({
    totalCourses: 0,
    totalStudents: 0,
    pendingGrading: 0,
    atRiskStudents: 0
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
        
        // Calculate total students (sum of enrollment_count from all courses)
        const totalStudents = courseList.reduce((sum, course) => sum + (course.enrollment_count || 0), 0);
        
        setStats({
          totalCourses: courseList.length,
          totalStudents: totalStudents,
          pendingGrading: 0,
          atRiskStudents: 0
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
              <span className="text-gray-700">Prof. {user?.last_name}</span>
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
            Teacher Dashboard
          </h2>
          <p className="mt-2 text-gray-600">Manage your courses and students</p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">Total Courses</h3>
            <p className="mt-2 text-3xl font-bold text-blue-600">{stats.totalCourses}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">Total Students</h3>
            <p className="mt-2 text-3xl font-bold text-green-600">{stats.totalStudents}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">Pending Grading</h3>
            <p className="mt-2 text-3xl font-bold text-orange-600">{stats.pendingGrading}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">At-Risk Students</h3>
            <p className="mt-2 text-3xl font-bold text-red-600">{stats.atRiskStudents}</p>
          </div>
        </div>

        {/* My Courses */}
        {courses.length > 0 && (
          <div className="bg-white rounded-lg shadow p-6 mb-8">
            <h3 className="text-xl font-bold text-gray-900 mb-4">My Courses</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {courses.map(course => (
                <div key={course.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition">
                  <div className="flex justify-between items-start">
                    <div>
                      <h4 className="font-semibold text-lg text-gray-900">{course.title}</h4>
                      <p className="text-sm text-gray-600 mt-1">{course.course_code}</p>
                    </div>
                    <span className="px-3 py-1 bg-blue-100 text-blue-700 text-sm rounded-full">
                      {course.enrollment_count || 0} students
                    </span>
                  </div>
                  <p className="text-sm text-gray-500 mt-2">{course.description}</p>
                  <div className="mt-3 flex gap-2">
                    <span className="px-2 py-1 bg-purple-100 text-purple-700 text-xs rounded">{course.subject}</span>
                    <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded">Grade {course.grade_level}</span>
                    {course.is_active && <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded">Active</span>}
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
              onClick={() => navigate('/course-management')}
              className="p-4 border-2 border-blue-200 rounded-lg hover:bg-blue-50 hover:border-blue-400 transition text-left"
            >
              <div className="font-semibold text-blue-600">📚 Manage Courses</div>
              <div className="text-sm text-gray-600">Create and manage your courses</div>
            </button>
            <button 
              onClick={() => navigate('/quiz')}
              className="p-4 border-2 border-purple-200 rounded-lg hover:bg-purple-50 hover:border-purple-400 transition text-left"
            >
              <div className="font-semibold text-purple-600">🎯 Generate Quiz</div>
              <div className="text-sm text-gray-600">AI-powered quiz creation</div>
            </button>
            <button 
              onClick={() => navigate('/progress')}
              className="p-4 border-2 border-green-200 rounded-lg hover:bg-green-50 hover:border-green-400 transition text-left"
            >
              <div className="font-semibold text-green-600">📊 View Analytics</div>
              <div className="text-sm text-gray-600">Student performance insights</div>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
