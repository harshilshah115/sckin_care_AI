"""
AI Service Module for Skin Analysis and Question Answering.
Integrates with Google Gemini AI for image analysis and Q&A.
"""

import time
import random
import re
import os
from typing import Dict, Any, List
from .gemini_client import get_gemini_client
from .grok_client import get_grok_client
from .safety_filters import get_safety_filter
from .prompts import (
    get_skin_analysis_prompt,
    get_question_answer_prompt,
    get_routine_generation_prompt
)


def _call_ai_with_fallback(primary_fn, fallback_fn, error_context='AI call failed'):
    """Try primary AI, then Grok fallback, then local fallback."""
    try:
        result = primary_fn()
        if result.get('success'):
            return result
        # Primary failed, try Grok
        grok = get_grok_client()
        if grok.is_available():
            grok_result = fallback_fn(grok)
            if grok_result.get('success'):
                return grok_result
    except Exception:
        pass
    return {'success': False, 'error': f'{error_context} - all AI providers failed'}


def analyze_skin_image(image_path: str, user_profile: dict = None) -> Dict[str, Any]:
    """
    Analyze a skin image using Gemini AI.
    
    Args:
        image_path: Path to the uploaded image
        user_profile: User's skin profile for personalization
    
    Returns:
        Dictionary containing analysis results
    """
    start_time = time.time()
    gemini = None
    safety = None
    
    try:
        # Get clients
        gemini = get_gemini_client()
        safety = get_safety_filter()
        
        # Generate prompt
        prompt = get_skin_analysis_prompt(user_profile)
        
        # Analyze image with Gemini
        response = gemini.analyze_image(image_path, prompt)
        
        if not response['success']:
            # Return error response
            return {
                'error': True,
                'message': f"AI analysis failed: {response.get('error', 'Unknown error')}",
                'processing_time': time.time() - start_time
            }
        
        # Get analysis data
        analysis = response['data']
        
        # Safety validation
        validated_analysis = safety.validate_skin_analysis(analysis)

        # Normalize legacy/flat Gemini responses into the expected schema
        validated_analysis = _normalize_analysis_payload(validated_analysis)
        
        # Check if doctor referral needed
        if validated_analysis.get('refer_to_doctor'):
            return {
                'refer_to_doctor': True,
                'message': validated_analysis['message'],
                'detected_issue': validated_analysis.get('detected_issue'),
                'disclaimer': safety.disclaimer,
                'processing_time': time.time() - start_time
            }
        
        analysis_block = validated_analysis.get('analysis', {})
        recommendations_block = validated_analysis.get('recommendations', {})
        routine_block = validated_analysis.get('routine', {})
        priority_summary = _build_priority_summary(
            analysis_block,
            recommendations_block,
            routine_block,
            validated_analysis.get('meta', {})
        )

        detected_issues = analysis_block.get('detected_issues', [])

        # Extract and structure the response
        result = {
            'detected_issues': detected_issues,
            'severity': _determine_overall_severity(detected_issues),
            'confidence_score': _calculate_average_confidence(detected_issues),
            'skin_score': analysis_block.get('skin_score', 75),
            'analysis_text': _build_analysis_summary(analysis_block),
            'recommendations': {
                'natural': recommendations_block.get('natural', []),
                'otc': recommendations_block.get('otc', []),
                'cosmetic': recommendations_block.get('cosmetic', []),
                'lifestyle': recommendations_block.get('lifestyle', []),
                'routine': routine_block,
                'priority': priority_summary,
                'meta': validated_analysis.get('meta', {}),
                'analysis': analysis_block,
                'progress_tracking': validated_analysis.get('progress_tracking', {}),
                'alerts': validated_analysis.get('alerts', [])
            },
            'ai_model_used': gemini.get_last_model_used(),
            'processing_time': time.time() - start_time,
            'disclaimer': validated_analysis.get('disclaimer', safety.disclaimer)
        }
        
        # Add severity warning if needed
        severity_warning = safety.add_severity_warning(result['severity'])
        if severity_warning:
            result['severity_warning'] = severity_warning
        
        return result
    
    except Exception as e:
        # Return error with fallback to mock data
        friendly_message = None
        alerts = None
        if hasattr(gemini, '_build_friendly_alert_message'):
            friendly_message = gemini._build_friendly_alert_message(str(e))
        if hasattr(gemini, '_build_fallback_response'):
            fallback = gemini._build_fallback_response(str(e))
            alerts = fallback.get('data', {}).get('alerts')
        return {
            'error': True,
            'message': f"Error during analysis: {str(e)}",
            'friendly_message': friendly_message,
            'alerts': alerts or [],
            'processing_time': time.time() - start_time,
            'fallback': True
        }


def answer_skincare_question(question: str, user_profile: dict = None) -> Dict[str, Any]:
    """
    Answer a skincare question using Gemini AI.
    
    Args:
        question: User's question
        user_profile: User's skin profile for personalization
    
    Returns:
        Dictionary containing the answer and recommendations
    """
    start_time = time.time()
    gemini = None
    safety = None
    
    try:
        if _is_greeting_question(question):
            return _build_greeting_response(question, start_time)

        # Get clients
        gemini = get_gemini_client()
        safety = get_safety_filter()
        
        # Generate prompt
        prompt = get_question_answer_prompt(question, user_profile)
        
        # Get answer from Gemini
        response = gemini.generate_text(prompt)
        
        if not response['success']:
            error_message = response.get('error', 'Unknown error')
            if _is_quota_error(error_message):
                return _build_question_fallback(question, safety, start_time)

            return {
                'error': True,
                'message': f"AI response failed: {error_message}",
                'processing_time': time.time() - start_time
            }
        
        # Get answer data
        answer = response['data']
        
        # Safety validation
        validated_answer = safety.validate_question_answer(answer)
        
        # Check for safety issues
        if validated_answer.get('safety_issues'):
            return {
                'answer_text': validated_answer['answer_text'],
                'disclaimer': validated_answer['disclaimer'],
                'safety_redirect': True,
                'processing_time': time.time() - start_time
            }
        
        normalized_answer = _ensure_question_defaults(validated_answer)

        # Structure the response
        result = {
            'answer_text': normalized_answer.get('answer_text', ''),
            'key_points': normalized_answer.get('key_points', []),
            'recommendations': {
                'natural_remedies': normalized_answer.get('natural_remedies', []),
                'products': normalized_answer.get('product_recommendations', []),
                'tips': normalized_answer.get('tips', []),
                'related_questions': normalized_answer.get('related_questions', [])
            },
            'ai_model_used': gemini.model_name,
            'processing_time': time.time() - start_time,
            'disclaimer': normalized_answer.get('disclaimer', safety.disclaimer)
        }
        
        return result
    
    except Exception as e:
        error_message = str(e)
        if _is_quota_error(error_message):
            return _build_question_fallback(question, safety, start_time)

        return {
            'error': True,
            'message': f"Error answering question: {error_message}",
            'processing_time': time.time() - start_time
        }


def _is_quota_error(message: str) -> bool:
    if not message:
        return False
    normalized = message.upper()
    return 'RESOURCE_EXHAUSTED' in normalized or '429' in normalized or 'QUOTA' in normalized


def _is_greeting_question(question: str) -> bool:
    if not question:
        return False
    normalized = question.strip().lower()
    return normalized in {'hi', 'hello', 'hey', 'hiya', 'hola', 'howdy'}


def _build_greeting_response(question: str, start_time: float) -> Dict[str, Any]:
    response_text = "Hi! How can I help you with your skincare today?"
    return {
        'answer_text': response_text,
        'key_points': [
            'Ask about routines, ingredients, or product types',
            'Share your skin type or concern for tailored tips',
            'I can suggest safe, general guidance'
        ],
        'natural_remedies': [
            {
                'name': 'Aloe vera gel',
                'description': 'Soothes and hydrates irritated skin.',
                'ingredients': ['Aloe vera'],
                'usage': 'Apply a thin layer to clean skin as needed.'
            }
        ],
        'product_recommendations': [
            {
                'type': 'moisturizer',
                'suggestion': 'Look for a fragrance-free, non-comedogenic moisturizer.',
                'key_ingredients': ['ceramides', 'glycerin'],
                'why': 'Supports the skin barrier without irritation.'
            }
        ],
        'tips': [
            'Keep a simple routine to start',
            'Introduce one new product at a time',
            'Use SPF daily'
        ],
        'related_questions': [
            'What routine suits oily skin?',
            'How can I reduce acne breakouts?',
            'What is a good daily moisturizer?'
        ],
        'ai_model_used': 'static-greeting',
        'processing_time': time.time() - start_time,
        'disclaimer': get_safety_filter().disclaimer
    }


def _build_question_fallback(question: str, safety: Any, start_time: float) -> Dict[str, Any]:
    dynamic_answer = _generate_local_answer(question, safety)
    dynamic_answer['processing_time'] = time.time() - start_time
    dynamic_answer['fallback'] = True
    return dynamic_answer


def _ensure_question_defaults(answer: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(answer, dict):
        return {
            'answer_text': '',
            'key_points': [],
            'natural_remedies': [],
            'product_recommendations': [],
            'tips': [],
            'related_questions': []
        }

    answer.setdefault('answer_text', '')
    answer.setdefault('key_points', [])
    answer.setdefault('natural_remedies', [])
    answer.setdefault('product_recommendations', [])
    answer.setdefault('tips', [])
    answer.setdefault('related_questions', [])

    if not answer['key_points']:
        answer['key_points'] = [
            'Start with a gentle cleanser and moisturizer',
            'Use SPF daily to protect your skin',
            'Introduce new products slowly'
        ]

    if not answer['tips']:
        answer['tips'] = [
            'Avoid over-exfoliation',
            'Patch test active ingredients',
            'Keep a consistent routine'
        ]

    if not answer['natural_remedies']:
        answer['natural_remedies'] = [
            {
                'name': 'Green tea compress',
                'description': 'Calms redness and irritation.',
                'ingredients': ['Green tea'],
                'usage': 'Apply a cool compress for 5-10 minutes.'
            }
        ]

    if not answer['product_recommendations']:
        answer['product_recommendations'] = [
            {
                'type': 'cleanser',
                'suggestion': 'Use a gentle, fragrance-free cleanser.',
                'key_ingredients': ['glycerin'],
                'why': 'Cleans without stripping the barrier.'
            }
        ]

    if not answer['related_questions']:
        answer['related_questions'] = [
            'How should I build a basic routine?',
            'What ingredients are safe for sensitive skin?',
            'How often should I exfoliate?'
        ]

    return answer


def _detect_intent(question: str) -> str:
    if _is_greeting_question(question):
        return 'GREETING'

    normalized = question.strip().lower()
    if not normalized:
        return 'OTHER'

    brand_keywords = [
        'brand', 'name', 'naming', 'company', 'startup', 'business', 'label',
        'cosmetic', 'beauty', 'skincare brand', 'product line'
    ]
    if any(keyword in normalized for keyword in brand_keywords):
        return 'BRAND'

    skincare_keywords = [
        'acne', 'skin', 'routine', 'cleanser', 'moisturizer', 'sunscreen',
        'serum', 'pores', 'oil', 'dry', 'sensitive', 'pigmentation', 'glow'
    ]
    if any(keyword in normalized for keyword in skincare_keywords):
        return 'SKINCARE'

    return 'OTHER'


def _generate_local_answer(question: str, safety: Any) -> Dict[str, Any]:
    intent = _detect_intent(question)

    if intent == 'GREETING':
        return _build_greeting_response(question, time.time())

    if intent == 'BRAND':
        return _build_brand_naming_response(question, safety)

    if intent == 'SKINCARE':
        return _build_skincare_fallback_response(question, safety)

    return _build_general_fallback_response(question, safety)


def _build_brand_naming_response(question: str, safety: Any) -> Dict[str, Any]:
    vibe = _infer_brand_vibe(question)
    name_list = _generate_brand_names(vibe, count=10)

    answer_text = (
        f"Here are some {vibe} cosmetic brand name ideas:\n" +
        "\n".join([f"- {name}" for name in name_list]) +
        "\n\nIf you want, share your target audience or vibe and I can refine the list."
    )

    return {
        'answer_text': answer_text,
        'key_points': [
            f"Vibe used: {vibe}",
            'Names are crafted to be short and brandable',
            'I can tailor names for luxury, natural, or modern styles'
        ],
        'natural_remedies': [
            {
                'name': 'Rosewater mist',
                'description': 'Gently refreshes skin during the day.',
                'ingredients': ['Rosewater'],
                'usage': 'Mist lightly after cleansing or as needed.'
            }
        ],
        'product_recommendations': [
            {
                'type': 'sunscreen',
                'suggestion': 'Offer a lightweight daily SPF in the line.',
                'key_ingredients': ['zinc oxide'],
                'why': 'SPF is essential for daily skincare routines.'
            }
        ],
        'tips': [
            'Check domain availability for top name choices',
            'Keep names easy to pronounce globally',
            'Avoid trademark conflicts'
        ],
        'related_questions': [
            'Can you name a luxury skincare line?',
            'What are good names for a herbal beauty brand?',
            'How should I position my cosmetic brand?'
        ],
        'ai_model_used': 'fallback-local',
        'disclaimer': getattr(safety, 'disclaimer', '')
    }


def _build_skincare_fallback_response(question: str, safety: Any) -> Dict[str, Any]:
    response_pool = [
        {
            'answer': (
                "Here is a simple, safe routine to start with:\n"
                "- Gentle cleanser\n"
                "- Fragrance-free moisturizer\n"
                "- Broad-spectrum SPF in the morning\n\n"
                "If irritation worsens, pause actives and consult a dermatologist."
            ),
            'points': [
                'Keep the routine gentle and consistent',
                'Use SPF every morning',
                'Introduce actives slowly'
            ],
            'tips': [
                'Patch test new products',
                'Avoid over-exfoliating',
                'Stay hydrated'
            ]
        },
        {
            'answer': (
                "Start with the basics and build up:\n"
                "- Cleanse twice daily\n"
                "- Moisturize after cleansing\n"
                "- SPF every morning\n\n"
                "If you have severe symptoms, seek professional advice."
            ),
            'points': [
                'Basics first, then add treatments',
                'Moisturize to support the barrier',
                'Sun protection matters daily'
            ],
            'tips': [
                'Avoid mixing many actives',
                'Give products 2-4 weeks to work',
                'Remove makeup gently'
            ]
        }
    ]

    choice = random.choice(response_pool)

    return {
        'answer_text': choice['answer'],
        'key_points': choice['points'],
        'natural_remedies': [
            {
                'name': 'Green tea compress',
                'description': 'Calms redness and supports the skin barrier.',
                'ingredients': ['Green tea'],
                'usage': 'Apply a cool compress for 5-10 minutes.'
            }
        ],
        'product_recommendations': [
            {
                'type': 'cleanser',
                'suggestion': 'Use a gentle, non-foaming cleanser.',
                'key_ingredients': ['glycerin'],
                'why': 'Prevents stripping and irritation.'
            }
        ],
        'tips': choice['tips'],
        'related_questions': [
            'What ingredients help with oil control?',
            'How often should I exfoliate?',
            'Can you suggest a basic routine?'
        ],
        'ai_model_used': 'fallback-local',
        'disclaimer': getattr(safety, 'disclaimer', '')
    }


def _build_general_fallback_response(question: str, safety: Any) -> Dict[str, Any]:
    answer_text = (
        "Thanks for your question. I can help with skincare routines, ingredients, "
        "or cosmetic brand ideas. Tell me a bit more about what you need."
    )

    return {
        'answer_text': answer_text,
        'key_points': [
            'Share your skin type or goal',
            'Ask about routines or products',
            'I can also generate brand name ideas'
        ],
        'natural_remedies': [
            {
                'name': 'Oatmeal mask',
                'description': 'Soothes and softens sensitive skin.',
                'ingredients': ['Oatmeal', 'water'],
                'usage': 'Apply for 10 minutes, then rinse gently.'
            }
        ],
        'product_recommendations': [
            {
                'type': 'moisturizer',
                'suggestion': 'Choose a lightweight, fragrance-free moisturizer.',
                'key_ingredients': ['ceramides'],
                'why': 'Supports the skin barrier.'
            }
        ],
        'tips': [
            'Keep routines simple at first',
            'Use SPF daily',
            'Avoid harsh scrubs'
        ],
        'related_questions': [
            'Can you suggest a routine for oily skin?',
            'What ingredients are good for acne?',
            'Suggest names for a natural beauty brand'
        ],
        'ai_model_used': 'fallback-local',
        'disclaimer': getattr(safety, 'disclaimer', '')
    }


def _infer_brand_vibe(question: str) -> str:
    normalized = question.lower()
    if any(word in normalized for word in ['luxury', 'premium', 'elite', 'noir', 'luxe']):
        return 'luxury'
    if any(word in normalized for word in ['herbal', 'botanical', 'natural', 'organic', 'earth']):
        return 'natural'
    if any(word in normalized for word in ['modern', 'minimal', 'clean', 'future', 'tech']):
        return 'modern'
    return 'modern'


def _generate_brand_names(vibe: str, count: int = 8) -> List[str]:
    random.seed(time.time())
    prefixes = {
        'luxury': ['Aura', 'Luxe', 'Velvet', 'Opal', 'Noble', 'Elysian', 'Noir', 'Serene'],
        'natural': ['Bloom', 'Herb', 'Sage', 'Luna', 'Terra', 'Fern', 'Aura', 'Sol'],
        'modern': ['Nova', 'Pure', 'Vivid', 'Halo', 'Pulse', 'Axiom', 'Lumen', 'Mode']
    }
    suffixes = {
        'luxury': ['Maison', 'Atelier', 'Couture', 'Essence', 'Studio', 'Lab', 'Reserve', 'Collection'],
        'natural': ['Botanics', 'Blend', 'Rituals', 'Glow', 'Roots', 'Essence', 'Harvest', 'Garden'],
        'modern': ['Lab', 'Studio', 'Skin', 'Form', 'Theory', 'Works', 'Collective', 'House']
    }

    words = []
    prefix_list = prefixes.get(vibe, prefixes['modern'])
    suffix_list = suffixes.get(vibe, suffixes['modern'])

    while len(words) < count:
        name = f"{random.choice(prefix_list)} {random.choice(suffix_list)}"
        if name not in words:
            words.append(name)

    return words


def generate_personalized_routine(skin_profile: dict) -> Dict[str, Any]:
    """
    Generate a personalized skincare routine using AI.
    
    Args:
        skin_profile: User's skin type, concerns, etc.
    
    Returns:
        Dictionary containing routine steps
    """
    start_time = time.time()
    
    try:
        gemini = get_gemini_client()
        
        skin_concerns = skin_profile.get('concerns', [])
        skin_type = skin_profile.get('skin_type', 'normal')
        plan_days = skin_profile.get('plan_days')
        prompt_context = {
            'age_group': skin_profile.get('age_group'),
            'sensitivity': skin_profile.get('sensitivity'),
            'allergies': skin_profile.get('allergies'),
            'scan_summary': skin_profile.get('scan_summary'),
            'question_summary': skin_profile.get('question_summary')
        }

        prompt = get_routine_generation_prompt(skin_concerns, skin_type, plan_days, prompt_context)
        
        response = gemini.generate_text(prompt)
        
        if not response['success']:
            error_message = str(response.get('error', 'Unknown error'))
            if _is_quota_error(error_message):
                return _build_routine_fallback(skin_profile, start_time)
            return {
                'error': True,
                'message': f"Routine generation failed: {error_message}",
                'processing_time': time.time() - start_time
            }
        
        routine = response['data']
        
        return {
            'morning_routine': routine.get('morning_routine', []),
            'night_routine': routine.get('night_routine', []),
            'weekly_treatments': routine.get('weekly_treatments', []),
            'general_tips': routine.get('general_tips', []),
            'processing_time': time.time() - start_time
        }
    
    except Exception as e:
        error_message = str(e)
        if _is_quota_error(error_message):
            return _build_routine_fallback(skin_profile, start_time)
        return {
            'error': True,
            'message': f"Error generating routine: {error_message}",
            'processing_time': time.time() - start_time
        }


def _build_routine_fallback(skin_profile: dict, start_time: float) -> Dict[str, Any]:
    skin_type = (skin_profile.get('skin_type') or 'normal').lower()
    concerns = [str(c).lower() for c in (skin_profile.get('concerns') or [])]

    morning = [
        {
            'step': 1,
            'name': 'Gentle Cleanser',
            'product_type': 'cleanser',
            'instructions': 'Cleanse with lukewarm water and a gentle cleanser.',
            'duration': '60 sec',
            'key_ingredients': ['glycerin']
        },
        {
            'step': 2,
            'name': 'Hydrating Serum',
            'product_type': 'serum',
            'instructions': 'Apply a thin layer to damp skin.',
            'duration': '30 sec',
            'key_ingredients': ['hyaluronic acid']
        },
        {
            'step': 3,
            'name': 'Moisturizer',
            'product_type': 'moisturizer',
            'instructions': 'Seal in hydration with a lightweight moisturizer.',
            'duration': '30 sec',
            'key_ingredients': ['ceramides']
        },
        {
            'step': 4,
            'name': 'Broad-Spectrum SPF',
            'product_type': 'sunscreen',
            'instructions': 'Apply SPF 30+ as the final step.',
            'duration': '30 sec',
            'key_ingredients': ['zinc oxide']
        }
    ]

    night = [
        {
            'step': 1,
            'name': 'Gentle Cleanser',
            'product_type': 'cleanser',
            'instructions': 'Cleanse to remove sunscreen and buildup.',
            'duration': '60 sec',
            'key_ingredients': ['glycerin']
        },
        {
            'step': 2,
            'name': 'Soothing Treatment',
            'product_type': 'treatment',
            'instructions': 'Apply a calming treatment suited to your concern.',
            'duration': '30 sec',
            'key_ingredients': ['niacinamide']
        },
        {
            'step': 3,
            'name': 'Moisturizer',
            'product_type': 'moisturizer',
            'instructions': 'Finish with a nourishing moisturizer.',
            'duration': '30 sec',
            'key_ingredients': ['ceramides']
        }
    ]

    weekly = [
        {
            'name': 'Hydrating Mask',
            'frequency': '1x per week',
            'day': 'Any',
            'description': 'Boosts hydration and supports the skin barrier.'
        }
    ]

    tips = [
        'Introduce new products one at a time',
        'Avoid over-exfoliating',
        'Use SPF daily'
    ]

    if skin_type in {'oily', 'combination'} or 'acne' in concerns:
        night.insert(2, {
            'step': 3,
            'name': 'Oil-Control Treatment',
            'product_type': 'treatment',
            'instructions': 'Apply a lightweight treatment to manage oil and breakouts.',
            'duration': '30 sec',
            'key_ingredients': ['salicylic acid']
        })
        night[-1]['step'] = 4

    if skin_type in {'dry', 'sensitive'} or 'irritation' in concerns:
        morning[1]['name'] = 'Soothing Serum'
        morning[1]['key_ingredients'] = ['panthenol']
        tips.append('Patch test active ingredients')

    return {
        'morning_routine': morning,
        'night_routine': night,
        'weekly_treatments': weekly,
        'general_tips': tips,
        'processing_time': time.time() - start_time,
        'fallback': True
    }


def get_product_recommendations(skin_profile: dict, concerns: List[str]) -> Dict[str, Any]:
    """
    Get personalized product recommendations based on skin profile.
    
    Args:
        skin_profile: User's skin type, sensitivity, etc.
        concerns: List of skin concerns
    
    Returns:
        Dictionary containing product recommendations
    """
    # This can be enhanced with a product database later
    # For now, use AI to generate recommendations
    
    user_profile = {
        **skin_profile,
        'concerns': concerns
    }
    
    question = f"What products do you recommend for {skin_profile.get('skin_type', 'normal')} skin with concerns about {', '.join(concerns)}?"
    
    return answer_skincare_question(question, user_profile)


# Helper functions
def _determine_overall_severity(issues: List[Dict]) -> str:
    """Determine overall severity from detected issues"""
    if not issues:
        return 'none'
    
    severity_map = {
        'high': 'severe',
        'severe': 'severe',
        'critical': 'severe',
        'moderate': 'moderate',
        'medium': 'moderate',
        'mild': 'mild',
        'low': 'mild',
        'refer_to_doctor': 'severe'
    }

    severities = [severity_map.get(str(issue.get('severity', 'mild')).lower(), 'mild') for issue in issues]
    
    if 'severe' in severities:
        return 'severe'
    elif 'moderate' in severities:
        return 'moderate'
    else:
        return 'mild'


def _calculate_average_confidence(issues: List[Dict]) -> float:
    """Calculate average confidence score from detected issues"""
    if not issues:
        return 0.0
    
    confidences = [issue.get('confidence', 0) for issue in issues]
    return sum(confidences) / len(confidences) if confidences else 0.0


def _build_analysis_summary(analysis: Dict[str, Any]) -> str:
    """Build a short summary string from the structured analysis."""
    if not analysis:
        return ''

    issues = analysis.get('detected_issues', [])
    causes = analysis.get('probable_causes', [])

    issue_names = [issue.get('name') for issue in issues if issue.get('name')]

    cause_names = []
    for cause in causes:
        if isinstance(cause, str) and cause:
            cause_names.append(cause)
        elif isinstance(cause, dict):
            value = cause.get('cause') or cause.get('name')
            if value:
                cause_names.append(value)

    summary_parts = []
    if issue_names:
        summary_parts.append(f"Detected issues: {', '.join(issue_names[:3])}.")
    if cause_names:
        summary_parts.append(f"Likely contributors: {', '.join(cause_names[:2])}.")

    return ' '.join(summary_parts)


def _build_priority_summary(
    analysis: Dict[str, Any],
    recommendations: Dict[str, Any],
    routine: Dict[str, Any],
    meta: Dict[str, Any]
) -> Dict[str, Any]:
    image_quality = meta.get('image_quality', {}) if isinstance(meta, dict) else {}
    confidence_cap = _determine_confidence_cap(image_quality)

    concerns = _collect_priority_concerns(analysis, confidence_cap)
    primary = concerns[:2]
    secondary = concerns[2:4]

    likely_causes = _build_likely_causes(analysis, primary)
    recommended_ingredients = _build_recommended_ingredients(recommendations, primary)
    action_plan = _build_action_plan(primary, recommended_ingredients)
    simple_routine = _build_simple_routine(routine, primary, recommended_ingredients)
    key_observations = _build_key_observations(analysis, primary)

    return {
        'primary_concerns': primary,
        'secondary_concerns': secondary,
        'key_observations': key_observations,
        'likely_causes': likely_causes,
        'action_plan': action_plan,
        'recommended_ingredients': recommended_ingredients,
        'simple_routine': simple_routine
    }


def _determine_confidence_cap(image_quality: Dict[str, Any]) -> int:
    confidence = _normalize_percent(image_quality.get('confidence', 0))
    lighting = str(image_quality.get('lighting', '')).lower()
    blur = str(image_quality.get('blur', '')).lower()
    angle = str(image_quality.get('angle', '')).lower()

    score = confidence
    if 'excellent' in lighting or 'good' in lighting:
        score += 10
    elif 'poor' in lighting:
        score -= 10

    if 'low' in blur or 'none' in blur:
        score += 10
    elif 'high' in blur:
        score -= 15

    if 'frontal' in angle or 'good' in angle:
        score += 5
    elif 'partial' in angle or 'side' in angle:
        score -= 5

    if score >= 80:
        return 85
    if score >= 60:
        return 70
    return 55


def _collect_priority_concerns(analysis: Dict[str, Any], confidence_cap: int) -> List[Dict[str, Any]]:
    concerns = []
    seen = set()

    for issue in analysis.get('detected_issues', []) or []:
        if not isinstance(issue, dict):
            issue = {'name': str(issue)}

        raw_name = issue.get('name', '')
        friendly = _humanize_issue_name(raw_name)
        if not friendly or _is_non_actionable_concern(friendly):
            continue

        key = friendly.lower()
        if key in seen:
            continue

        severity = _normalize_severity_level(issue.get('severity'))
        base_confidence = _normalize_percent(issue.get('confidence', 50))
        confidence = _cap_confidence(base_confidence, confidence_cap)
        concerns.append({
            'concern': friendly,
            'severity': severity,
            'confidence': confidence,
            'why_it_matters': _why_it_matters(friendly)
        })
        seen.add(key)

    metrics = analysis.get('metrics', {}) or {}
    metric_concerns = _metric_concerns(metrics, confidence_cap)
    for entry in metric_concerns:
        key = entry['concern'].lower()
        if key in seen:
            continue
        concerns.append(entry)
        seen.add(key)

    concerns.sort(
        key=lambda item: (_severity_score(item['severity']), item['confidence']),
        reverse=True
    )
    return concerns


def _metric_concerns(metrics: Dict[str, Any], confidence_cap: int) -> List[Dict[str, Any]]:
    entries = []

    oiliness = _metric_value(metrics.get('oiliness'))
    if oiliness is not None and oiliness >= 60:
        entries.append(_build_metric_concern('Excess oil', oiliness, confidence_cap))

    texture = _metric_value(metrics.get('texture'))
    if texture is not None and texture >= 60:
        entries.append(_build_metric_concern('Uneven texture', texture, confidence_cap))

    pores = _metric_value(metrics.get('pore_visibility'))
    if pores is not None and pores >= 60:
        entries.append(_build_metric_concern('Visible pores', pores, confidence_cap))

    pigmentation = _metric_value(metrics.get('pigmentation'))
    if pigmentation is not None and pigmentation >= 55:
        entries.append(_build_metric_concern('Dark marks', pigmentation, confidence_cap))

    hydration = _metric_value(metrics.get('hydration'))
    if hydration is not None and hydration <= 45:
        severity = 'high' if hydration <= 35 else 'medium'
        confidence = _cap_confidence(100 - hydration, confidence_cap)
        entries.append({
            'concern': 'Dehydration',
            'severity': severity,
            'confidence': confidence,
            'why_it_matters': _why_it_matters('Dehydration')
        })

    return entries


def _build_metric_concern(label: str, score: int, confidence_cap: int) -> Dict[str, Any]:
    severity = 'high' if score >= 75 else 'medium' if score >= 60 else 'low'
    confidence = _cap_confidence(score, confidence_cap)
    return {
        'concern': label,
        'severity': severity,
        'confidence': confidence,
        'why_it_matters': _why_it_matters(label)
    }


def _build_likely_causes(analysis: Dict[str, Any], primary: List[Dict[str, Any]]) -> List[str]:
    causes = []
    for cause in analysis.get('probable_causes', []) or []:
        if isinstance(cause, str):
            label = cause
        elif isinstance(cause, dict):
            label = cause.get('cause') or cause.get('name') or ''
        else:
            label = ''
        label = _humanize_cause(label)
        if label:
            causes.append(label)

    if not causes:
        for item in primary:
            inferred = _infer_cause_from_concern(item.get('concern', ''))
            if inferred:
                causes.append(inferred)

    return causes[:3]


def _build_recommended_ingredients(
    recommendations: Dict[str, Any],
    primary: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    ingredients = []
    seen = set()

    for item in recommendations.get('otc', []) or []:
        if not isinstance(item, dict):
            name = str(item)
        else:
            name = item.get('ingredient') or item.get('name') or ''
            if item.get('concentration') and item.get('concentration') not in name:
                name = f"{name} {item.get('concentration')}"
        name = _normalize_ingredient_name(name)
        if not name or _is_prescription_ingredient(name):
            continue
        key = name.lower()
        if key in seen:
            continue
        ingredients.append({
            'name': name,
            'why': _ingredient_reason(name, primary)
        })
        seen.add(key)
        if len(ingredients) >= 3:
            return ingredients

    for item in recommendations.get('cosmetic', []) or []:
        if not isinstance(item, dict):
            continue
        for key_ingredient in item.get('key_ingredients', []) or []:
            name = _normalize_ingredient_name(key_ingredient)
            if not name or _is_prescription_ingredient(name):
                continue
            lowered = name.lower()
            if lowered in seen:
                continue
            ingredients.append({
                'name': name,
                'why': _ingredient_reason(name, primary)
            })
            seen.add(lowered)
            if len(ingredients) >= 3:
                return ingredients

    defaults = _default_ingredients_for_concerns(primary)
    for name in defaults:
        if name.lower() in seen:
            continue
        ingredients.append({
            'name': name,
            'why': _ingredient_reason(name, primary)
        })
        if len(ingredients) >= 3:
            break

    return ingredients


def _build_action_plan(
    primary: List[Dict[str, Any]],
    ingredients: List[Dict[str, Any]]
) -> List[str]:
    steps = []
    steps.append(
        "Step 1: Keep it gentle. Use a mild cleanser and a lightweight, non-comedogenic moisturizer."
    )

    target = primary[0]['concern'].lower() if primary else 'your main concern'
    active = ingredients[0]['name'] if ingredients else 'one targeted active'
    steps.append(
        f"Step 2: Introduce {active} to target {target}. Start slowly and track tolerance."
    )

    steps.append(
        "Step 3: Wear SPF every morning and avoid picking to reduce lingering marks."
    )

    return steps


def _build_simple_routine(
    routine: Dict[str, Any],
    primary: List[Dict[str, Any]],
    ingredients: List[Dict[str, Any]]
) -> Dict[str, List[str]]:
    morning = _format_routine_steps(routine.get('morning'))
    night = _format_routine_steps(routine.get('night'))

    if not morning:
        morning = [
            'Gentle cleanser',
            'Lightweight moisturizer',
            'Broad-spectrum SPF 30+'
        ]

    if not night:
        active = ingredients[0]['name'] if ingredients else 'Targeted treatment'
        night = [
            'Gentle cleanser',
            f"{active} (start 2-3 nights per week)",
            'Moisturizer'
        ]

    return {
        'morning': morning[:4],
        'night': night[:4]
    }


def _build_key_observations(analysis: Dict[str, Any], primary: List[Dict[str, Any]]) -> List[str]:
    observations = []

    zones = _collect_zones_from_issues(analysis.get('detected_issues', []) or [])
    if zones:
        zones_text = ', '.join(zones[:2])
        observations.append(f"Most noticeable on {zones_text}.")

    if primary:
        observations.append(f"Main visible pattern: {primary[0]['concern'].lower()}.")

    if not observations:
        observations.append('Visible imbalance in texture and tone.')

    return observations[:3]


def _collect_zones_from_issues(issues: List[Dict[str, Any]]) -> List[str]:
    zones = []
    for issue in issues:
        if not isinstance(issue, dict):
            continue
        issue_zones = issue.get('zones') or issue.get('location') or []
        if isinstance(issue_zones, str):
            issue_zones = [issue_zones]
        for zone in issue_zones:
            if not zone:
                continue
            cleaned = str(zone).replace('_', ' ').strip().lower()
            if cleaned and cleaned not in zones:
                zones.append(cleaned)
    return zones


def _format_routine_steps(steps: Any) -> List[str]:
    if not steps:
        return []

    formatted = []
    for step in steps:
        if isinstance(step, str):
            formatted.append(step)
            continue
        if not isinstance(step, dict):
            continue

        action = step.get('action') or step.get('name') or ''
        details = step.get('details') or step.get('instructions') or ''
        if action and details:
            formatted.append(f"{action} - {details}")
        elif action:
            formatted.append(action)
        elif details:
            formatted.append(details)

    return formatted


def _humanize_issue_name(name: str) -> str:
    if not name:
        return ''

    lowered = str(name).lower()
    if 'consultation' in lowered or 'refer_to_doctor' in lowered:
        return ''

    if 'inflammatory' in lowered or 'papule' in lowered or 'pustule' in lowered:
        return 'Inflamed breakouts'
    if 'acne' in lowered:
        return 'Breakouts'
    if 'erythema' in lowered or 'redness' in lowered:
        return 'Redness'
    if 'pigment' in lowered or 'pih' in lowered:
        return 'Dark marks'
    if 'pore' in lowered:
        return 'Visible pores'
    if 'texture' in lowered or 'rough' in lowered or 'uneven' in lowered:
        return 'Uneven texture'
    if 'oil' in lowered or 'sebum' in lowered:
        return 'Excess oil'
    if 'dry' in lowered or 'dehydrat' in lowered:
        return 'Dehydration'
    if 'barrier' in lowered:
        return 'Skin barrier stress'
    if 'scar' in lowered:
        return 'Scarring risk'
    if 'blackhead' in lowered or 'whitehead' in lowered or 'comedone' in lowered:
        return 'Clogged pores'
    if 'dull' in lowered:
        return 'Dullness'

    cleaned = re.sub(r'[_\-]+', ' ', lowered).strip()
    return cleaned.title() if cleaned else ''


def _why_it_matters(concern: str) -> str:
    label = concern.lower()
    if 'breakout' in label or 'clogged' in label:
        return 'Active inflammation can lead to marks and lingering redness.'
    if 'redness' in label:
        return 'Ongoing redness often signals irritation and a stressed barrier.'
    if 'dark' in label or 'mark' in label or 'pigment' in label:
        return 'Marks can linger and darken without sun protection.'
    if 'oil' in label:
        return 'Excess oil can clog pores and fuel new breakouts.'
    if 'pore' in label:
        return 'Congested pores can look more prominent over time.'
    if 'texture' in label:
        return 'Rough texture can make skin look dull and feel bumpy.'
    if 'dehydration' in label or 'dry' in label:
        return 'Low hydration can increase irritation and oil rebound.'
    if 'barrier' in label:
        return 'A weakened barrier makes skin more reactive.'
    if 'scar' in label:
        return 'Untreated inflammation can leave long-term marks.'
    return 'This concern can impact overall skin clarity and comfort.'


def _normalize_severity_level(value: Any) -> str:
    normalized = str(value or '').lower()
    if normalized in {'high', 'severe', 'critical'}:
        return 'high'
    if normalized in {'moderate', 'medium'}:
        return 'medium'
    if normalized in {'low', 'mild'}:
        return 'low'
    return 'medium'


def _severity_score(level: str) -> int:
    return {'high': 3, 'medium': 2, 'low': 1}.get(level, 2)


def _cap_confidence(value: int, cap: int) -> int:
    return max(20, min(int(value), int(cap)))


def _normalize_percent(value: Any) -> int:
    if value is None:
        return 0
    if isinstance(value, (int, float)):
        numeric = float(value)
    else:
        cleaned = str(value).replace('%', '').strip()
        try:
            numeric = float(cleaned)
        except ValueError:
            numeric = _level_to_score(str(value))

    if numeric <= 1:
        numeric *= 100
    return max(0, min(int(round(numeric)), 100))


def _metric_value(value: Any) -> int:
    if value is None:
        return None
    if isinstance(value, dict):
        if value.get('score') is not None:
            return _normalize_percent(value.get('score'))
        if value.get('level') is not None:
            return _level_to_score(value.get('level'))
        return None
    if isinstance(value, (int, float)):
        return int(value)
    if isinstance(value, str):
        return _level_to_score(value)
    return None


def _level_to_score(level: str) -> int:
    normalized = str(level).lower()
    if 'very' in normalized and 'high' in normalized:
        return 85
    if 'high' in normalized:
        return 75
    if 'uneven' in normalized or 'rough' in normalized:
        return 70
    if 'moderate' in normalized or 'medium' in normalized:
        return 60
    if 'low' in normalized:
        return 40
    if 'poor' in normalized:
        return 35
    if 'good' in normalized:
        return 70
    if 'excellent' in normalized:
        return 85
    return 50


def _is_non_actionable_concern(name: str) -> bool:
    lowered = name.lower()
    return 'consultation' in lowered or 'doctor' in lowered


def _humanize_cause(name: str) -> str:
    if not name:
        return ''
    normalized = str(name).lower().replace('_', ' ').replace('-', ' ').strip()
    normalized = normalized.replace('p. acnes', 'skin bacteria')
    normalized = normalized.replace('p acnes', 'skin bacteria')

    replacements = {
        'excess sebum production': 'excess oil production',
        'bacterial overgrowth': 'bacterial buildup',
        'follicular hyperkeratinization': 'clogged pores',
        'hormonal factors': 'hormonal influence',
        'hormonal fluctuations': 'hormonal shifts'
    }
    normalized = replacements.get(normalized, normalized)

    if not normalized:
        return ''

    if normalized.startswith(('possible', 'likely', 'may')):
        return normalized.capitalize()
    return f"Possible {normalized}"


def _infer_cause_from_concern(concern: str) -> str:
    label = concern.lower()
    if 'breakout' in label or 'clogged' in label:
        return 'Possible pore congestion'
    if 'oil' in label:
        return 'Possible excess oil production'
    if 'dark' in label or 'mark' in label:
        return 'Possible post-breakout pigmentation'
    if 'redness' in label:
        return 'Possible barrier stress'
    if 'dehydration' in label:
        return 'Possible low hydration'
    return ''


def _normalize_ingredient_name(name: str) -> str:
    if not name:
        return ''
    cleaned = ' '.join(str(name).replace('_', ' ').split())
    return cleaned.strip()


def _is_prescription_ingredient(name: str) -> bool:
    lowered = name.lower()
    blocked = {
        'tretinoin', 'retin-a', 'accutane', 'isotretinoin', 'adapalene',
        'tazarotene', 'clindamycin', 'erythromycin', 'doxycycline',
        'spironolactone', 'hydroquinone 4%', 'cortisone', 'prednisone',
        'tacrolimus', 'pimecrolimus'
    }
    return any(item in lowered for item in blocked)


def _ingredient_reason(name: str, primary: List[Dict[str, Any]]) -> str:
    lowered = name.lower()
    concerns_text = ' '.join([item.get('concern', '').lower() for item in primary])

    if 'salicylic' in lowered:
        return 'Helps clear pores and reduce congestion.'
    if 'benzoyl' in lowered:
        return 'Reduces bacteria and inflamed spots.'
    if 'niacinamide' in lowered:
        return 'Calms redness and supports the skin barrier.'
    if 'azelaic' in lowered:
        return 'Targets marks and helps calm redness.'
    if 'vitamin c' in lowered:
        return 'Brightens dullness and supports even tone.'
    if 'hyaluronic' in lowered or 'glycerin' in lowered:
        return 'Boosts hydration without heaviness.'
    if 'ceramide' in lowered:
        return 'Strengthens the moisture barrier.'
    if 'zinc' in lowered:
        return 'Helps reduce surface oil and shine.'

    if 'breakout' in concerns_text or 'clogged' in concerns_text:
        return 'Supports clearer-looking skin and smoother texture.'
    if 'dark' in concerns_text or 'mark' in concerns_text:
        return 'Supports a more even-looking tone.'
    return 'Supports overall skin balance.'


def _default_ingredients_for_concerns(primary: List[Dict[str, Any]]) -> List[str]:
    labels = ' '.join([item.get('concern', '').lower() for item in primary])
    if 'breakout' in labels or 'clogged' in labels:
        return ['Salicylic Acid', 'Niacinamide']
    if 'dark' in labels or 'mark' in labels:
        return ['Azelaic Acid', 'Niacinamide']
    if 'oil' in labels:
        return ['Niacinamide', 'Zinc']
    if 'dehydration' in labels:
        return ['Hyaluronic Acid', 'Ceramides']
    return ['Niacinamide']


def _normalize_analysis_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Normalize flat Gemini analysis payloads into the expected schema."""
    if not isinstance(payload, dict):
        return {}

    if isinstance(payload.get('analysis'), dict):
        return payload

    # Flat schema fallback (as defined in prompt_templates/skin_analysis.txt)
    analysis = {
        'skin_score': payload.get('skin_score', 0),
        'skin_type_detected': payload.get('skin_type_detected'),
        'metrics': payload.get('metrics', {}),
        'face_zones': payload.get('face_zones', {}),
        'detected_issues': payload.get('detected_issues', []),
        'probable_causes': payload.get('probable_causes', []),
        'risk_flags': payload.get('risk_flags', [])
    }

    meta = payload.get('meta', {}) if isinstance(payload.get('meta'), dict) else {}
    if payload.get('image_quality') and not meta.get('image_quality'):
        meta = {**meta, 'image_quality': payload.get('image_quality')}

    return {
        **payload,
        'meta': meta,
        'analysis': analysis,
        'recommendations': payload.get('recommendations', {}),
        'routine': payload.get('routine', {}),
        'progress_tracking': payload.get('progress_tracking', {}),
        'alerts': payload.get('alerts', [])
    }


def test_ai_connection() -> Dict[str, Any]:
    """Test AI service connection"""
    start_time = time.time()
    
    try:
        # Test 1: Check if library is available
        try:
            from google import genai
        except ImportError as e:
            return {
                'success': False,
                'status': 'error',
                'error': 'google-genai library not installed',
                'message': 'Please run: pip install google-genai==0.2.2',
                'details': str(e),
                'response_time': time.time() - start_time
            }
        
        # Test 2: Check if API key is set
        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return {
                'success': False,
                'status': 'error',
                'error': 'API key not configured',
                'message': 'GEMINI_API_KEY not found in .env file',
                'response_time': time.time() - start_time
            }
        
        # Test 3: Try to initialize client
        try:
            gemini = get_gemini_client()
        except Exception as e:
            return {
                'success': False,
                'status': 'error',
                'error': 'Failed to initialize Gemini client',
                'message': str(e),
                'response_time': time.time() - start_time
            }
        
        # Test 4: Try to connect
        try:
            test_result = gemini.test_connection()
        except Exception as e:
            return {
                'success': False,
                'status': 'error',
                'error': 'Failed to test connection',
                'message': str(e),
                'response_time': time.time() - start_time
            }
        
        if test_result.get('success'):
            # Test 5: Connection successful
            return {
                'success': True,
                'status': 'connected',
                'provider': 'gemini',
                'model': gemini.model_name,
                'message': 'AI service is fully operational',
                'test_response': test_result.get('response', ''),
                'response_time': time.time() - start_time
            }
        else:
            # Connection failed - return detailed error
            return {
                'success': False,
                'status': 'connection_failed',
                'provider': 'gemini',
                'model': gemini.model_name,
                'message': 'AI service connection test failed',
                'error': test_result.get('error', 'Unknown error'),
                'error_type': test_result.get('error_type', 'Unknown'),
                'response_time': time.time() - start_time
            }
    
    except Exception as e:
        import traceback
        return {
            'success': False,
            'status': 'error',
            'error': str(e),
            'error_type': type(e).__name__,
            'message': 'Failed to connect to AI service',
            'traceback': traceback.format_exc(),
            'response_time': time.time() - start_time
        }


