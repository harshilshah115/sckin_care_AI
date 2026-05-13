"""
AI Setup and Test Script
Run this to install dependencies and test AI connection
"""

import sys
import os
import subprocess

def print_header(text):
    print("\n" + "="*60)
    print(text)
    print("="*60)

def print_step(num, text):
    print(f"\n[{num}] {text}")

def run_command(cmd, description):
    """Run a command and return success status"""
    try:
        print(f"Running: {cmd}")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✓ {description} - SUCCESS")
            if result.stdout:
                print(result.stdout[:500])
            return True
        else:
            print(f"✗ {description} - FAILED")
            if result.stderr:
                print(result.stderr[:500])
            return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False

def main():
    print_header("🧪 AI Backend Setup & Test")
    
    # Step 1: Check Python version
    print_step(1, "Checking Python version")
    print(f"Python version: {sys.version}")
    if sys.version_info < (3, 8):
        print("✗ Python 3.8+ required")
        return False
    print("✓ Python version OK")
    
    # Step 2: Check if we're in virtual environment
    print_step(2, "Checking virtual environment")
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    if in_venv:
        print("✓ Running in virtual environment")
    else:
        print("⚠ Not in virtual environment (this is OK if venv is activated)")
    
    # Step 3: Install/upgrade google-genai
    print_step(3, "Installing google-genai package")
    if not run_command(
        "pip install --upgrade google-genai==0.2.2",
        "Installing google-genai"
    ):
        print("\n❌ Installation failed!")
        print("Try manually: pip install google-genai==0.2.2")
        return False
    
    # Step 4: Verify installation
    print_step(4, "Verifying installation")
    try:
        from google import genai
        print(f"✓ google-genai imported successfully")
        print(f"  Module location: {genai.__file__}")
    except ImportError as e:
        print(f"✗ Failed to import google-genai: {e}")
        return False
    
    # Step 5: Check .env file
    print_step(5, "Checking .env configuration")
    env_path = os.path.join(os.path.dirname(__file__), '.env')
    if not os.path.exists(env_path):
        print(f"✗ .env file not found at {env_path}")
        return False
    
    with open(env_path, 'r') as f:
        env_content = f.read()
        if 'GEMINI_API_KEY' in env_content:
            print("✓ GEMINI_API_KEY found in .env")
            # Check if it's not empty
            for line in env_content.split('\n'):
                if line.startswith('GEMINI_API_KEY='):
                    key = line.split('=', 1)[1].strip()
                    if key and key != 'your_api_key_here':
                        print(f"✓ API key is set (length: {len(key)} chars)")
                    else:
                        print("✗ API key is empty or placeholder")
                        return False
        else:
            print("✗ GEMINI_API_KEY not found in .env")
            return False
    
    # Step 6: Load Django and test AI
    print_step(6, "Testing Django AI integration")
    try:
        # Setup Django
        sys.path.insert(0, os.path.dirname(__file__))
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skincare.settings')
        
        import django
        django.setup()
        
        print("✓ Django loaded successfully")
        
        # Import AI service
        from apps.skincare_analysis.ai_service import test_ai_connection
        
        print("\nTesting AI connection...")
        result = test_ai_connection()
        
        print("\n--- AI Connection Test Result ---")
        import json
        print(json.dumps(result, indent=2))
        
        if result.get('success') or result.get('status') == 'connected':
            print("\n✅ AI CONNECTION SUCCESSFUL!")
            return True
        else:
            print("\n❌ AI CONNECTION FAILED")
            print(f"Error: {result.get('error', result.get('message'))}")
            
            if 'traceback' in result:
                print("\n--- Error Details ---")
                print(result['traceback'])
            
            return False
            
    except Exception as e:
        print(f"\n✗ Error testing AI: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    print("\nNOTE: Make sure you're in the backend directory and venv is activated!")
    print("If not activated, run: venv\\Scripts\\activate\n")
    
    success = main()
    
    if success:
        print("\n" + "="*60)
        print("✅ ALL CHECKS PASSED!")
        print("="*60)
        print("\nYou can now:")
        print("1. Start Django: python manage.py runserver")
        print("2. Test endpoint: http://127.0.0.1:8000/api/scan/test/")
        print("3. Open test page: test_ai.html")
    else:
        print("\n" + "="*60)
        print("❌ SETUP INCOMPLETE")
        print("="*60)
        print("\nPlease fix the errors above and try again.")
    
    input("\nPress Enter to exit...")
