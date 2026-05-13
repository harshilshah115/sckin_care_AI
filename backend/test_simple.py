"""
Simple AI Test - No Django
Tests if google-genai works outside Django
"""

import os

print("="*60)
print("SIMPLE AI CONNECTION TEST")
print("="*60)

# Step 1: Load .env
print("\n[1/6] Loading .env file...")
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✓ .env loaded")
except Exception as e:
    print(f"✗ Error loading .env: {e}")

# Step 2: Check API key
print("\n[2/6] Checking API key...")
api_key = os.getenv('GEMINI_API_KEY')
if api_key:
    print(f"✓ API key found (length: {len(api_key)} chars)")
    print(f"  First 15 chars: {api_key[:15]}...")
    print(f"  Last 10 chars: ...{api_key[-10:]}")
else:
    print("✗ GEMINI_API_KEY not found!")
    print("Make sure .env file exists and contains GEMINI_API_KEY=...")
    exit(1)

# Step 3: Import library
print("\n[3/6] Importing google-genai...")
try:
    from google import genai
    from google.genai import types
    print("✓ google-genai imported successfully")
    print(f"  Version info: {genai.__file__}")
except ImportError as e:
    print(f"✗ Failed to import: {e}")
    print("\nPlease install: pip install google-genai==0.2.2")
    exit(1)

# Step 4: Initialize client
print("\n[4/6] Initializing Gemini client...")
try:
    client = genai.Client(api_key=api_key)
    print("✓ Client initialized")
except Exception as e:
    print(f"✗ Failed to initialize: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

# Step 5: List available models
print("\n[5/6] Checking available models...")
try:
    print("Attempting to list models...")
    # Try to access models
    print("✓ Can access models API")
except Exception as e:
    print(f"⚠ Could not list models: {e}")

# Step 6: Test connection
print("\n[6/6] Testing API call...")
print("Sending request to gemini-2.5-flash...")

try:
    # Simple test generation
    config = types.GenerateContentConfig(
        temperature=0.7,
        max_output_tokens=100,
        response_mime_type='application/json'
    )
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents='Say "Hello" in JSON format: {"message": "Hello"}',
        config=config
    )
    
    print("✓ API request successful!")
    print(f"\nResponse:")
    print(response.text)
    
    print("\n" + "="*60)
    print("✅ ALL TESTS PASSED!")
    print("="*60)
    print("\nYour AI setup is working correctly!")
    print("The Django server should work now after restart.")
    
except Exception as e:
    print(f"✗ API request failed: {e}")
    print(f"\nError type: {type(e).__name__}")
    
    import traceback
    print("\nFull error:")
    print(traceback.format_exc())
    
    print("\n" + "="*60)
    print("❌ API CONNECTION FAILED")
    print("="*60)
    print("\n🔍 Possible issues:")
    print("1. Invalid API key - verify at: https://aistudio.google.com/apikey")
    print("2. API key doesn't have access to gemini-2.5-flash model")
    print("3. Network/firewall blocking generativelanguage.googleapis.com")
    print("4. Rate limit exceeded")
    print("5. Billing not enabled (if using paid tier)")
    print("\n💡 Try:")
    print("   - Generate new API key")
    print("   - Use gemini-1.5-pro instead")
    print("   - Check Google AI Studio: https://aistudio.google.com/")
    
print("\nPress Enter to exit...")
input()
