"""
Quick API Test - Shows detailed error
"""

import os
import sys

# Setup Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skincare.settings')

import django
django.setup()

from apps.skincare_analysis.ai_service import test_ai_connection
import json

print("\n" + "="*60)
print("TESTING AI CONNECTION WITH DETAILED ERRORS")
print("="*60)

result = test_ai_connection()

print("\n" + json.dumps(result, indent=2))

if result.get('success'):
    print("\n✅ SUCCESS - AI is working!")
else:
    print("\n❌ FAILED - See error details above")
    
    if 'error' in result:
        print(f"\n🔍 Error: {result['error']}")
    if 'error_type' in result:
        print(f"🔍 Error Type: {result['error_type']}")
    if 'traceback' in result:
        print(f"\n📋 Full Traceback:\n{result['traceback']}")

print("\n" + "="*60)
