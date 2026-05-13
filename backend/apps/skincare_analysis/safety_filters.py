"""
Safety Filters for AI Responses
Ensures AI responses are safe and don't contain medical advice
"""

import re
from typing import Dict, List, Tuple


# Dangerous medical terms that should trigger warnings
MEDICAL_CONDITIONS = [
    'eczema', 'psoriasis', 'rosacea', 'melanoma', 'dermatitis',
    'lupus', 'vitiligo', 'shingles', 'herpes', 'impetigo',
    'cellulitis', 'abscess', 'cyst', 'tumor', 'lesion',
    'basal cell', 'squamous cell', 'skin cancer', 'carcinoma'
]

# Prescription medications that should not be recommended
PRESCRIPTION_MEDS = [
    'tretinoin', 'retin-a', 'accutane', 'isotretinoin', 'adapalene',
    'tazarotene', 'clindamycin', 'erythromycin', 'doxycycline',
    'spironolactone', 'hydroquinone 4%', 'cortisone', 'prednisone',
    'tacrolimus', 'pimecrolimus'
]

# Dangerous ingredients or high concentrations
DANGEROUS_INGREDIENTS = [
    'mercury', 'lead', 'arsenic', 'hydroquinone 4%',
    'tretinoin', 'prescription', 'steroid'
]

# Safe OTC ingredients and their max concentrations
SAFE_OTC_INGREDIENTS = {
    'benzoyl peroxide': 10.0,
    'salicylic acid': 2.0,
    'niacinamide': 10.0,
    'hyaluronic acid': 100.0,  # No real limit
    'vitamin c': 20.0,
    'retinol': 1.0,
    'glycolic acid': 10.0,
    'lactic acid': 10.0,
    'azelaic acid': 10.0,
    'zinc oxide': 25.0,
}


class SafetyFilter:
    """Validates AI responses for safety"""
    
    def __init__(self):
        self.disclaimer = (
            "WARNING: This analysis is for informational and educational "
            "purposes only. It is NOT a medical diagnosis. For persistent skin "
            "concerns, unusual symptoms, or before starting any new treatment, "
            "please consult a board-certified dermatologist or healthcare professional."
        )
    
    def check_response_safety(self, response_text: str) -> Tuple[bool, List[str]]:
        """
        Check if AI response is safe
        
        Args:
            response_text: The AI response to check
        
        Returns:
            Tuple of (is_safe, list_of_issues)
        """
        issues = []
        response_lower = response_text.lower()
        
        # Check for medical conditions
        for condition in MEDICAL_CONDITIONS:
            if re.search(r'\b' + condition + r'\b', response_lower):
                issues.append(f"Contains medical diagnosis term: '{condition}'")
        
        # Check for prescription medications
        for med in PRESCRIPTION_MEDS:
            if re.search(r'\b' + med + r'\b', response_lower):
                issues.append(f"Recommends prescription medication: '{med}'")
        
        # Check for dangerous ingredients
        for ingredient in DANGEROUS_INGREDIENTS:
            if ingredient in response_lower:
                issues.append(f"Contains dangerous ingredient: '{ingredient}'")
        
        # If any issues found, not safe
        is_safe = len(issues) == 0
        
        return is_safe, issues
    
    def validate_skin_analysis(self, analysis: Dict) -> Dict:
        """
        Validate and sanitize skin analysis response
        
        Args:
            analysis: Raw AI analysis
        
        Returns:
            Sanitized analysis with safety checks
        """
        # Check detected issues
        detected_issues = analysis.get('detected_issues')
        if not detected_issues and isinstance(analysis.get('analysis'), dict):
            detected_issues = analysis.get('analysis', {}).get('detected_issues', [])

        if detected_issues:
            for issue in detected_issues:
                if isinstance(issue, str):
                    issue_name = issue.lower()
                elif isinstance(issue, dict):
                    issue_name = issue.get('name', '').lower()
                else:
                    issue_name = ''
                
                # Check if it's a medical condition
                for condition in MEDICAL_CONDITIONS:
                    if condition in issue_name:
                        # Replace with generic term and flag for doctor visit
                        return {
                            'refer_to_doctor': True,
                            'message': (
                                "We've detected something that may require professional "
                                "evaluation. Please consult a dermatologist for an accurate "
                                "assessment and treatment plan."
                            ),
                            'detected_issue': 'Requires Professional Assessment'
                        }
        
        # Add disclaimer
        analysis['disclaimer'] = self.disclaimer
        
        # Validate OTC suggestions
        otc_suggestions = analysis.get('otc_suggestions')
        if otc_suggestions is None and isinstance(analysis.get('recommendations'), dict):
            otc_suggestions = analysis.get('recommendations', {}).get('otc')

        if otc_suggestions is not None:
            safe_otc = self._validate_otc_suggestions(otc_suggestions)
            if 'otc_suggestions' in analysis:
                analysis['otc_suggestions'] = safe_otc
            elif isinstance(analysis.get('recommendations'), dict):
                analysis['recommendations']['otc'] = safe_otc
        
        return analysis
    
    def validate_question_answer(self, answer: Dict) -> Dict:
        """
        Validate and sanitize question answer response
        
        Args:
            answer: Raw AI answer
        
        Returns:
            Sanitized answer with safety checks
        """
        # Check answer text for safety
        if 'answer_text' in answer:
            is_safe, issues = self.check_response_safety(answer['answer_text'])
            
            if not is_safe:
                # Return safe fallback response
                return {
                    'answer_text': (
                        "Your question touches on medical topics that require "
                        "professional evaluation. I recommend consulting a "
                        "board-certified dermatologist who can provide personalized "
                        "medical advice based on a proper examination."
                    ),
                    'disclaimer': self.disclaimer,
                    'safety_issues': issues
                }
        
        # Add disclaimer
        answer['disclaimer'] = self.disclaimer
        
        return answer
    
    def _validate_otc_suggestions(self, suggestions: List[Dict]) -> List[Dict]:
        """Validate OTC ingredient concentrations"""
        safe_suggestions = []
        
        for suggestion in suggestions:
            if isinstance(suggestion, str):
                suggestion = {'ingredient': suggestion}
            if not isinstance(suggestion, dict):
                continue

            ingredient = suggestion.get('ingredient', '')
            ingredient_lower = ingredient.lower()
            
            # Check if it's a prescription item
            is_prescription = any(
                med in ingredient_lower for med in PRESCRIPTION_MEDS
            )
            
            if is_prescription:
                continue  # Skip prescription items
            
            # Check concentration if specified
            concentration = self._extract_concentration(ingredient_lower)
            if not concentration and suggestion.get('concentration'):
                concentration = self._extract_concentration(str(suggestion.get('concentration')).lower())
            if concentration:
                ingredient_name = self._get_ingredient_name(ingredient_lower)
                max_safe = SAFE_OTC_INGREDIENTS.get(ingredient_name)
                
                if max_safe and concentration > max_safe:
                    # Adjust to safe concentration
                    suggestion['ingredient'] = f"{ingredient_name} {max_safe}%"
                    suggestion['caution'] = (
                        f"Use maximum {max_safe}% concentration for safety. "
                        f"{suggestion.get('caution', '')}"
                    )
            
            safe_suggestions.append(suggestion)
        
        return safe_suggestions
    
    def _extract_concentration(self, ingredient_str: str) -> float:
        """Extract percentage concentration from ingredient string"""
        match = re.search(r'(\d+(?:\.\d+)?)\s*%', ingredient_str)
        if match:
            return float(match.group(1))
        return 0.0
    
    def _get_ingredient_name(self, ingredient_str: str) -> str:
        """Extract ingredient name without concentration"""
        # Remove percentage
        name = re.sub(r'\d+(?:\.\d+)?\s*%', '', ingredient_str)
        return name.strip().lower()
    
    def add_severity_warning(self, severity: str) -> str:
        """Add appropriate warning based on severity"""
        if severity == 'severe' or severity == 'refer_to_doctor':
            return (
                "⚠️ IMPORTANT: This appears to be a condition that requires "
                "professional medical attention. Please schedule an appointment "
                "with a dermatologist as soon as possible."
            )
        elif severity == 'moderate':
            return (
                "ℹ️ Note: While this condition may be manageable with OTC products, "
                "consider consulting a dermatologist if it doesn't improve within "
                "4-6 weeks or gets worse."
            )
        else:
            return ""


# Singleton instance
_safety_filter = None


def get_safety_filter() -> SafetyFilter:
    """Get or create SafetyFilter instance"""
    global _safety_filter
    if _safety_filter is None:
        _safety_filter = SafetyFilter()
    return _safety_filter
