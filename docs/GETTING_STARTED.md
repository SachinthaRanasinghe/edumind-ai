# Getting Started with EduMind AI

Welcome to EduMind AI! This guide will help you understand the project structure and start contributing.

## 📋 Table of Contents

1. [Project Overview](#project-overview)
2. [Quick Start](#quick-start)
3. [Project Structure](#project-structure)
4. [Technology Stack](#technology-stack)
5. [Development Phases](#development-phases)
6. [Key Features](#key-features)
7. [API Documentation](#api-documentation)

## 🎯 Project Overview

EduMind AI is an AI-powered education intelligence platform with three core modules:

### 1. **Adaptive Learning Engine** (Phase 1 - MVP)
- Personalized learning paths for each student
- AI-generated quizzes based on skill level
- Real-time AI tutor assistance
- Spaced repetition for better retention
- Dynamic difficulty adjustment

### 2. **Automated Grading System** (Phase 2)
- AI-powered essay grading
- Rubric-based evaluation
- Instant feedback generation
- 60-80% reduction in grading time
- Human oversight for quality control

### 3. **Predictive Analytics** (Phase 3)
- Early dropout prediction
- At-risk student identification
- Intervention recommendations
- Teacher alert system
- Performance trend analysis

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+
- PostgreSQL 15+ (or SQLite for development)
- Groq API Key ([Get one here](https://console.groq.com))

### Installation

1. **Clone and setup backend:**
```bash
cd EduMind-AI/backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API keys
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

2. **Setup frontend:**
```bash
cd EduMind-AI/frontend
npm install
cp .env.example .env
npm run dev
```

3. **Access the application:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- Admin Panel: http://localhost:8000/admin

## 📁 Project Structure

```
EduMind-AI/
├── backend/                    # Django backend
│   ├── core/                  # Project settings and config
│   ├── users/                 # User authentication & profiles
│   │   ├── models.py         # User, Student, Teacher models
│   │   ├── serializers.py    # DRF serializers
│   │   ├── views.py          # API views
│   │   └── urls.py           # URL routing
│   ├── learning/              # Adaptive learning module
│   │   ├── models.py         # Course, Assessment, Submission models
│   │   └── admin.py          # Admin interface
│   ├── grading/               # Automated grading module
│   ├── analytics/             # Predictive analytics module
│   └── ai_services/           # AI/ML integration
│       ├── groq_client.py    # Groq LLM client
│       └── adaptive_engine.py # Adaptive learning algorithms
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── pages/            # Page components
│   │   ├── services/         # API service layer
│   │   └── App.jsx           # Main app component
│   └── package.json
├── docs/                      # Documentation
│   ├── DATABASE_SCHEMA.md    # Complete database schema
│   ├── SETUP_GUIDE.md        # Detailed setup instructions
│   └── GETTING_STARTED.md    # This file
└── README.md                  # Project overview
```

## 🛠️ Technology Stack

### Backend
- **Framework**: Django 5.0 + Django REST Framework
- **Database**: PostgreSQL (production) / SQLite (development)
- **AI/ML**: 
  - Groq API (LLM for chat, quiz generation, grading)
  - scikit-learn (ML models for predictions)
  - pandas, numpy (data processing)
- **Authentication**: JWT with djangorestframework-simplejwt
- **Task Queue**: Celery + Redis (for async tasks)

### Frontend
- **Framework**: React 18 with Vite
- **Routing**: React Router v6
- **State Management**: React Query (@tanstack/react-query)
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios
- **Notifications**: react-hot-toast
- **Charts**: Recharts

### AI/ML Stack
- **LLM Provider**: Groq (Llama 3 models)
- **NLP**: Transformers (Hugging Face)
- **ML Libraries**: scikit-learn, pandas, numpy

## 🗓️ Development Phases

### ✅ Phase 0 - Foundation (CURRENT)
- [x] Project structure setup
- [x] Database schema design
- [x] Authentication system
- [x] Basic frontend pages
- [ ] Sample data generation
- [ ] API endpoint testing

### 📝 Phase 1 - MVP Adaptive Learning (6-8 weeks)
- [ ] Course and topic management
- [ ] Quiz generation with Groq
- [ ] Adaptive difficulty algorithm
- [ ] AI tutor chat interface
- [ ] Student skill profiling
- [ ] Learning session tracking
- [ ] Basic analytics dashboard

### 📝 Phase 2 - Automated Grading (4-6 weeks)
- [ ] Essay submission system
- [ ] Rubric configuration
- [ ] AI essay grading with Groq
- [ ] Feedback generation
- [ ] Teacher review interface
- [ ] Grade analytics

### 📝 Phase 3 - Predictive Analytics (6-8 weeks)
- [ ] Engagement data collection
- [ ] Dropout prediction model
- [ ] Risk score calculation
- [ ] Intervention system
- [ ] Teacher alert dashboard
- [ ] Performance trend analysis

## 🎯 Key Features

### For Students
- 📚 Personalized learning paths
- 🎯 Adaptive quizzes matching skill level
- 🤖 24/7 AI tutor assistance
- 📊 Progress tracking and analytics
- ⏰ Spaced repetition reminders
- 🏆 Achievement system

### For Teachers
- 👥 Class management
- 📝 AI-powered quiz generation
- ✍️ Automated essay grading
- 📈 Student performance analytics
- 🚨 At-risk student alerts
- 📋 Rubric-based grading

### For Administrators
- 📊 Platform-wide analytics
- 👤 User management
- 🔧 System configuration
- 📈 Usage statistics
- 🎓 Course oversight

## 📡 API Documentation

### Authentication Endpoints

```javascript
// Login
POST /api/auth/token/
Body: { "email": "user@example.com", "password": "password123" }
Response: { "access": "token...", "refresh": "token..." }

// Register Student
POST /api/users/register/student/
Body: {
  "email": "student@example.com",
  "password": "password123",
  "password_confirm": "password123",
  "first_name": "John",
  "last_name": "Doe",
  "student_id": "STU001",
  "grade_level": 10
}

// Get Current User
GET /api/users/me/
Headers: { "Authorization": "Bearer <access_token>" }
```

### Learning Endpoints (Coming Soon)

```javascript
// Get Courses
GET /api/learning/courses/

// Get Course Topics
GET /api/learning/courses/{id}/topics/

// Submit Assessment
POST /api/learning/assessments/{id}/submit/
```

### AI Services Endpoints (Coming Soon)

```javascript
// Generate Quiz
POST /api/ai/generate-quiz/
Body: { "topic_id": "uuid", "difficulty": "medium", "count": 10 }

// Chat with AI Tutor
POST /api/ai/tutor/chat/
Body: { "message": "Help me understand...", "context": {...} }

// Grade Essay
POST /api/ai/grade-essay/
Body: { "essay_text": "...", "rubric": {...} }
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
python manage.py test
```

### Frontend Tests
```bash
cd frontend
npm run test  # (to be configured)
```

## 🔐 Security Considerations

- JWT token-based authentication
- Password hashing with Django's built-in system
- CORS protection configured
- SQL injection protection (Django ORM)
- XSS protection in React
- Rate limiting (to be implemented)
- Input validation on both frontend and backend

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Make your changes
3. Test thoroughly
4. Commit: `git commit -m "Add my feature"`
5. Push: `git push origin feature/my-feature`
6. Create a Pull Request

## 📚 Additional Resources

- [Complete Database Schema](./DATABASE_SCHEMA.md)
- [Detailed Setup Guide](./SETUP_GUIDE.md)
- [Django Documentation](https://docs.djangoproject.com/)
- [React Documentation](https://react.dev/)
- [Groq API Documentation](https://console.groq.com/docs)

## 🐛 Common Issues

### Database Migration Errors
```bash
python manage.py makemigrations
python manage.py migrate
```

### Port Already in Use
```bash
# Backend - use different port
python manage.py runserver 8001

# Frontend - edit vite.config.js
```

### CORS Errors
Check `CORS_ALLOWED_ORIGINS` in backend `.env` file.

## 📞 Support

For questions or issues:
1. Check existing documentation
2. Search closed issues on GitHub
3. Open a new issue with detailed description

---

**Happy Coding! 🚀**

Built with ❤️ for educators and students worldwide.
