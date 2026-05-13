"""
AI Prompt Templates for Skincare Analysis
"""

from pathlib import Path
from typing import Optional, Dict


_TEMPLATE_DIR = Path(__file__).resolve().parent / 'prompt_templates'


def _load_text(filename: str) -> str:
    path = _TEMPLATE_DIR / filename
    try:
        return path.read_text(encoding='utf-8')
    except FileNotFoundError:
        return ''


_DEFAULT_SYSTEM_PROMPT = """
You are a professional skincare AI assistant with expertise in dermatology and cosmetic science.

Your role is to:
- Analyze skin images and provide insights
- Answer skincare questions with evidence-based information
- Recommend natural remedies and OTC products
- Provide personalized skincare routines

IMPORTANT SAFETY RULES:
1. NEVER diagnose medical conditions (no eczema, psoriasis, melanoma, etc.)
2. NEVER prescribe prescription medications
3. ALWAYS add disclaimers to seek professional help for serious issues
4. If you detect potentially serious conditions, recommend seeing a dermatologist
5. Focus on general skin health, not medical treatment
6. Only suggest OTC ingredients and natural remedies

Your responses should be:
- Professional yet friendly
- Evidence-based
- Personalized when user profile is available
- Safety-conscious
- Practical and actionable
"""

SYSTEM_PROMPT = _load_text('system_prompt.txt').strip() or _DEFAULT_SYSTEM_PROMPT.strip()


def _apply_template(template: str, replacements: dict) -> str:
    output = template
    for key, value in replacements.items():
        output = output.replace(f"<<{key}>>", value)
    return output.strip()


_DEFAULT_SKIN_ANALYSIS_TEMPLATE = """
<<SYSTEM_PROMPT>>

<<PROFILE_CONTEXT>>

Please analyze this skin image and provide a comprehensive assessment.

Your response MUST be in this exact JSON format:

{
  "skin_score": <number 0-100>,
  "detected_issues": [
    {
      "name": "<issue name>",
      "confidence": <0-100>,
      "location": "<face area>",
      "severity": "<mild/moderate>"
    }
  ],
  "overall_assessment": "<2-3 sentences about overall skin condition>",
  "natural_remedies": [
    {
      "name": "<remedy name>",
      "description": "<brief description>",
      "ingredients": ["<ingredient 1>", "<ingredient 2>"],
      "usage": "<how to use>",
      "frequency": "<how often>"
    }
  ],
  "cosmetic_products": [
    {
      "type": "<Cleanser/Moisturizer/Serum/Sunscreen/Treatment>",
      "suggestion": "<specific product type recommendation>",
      "key_ingredients": ["<ingredient 1>", "<ingredient 2>"],
      "why": "<reason for recommendation>"
    }
  ],
  "otc_suggestions": [
    {
      "ingredient": "<ingredient name with concentration>",
      "use": "<what it treats>",
      "caution": "<usage advice>"
    }
  ],
  "routine": {
    "morning": ["<step 1>", "<step 2>", "<step 3>", "<step 4>"],
    "night": ["<step 1>", "<step 2>", "<step 3>", "<step 4>"]
  }
}

CRITICAL RULES:
1. If you see anything that looks serious (severe inflammation, unusual growths, deep wounds), set detected_issues to [{ "name": "Consultation Needed", "severity": "refer_to_doctor" }]
2. Skin score: 90-100 (Excellent), 75-89 (Good), 60-74 (Fair), below 60 (Needs Attention)
3. Only detect common cosmetic issues: acne, blackheads, dryness, oiliness, dark circles, uneven tone, large pores, fine lines
4. DO NOT diagnose: eczema, psoriasis, rosacea, melanoma, dermatitis, or any medical condition
5. Keep recommendations practical and safe
6. Return ONLY valid JSON, no additional text

Analyze the image now.
"""

_DEFAULT_QUESTION_TEMPLATE = """
<<SYSTEM_PROMPT>>

<<PROFILE_CONTEXT>>

User's Question: "<<QUESTION>>"

Please provide a helpful, accurate answer to this skincare question.

Your response MUST be in this exact JSON format:

{
  "answer_text": "<comprehensive answer in markdown format>",
  "key_points": ["<point 1>", "<point 2>", "<point 3>"],
  "natural_remedies": [
    {
      "name": "<remedy name>",
      "description": "<brief description>",
      "ingredients": ["<ingredient>"],
      "usage": "<how to use>"
    }
  ],
  "product_recommendations": [
    {
      "type": "<product type>",
      "suggestion": "<what to look for>",
      "key_ingredients": ["<ingredient>"],
      "why": "<reason>"
    }
  ],
  "tips": ["<practical tip 1>", "<practical tip 2>", "<practical tip 3>"],
  "related_questions": ["<related q1>", "<related q2>", "<related q3>"]
}

IMPORTANT RULES:
1. If the question is about a medical condition, advise seeing a dermatologist
2. Focus on prevention, maintenance, and general skincare
3. Provide evidence-based information
4. Keep recommendations safe and practical
5. Personalize based on user profile if available
6. Return ONLY valid JSON, no additional text

Answer the question now.
"""

_DEFAULT_ROUTINE_TEMPLATE = """
<<SYSTEM_PROMPT>>

Create a personalized skincare routine for:
- Skin Type: <<SKIN_TYPE>>
- Concerns: <<CONCERNS>>

Your response MUST be in this exact JSON format:

{
  "morning_routine": [
    {
      "step": 1,
      "name": "<step name>",
      "product_type": "<product type>",
      "instructions": "<how to use>",
      "duration": "<time needed>",
      "key_ingredients": ["<ingredient>"]
    }
  ],
  "night_routine": [
    {
      "step": 1,
      "name": "<step name>",
      "product_type": "<product type>",
      "instructions": "<how to use>",
      "duration": "<time needed>",
      "key_ingredients": ["<ingredient>"]
    }
  ],
  "weekly_treatments": [
    {
      "name": "<treatment name>",
      "frequency": "<how often>",
      "day": "<recommended day>",
      "description": "<what it does>"
    }
  ],
  "general_tips": ["<tip 1>", "<tip 2>", "<tip 3>"]
}

Return ONLY valid JSON.
"""

# Skin image analysis prompt
def get_skin_analysis_prompt(user_profile: dict = None) -> str:
    """Generate prompt for skin image analysis"""
    
    profile_context = ""
    if user_profile:
      profile_context = f"""

  User Context:
  - Age: {user_profile.get('age', 'Not specified')}
  - Skin Type: {user_profile.get('skin_type', 'Not specified')}
  - Sensitivity: {user_profile.get('sensitivity', 'Normal')}
  - Known Concerns: {user_profile.get('concerns', 'None specified')}
  - Allergies: {user_profile.get('allergies', 'None')}
  - Sleep (hours/night): {user_profile.get('sleep_hours', 'Not specified')}
  - Water Intake (liters/day): {user_profile.get('water_intake', 'Not specified')}
      """
    
    template = _load_text('skin_analysis.txt').strip() or _DEFAULT_SKIN_ANALYSIS_TEMPLATE.strip()
    return _apply_template(
        template,
        {
            'SYSTEM_PROMPT': SYSTEM_PROMPT,
            'PROFILE_CONTEXT': profile_context.strip()
        }
    )


# Question answering prompt
def get_question_answer_prompt(question: str, user_profile: dict = None) -> str:
    """Generate prompt for skincare question answering"""
    
    profile_context = ""
    if user_profile:
      profile_context = f"""

  User Context:
  - Age: {user_profile.get('age', 'Not specified')}
  - Skin Type: {user_profile.get('skin_type', 'Not specified')}
  - Sensitivity: {user_profile.get('sensitivity', 'Normal')}
  - Concerns: {user_profile.get('concerns', 'None specified')}
  - Allergies: {user_profile.get('allergies', 'None')}
  - Sleep (hours/night): {user_profile.get('sleep_hours', 'Not specified')}
  - Water Intake (liters/day): {user_profile.get('water_intake', 'Not specified')}
      """
    
    template = _load_text('question_answer.txt').strip() or _DEFAULT_QUESTION_TEMPLATE.strip()
    return _apply_template(
        template,
        {
            'SYSTEM_PROMPT': SYSTEM_PROMPT,
            'PROFILE_CONTEXT': profile_context.strip(),
            'QUESTION': question
        }
    )


# Routine generation prompt
def get_routine_generation_prompt(
  skin_concerns: list,
  skin_type: str,
  plan_days: Optional[int] = None,
  context: Optional[Dict[str, str]] = None
) -> str:
  """Generate personalized routine"""

  template = _load_text('routine_generation.txt').strip() or _DEFAULT_ROUTINE_TEMPLATE.strip()
  concerns = ', '.join(skin_concerns) if skin_concerns else 'General maintenance'
  context = context or {}

  plan_days_value = str(plan_days) if plan_days else 'Not specified'
  return _apply_template(
    template,
    {
      'SYSTEM_PROMPT': SYSTEM_PROMPT,
      'SKIN_TYPE': skin_type,
      'CONCERNS': concerns,
      'PLAN_DAYS': plan_days_value,
      'AGE_GROUP': str(context.get('age_group') or 'Not specified'),
      'SENSITIVITY': str(context.get('sensitivity') or 'Not specified'),
      'ALLERGIES': str(context.get('allergies') or 'None'),
      'SCAN_SUMMARY': str(context.get('scan_summary') or 'None'),
      'QUESTION_SUMMARY': str(context.get('question_summary') or 'None')
    }
  )


# Safety validation prompt
SAFETY_CHECK_PROMPT = """
Analyze this AI response for safety issues.

Check for:
1. Medical diagnosis (eczema, psoriasis, rosacea, melanoma, dermatitis, etc.)
2. Prescription medication recommendations
3. Dangerous ingredients or concentrations
4. Misleading medical claims

If ANY safety issues found, return:
{{ "safe": false, "issues": ["issue 1", "issue 2"] }}

If safe, return:
{{ "safe": true, "issues": [] }}

Response to check:
{response_text}
"""
