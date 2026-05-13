"""
Validate Gemini API Key Format
"""

import os
from dotenv import load_dotenv

print("="*60)
print("GEMINI API KEY VALIDATOR")
print("="*60)

load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')

print(f"\n[1] API Key Loaded")
print(f"    Length: {len(api_key) if api_key else 0} characters")
print(f"    Starts with: {api_key[:10] if api_key else 'N/A'}...")
print(f"    Ends with: ...{api_key[-10:] if api_key else 'N/A'}")

# Validate format
if not api_key:
    print("\n❌ ERROR: No API key found!")
    print("   Add GEMINI_API_KEY=... to .env file")
    exit(1)

if not api_key.startswith('AIza'):
    print("\n⚠️  WARNING: API key doesn't start with 'AIza'")
    print("   Google Gemini API keys typically start with 'AIzaSy...'")
    print("   Your key starts with:", api_key[:10])
    print("\n   This might not be a valid Gemini API key!")
    print("   Get a valid key from: https://aistudio.google.com/apikey")
else:
    print("\n✓ API key format looks correct")

# Check length
if len(api_key) < 30:
    print(f"\n⚠️  WARNING: API key seems too short ({len(api_key)} chars)")
    print("   Typical Gemini API keys are 39 characters")
elif len(api_key) > 50:
    print(f"\n⚠️  WARNING: API key seems too long ({len(api_key)} chars)")
else:
    print(f"✓ API key length is reasonable ({len(api_key)} chars)")

# Test with actual API call
print("\n[2] Testing API Connection...")
print("    Attempting to connect to Google Gemini...")

try:
    from google import genai
    from google.genai import types
    
    client = genai.Client(api_key=api_key)
    
    # Try a simple request
    config = types.GenerateContentConfig(
        temperature=0.7,
        max_output_tokens=50,
    )
    
    print("    Sending test request...")
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents='Say hello',
        config=config
    )
    
    print("\n✅ SUCCESS!")
    print(f"Response: {response.text[:100]}")
    
except Exception as e:
    print(f"\n❌ FAILED!")
    print(f"Error: {e}")
    print(f"Type: {type(e).__name__}")
    
    error_str = str(e).lower()
    
    print("\n🔍 Diagnosis:")
    if 'api key not valid' in error_str or 'invalid' in error_str:
        print("   → API key is INVALID")
        print("   → Get a new key: https://aistudio.google.com/apikey")
    elif '403' in error_str or 'permission' in error_str:
        print("   → API key doesn't have permission for this model")
        print("   → Try enabling Gemini API in Google Cloud Console")
    elif '404' in error_str or 'not found' in error_str:
        print("   → Model 'gemini-2.5-flash' not found")
        print("   → Try 'gemini-1.5-pro' or 'gemini-pro' instead")
    elif 'quota' in error_str or '429' in error_str:
        print("   → Rate limit exceeded")
        print("   → Wait a few minutes and try again")
    elif 'network' in error_str or 'connection' in error_str:
        print("   → Network/firewall issue")
        print("   → Check internet connection")
    else:
        print("   → Unknown error - see details above")
    
    import traceback
    print("\nFull traceback:")
    print(traceback.format_exc())

print("\n" + "="*60)
input("Press Enter to exit...")
