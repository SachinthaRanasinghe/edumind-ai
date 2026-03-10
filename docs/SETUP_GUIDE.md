# EduMind AI - Setup Guide

This guide will help you set up and run the EduMind AI platform locally.

## Prerequisites

Make sure you have the following installed:
- **Python 3.11+**
- **Node.js 18+**
- **PostgreSQL 15+** (or use SQLite for development)
- **Git**

## Backend Setup

### 1. Navigate to Backend Directory

```bash
cd EduMind-AI/backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

### 3. Activate Virtual Environment

**macOS/Linux:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` file and add your configuration:

```env
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (use SQLite for development)
DATABASE_URL=sqlite:///db.sqlite3

# Or PostgreSQL
# DATABASE_URL=postgresql://username:password@localhost:5432/edumind_db

# Groq API (get key from https://console.groq.com)
GROQ_API_KEY=your-groq-api-key-here

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 6. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create Superuser (Admin)

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin account.

### 8. Run Development Server

```bash
python manage.py runserver
```

Backend should now be running at `http://localhost:8000`

### 9. Access Admin Panel

Visit `http://localhost:8000/admin` and login with your superuser credentials.

## Frontend Setup

### 1. Navigate to Frontend Directory

Open a new terminal window:

```bash
cd EduMind-AI/frontend
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Configure Environment Variables

```bash
cp .env.example .env
```

The default configuration should work:

```env
VITE_API_BASE_URL=http://localhost:8000/api
VITE_APP_NAME=EduMind AI
```

### 4. Run Development Server

```bash
npm run dev
```

Frontend should now be running at `http://localhost:3000`

## Verify Installation

1. **Backend API**: Visit `http://localhost:8000/admin` - you should see Django admin
2. **Frontend**: Visit `http://localhost:3000` - you should see the EduMind AI homepage
3. **API Connection**: Try registering a new account from the frontend

## Getting a Groq API Key

1. Visit [https://console.groq.com](https://console.groq.com)
2. Sign up or login
3. Navigate to API Keys section
4. Create a new API key
5. Copy the key and paste it in your `.env` file

## Database Setup (PostgreSQL - Optional)

If you want to use PostgreSQL instead of SQLite:

### 1. Install PostgreSQL

**macOS (using Homebrew):**
```bash
brew install postgresql
brew services start postgresql
```

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

**Windows:**
Download and install from [https://www.postgresql.org/download/windows/](https://www.postgresql.org/download/windows/)

### 2. Create Database

```bash
psql postgres
CREATE DATABASE edumind_db;
CREATE USER edumind_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE edumind_db TO edumind_user;
\q
```

### 3. Update .env

```env
DATABASE_URL=postgresql://edumind_user:your_password@localhost:5432/edumind_db
```

### 4. Run Migrations

```bash
python manage.py migrate
```

## Common Issues

### Port Already in Use

If port 8000 or 3000 is already in use:

**Backend:**
```bash
python manage.py runserver 8001
```

**Frontend:**
Update `vite.config.js`:
```javascript
server: {
  port: 3001,
}
```

### Database Connection Error

- Ensure PostgreSQL is running: `brew services list` (macOS) or `systemctl status postgresql` (Linux)
- Check database credentials in `.env`
- For development, you can use SQLite: `DATABASE_URL=sqlite:///db.sqlite3`

### Module Not Found Errors

Make sure virtual environment is activated and dependencies are installed:
```bash
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -r requirements.txt
```

### CORS Errors

Ensure `CORS_ALLOWED_ORIGINS` in backend `.env` includes your frontend URL:
```env
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## Next Steps

1. ✅ Backend and Frontend running
2. 📝 Create sample data (courses, topics, questions)
3. 🤖 Test AI features (quiz generation, tutor chat)
4. 📊 Explore analytics and adaptive learning
5. 🚀 Start building Phase 1 MVP features

## Development Workflow

1. **Backend changes**: Restart Django server if needed
2. **Frontend changes**: Hot reload should work automatically
3. **Database changes**: Run `python manage.py makemigrations` and `migrate`
4. **New dependencies**: 
   - Backend: Add to `requirements.txt` and `pip install`
   - Frontend: `npm install package-name`

## Testing

Run backend tests:
```bash
python manage.py test
```

Run frontend linting:
```bash
npm run lint
```

## Production Deployment

See separate deployment guide for production setup with:
- Gunicorn (backend)
- Nginx (reverse proxy)
- PostgreSQL (production database)
- Environment-specific configuration

---

**Need Help?** Check the main README.md or open an issue on GitHub.
