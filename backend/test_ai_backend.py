"""
Test AI Backend Functionality
Run this script to test if Gemini AI is working correctly
"""

import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'skincare.settings')
django.setup()

from apps.skincare_analysis.ai_service import test_ai_connection, answer_skincare_question
from apps.skincare_analysis.gemini_client import get_gemini_client
import json


def test_connection():
    """Test basic AI connection"""
    print("\n" + "="*60)
    print("TEST 1: Testing AI Connection")
    print("="*60)
    
    result = test_ai_connection()
    print(f"✓ Connection Status: {result['status']}")
    print(f"✓ AI Model: {result['model']}")
    print(f"✓ Response Time: {result['response_time']:.3f}s")
    
    if result['test_response']:
        print(f"✓ Test Response: {json.dumps(result['test_response'], indent=2)}")
    
    return result['status'] == 'connected'


def test_text_generation():
    """Test simple text generation"""
    print("\n" + "="*60)
    print("TEST 2: Testing Text Generation (Simple Question)")
    print("="*60)
    
    question = "What is the best way to clean oily skin?"
    user_profile = {
        'skin_type': 'oily',
        'sensitivity': 'normal',
        'concerns': ['acne', 'large_pores']
    }
    
    print(f"Question: {question}")
    print(f"User Profile: {user_profile}")
    print("\nGenerating answer...")
    
    answer = answer_skincare_question(question, user_profile)
    
    if answer.get('error'):
        print(f"✗ Error: {answer['message']}")
        return False
    
    print(f"\n✓ Answer Generated!")
    print(f"✓ Model Used: {answer.get('ai_model_used', os.getenv('AI_MODEL', 'gemini-2.0-flash'))}")
    print(f"✓ Processing Time: {answer['processing_time']:.3f}s")
    print(f"\n--- Answer Text ---")
    print(answer['answer_text'][:500] + "..." if len(answer['answer_text']) > 500 else answer['answer_text'])
    
    if answer.get('recommendations'):
        print(f"\n--- Recommendations ---")
        print(json.dumps(answer['recommendations'], indent=2)[:500])
    
    return True


def test_image_analysis():
    """Test image analysis (requires a test image)"""
    print("\n" + "="*60)
    print("TEST 3: Testing Image Analysis")
    print("="*60)
    
    # Check if test image exists
    test_image_path = os.path.join(os.path.dirname(__file__), 'media', 'skin_scans')
    
    if not os.path.exists(test_image_path):
        print("⚠ No test images found in media/skin_scans/")
        print("⚠ Upload an image through frontend first, then run this test")
        return None
    
    # Find first image
    images = [f for f in os.listdir(test_image_path) if f.endswith(('.jpg', '.jpeg', '.png', '.jfif'))]
    
    if not images:
        print("⚠ No test images found")
        return None
    
    test_image = os.path.join(test_image_path, images[0])
    print(f"Using test image: {images[0]}")
    
    from apps.skincare_analysis.ai_service import analyze_skin_image
    
    user_profile = {
        'skin_type': 'combination',
        'sensitivity': 'normal',
        'concerns': [],
        'allergies': []
    }
    
    print("Analyzing image...")
    analysis = analyze_skin_image(test_image, user_profile)
    
    if analysis.get('error'):
        print(f"✗ Error: {analysis['message']}")
        return False
    
    if analysis.get('refer_to_doctor'):
        print(f"\n⚠ DOCTOR REFERRAL TRIGGERED")
        print(f"Issue: {analysis['detected_issue']}")
        print(f"Message: {analysis['message']}")
        return True
    
    print(f"\n✓ Analysis Complete!")
    print(f"✓ Model Used: {analysis['ai_model_used']}")
    print(f"✓ Processing Time: {analysis['processing_time']:.3f}s")
    print(f"✓ Severity: {analysis['severity']}")
    print(f"✓ Confidence Score: {analysis['confidence_score']}%")
    print(f"✓ Skin Score: {analysis['skin_score']}/100")
    
    print(f"\n--- Detected Issues ---")
    for issue in analysis.get('detected_issues', []):
        print(f"  • {issue['name']} ({issue.get('severity', 'unknown')})")
    
    print(f"\n--- Analysis Text (Preview) ---")
    print(analysis['analysis_text'][:300] + "...")
    
    return True


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 AI BACKEND TEST SUITE")
    print("="*60)
    
    try:
        # Test 1: Connection
        if not test_connection():
            print("\n❌ Connection test failed! Check your API key.")
            return
        
        # Test 2: Text Generation
        if not test_text_generation():
            print("\n❌ Text generation test failed!")
            return
        
        # Test 3: Image Analysis (optional)
        result = test_image_analysis()
        if result is None:
            print("\n⚠ Image analysis test skipped (no test images)")
        elif not result:
            print("\n❌ Image analysis test failed!")
            return
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60)
        print("\nYour AI backend is working correctly!")
        print("You can now test it through the Django API endpoints:")
        print("  • POST /api/scan/ask/  - Ask questions")
        print("  • POST /api/scan/       - Upload skin images")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
