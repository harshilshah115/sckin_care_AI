# 🧪 Quick AI Testing Guide (No Authentication Required)

## Public Test Endpoints

These endpoints **DO NOT** require authentication - you can test them directly in your browser or with curl!

---

## ✅ Test 1: Check AI Connection

**URL:** `http://127.0.0.1:8000/api/scan/test/`

**Method:** GET

**Browser Access:** Just open the URL in your browser!

**Expected Response:**
```json
{
    "success": true,
    "status": "connected",
    "model": "gemini-2.5-flash",
    "response_time": 0.5,
    "test_response": {
        "message": "Hello"
    }
}
```

---

## ✅ Test 2: Test AI Question (Default)

**URL:** `http://127.0.0.1:8000/api/scan/test/question/`

**Method:** GET (to see instructions) or POST (to test)

**Browser Access:** 
1. Open `http://127.0.0.1:8000/api/scan/test/question/` in browser
2. You'll see a form with instructions
3. Click "POST" button and submit to test with default question

**Expected Response:**
```json
{
    "success": true,
    "message": "AI question test successful",
    "question": "What is the best way to clean oily skin?",
    "answer": "For oily skin, it's best to use a gentle gel-based cleanser...",
    "processing_time": 1.2,
    "model_used": "gemini-2.5-flash"
}
```

---

## ✅ Test 3: Test AI Question (Custom)

**Method:** POST to `http://127.0.0.1:8000/api/scan/test/question/`

**Using Browser (DRF Interface):**
1. Open `http://127.0.0.1:8000/api/scan/test/question/`
2. Scroll to the bottom form
3. Enter JSON in "Content" field:
```json
{
    "question": "How to treat acne?",
    "skin_type": "oily",
    "sensitivity": "normal",
    "concerns": ["acne"]
}
```
4. Click "POST" button

**Using Curl:**
```bash
curl -X POST http://127.0.0.1:8000/api/scan/test/question/ \
  -H "Content-Type: application/json" \
  -d '{"question": "How to treat acne?"}'
```

**Using Python:**
```python
import requests

response = requests.post(
    'http://127.0.0.1:8000/api/scan/test/question/',
    json={
        'question': 'How to remove dark circles?',
        'skin_type': 'dry',
        'sensitivity': 'high'
    }
)

print(response.json())
```

---

## 🔒 Protected Endpoints (Require Login)

These endpoints need JWT authentication:

### Login First:
```python
import requests

# 1. Login to get token
login = requests.post('http://127.0.0.1:8000/api/auth/login/', json={
    'email': 'your_email@example.com',
    'password': 'your_password'
})

token = login.json()['access']
headers = {'Authorization': f'Bearer {token}'}

# 2. Now you can use protected endpoints
question = requests.post(
    'http://127.0.0.1:8000/api/scan/ask/',
    headers=headers,
    json={'question_text': 'How to clean oily skin?'}
)

print(question.json())
```

### Upload Image:
```python
# 3. Upload skin image
with open('test_image.jpg', 'rb') as f:
    response = requests.post(
        'http://127.0.0.1:8000/api/scan/',
        headers=headers,
        files={'image': f},
        data={'scan_type': 'full_face'}
    )

print(response.json())
```

---

## 🎯 Quick Testing Steps

**Step 1:** Start Django server
```bash
cd "d:\Harshil Projects\Sckin Care\backend"
venv\Scripts\activate
python manage.py runserver
```

**Step 2:** Test AI Connection
- Open browser: `http://127.0.0.1:8000/api/scan/test/`
- Should see `"status": "connected"`

**Step 3:** Test AI Question
- Open browser: `http://127.0.0.1:8000/api/scan/test/question/`
- Click "POST" button at bottom
- Should see AI answer

**Step 4:** Test from Frontend
- Start React app: `npm run dev`
- Login and upload image or ask question

---

## ❌ Common Errors

### 401 Unauthorized
- **Cause:** Trying to access protected endpoint without login
- **Fix:** Use test endpoints OR login first to get token

### 405 Method Not Allowed
- **Cause:** Using GET on POST-only endpoint
- **Fix:** Use correct HTTP method (check endpoint docs)

### 500 Internal Server Error
- **Cause:** AI API key issue or network error
- **Fix:** 
  - Check `.env` has valid `GEMINI_API_KEY`
  - Check internet connection
  - Look at server console for detailed error

### Connection Refused
- **Cause:** Django server not running
- **Fix:** Start server with `python manage.py runserver`

---

## ✅ Success Checklist

- [ ] Server starts without errors
- [ ] `/api/scan/test/` returns `"status": "connected"`
- [ ] `/api/scan/test/question/` returns AI answer
- [ ] No FutureWarning about google.generativeai
- [ ] Frontend can upload images and ask questions

---

## 📝 Notes

- Test endpoints are **public** (no auth needed)
- Real endpoints are **protected** (need JWT token)
- All AI responses have safety filters applied
- Processing time varies (1-5 seconds typically)
- Gemini API has rate limits (60 requests/minute on free tier)
