"""
Ingredient Analysis Module
Analyzes skincare product ingredients for safety and suitability.
"""

import os
import json
import time
from typing import Dict, Any, List
from .gemini_client import get_gemini_client


def analyze_ingredients(ingredients: List[str], user_profile: dict = None) -> Dict[str, Any]:
    """
    Analyze skincare ingredients for safety and skin-type suitability.
    
    Args:
        ingredients: List of ingredient names
        user_profile: Optional user skin profile
    
    Returns:
        Analysis results with safety ratings and explanations
    """
    start_time = time.time()
    gemini = None
    
    try:
        gemini = get_gemini_client()
        
        profile_context = ""
        if user_profile:
            profile_context = f"""
User Skin Profile:
- Skin Type: {user_profile.get('skin_type', 'Unknown')}
- Concerns: {user_profile.get('concerns', [])}
- Allergies: {user_profile.get('allergies', 'None')}
- Sensitivity: {user_profile.get('sensitivity', 'Normal')}
"""
        
        prompt = f"""You are a cosmetic chemist and dermatology expert. Analyze the following skincare product ingredients.

{profile_context}

Ingredients to analyze:
{', '.join(ingredients)}

Return a JSON response with this exact structure:
{{
    "overall_safety": "safe" | "caution" | "avoid",
    "overall_score": 1-100,
    "suitable_for_user": true | false,
    "ingredients": [
        {{
            "name": "ingredient name",
            "function": "what it does",
            "safety": "safe" | "caution" | "avoid",
            "suitable": true | false,
            "reason": "brief explanation",
            "common_in": ["product types this is found in"]
        }}
    ],
    "good_for": ["skin concerns this helps with"],
    "avoid_if": ["conditions where this should be avoided"],
    "pregnancy_safe": true | false | "unknown",
    "disclaimer": "This is not medical advice. Consult a dermatologist for personalized recommendations."
}}

Rules:
1. Be conservative with safety ratings
2. Flag known irritants, allergens, and comedogenic ingredients
3. Consider the user's skin profile when rating suitability
4. Do not recommend prescription ingredients
5. Include a clear disclaimer
"""
        
        response = gemini.generate_text(prompt)
        
        if response.get('success'):
            data = response['data']
            data['processing_time'] = time.time() - start_time
            return data
        
        return _build_ingredient_fallback(ingredients, str(response.get('error', 'Unknown error')))
    
    except Exception as e:
        return _build_ingredient_fallback(ingredients, str(e))


def _build_ingredient_fallback(ingredients: List[str], error: str) -> Dict[str, Any]:
    """Build fallback when AI is unavailable."""
    return {
        'overall_safety': 'unknown',
        'overall_score': 50,
        'suitable_for_user': True,
        'ingredients': [
            {
                'name': ing,
                'function': 'Unable to analyze (AI service unavailable)',
                'safety': 'unknown',
                'suitable': True,
                'reason': 'AI analysis temporarily unavailable. Please consult a dermatologist.',
                'common_in': [],
            }
            for ing in ingredients
        ],
        'good_for': [],
        'avoid_if': [],
        'pregnancy_safe': 'unknown',
        'disclaimer': 'AI analysis is temporarily unavailable. This is not medical advice.',
        'fallback': True,
        'error': error,
    }
