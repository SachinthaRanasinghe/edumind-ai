# 🔑 How to Get Your Groq API Key

Follow these simple steps to get your free Groq API key:

## Step 1: Visit Groq Console
Go to: **https://console.groq.com**

## Step 2: Sign Up / Login
- Click **"Sign Up"** if you don't have an account
- Or **"Login"** if you already have one
- You can sign up with Google, GitHub, or email

## Step 3: Navigate to API Keys
- Once logged in, click on your profile/account
- Go to **"API Keys"** section
- Or directly visit: https://console.groq.com/keys

## Step 4: Create New API Key
- Click **"Create API Key"** button
- Give it a name (e.g., "EduMind AI Development")
- Click **"Create"**

## Step 5: Copy Your Key
- **IMPORTANT**: Copy the key immediately!
- It will only be shown once
- Store it safely

## Step 6: Add to Environment File

Open `EduMind-AI/backend/.env` and add your key:

```env
GROQ_API_KEY=gsk_your_actual_key_here
```

Replace `gsk_your_actual_key_here` with your actual key.

## Step 7: Verify It Works

```bash
cd EduMind-AI/backend
source venv/bin/activate
python -c "from ai_services.groq_client import get_groq_client; client = get_groq_client(); print('✅ Groq API is configured!')"
```

---

## 🆓 Groq Free Tier

Groq offers a generous free tier:
- **Fast inference** (much faster than OpenAI)
- **Free API access** for development
- **Multiple models** (Llama 3, Mixtral, etc.)

---

## 🔒 Security Notes

- ⚠️ Never commit your API key to git
- ✅ The `.env` file is already in `.gitignore`
- 🔄 Rotate keys regularly for production
- 📝 Use different keys for dev/production

---

## ❓ Having Issues?

1. **Key not working?** 
   - Make sure you copied it correctly
   - Check for extra spaces
   - Verify it's in the `.env` file

2. **Rate limits?**
   - Free tier has limits
   - Upgrade to paid plan if needed
   - Consider implementing request caching

3. **Can't create account?**
   - Try a different sign-up method
   - Check your email for verification
   - Contact Groq support

---

## 🎯 After Getting Your Key

Once you have your Groq API key set up:

```bash
# Test the backend
cd EduMind-AI/backend
python manage.py runserver

# In another terminal, test AI features
python manage.py shell
>>> from ai_services.groq_client import get_groq_client
>>> client = get_groq_client()
>>> client.generate_quiz_question("Python Programming", "medium")
```

---

**Ready to continue?** Once you have your key in the `.env` file, the AI features will work! 🚀
