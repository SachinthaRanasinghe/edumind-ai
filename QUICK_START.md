# EduMind AI - Quick Start ⚡

Get up and running in 5 minutes!

## 1️⃣ Backend Setup (2 minutes)

```bash
# Navigate to backend
cd EduMind-AI/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp .env.example .env

# Run migrations (using SQLite by default)
python manage.py migrate

# Create admin user
python manage.py createsuperuser

# Start server
python manage.py runserver
```

✅ Backend running at: http://localhost:8000

## 2️⃣ Frontend Setup (2 minutes)

```bash
# Open new terminal
cd EduMind-AI/frontend

# Install dependencies
npm install

# Copy environment file
cp .env.example .env

# Start development server
npm run dev
```

✅ Frontend running at: http://localhost:3000

## 3️⃣ Get Groq API Key (1 minute)

1. Visit: https://console.groq.com
2. Sign up/Login
3. Create API Key
4. Add to `backend/.env`:
   ```
   GROQ_API_KEY=your-key-here
   ```

## 4️⃣ Test the Application

1. **Visit Frontend**: http://localhost:3000
2. **Click "Get Started"** → Register as Student or Teacher
3. **Fill the form** and create account
4. **You're in!** 🎉

## 5️⃣ Access Admin Panel

- URL: http://localhost:8000/admin
- Login with superuser credentials
- Explore Django admin interface

## 🎯 Next Steps

- [x] Application running
- [ ] Read [Getting Started Guide](./docs/GETTING_STARTED.md)
- [ ] Check [Database Schema](./docs/DATABASE_SCHEMA.md)
- [ ] Explore API at http://localhost:8000/api/
- [ ] Start building features!

## 🐛 Having Issues?

**Database Error?**
```bash
python manage.py migrate
```

**Module Not Found?**
```bash
pip install -r requirements.txt
```

**Port Already in Use?**
```bash
# Use different port
python manage.py runserver 8001
```

**CORS Error?**
Check `CORS_ALLOWED_ORIGINS` in `backend/.env`

## 📚 Documentation

- [Complete Setup Guide](./docs/SETUP_GUIDE.md)
- [Getting Started](./docs/GETTING_STARTED.md)
- [Database Schema](./docs/DATABASE_SCHEMA.md)

---

**Ready to build? Let's go! 🚀**
