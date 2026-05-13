# 🧴 AI Skincare Assistant

> An AI-powered skincare platform providing personalized, safe, and holistic skincare recommendations using image analysis and natural language processing.

[![Django](https://img.shields.io/badge/Django-4.x-green)](https://www.djangoproject.com/)
[![React](https://img.shields.io/badge/React-18.x-blue)](https://reactjs.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## 📑 Table of Contents

1. [Overview](#-overview)
2. [Features](#-features)
3. [Tech Stack](#-tech-stack)
4. [System Architecture](#-system-architecture)
5. [Project Structure](#-project-structure)
6. [Database Schema](#-database-schema)
7. [API Documentation](#-api-documentation)
8. [AI Integration](#-ai-integration)
9. [Frontend Architecture](#-frontend-architecture)
10. [Authentication](#-authentication)
11. [Safety & Medical Guardrails](#-safety--medical-guardrails)
12. [Installation & Setup](#-installation--setup)
13. [Environment Variables](#-environment-variables)
14. [Deployment](#-deployment)
15. [Monetization Model](#-monetization-model)
16. [Roadmap](#-roadmap)
17. [Contributing](#-contributing)
18. [License](#-license)

---

## 🎯 Overview

### Vision
Build an AI-powered skincare platform that provides **personalized, safe, and holistic skincare recommendations** using image analysis (skin photos) and natural language queries (user questions).

### Mission
Enable users to understand and improve their skin health by combining AI insights, dermatology-backed knowledge, and personalized product recommendations.

### Core Value Proposition
Users can:
- Upload a skin image OR ask a question
- Receive:
  - Skin issue analysis
  - Natural remedies
  - Cosmetic product suggestions
  - Safe OTC guidance (non-prescriptive)

---

## ✨ Features

### Core Features

| Feature | Description |
|---------|-------------|
| **🔐 Authentication** | Signup/Login with Email/Social, profile management, skin profile setup |
| **📸 AI Skin Scan** | Upload skin images for AI analysis with issue detection and severity levels |
| **💬 AI Chat System** | Ask skincare questions and get personalized answers |
| **🎁 Recommendation Engine** | Natural remedies, cosmetic products, and safe OTC suggestions |
| **📅 Routine Generator** | Personalized morning/night routines and weekly care plans |
| **📊 Progress Tracking** | Upload images over time, compare results, track improvements |
| **💾 Saved Recommendations** | Bookmark products and save routines |
| **📜 History Dashboard** | View past scans, questions, and recommendations timeline |

### User Personas

| Persona | Description |
|---------|-------------|
| **End Users** | People with acne, pigmentation, oily/dry skin; teenagers & young adults; skincare beginners |
| **Advanced Users** | Skincare enthusiasts tracking long-term skin improvement |
| **Business Users** | Skincare brands, dermatology clinics (future) |

---

## 🛠 Tech Stack

### Frontend
| Technology | Purpose |
|------------|---------|
| React (Vite) | UI Framework |
| Normal CSS | Styling (Flexbox, Grid) |
| React Hooks/Context API | State Management |
| Axios/Fetch | API Communication |

### Backend
| Technology | Purpose |
|------------|---------|
| Django | Web Framework |
| Django REST Framework | API Development |
| SimpleJWT | Authentication |
| SQLite | Database (MVP) |
| Local Storage | Media Storage (MVP) |

### AI Integration
| Service | Purpose | Tier |
|---------|---------|------|
| **xAI Grok API** | Primary AI (Text + Reasoning) | Free |
| **Hugging Face** | Image Classification, Text Generation | Free |
| **Google Gemini** | Multimodal Support | Free (Limited) |
| **OpenAI** | Best Accuracy (Optional) | Paid |

---

## 🏗 System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                           │
│                     (React + Vite + CSS)                        │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────────┐
│                     DJANGO REST API                             │
│              (Authentication, Business Logic)                   │
└─────────────────────────┬───────────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
┌─────────────────┐ ┌───────────────┐ ┌───────────────────────────┐
│   AI LAYER      │ │  RAG LAYER    │ │      DATABASE             │
│ (Grok/HF/Gemini)│ │ (FAISS/Chroma)│ │      (SQLite)             │
└─────────────────┘ └───────────────┘ └───────────────────────────┘
```

### End-to-End Flow

```
User Registers/Login
        ↓
Uploads Image / Asks Question
        ↓
Frontend sends request to Django
        ↓
Django calls AI API
        ↓
AI returns response
        ↓
Backend processes + adds recommendations
        ↓
Safety Filter Layer validates output
        ↓
Save in database
        ↓
Return to frontend
        ↓
Display results with disclaimer
```

---

## 📁 Project Structure

### Backend (Django)

```
skincare_backend/
│
├── manage.py                    # Django management script
├── requirements.txt             # Python dependencies
├── .env                         # Environment variables
│
├── skincare/                    # Main project config
│   ├── __init__.py
│   ├── settings.py              # Django settings
│   ├── urls.py                  # Root URL configuration
│   ├── wsgi.py
│   └── asgi.py
│
├── apps/                        # Django applications
│   │
│   ├── users/                   # User management
│   │   ├── models.py            # User model
│   │   ├── views.py             # Auth views
│   │   ├── serializers.py       # DRF serializers
│   │   ├── urls.py
│   │   └── admin.py
│   │
│   ├── skincare_analysis/       # Skin scan module
│   │   ├── models.py            # SkinScan model
│   │   ├── views.py             # Scan views
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── ai_service.py        # AI API integration
│   │
│   ├── recommendations/         # Recommendation engine
│   │   ├── models.py            # Recommendation model
│   │   ├── views.py
│   │   ├── serializers.py
│   │   ├── urls.py
│   │   └── engine.py            # Recommendation logic
│   │
│   ├── history/                 # History tracking
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── serializers.py
│   │   └── urls.py
│   │
│   └── products/                # Product catalog
│       ├── models.py            # Product model
│       ├── views.py
│       ├── serializers.py
│       └── urls.py
│
├── media/                       # Uploaded images
│   └── skin_scans/
│
└── static/                      # Static files
```

### Frontend (React)

```
skincare-frontend/
│
├── index.html
├── package.json
├── vite.config.js
│
├── public/
│   └── assets/                  # Static assets
│
└── src/
    │
    ├── main.jsx                 # Entry point
    ├── App.jsx                  # Root component
    │
    ├── components/              # Reusable components
    │   ├── Navbar/
    │   │   ├── Navbar.jsx
    │   │   └── Navbar.css
    │   ├── ImageUpload/
    │   │   ├── ImageUpload.jsx
    │   │   └── ImageUpload.css
    │   ├── ResultCard/
    │   │   ├── ResultCard.jsx
    │   │   └── ResultCard.css
    │   ├── ProductCard/
    │   │   ├── ProductCard.jsx
    │   │   └── ProductCard.css
    │   └── Loader/
    │       ├── Loader.jsx
    │       └── Loader.css
    │
    ├── pages/                   # Page components
    │   ├── Home/
    │   ├── Login/
    │   ├── Register/
    │   ├── Dashboard/
    │   ├── SkinScan/
    │   ├── AskQuestion/
    │   └── History/
    │
    ├── services/                # API services
    │   ├── api.js               # Axios instance
    │   ├── authService.js
    │   ├── scanService.js
    │   └── questionService.js
    │
    ├── context/                 # React Context
    │   └── AuthContext.jsx
    │
    └── styles/                  # Global styles
        ├── global.css
        └── variables.css
```

---

## 🗄 Database Schema

### Entity Relationship Diagram

```
┌──────────────┐       ┌──────────────┐       ┌──────────────────┐
│    User      │       │   SkinScan   │       │   Recommendation │
├──────────────┤       ├──────────────┤       ├──────────────────┤
│ id (PK)      │──┐    │ id (PK)      │──┐    │ id (PK)          │
│ name         │  │    │ user (FK)    │  │    │ user (FK)        │
│ email        │  └───>│ image        │  └───>│ scan (FK)        │
│ password     │       │ result_text  │       │ question (FK)    │
│ skin_type    │       │ detected_issue│      │ products (M2M)   │
│ allergies    │       │ severity     │       │ natural_remedies │
│ created_at   │       │ confidence   │       │ created_at       │
└──────────────┘       │ created_at   │       └──────────────────┘
                       └──────────────┘
        │                                              │
        │              ┌──────────────┐                │
        │              │   Question   │                │
        │              ├──────────────┤                │
        └─────────────>│ id (PK)      │<───────────────┘
                       │ user (FK)    │
                       │ question     │
                       │ answer       │
                       │ created_at   │
                       └──────────────┘

┌──────────────┐
│   Product    │
├──────────────┤
│ id (PK)      │
│ name         │
│ category     │
│ ingredients  │
│ skin_type    │
│ price        │
│ affiliate_url│
└──────────────┘
```

### Model Definitions

#### User Model
```python
class User(AbstractUser):
    SKIN_TYPES = [
        ('oily', 'Oily'),
        ('dry', 'Dry'),
        ('combination', 'Combination'),
        ('normal', 'Normal'),
        ('sensitive', 'Sensitive'),
    ]
    
    skin_type = models.CharField(max_length=20, choices=SKIN_TYPES, null=True)
    allergies = models.TextField(blank=True)
    sensitivity_level = models.IntegerField(default=1)  # 1-5 scale
    created_at = models.DateTimeField(auto_now_add=True)
```

#### SkinScan Model
```python
class SkinScan(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='skin_scans/')
    result_text = models.TextField()
    detected_issue = models.CharField(max_length=100)
    severity = models.CharField(max_length=20)  # mild, moderate, severe
    confidence_score = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)
```

#### Question Model
```python
class Question(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
```

#### Product Model
```python
class Product(models.Model):
    CATEGORIES = [
        ('face_wash', 'Face Wash'),
        ('moisturizer', 'Moisturizer'),
        ('sunscreen', 'Sunscreen'),
        ('serum', 'Serum'),
        ('toner', 'Toner'),
    ]
    
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=50, choices=CATEGORIES)
    ingredients = models.TextField()
    suitable_skin_types = models.JSONField()  # ['oily', 'combination']
    price = models.DecimalField(max_digits=10, decimal_places=2)
    affiliate_url = models.URLField(blank=True)
```

#### Recommendation Model
```python
class Recommendation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    scan = models.ForeignKey(SkinScan, null=True, on_delete=models.SET_NULL)
    question = models.ForeignKey(Question, null=True, on_delete=models.SET_NULL)
    products = models.ManyToManyField(Product)
    natural_remedies = models.JSONField()  # List of remedies
    otc_suggestions = models.JSONField()   # Safe OTC ingredients
    routine = models.JSONField(null=True)  # Morning/Night routine
    created_at = models.DateTimeField(auto_now_add=True)
```

---

## 📡 API Documentation

### Base URL
```
Development: http://localhost:8000/api/
Production:  https://your-domain.com/api/
```

### Authentication Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/auth/register/` | User registration | No |
| POST | `/auth/login/` | User login (returns JWT) | No |
| POST | `/auth/token/refresh/` | Refresh access token | No |
| GET | `/auth/profile/` | Get user profile | Yes |
| PUT | `/auth/profile/` | Update user profile | Yes |

#### Register Request
```json
POST /api/auth/register/
{
    "email": "user@example.com",
    "password": "securepassword123",
    "name": "John Doe",
    "skin_type": "oily",
    "allergies": "none"
}
```

#### Login Response
```json
{
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "name": "John Doe",
        "skin_type": "oily"
    }
}
```

### Skin Scan Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/scan/` | Upload and analyze skin image | Yes |
| GET | `/scan/` | List user's scans | Yes |
| GET | `/scan/{id}/` | Get specific scan details | Yes |
| DELETE | `/scan/{id}/` | Delete a scan | Yes |

#### Scan Request
```json
POST /api/scan/
Content-Type: multipart/form-data

{
    "image": <file>
}
```

Optional personalization fields (multipart/form-data):

```
age=24
skin_type=oily
sleep_hours=7.5
water_intake=2
```

#### Scan Response
```json
{
    "id": 1,
    "detected_issue": "Mild Acne",
    "severity": "mild",
    "confidence_score": 0.87,
    "analysis": {
        "description": "Light acne detected on forehead and chin area.",
        "causes": ["Excess oil production", "Hormonal changes"],
        "recommendations": {
            "natural_remedies": [
                {
                    "name": "Tea Tree Oil",
                    "usage": "Apply diluted tea tree oil on affected areas",
                    "frequency": "Twice daily"
                },
                {
                    "name": "Aloe Vera Gel",
                    "usage": "Apply fresh aloe vera gel as a mask",
                    "frequency": "Once daily"
                }
            ],
            "products": [
                {
                    "id": 1,
                    "name": "Salicylic Acid Face Wash",
                    "category": "face_wash"
                }
            ],
            "otc_ingredients": ["Salicylic Acid 2%", "Niacinamide 5%"]
        },
        "routine": {
            "morning": ["Gentle cleanser", "Niacinamide serum", "Moisturizer", "Sunscreen"],
            "night": ["Oil-based cleanser", "Salicylic acid treatment", "Moisturizer"]
        }
    },
    "disclaimer": "This is not a medical diagnosis. Please consult a dermatologist for serious conditions.",
    "created_at": "2026-04-05T10:30:00Z"
}
```

### Question Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| POST | `/ask/` | Ask a skincare question | Yes |
| GET | `/ask/` | List user's questions | Yes |
| GET | `/ask/{id}/` | Get specific Q&A | Yes |

#### Ask Request
```json
POST /api/ask/
{
    "question": "How to remove dark circles naturally?"
}
```

#### Ask Response
```json
{
    "id": 1,
    "question": "How to remove dark circles naturally?",
    "answer": {
        "explanation": "Dark circles can be caused by lack of sleep, genetics, or dehydration...",
        "steps": [
            "Get adequate sleep (7-8 hours)",
            "Stay hydrated",
            "Use cold compress",
            "Apply cucumber slices"
        ],
        "natural_remedies": [
            {
                "name": "Cold Tea Bags",
                "instructions": "Place cold green tea bags on eyes for 15 minutes"
            },
            {
                "name": "Almond Oil Massage",
                "instructions": "Gently massage almond oil around eyes before bed"
            }
        ],
        "product_suggestions": [
            {
                "id": 5,
                "name": "Vitamin C Eye Cream",
                "category": "eye_care"
            }
        ]
    },
    "created_at": "2026-04-05T10:35:00Z"
}
```

### History Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/history/` | Get all user history | Yes |
| GET | `/history/scans/` | Get scan history | Yes |
| GET | `/history/questions/` | Get question history | Yes |

### Product Endpoints

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| GET | `/products/` | List all products | No |
| GET | `/products/{id}/` | Get product details | No |
| GET | `/products/?skin_type=oily` | Filter by skin type | No |
| GET | `/products/?category=moisturizer` | Filter by category | No |

---

## 🤖 AI Integration

### AI Processing Pipeline

```
User Input (Image/Text)
        ↓
┌───────────────────────┐
│  Input Validation     │
│  - Image size/type    │
│  - Text sanitization  │
└───────────────────────┘
        ↓
┌───────────────────────┐
│  AI API Call          │
│  - Grok API (Primary) │
│  - Fallback to HF     │
└───────────────────────┘
        ↓
┌───────────────────────┐
│  RAG Enhancement      │  (Phase 2)
│  - Vector DB search   │
│  - Knowledge merge    │
└───────────────────────┘
        ↓
┌───────────────────────┐
│  Response Processing  │
│  - Parse AI output    │
│  - Add products       │
└───────────────────────┘
        ↓
┌───────────────────────┐
│  Safety Filter        │
│  - Block unsafe       │
│  - Add disclaimers    │
└───────────────────────┘
        ↓
Final Response
```

### Sample AI Prompt (Image Analysis)

```python
SKIN_ANALYSIS_PROMPT = """
Analyze this skin image and provide a detailed assessment.

OUTPUT FORMAT (JSON):
{
    "detected_issue": "Issue name",
    "severity": "mild/moderate/severe",
    "confidence": 0.0-1.0,
    "description": "Detailed description",
    "causes": ["cause1", "cause2"],
    "natural_remedies": [
        {"name": "Remedy", "usage": "How to use", "frequency": "How often"}
    ],
    "cosmetic_suggestions": ["Product type 1", "Product type 2"],
    "safe_otc_ingredients": ["Ingredient 1", "Ingredient 2"],
    "morning_routine": ["Step 1", "Step 2"],
    "night_routine": ["Step 1", "Step 2"]
}

IMPORTANT RULES:
1. Do NOT provide medical diagnosis
2. Do NOT prescribe medications
3. Only suggest safe, commonly available ingredients
4. If condition appears serious, recommend dermatologist consultation
5. Include disclaimer in response
"""
```

### Sample AI Prompt (Question)

```python
QUESTION_PROMPT = """
You are a helpful skincare assistant. Answer the user's question.

User Skin Profile:
- Skin Type: {skin_type}
- Allergies: {allergies}
- Sensitivity: {sensitivity_level}

Question: {user_question}

Provide:
1. Clear explanation
2. Step-by-step guidance
3. Natural home remedies
4. Product ingredient suggestions (not specific brands)
5. Any precautions

RULES:
- Be safe and conservative
- No medical advice
- No prescription drugs
- Recommend dermatologist for serious concerns
"""
```

### AI Service Implementation

```python
# apps/skincare_analysis/ai_service.py

import os
import requests
from django.conf import settings

class AIService:
    def __init__(self):
        self.grok_api_key = settings.GROK_API_KEY
        self.grok_endpoint = "https://api.x.ai/v1/chat/completions"
        
    def analyze_image(self, image_path: str, user_profile: dict) -> dict:
        """Analyze skin image using AI API"""
        
        # Encode image to base64
        with open(image_path, 'rb') as f:
            image_data = base64.b64encode(f.read()).decode()
        
        payload = {
            "model": "grok-vision-beta",
            "messages": [
                {
                    "role": "system",
                    "content": SKIN_ANALYSIS_PROMPT
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}},
                        {"type": "text", "text": f"User skin type: {user_profile.get('skin_type', 'unknown')}"}
                    ]
                }
            ]
        }
        
        response = requests.post(
            self.grok_endpoint,
            headers={"Authorization": f"Bearer {self.grok_api_key}"},
            json=payload
        )
        
        return self._process_response(response.json())
    
    def answer_question(self, question: str, user_profile: dict) -> dict:
        """Answer skincare question using AI"""
        
        prompt = QUESTION_PROMPT.format(
            skin_type=user_profile.get('skin_type', 'unknown'),
            allergies=user_profile.get('allergies', 'none'),
            sensitivity_level=user_profile.get('sensitivity_level', 1),
            user_question=question
        )
        
        payload = {
            "model": "grok-beta",
            "messages": [
                {"role": "system", "content": prompt},
                {"role": "user", "content": question}
            ]
        }
        
        response = requests.post(
            self.grok_endpoint,
            headers={"Authorization": f"Bearer {self.grok_api_key}"},
            json=payload
        )
        
        return self._process_response(response.json())
    
    def _process_response(self, response: dict) -> dict:
        """Process and validate AI response"""
        # Parse response
        # Apply safety filters
        # Add disclaimers
        return processed_response
```

### RAG System (Phase 2)

```python
# apps/recommendations/rag_service.py

from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceEmbeddings

class RAGService:
    def __init__(self):
        self.embeddings = HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2"
        )
        self.vector_store = FAISS.load_local("knowledge_base", self.embeddings)
    
    def retrieve_context(self, query: str, k: int = 5) -> list:
        """Retrieve relevant skincare knowledge"""
        docs = self.vector_store.similarity_search(query, k=k)
        return [doc.page_content for doc in docs]
    
    def enhance_response(self, ai_response: dict, query: str) -> dict:
        """Enhance AI response with RAG context"""
        context = self.retrieve_context(query)
        # Merge context with AI response
        return enhanced_response
```

---

## 🎨 Frontend Architecture

### Component Hierarchy

```
App
├── Navbar
├── Routes
│   ├── Home
│   │   ├── Hero
│   │   ├── Features
│   │   └── CTA
│   │
│   ├── Login
│   │   └── LoginForm
│   │
│   ├── Register
│   │   └── RegisterForm
│   │
│   ├── Dashboard (Protected)
│   │   ├── WelcomeCard
│   │   ├── QuickActions
│   │   ├── RecentScans
│   │   └── RecentQuestions
│   │
│   ├── SkinScan (Protected)
│   │   ├── ImageUpload
│   │   ├── Loader
│   │   └── ResultCard
│   │       ├── IssueDetails
│   │       ├── RemediesList
│   │       ├── ProductSuggestions
│   │       └── RoutineDisplay
│   │
│   ├── AskQuestion (Protected)
│   │   ├── QuestionInput
│   │   ├── Loader
│   │   └── AnswerCard
│   │
│   └── History (Protected)
│       ├── ScanHistory
│       └── QuestionHistory
│
└── Footer
```

### Sample Component

```jsx
// src/components/ImageUpload/ImageUpload.jsx

import { useState, useRef } from 'react';
import './ImageUpload.css';

function ImageUpload({ onUpload, isLoading }) {
    const [preview, setPreview] = useState(null);
    const [dragActive, setDragActive] = useState(false);
    const inputRef = useRef(null);

    const handleFile = (file) => {
        if (file && file.type.startsWith('image/')) {
            setPreview(URL.createObjectURL(file));
            onUpload(file);
        }
    };

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(e.type === 'dragenter' || e.type === 'dragover');
    };

    const handleDrop = (e) => {
        e.preventDefault();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            handleFile(e.dataTransfer.files[0]);
        }
    };

    return (
        <div 
            className={`upload-container ${dragActive ? 'drag-active' : ''}`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
        >
            {preview ? (
                <div className="preview-container">
                    <img src={preview} alt="Preview" className="preview-image" />
                    <button 
                        className="remove-btn"
                        onClick={() => setPreview(null)}
                    >
                        Remove
                    </button>
                </div>
            ) : (
                <div className="upload-placeholder">
                    <div className="upload-icon">📸</div>
                    <p>Drag & drop your skin image here</p>
                    <p className="or-text">or</p>
                    <button 
                        className="browse-btn"
                        onClick={() => inputRef.current.click()}
                    >
                        Browse Files
                    </button>
                </div>
            )}
            
            <input
                ref={inputRef}
                type="file"
                accept="image/*"
                onChange={(e) => handleFile(e.target.files[0])}
                hidden
            />
            
            {isLoading && (
                <div className="loading-overlay">
                    <div className="spinner"></div>
                    <p>Analyzing your skin...</p>
                </div>
            )}
        </div>
    );
}

export default ImageUpload;
```

### Sample CSS

```css
/* src/components/ImageUpload/ImageUpload.css */

.upload-container {
    width: 100%;
    max-width: 500px;
    min-height: 300px;
    border: 2px dashed #ccc;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
    transition: all 0.3s ease;
    background: #fafafa;
}

.upload-container.drag-active {
    border-color: #4a90d9;
    background: #f0f7ff;
}

.upload-placeholder {
    text-align: center;
    padding: 40px;
}

.upload-icon {
    font-size: 48px;
    margin-bottom: 16px;
}

.browse-btn {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 8px;
    cursor: pointer;
    font-size: 16px;
    margin-top: 16px;
    transition: transform 0.2s ease;
}

.browse-btn:hover {
    transform: scale(1.05);
}

.preview-container {
    position: relative;
    width: 100%;
    height: 100%;
}

.preview-image {
    width: 100%;
    height: 300px;
    object-fit: cover;
    border-radius: 10px;
}

.loading-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(255, 255, 255, 0.9);
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    border-radius: 12px;
}

.spinner {
    width: 40px;
    height: 40px;
    border: 4px solid #f3f3f3;
    border-top: 4px solid #667eea;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
```

### API Service Layer

```javascript
// src/services/api.js

import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        'Content-Type': 'application/json',
    },
});

// Request interceptor - add auth token
api.interceptors.request.use((config) => {
    const token = localStorage.getItem('access_token');
    if (token) {
        config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});

// Response interceptor - handle token refresh
api.interceptors.response.use(
    (response) => response,
    async (error) => {
        if (error.response?.status === 401) {
            const refreshToken = localStorage.getItem('refresh_token');
            if (refreshToken) {
                try {
                    const response = await axios.post(`${API_BASE_URL}/auth/token/refresh/`, {
                        refresh: refreshToken
                    });
                    localStorage.setItem('access_token', response.data.access);
                    error.config.headers.Authorization = `Bearer ${response.data.access}`;
                    return api.request(error.config);
                } catch (refreshError) {
                    localStorage.removeItem('access_token');
                    localStorage.removeItem('refresh_token');
                    window.location.href = '/login';
                }
            }
        }
        return Promise.reject(error);
    }
);

export default api;
```

```javascript
// src/services/scanService.js

import api from './api';

export const scanService = {
    uploadScan: async (imageFile) => {
        const formData = new FormData();
        formData.append('image', imageFile);
        
        const response = await api.post('/scan/', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
        });
        return response.data;
    },
    
    getScanHistory: async () => {
        const response = await api.get('/scan/');
        return response.data;
    },
    
    getScanById: async (id) => {
        const response = await api.get(`/scan/${id}/`);
        return response.data;
    },
    
    deleteScan: async (id) => {
        await api.delete(`/scan/${id}/`);
    }
};
```

---

## 🔐 Authentication

### JWT Authentication Flow

```
┌──────────────┐         ┌──────────────┐         ┌──────────────┐
│    Client    │         │    Server    │         │   Database   │
└──────┬───────┘         └──────┬───────┘         └──────┬───────┘
       │                        │                        │
       │  POST /auth/login/     │                        │
       │  {email, password}     │                        │
       │───────────────────────>│                        │
       │                        │  Verify credentials    │
       │                        │───────────────────────>│
       │                        │<───────────────────────│
       │                        │                        │
       │  {access, refresh}     │                        │
       │<───────────────────────│                        │
       │                        │                        │
       │  Store tokens in       │                        │
       │  localStorage          │                        │
       │                        │                        │
       │  GET /api/scan/        │                        │
       │  Authorization: Bearer │                        │
       │───────────────────────>│                        │
       │                        │  Validate JWT          │
       │                        │  Return data           │
       │<───────────────────────│                        │
       │                        │                        │
```

### Token Configuration

```python
# settings.py

from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}
```

### Protected Routes (React)

```jsx
// src/components/ProtectedRoute.jsx

import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

function ProtectedRoute({ children }) {
    const { isAuthenticated, isLoading } = useAuth();
    const location = useLocation();

    if (isLoading) {
        return <div className="loading">Loading...</div>;
    }

    if (!isAuthenticated) {
        return <Navigate to="/login" state={{ from: location }} replace />;
    }

    return children;
}

export default ProtectedRoute;
```

---

## 🛡 Safety & Medical Guardrails

### Disclaimer System

All AI responses MUST include:

```
⚠️ DISCLAIMER: This is not a medical diagnosis. The information provided 
is for educational purposes only. Please consult a qualified dermatologist 
for proper diagnosis and treatment of skin conditions.
```

### Risk Detection Layer

```python
# apps/skincare_analysis/safety.py

SERIOUS_CONDITIONS = [
    'melanoma', 'skin cancer', 'severe infection', 
    'psoriasis', 'eczema (severe)', 'rosacea',
    'herpes', 'shingles', 'cellulitis'
]

BANNED_SUGGESTIONS = [
    'prescription', 'antibiotic', 'steroid',
    'retinoid (prescription)', 'hydroquinone > 2%',
    'tretinoin', 'isotretinoin', 'accutane'
]

class SafetyFilter:
    def check_response(self, ai_response: dict) -> dict:
        """Validate and filter AI response for safety"""
        
        # Check for serious conditions
        if self._detect_serious_condition(ai_response):
            ai_response['warning'] = {
                'level': 'HIGH',
                'message': 'This condition may require professional medical attention. Please consult a dermatologist immediately.'
            }
        
        # Remove any banned suggestions
        ai_response = self._filter_banned_content(ai_response)
        
        # Add standard disclaimer
        ai_response['disclaimer'] = self.get_disclaimer()
        
        return ai_response
    
    def _detect_serious_condition(self, response: dict) -> bool:
        detected = response.get('detected_issue', '').lower()
        return any(condition in detected for condition in SERIOUS_CONDITIONS)
    
    def _filter_banned_content(self, response: dict) -> dict:
        # Filter out any prescription medications
        # Filter out dangerous ingredient suggestions
        return response
    
    def get_disclaimer(self) -> str:
        return "This is not a medical diagnosis. Please consult a dermatologist for serious conditions."
```

### Content Validation Rules

| Category | Allowed | Not Allowed |
|----------|---------|-------------|
| **Ingredients** | Salicylic acid ≤2%, Niacinamide, Vitamin C, Hyaluronic acid | Prescription retinoids, Hydroquinone >2%, Steroids |
| **Advice** | General skincare tips, Natural remedies, OTC products | Medical diagnosis, Drug prescriptions, Treatment claims |
| **Conditions** | Mild acne, Dry skin, Oily skin, Dark spots | Cancer diagnosis, Severe infections, Autoimmune conditions |

---

## 🚀 Installation & Setup

### Prerequisites

- Python 3.10+
- Node.js 18+
- npm or yarn

### Backend Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/skincare-assistant.git
cd skincare-assistant

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
cd skincare_backend
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your API keys

# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (for admin)
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

### Frontend Setup

```bash
# Navigate to frontend directory
cd skincare-frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env with your API URL

# Run development server
npm run dev
```

### Requirements Files

**requirements.txt (Backend)**
```
Django>=4.2,<5.0
djangorestframework>=3.14.0
djangorestframework-simplejwt>=5.3.0
django-cors-headers>=4.3.0
Pillow>=10.0.0
requests>=2.31.0
python-dotenv>=1.0.0
gunicorn>=21.0.0

# Optional for RAG (Phase 2)
# langchain>=0.1.0
# faiss-cpu>=1.7.4
# sentence-transformers>=2.2.2
```

**package.json (Frontend)**
```json
{
  "name": "skincare-frontend",
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "preview": "vite preview"
  },
  "dependencies": {
    "axios": "^1.6.0",
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.20.0"
  },
  "devDependencies": {
    "@vitejs/plugin-react": "^4.2.0",
    "vite": "^5.0.0"
  }
}
```

---

## ⚙️ Environment Variables

### Backend (.env)

```env
# Django Settings
SECRET_KEY=your-super-secret-django-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database (MVP uses SQLite by default)
# DATABASE_URL=mysql://user:pass@localhost:3306/skincare_db

# AI API Keys
GROK_API_KEY=your-grok-api-key
HUGGINGFACE_API_KEY=your-hf-api-key
GEMINI_API_KEY=your-gemini-api-key

# JWT Settings
JWT_SECRET_KEY=your-jwt-secret

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:5173,http://127.0.0.1:5173
```

### Frontend (.env)

```env
VITE_API_URL=http://localhost:8000/api
VITE_APP_NAME=AI Skincare Assistant
```

---

## 🌐 Deployment

### Backend Deployment (Render/Railway)

```yaml
# render.yaml
services:
  - type: web
    name: skincare-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: gunicorn skincare.wsgi:application
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: SECRET_KEY
        generateValue: true
      - key: DEBUG
        value: false
```

### Frontend Deployment (Vercel/Netlify)

```json
// vercel.json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "rewrites": [
    { "source": "/(.*)", "destination": "/index.html" }
  ]
}
```

### Production Checklist

- [ ] Set `DEBUG=False` in production
- [ ] Use proper secret keys (not defaults)
- [ ] Configure HTTPS
- [ ] Set up proper CORS origins
- [ ] Configure media storage (AWS S3)
- [ ] Set up database backups
- [ ] Configure logging and monitoring
- [ ] Add rate limiting

---

## 💰 Monetization Model

### Revenue Streams

| Model | Description | Implementation |
|-------|-------------|----------------|
| **Freemium** | Free: 5 scans/month, Paid: Unlimited | Track usage in database |
| **Subscription** | ₹99-₹299/month tiers | Stripe/Razorpay integration |
| **Affiliate** | Commission on product links | Track clicks & conversions |
| **B2B API** | White-label for brands | API key authentication |

### Subscription Tiers

| Tier | Price | Features |
|------|-------|----------|
| **Free** | ₹0 | 5 scans/month, Basic Q&A |
| **Basic** | ₹99/month | 30 scans, Full Q&A, History |
| **Premium** | ₹299/month | Unlimited scans, Priority AI, Expert routines |

---

## 📈 Roadmap

### Phase 1: MVP (Weeks 1-4)
- [x] Project setup
- [ ] User authentication (JWT)
- [ ] Basic image upload
- [ ] Grok API integration
- [ ] Simple recommendations
- [ ] Basic UI (React + CSS)

### Phase 2: Enhanced Features (Weeks 5-8)
- [ ] RAG knowledge system
- [ ] Personalization engine
- [ ] Affiliate product links
- [ ] Progress tracking
- [ ] History dashboard

### Phase 3: Monetization (Weeks 9-12)
- [ ] Subscription system
- [ ] Payment integration
- [ ] Usage tracking
- [ ] Admin analytics

### Phase 4: Scale (Months 4-6)
- [ ] Custom AI model training
- [ ] B2B API platform
- [ ] AR visualization
- [ ] Community features
- [ ] Multilingual support

---

## 🧪 Testing

### Backend Tests

```bash
# Run all tests
python manage.py test

# Run specific app tests
python manage.py test apps.users
python manage.py test apps.skincare_analysis

# Run with coverage
coverage run manage.py test
coverage report
```

### Frontend Tests

```bash
# Run tests
npm test

# Run with coverage
npm run test:coverage
```

---

## 📊 Admin Panel Features

### User Management
- View all registered users
- Manage user accounts (activate/deactivate)
- View user activity logs

### Content Management
- Add/edit skincare articles
- Manage natural remedies database
- Update product catalog

### AI Monitoring
- Track AI response quality
- Flag and review unsafe outputs
- Monitor API usage and costs

### Analytics Dashboard
- Daily/monthly active users
- Scan and question counts
- Revenue tracking
- Conversion metrics

---

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

### Code Style

- **Python**: Follow PEP 8, use Black formatter
- **JavaScript**: Use ESLint with Airbnb config
- **CSS**: Use BEM naming convention

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- xAI for Grok API
- Hugging Face for open-source models
- Django & React communities

---

## 📞 Support

For support, email support@skincare-ai.com or join our Discord community.

---

<div align="center">
  <p>Built with ❤️ for healthier skin</p>
  <p>© 2026 AI Skincare Assistant. All rights reserved.</p>
</div>
