# AI Backend API Testing Guide

## Prerequisites
1. Django server must be running: `python manage.py runserver`
2. You must have a valid JWT token (login first)

---

## Test 1: Check AI Connection

```bash
GET http://127.0.0.1:8000/api/scans/test/
```

**Expected Response:**
```json
{
    "status": "connected",
    "model": "gemini-2.5-flash",
    "test_response": {...},
    "response_time": 0.5
}
```

---

## Test 2: Ask a Skincare Question

```bash
POST http://127.0.0.1:8000/api/scan/ask/
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json

{
    "question_text": "What is the best way to clean oily skin?"
}
```

**Expected Response:**
```json
{
    "message": "Question answered successfully",
    "question": {
        "id": 1,
        "question_text": "What is the best way to clean oily skin?",
        "answer_text": "For oily skin, use a gentle gel-based cleanser...",
        "recommendations": {
            "products": [...],
            "remedies": [...]
        },
        "ai_model_used": "gemini-2.5-flash",
        "processing_time": 1.2,
        "created_at": "..."
    },
    "disclaimer": "This is educational information..."
}
```

---

## Test 3: Upload Skin Image for Analysis

```bash
POST http://127.0.0.1:8000/api/scan/
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: multipart/form-data

image: <upload_file>
scan_type: full_face
```

**Expected Response:**
```json
{
    "message": "Skin analysis completed successfully",
    "scan": {
        "id": 1,
        "image": "/media/skin_scans/image.jpg",
        "scan_type": "full_face",
        "detected_issues": [
            {
                "name": "Acne",
                "severity": "moderate",
                "confidence": 85
            }
        ],
        "severity": "moderate",
        "confidence_score": 85,
        "skin_score": 72,
        "analysis_text": "Your skin shows...",
        "recommendations": {
            "products": [...],
            "remedies": [...]
        },
        "ai_model_used": "gemini-2.5-flash",
        "processing_time": 2.5
    },
    "disclaimer": "This is not medical advice..."
}
```

---

## Error Responses

### AI Service Error
```json
{
    "message": "Scan uploaded but AI analysis failed",
    "scan": {...},
    "error": "API connection failed",
    "fallback": true
}
```

### Doctor Referral
```json
{
    "message": "Analysis complete - professional consultation recommended",
    "scan": {...},
    "refer_to_doctor": true,
    "disclaimer": "Please consult a dermatologist..."
}
```

### Safety Redirect (Questions)
```json
{
    "message": "Question answered - please consult a professional",
    "question": {...},
    "safety_redirect": true,
    "disclaimer": "This requires professional medical evaluation..."
}
```

---

## Testing with Python Requests

```python
import requests

# 1. Login to get token
login_response = requests.post('http://127.0.0.1:8000/api/auth/login/', json={
    'email': 'your_email@example.com',
    'password': 'your_password'
})
token = login_response.json()['access']

# 2. Ask a question
headers = {'Authorization': f'Bearer {token}'}
question_response = requests.post(
    'http://127.0.0.1:8000/api/scan/ask/',
    headers=headers,
    json={'question_text': 'How to treat acne?'}
)
print(question_response.json())

# 3. Upload skin image
with open('test_image.jpg', 'rb') as f:
    files = {'image': f}
    data = {'scan_type': 'full_face'}
    scan_response = requests.post(
        'http://127.0.0.1:8000/api/scan/',
        headers=headers,
        files=files,
        data=data
    )
print(scan_response.json())
```

---

## Django Shell Testing

```python
python manage.py shell

# In shell:
from apps.skincare_analysis.ai_service import test_ai_connection, answer_skincare_question

# Test connection
result = test_ai_connection()
print(result)

# Test question
answer = answer_skincare_question("How to clean oily skin?", {'skin_type': 'oily'})
print(answer)
```

---

## Common Issues

1. **"API key not found"** → Check `.env` file has `GEMINI_API_KEY`
2. **"Connection timeout"** → Check internet connection
3. **"Invalid JSON"** → AI response parsing failed, check prompts
4. **"Files.upload() error"** → Library version mismatch, reinstall google-genai
5. **"401 Unauthorized"** → JWT token expired, login again

---

## Next Steps After Testing

1. ✅ Verify all 3 tests pass
2. ✅ Test from frontend (React app)
3. ✅ Check error handling works correctly
4. ✅ Verify safety filters block dangerous content
5. ✅ Test with different skin types and questions
