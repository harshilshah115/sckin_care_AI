"""
Grok API Client Wrapper
Handles interactions with xAI's Grok API as fallback AI provider.
"""

import os
import json
import time
import requests
from typing import Dict, Any, Optional


class GrokClient:
    """Wrapper for xAI Grok API."""
    
    def __init__(self):
        self.api_key = os.getenv('GROK_API_KEY', '')
        self.api_url = 'https://api.x.ai/v1/chat/completions'
        self.model = os.getenv('GROK_MODEL', 'grok-beta')
        self.timeout = int(os.getenv('AI_TIMEOUT', '30'))
    
    def is_available(self) -> bool:
        return bool(self.api_key) and self.api_key != 'your-grok-api-key'
    
    def analyze_image(self, image_bytes: bytes, prompt: str) -> Dict[str, Any]:
        """Analyze an image using Grok vision."""
        if not self.is_available():
            return {'success': False, 'error': 'Grok API key not configured'}
        
        import base64
        encoded = base64.b64encode(image_bytes).decode('utf-8')
        
        try:
            response = requests.post(
                self.api_url,
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json',
                },
                json={
                    'model': 'grok-vision-beta',
                    'messages': [
                        {'role': 'system', 'content': prompt},
                        {
                            'role': 'user',
                            'content': [
                                {'type': 'image_url', 'image_url': {'url': f'data:image/jpeg;base64,{encoded}'}},
                                {'type': 'text', 'text': 'Analyze this skin image and return JSON.'}
                            ]
                        }
                    ],
                    'temperature': 0.3,
                    'max_tokens': 2048,
                    'response_format': {'type': 'json_object'},
                },
                timeout=self.timeout,
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                return self._parse_json(content)
            
            return {'success': False, 'error': f'Grok API error: {response.status_code}'}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def generate_text(self, prompt: str) -> Dict[str, Any]:
        """Generate text response from Grok."""
        if not self.is_available():
            return {'success': False, 'error': 'Grok API key not configured'}
        
        try:
            response = requests.post(
                self.api_url,
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json',
                },
                json={
                    'model': self.model,
                    'messages': [
                        {'role': 'system', 'content': 'You are a skincare expert. Always respond in JSON format.'},
                        {'role': 'user', 'content': prompt},
                    ],
                    'temperature': 0.3,
                    'max_tokens': 2048,
                    'response_format': {'type': 'json_object'},
                },
                timeout=self.timeout,
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                return self._parse_json(content)
            
            return {'success': False, 'error': f'Grok API error: {response.status_code}'}
        
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def _parse_json(self, text: str) -> Dict[str, Any]:
        """Parse JSON from Grok response."""
        try:
            parsed = json.loads(text)
            return {'success': True, 'data': parsed, 'raw_response': text}
        except json.JSONDecodeError:
            # Try to extract JSON from markdown
            import re
            match = re.search(r'```(?:json)?\s*([\s\S]*?)```', text)
            if match:
                try:
                    parsed = json.loads(match.group(1))
                    return {'success': True, 'data': parsed, 'raw_response': text}
                except json.JSONDecodeError:
                    pass
            return {'success': False, 'error': 'Failed to parse Grok response as JSON', 'raw_response': text}


def get_grok_client() -> GrokClient:
    """Get or create a Grok client instance."""
    return GrokClient()
