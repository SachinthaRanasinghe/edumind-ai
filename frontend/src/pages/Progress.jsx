import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import toast from 'react-hot-toast';

export default function Progress() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [courses, setCourses] = useState([]);
  const [overallStats, setOverallStats] = useState({
    totalCourses: 0,
    completedAssessments: 0,
    averageScore: 0,
    totalStudyTime: 0
  });

  useEffect(() => {
    fetchProgress();
  }, []);

  const fetchProgress = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      
      // Fetch courses
      const coursesResponse = await fetch('http://localhost:8000/api/learning/courses/', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      
      if (coursesResponse.ok) {
        const coursesData = await coursesResponse.json();
        const courseList = coursesData.results || coursesData;
        setCourses(courseList);
        
        setOverallStats({
          totalCourses: courseList.length,
          completedAssessments: 0,
          averageScore: 85, // Mock data
          totalStudyTime: 24 // Mock data in hours
        });
      }
    } catch (error) {
      toast.error('Failed to load progress data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-xl text-gray-600">Loading progress...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <button
            onClick={() => navigate(-1)}
            className="mb-2 text-blue-600 hover:text-blue-700 font-medium"
          >
            ← Back to Dashboard
          </button>
          <h1 className="text-3xl font-bold">📊 Learning Progress</h1>
          <p className="text-gray-600 mt-1">Track your learning journey</p>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Overall Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">Enrolled Courses</h3>
            <p className="mt-2 text-3xl font-bold text-blue-600">{overallStats.totalCourses}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">Completed Assessments</h3>
            <p className="mt-2 text-3xl font-bold text-green-600">{overallStats.completedAssessments}</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">Average Score</h3>
            <p className="mt-2 text-3xl font-bold text-purple-600">{overallStats.averageScore}%</p>
          </div>
          <div className="bg-white p-6 rounded-lg shadow">
            <h3 className="text-sm font-medium text-gray-500">Study Time</h3>
            <p className="mt-2 text-3xl font-bold text-orange-600">{overallStats.totalStudyTime}h</p>
          </div>
        </div>

        {/* Course Progress */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-2xl font-bold mb-6">Course Progress</h2>
          
          {courses.length === 0 ? (
            <div className="text-center py-12">
              <p className="text-gray-600 mb-4">No courses enrolled yet</p>
              <button
                onClick={() => navigate('/dashboard/student')}
                className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
              >
                Browse Courses
              </button>
            </div>
          ) : (
            <div className="space-y-6">
              {courses.map((course, index) => {
                const progress = Math.floor(Math.random() * 100); // Mock progress
                const mastery = Math.floor(Math.random() * 100); // Mock mastery
                
                return (
                  <div key={course.id} className="border border-gray-200 rounded-lg p-6">
                    <div className="flex justify-between items-start mb-4">
                      <div>
                        <h3 className="text-xl font-semibold">{course.title}</h3>
                        <p className="text-sm text-gray-600">{course.course_code}</p>
                      </div>
                      <span className="px-3 py-1 bg-blue-100 text-blue-700 rounded-full text-sm font-medium">
                        {progress}% Complete
                      </span>
                    </div>
                    
                    {/* Progress Bar */}
                    <div className="mb-4">
                      <div className="flex justify-between text-sm text-gray-600 mb-1">
                        <span>Overall Progress</span>
                        <span>{progress}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-3">
                        <div
                          className="bg-blue-600 h-3 rounded-full transition-all"
                          style={{ width: `${progress}%` }}
                        ></div>
                      </div>
                    </div>

                    {/* Mastery Level */}
                    <div className="mb-4">
                      <div className="flex justify-between text-sm text-gray-600 mb-1">
                        <span>Mastery Level</span>
                        <span>{mastery}%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-3">
                        <div
                          className="bg-green-600 h-3 rounded-full transition-all"
                          style={{ width: `${mastery}%` }}
                        ></div>
                      </div>
                    </div>

                    {/* Stats Grid */}
                    <div className="grid grid-cols-3 gap-4 mt-4 pt-4 border-t border-gray-200">
                      <div>
                        <p className="text-sm text-gray-500">Quizzes</p>
                        <p className="text-lg font-semibold">{Math.floor(Math.random() * 10)}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Avg Score</p>
                        <p className="text-lg font-semibold">{Math.floor(Math.random() * 20 + 70)}%</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-500">Study Time</p>
                        <p className="text-lg font-semibold">{Math.floor(Math.random() * 10 + 5)}h</p>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
