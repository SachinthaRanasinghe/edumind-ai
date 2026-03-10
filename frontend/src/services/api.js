/**
 * API service for backend communication
 */
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor to handle token refresh
api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // If error is 401 and we haven't retried yet
    if (error.response?.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
          refresh: refreshToken,
        });

        const { access } = response.data;
        localStorage.setItem('access_token', access);

        // Retry original request with new token
        originalRequest.headers.Authorization = `Bearer ${access}`;
        return api(originalRequest);
      } catch (refreshError) {
        // Refresh failed, logout user
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        window.location.href = '/login';
        return Promise.reject(refreshError);
      }
    }

    return Promise.reject(error);
  }
);

// Authentication APIs
export const authAPI = {
  login: async (email, password) => {
    const response = await api.post('/auth/token/', { email, password });
    const { access, refresh } = response.data;
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);
    return response.data;
  },

  registerStudent: async (data) => {
    const response = await api.post('/users/register/student/', data);
    const { tokens } = response.data;
    localStorage.setItem('access_token', tokens.access);
    localStorage.setItem('refresh_token', tokens.refresh);
    return response.data;
  },

  registerTeacher: async (data) => {
    const response = await api.post('/users/register/teacher/', data);
    const { tokens } = response.data;
    localStorage.setItem('access_token', tokens.access);
    localStorage.setItem('refresh_token', tokens.refresh);
    return response.data;
  },

  logout: async () => {
    const refreshToken = localStorage.getItem('refresh_token');
    try {
      await api.post('/users/logout/', { refresh_token: refreshToken });
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    }
  },

  getCurrentUser: async () => {
    const response = await api.get('/users/me/');
    return response.data;
  },
};

// User APIs
export const userAPI = {
  updateProfile: async (data) => {
    const response = await api.patch('/users/profile/update/', data);
    return response.data;
  },

  updateStudentProfile: async (data) => {
    const response = await api.patch('/users/profile/student/update/', data);
    return response.data;
  },

  updateTeacherProfile: async (data) => {
    const response = await api.patch('/users/profile/teacher/update/', data);
    return response.data;
  },
};

// Learning APIs
export const learningAPI = {
  getCourses: async () => {
    const response = await api.get('/learning/courses/');
    return response.data;
  },

  getCourseDetails: async (courseId) => {
    const response = await api.get(`/learning/courses/${courseId}/`);
    return response.data;
  },

  createCourse: async (data) => {
    const response = await api.post('/learning/courses/', data);
    return response.data;
  },

  updateCourse: async (courseId, data) => {
    const response = await api.patch(`/learning/courses/${courseId}/`, data);
    return response.data;
  },

  deleteCourse: async (courseId) => {
    await api.delete(`/learning/courses/${courseId}/`);
  },

  enrollInCourse: async (courseId) => {
    const response = await api.post(`/learning/courses/${courseId}/enroll/`);
    return response.data;
  },

  getTopics: async (courseId) => {
    const response = await api.get('/learning/topics/', { params: { course: courseId } });
    return response.data;
  },

  createTopic: async (data) => {
    const response = await api.post('/learning/topics/', data);
    return response.data;
  },

  getAssessments: async (courseId) => {
    const response = await api.get('/learning/assessments/', { params: { course: courseId } });
    return response.data;
  },

  getProgress: async () => {
    const response = await api.get('/learning/progress/');
    return response.data;
  },

  getCourseProgress: async (courseId) => {
    const response = await api.get(`/learning/progress/${courseId}/`);
    return response.data;
  },

  generateQuiz: async (courseId, topicName, difficulty = 'medium', numQuestions = 5) => {
    const response = await api.post(`/learning/courses/${courseId}/generate_quiz/`, {
      topic: topicName,
      difficulty,
      num_questions: numQuestions,
    });
    return response.data;
  },

  submitQuizAnswers: async (data) => {
    const response = await api.post('/learning/quiz/submit/', data);
    return response.data;
  },
};

// AI Services APIs
export const aiAPI = {
  chatWithTutor: async (message, conversationId = null, context = null) => {
    const response = await api.post('/ai-services/tutor/chat/', {
      message,
      conversation_id: conversationId,
      context,
    });
    return response.data;
  },
};

export default api;
