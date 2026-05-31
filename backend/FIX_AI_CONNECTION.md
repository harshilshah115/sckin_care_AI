# 🔧 AI Connection Issue - Quick Fix

## ❌ Problem
You're getting **503 Service Unavailable** when testing `/api/scan/test/`

This means the AI service cannot connect to Gemini API.

---

## ✅ Solution

**Run this ONE command:**

```bash
cd "d:\Harshil Projects\Sckin Care\backend"
venv\Scripts\activate
python setup_and_test_ai.py
```

This script will:
1. ✓ Check Python version
2. ✓ Install google-genai library
3. ✓ Verify .env configuration  
4. ✓ Test AI connection
5. ✓ Show detailed error if any

---

## 🎯 Alternative: Manual Fix

If script doesn't work, do these steps manually:

### Step 1: Install Library
```bash
cd "d:\Harshil Projects\Sckin Care\backend"
venv\Scripts\activate
pip install google-genai==0.2.2
```

### Step 2: Verify Installation
```bash
python -c "from google import genai; print('✓ Installed')"
```

### Step 3: Test AI Connection
```bash
python
>>> from apps.skincare_analysis.gemini_client import get_gemini_client
>>> client = get_gemini_client()
>>> client.test_connection()
```

Should return `True`

### Step 4: Restart Django
```bash
python manage.py runserver
```

### Step 5: Test Endpoint
Open: `http://127.0.0.1:8000/api/scan/test/`

Should see: `"status": "connected"`

---

## 🐛 Common Issues

### Issue 1: "google-genai not installed"
**Fix:**
```bash
pip install google-genai==0.2.2
pip list | findstr google
```

### Issue 2: "API key not configured"
**Fix:** Check `.env` file has:
```env
GEMINI_API_KEY=**************************
```

### Issue 3: "Invalid API key"
**Fix:** Get new key from: https://makersuite.google.com/app/apikey

### Issue 4: "Module not found"
**Fix:** Make sure virtual environment is activated:
```bash
venv\Scripts\activate
# You should see (venv) in prompt
```

---

## 📝 What Changed

I updated the code to give better error messages:

**Before:**
```json
{
  "success": false,
  "message": "Failed to connect"
}
```

**After:**
```json
{
  "success": false,
  "status": "error",
  "error": "google-genai library not installed",
  "message": "Please run: pip install google-genai==0.2.2",
  "traceback": "..."
}
```

Now you'll see exactly what's wrong!

---

## 🚀 Quick Test After Fix

1. **Start server:** `python manage.py runserver`
2. **Open browser:** `http://127.0.0.1:8000/api/scan/test/`
3. **Expected response:**
```json
{
  "success": true,
  "status": "connected",
  "model": "gemini-2.5-flash",
  "message": "AI service is fully operational"
}
```

---

## 💡 Need Help?

Run the diagnostic script to see detailed error:
```bash
python setup_and_test_ai.py
```

It will tell you exactly what's wrong and how to fix it!
