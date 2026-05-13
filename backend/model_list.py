from google import genai
import os
from dotenv import load_dotenv
from pathlib import Path

# ✅ Load .env file explicitly
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

# ✅ Debug: check if API key is loaded
api_key = os.getenv("GEMINI_API_KEY")
print("API KEY LOADED:", api_key[:10] + "..." if api_key else "❌ NOT FOUND")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found. Check your .env loading.")

# ✅ Initialize client
client = genai.Client(api_key=api_key)

print("\nListing available models...\n")

try:
    models = client.models.list()

    found = False
    for m in models:
        print("👉", m.name)
        found = True

    if not found:
        print("⚠️ No models returned (check billing or API access)")

except Exception as e:
    print("❌ ERROR:", str(e))