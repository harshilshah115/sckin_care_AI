import time
"""
Gemini API Client Wrapper
Handles all interactions with Google's Gemini AI
"""

import os
import json
import base64
import re
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, Optional
from google import genai
from google.genai import types
from PIL import Image
import io


class GeminiClient:
    """Client for Google Gemini AI API"""
    
    def __init__(self):
        """Initialize Gemini client with API key"""
        self.api_key = os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        # Initialize client using the installed SDK's supported signature
        self.client = self._create_client()
        
        # Model configuration
        self.primary_model = os.getenv('AI_PRIMARY_MODEL', os.getenv('AI_MODEL', 'gemini-2.5-flash'))
        self.fallback_model = os.getenv('AI_FALLBACK_MODEL', 'gemini-2.0-flash')
        self.model_name = self.primary_model
        self.temperature = float(os.getenv('AI_TEMPERATURE', '0.1'))
        self.max_tokens = int(os.getenv('AI_MAX_TOKENS', '4096'))
        
        # Base generation config
        self.generation_config = self._build_generation_config()
        self._last_call_time = 0.0
        self._min_call_interval = float(os.getenv('AI_MIN_CALL_INTERVAL_SEC', '1'))
        self._last_model_used = self.model_name
    
    def analyze_image(self, image_path: str, prompt: str) -> Dict[str, Any]:
        """
        Analyze an image with Gemini Vision
        
        Args:
            image_path: Path to the image file
            prompt: Text prompt for analysis
        
        Returns:
            Parsed JSON response from Gemini
        """
        try:
            # Load and prepare image
            img = Image.open(image_path)
            
            # Convert to RGB if needed
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            # Resize if too large (Gemini has size limits)
            max_size = 1024
            if max(img.size) > max_size:
                img.thumbnail((max_size, max_size), Image.Resampling.LANCZOS)
            
            # Convert image to base64 for inline upload
            img_byte_arr = io.BytesIO()
            img.save(img_byte_arr, format='JPEG')
            img_bytes = img_byte_arr.getvalue()
            
            # Create image part using types.Part with inline_data
            image_part = types.Part.from_bytes(
                data=img_bytes,
                mime_type='image/jpeg'
            )
            
            # Generate content with image and prompt
            response = self._analyze_with_schema(prompt, image_part, self._analysis_response_schema())
            if os.getenv('DEBUG'):
                print("Raw Gemini response:", response.text)
            self._log_ai_output('initial', response.text)

            if not response or not response.text:
                return self._build_fallback_response('Empty AI response')

            parsed = self._parse_json_response(response.text)
            if parsed.get('success'):
                return parsed

            # Retry once with a compact prompt to reduce long JSON outputs.
            compact_prompt = self._build_compact_prompt(prompt)
            response = self._analyze_with_schema(compact_prompt, image_part, self._analysis_response_schema())
            self._log_ai_output('compact', response.text)

            if not response or not response.text:
                return self._build_fallback_response('Empty AI response')

            parsed_retry = self._parse_json_response(response.text)
            if parsed_retry.get('success'):
                return parsed_retry

            # Final attempt: smaller schema to maximize valid output.
            minimal_prompt = self._build_analysis_only_prompt(prompt)
            minimal_response = self._analyze_with_schema(
                minimal_prompt,
                image_part,
                self._analysis_only_response_schema()
            )
            self._log_ai_output('minimal', minimal_response.text)
            if not minimal_response or not minimal_response.text:
                return self._build_fallback_response('Empty AI response')
            minimal_parsed = self._parse_json_response(minimal_response.text)
            if minimal_parsed.get('success'):
                merged = self._merge_minimal_into_full(minimal_parsed.get('data', {}))
                return {
                    'success': True,
                    'data': merged,
                    'raw_response': minimal_parsed.get('raw_response')
                }

            return self._build_fallback_response(parsed_retry.get('error'))
        
        except Exception as e:
            return self._build_fallback_response(str(e))
    
    def generate_text(self, prompt: str) -> Dict[str, Any]:
        """
        Generate text response from Gemini
        
        Args:
            prompt: Text prompt
        
        Returns:
            Parsed JSON response from Gemini
        """
        try:
            response = self._generate_content_with_rate_limit(
                contents=prompt,
                config=self.generation_config
            )

            self._log_ai_output('text', response.text)
            
            return self._parse_json_response(response.text)
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'raw_response': None
            }
    
    def test_connection(self) -> Dict[str, Any]:
        """Test if Gemini API is working"""
        try:
            response = self._generate_content_with_rate_limit(
                contents="Say 'Hello' in JSON format: {\"message\": \"Hello\"}",
                config=self.generation_config
            )
            return {
                'success': True,
                'response': response.text
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'error_type': type(e).__name__
            }

    def _build_generation_config(self, response_schema: Optional[Dict[str, Any]] = None):
        """Build a generation config."""
        return types.GenerateContentConfig(
            temperature=self.temperature,
            max_output_tokens=self.max_tokens,
            response_mime_type='application/json'
        )

    def _create_client(self):
        """Create a Gemini client with a safe fallback for older SDKs."""
        api_endpoint = os.getenv('AI_API_ENDPOINT')
        client_options = None
        if api_endpoint:
            client_options = {'api_endpoint': api_endpoint}

        try:
            if client_options:
                return genai.Client(api_key=self.api_key, client_options=client_options)
            return genai.Client(api_key=self.api_key)
        except TypeError:
            # Older SDKs do not accept client_options; fall back to basic init.
            return genai.Client(api_key=self.api_key)

    def _analysis_response_schema(self) -> Dict[str, Any]:
        """Schema for structured skin analysis JSON responses."""
        return {
            'type': 'OBJECT',
            'properties': {
                'meta': {
                    'type': 'OBJECT',
                    'properties': {
                        'request_id': {'type': 'STRING'},
                        'timestamp': {'type': 'STRING'},
                        'model_version': {'type': 'STRING'},
                        'processing_time_ms': {'type': 'INTEGER'},
                        'image_quality': {
                            'type': 'OBJECT',
                            'properties': {
                                'lighting': {'type': 'STRING'},
                                'blur': {'type': 'STRING'},
                                'angle': {'type': 'STRING'},
                                'confidence': {'type': 'INTEGER'}
                            },
                            'required': ['lighting', 'blur', 'angle', 'confidence']
                        }
                    },
                    'required': ['request_id', 'timestamp', 'model_version', 'processing_time_ms', 'image_quality']
                },
                'user_profile': {
                    'type': 'OBJECT',
                    'properties': {
                        'age_range': {'type': 'STRING'},
                        'gender': {'type': 'STRING'},
                        'skin_type_self_reported': {'type': 'STRING'},
                        'lifestyle': {
                            'type': 'OBJECT',
                            'properties': {
                                'sleep_hours': {'type': 'NUMBER'},
                                'water_intake_liters': {'type': 'NUMBER'},
                                'diet_type': {'type': 'STRING'},
                                'stress_level': {'type': 'STRING'}
                            },
                            'required': ['sleep_hours', 'water_intake_liters', 'diet_type', 'stress_level']
                        }
                    },
                    'required': ['age_range', 'gender', 'skin_type_self_reported', 'lifestyle']
                },
                'analysis': {
                    'type': 'OBJECT',
                    'properties': {
                        'skin_score': {'type': 'INTEGER'},
                        'skin_type_detected': {
                            'type': 'OBJECT',
                            'properties': {
                                'type': {'type': 'STRING'},
                                'confidence': {'type': 'INTEGER'}
                            },
                            'required': ['type', 'confidence']
                        },
                        'metrics': {
                            'type': 'OBJECT',
                            'properties': {
                                'oiliness': {'type': 'INTEGER'},
                                'hydration': {'type': 'INTEGER'},
                                'texture': {'type': 'INTEGER'},
                                'pore_visibility': {'type': 'INTEGER'},
                                'pigmentation': {'type': 'INTEGER'},
                                'overall_health': {'type': 'INTEGER'}
                            },
                            'required': ['oiliness', 'hydration', 'texture', 'pore_visibility', 'pigmentation', 'overall_health']
                        },
                        'face_zones': {
                            'type': 'ARRAY',
                            'items': {
                                'type': 'OBJECT',
                                'properties': {
                                    'zone': {'type': 'STRING'},
                                    'conditions': {
                                        'type': 'ARRAY',
                                        'items': {
                                            'type': 'OBJECT',
                                            'properties': {
                                                'name': {'type': 'STRING'},
                                                'severity': {'type': 'STRING'},
                                                'confidence': {'type': 'INTEGER'}
                                            },
                                            'required': ['name', 'severity', 'confidence']
                                        }
                                    }
                                },
                                'required': ['zone', 'conditions']
                            }
                        },
                        'detected_issues': {
                            'type': 'ARRAY',
                            'items': {
                                'type': 'OBJECT',
                                'properties': {
                                    'name': {'type': 'STRING'},
                                    'severity': {'type': 'STRING'},
                                    'confidence': {'type': 'INTEGER'},
                                    'affected_area_percent': {'type': 'INTEGER'},
                                    'zones': {
                                        'type': 'ARRAY',
                                        'items': {'type': 'STRING'}
                                    }
                                },
                                'required': ['name', 'severity', 'confidence', 'affected_area_percent', 'zones']
                            }
                        },
                        'probable_causes': {
                            'type': 'ARRAY',
                            'items': {
                                'type': 'OBJECT',
                                'properties': {
                                    'cause': {'type': 'STRING'},
                                    'confidence': {'type': 'INTEGER'}
                                },
                                'required': ['cause', 'confidence']
                            }
                        },
                        'risk_flags': {
                            'type': 'ARRAY',
                            'items': {
                                'type': 'OBJECT',
                                'properties': {
                                    'risk': {'type': 'STRING'},
                                    'level': {'type': 'STRING'}
                                },
                                'required': ['risk', 'level']
                            }
                        }
                    },
                    'required': ['skin_score', 'skin_type_detected', 'metrics', 'face_zones', 'detected_issues', 'probable_causes', 'risk_flags']
                },
                'recommendations': {
                    'type': 'OBJECT',
                    'properties': {
                        'natural': {
                            'type': 'ARRAY',
                            'items': {
                                'type': 'OBJECT',
                                'properties': {
                                    'name': {'type': 'STRING'},
                                    'type': {'type': 'STRING'},
                                    'ingredients': {'type': 'ARRAY', 'items': {'type': 'STRING'}},
                                    'benefits': {'type': 'ARRAY', 'items': {'type': 'STRING'}},
                                    'usage': {'type': 'STRING'},
                                    'frequency': {'type': 'STRING'},
                                    'suitable_for': {'type': 'ARRAY', 'items': {'type': 'STRING'}}
                                },
                                'required': ['name', 'type', 'ingredients', 'benefits', 'usage', 'frequency', 'suitable_for']
                            }
                        },
                        'otc': {
                            'type': 'ARRAY',
                            'items': {
                                'type': 'OBJECT',
                                'properties': {
                                    'ingredient': {'type': 'STRING'},
                                    'concentration': {'type': 'STRING'},
                                    'benefits': {'type': 'ARRAY', 'items': {'type': 'STRING'}},
                                    'usage': {'type': 'STRING'},
                                    'caution': {'type': 'STRING'},
                                    'suitable_for': {'type': 'ARRAY', 'items': {'type': 'STRING'}}
                                },
                                'required': ['ingredient', 'concentration', 'benefits', 'usage', 'caution', 'suitable_for']
                            }
                        },
                        'cosmetic': {
                            'type': 'ARRAY',
                            'items': {
                                'type': 'OBJECT',
                                'properties': {
                                    'category': {'type': 'STRING'},
                                    'suggestion': {'type': 'STRING'},
                                    'key_ingredients': {'type': 'ARRAY', 'items': {'type': 'STRING'}},
                                    'skin_type_match': {'type': 'ARRAY', 'items': {'type': 'STRING'}},
                                    'why': {'type': 'STRING'}
                                },
                                'required': ['category', 'suggestion', 'key_ingredients', 'skin_type_match', 'why']
                            }
                        },
                        'lifestyle': {'type': 'ARRAY', 'items': {'type': 'STRING'}}
                    },
                    'required': ['natural', 'otc', 'cosmetic', 'lifestyle']
                },
                'routine': {
                    'type': 'OBJECT',
                    'properties': {
                        'morning': {
                            'type': 'ARRAY',
                            'items': {
                                'type': 'OBJECT',
                                'properties': {
                                    'step': {'type': 'INTEGER'},
                                    'action': {'type': 'STRING'},
                                    'details': {'type': 'STRING'}
                                },
                                'required': ['step', 'action', 'details']
                            }
                        },
                        'night': {
                            'type': 'ARRAY',
                            'items': {
                                'type': 'OBJECT',
                                'properties': {
                                    'step': {'type': 'INTEGER'},
                                    'action': {'type': 'STRING'},
                                    'details': {'type': 'STRING'}
                                },
                                'required': ['step', 'action', 'details']
                            }
                        },
                        'weekly': {
                            'type': 'ARRAY',
                            'items': {
                                'type': 'OBJECT',
                                'properties': {
                                    'action': {'type': 'STRING'},
                                    'details': {'type': 'STRING'}
                                },
                                'required': ['action', 'details']
                            }
                        }
                    },
                    'required': ['morning', 'night', 'weekly']
                },
                'progress_tracking': {
                    'type': 'OBJECT',
                    'properties': {
                        'enabled': {'type': 'BOOLEAN'},
                        'comparison': {
                            'type': 'OBJECT',
                            'properties': {
                                'previous_score': {'type': 'INTEGER'},
                                'current_score': {'type': 'INTEGER'},
                                'change': {'type': 'STRING'},
                                'trend': {'type': 'STRING'}
                            },
                            'required': ['previous_score', 'current_score', 'change', 'trend']
                        }
                    },
                    'required': ['enabled', 'comparison']
                },
                'alerts': {
                    'type': 'ARRAY',
                    'items': {
                        'type': 'OBJECT',
                        'properties': {
                            'type': {'type': 'STRING'},
                            'message': {'type': 'STRING'}
                        },
                        'required': ['type', 'message']
                    }
                }
            },
            'required': ['meta', 'user_profile', 'analysis', 'recommendations', 'routine', 'progress_tracking', 'alerts']
        }

    def _analysis_only_response_schema(self) -> Dict[str, Any]:
        """Schema for a smaller analysis-only response."""
        return {
            'type': 'OBJECT',
            'properties': {
                'meta': self._analysis_response_schema()['properties']['meta'],
                'analysis': self._analysis_response_schema()['properties']['analysis'],
                'progress_tracking': self._analysis_response_schema()['properties']['progress_tracking'],
                'alerts': self._analysis_response_schema()['properties']['alerts']
            },
            'required': ['meta', 'analysis', 'progress_tracking', 'alerts']
        }

    def _analyze_with_schema(self, prompt: str, image_part: types.Part, schema: Dict[str, Any]):
        """Run a vision request with the provided schema (no retry on API failures)."""
        return self._generate_content_with_rate_limit(
            contents=[prompt, image_part],
            config=self._build_generation_config(schema)
        )


    def _build_compact_prompt(self, prompt: str) -> str:
        """Append compact-output rules to reduce JSON size."""
        compact_rules = (
            "\n\nCOMPACT MODE RULES:\n"
            "- Keep strings concise and single-line (no raw line breaks).\n"
            "- Limit arrays to a maximum of 5 items.\n"
            "- Prefer short, concrete phrases.\n"
            "- If unsure, use empty arrays or nulls.\n"
            "- Do not add any extra fields.\n"
        )
        return f"{prompt}{compact_rules}"

    def _build_analysis_only_prompt(self, prompt: str) -> str:
        """Reduce the response to core analysis fields only."""
        rules = (
            "\n\nANALYSIS-ONLY MODE:\n"
            "- Return ONLY: meta, analysis, progress_tracking, alerts.\n"
            "- Do not include user_profile, recommendations, or routine.\n"
            "- Keep strings concise and single-line.\n"
            "- If unsure, use empty arrays or nulls.\n"
            "- Do not add extra fields.\n"
        )
        return f"{prompt}{rules}"

    def _parse_json_response(self, text: str) -> Dict[str, Any]:
        """Parse JSON response with a safe fallback extractor."""
        normalized = self._normalize_json_text(text)
        try:
            result = json.loads(normalized)
            return {
                'success': True,
                'data': result,
                'raw_response': text
            }
        except json.JSONDecodeError as e:
            extracted = self._extract_json(normalized)
            if extracted:
                try:
                    cleaned = self._cleanup_json(extracted)
                    result = json.loads(cleaned)
                    return {
                        'success': True,
                        'data': result,
                        'raw_response': text
                    }
                except json.JSONDecodeError as inner_error:
                    return {
                        'success': False,
                        'error': f'Failed to parse JSON: {str(inner_error)}',
                        'raw_response': text
                    }

            return {
                'success': False,
                'error': f'Failed to parse JSON: {str(e)}',
                'raw_response': text
            }

    def _build_fallback_response(self, error_message: Optional[str] = None) -> Dict[str, Any]:
        """Return a valid minimal payload when parsing fails."""
        now = datetime.now(timezone.utc).isoformat()
        alert_message = self._build_friendly_alert_message(error_message)
        fallback = {
            'meta': {
                'request_id': str(uuid.uuid4()),
                'timestamp': now,
                'model_version': self.model_name,
                'processing_time_ms': 0,
                'image_quality': {
                    'lighting': 'low',
                    'blur': 'medium',
                    'angle': 'frontal',
                    'confidence': 0
                }
            },
            'user_profile': {
                'age_range': 'unknown',
                'gender': 'unknown',
                'skin_type_self_reported': 'unknown',
                'lifestyle': {
                    'sleep_hours': 0,
                    'water_intake_liters': 0,
                    'diet_type': 'unknown',
                    'stress_level': 'low'
                }
            },
            'analysis': {
                'skin_score': 0,
                'skin_type_detected': {
                    'type': 'normal',
                    'confidence': 0
                },
                'metrics': {
                    'oiliness': 0,
                    'hydration': 0,
                    'texture': 0,
                    'pore_visibility': 0,
                    'pigmentation': 0,
                    'overall_health': 0
                },
                'face_zones': [],
                'detected_issues': [],
                'probable_causes': [],
                'risk_flags': []
            },
            'recommendations': {
                'natural': [],
                'otc': [],
                'cosmetic': [],
                'lifestyle': []
            },
            'routine': {
                'morning': [],
                'night': [],
                'weekly': []
            },
            'progress_tracking': {
                'enabled': False,
                'comparison': {
                    'previous_score': 0,
                    'current_score': 0,
                    'change': '0',
                    'trend': 'stable'
                }
            },
            'alerts': [
                {
                    'type': 'general',
                    'message': alert_message
                }
            ]
        }

        if error_message:
            fallback['alerts'].append({
                'type': 'general',
                'message': f'AI parsing error: {error_message}'
            })

        return {
            'success': True,
            'data': fallback,
            'raw_response': None
        }

    def _log_ai_output(self, stage: str, text: Optional[str]) -> None:
        """Append raw AI output to backend/logs/ai_raw.txt."""
        if text is None:
            return

        try:
            log_dir = Path(__file__).resolve().parents[2] / 'logs'
            log_dir.mkdir(parents=True, exist_ok=True)
            log_path = log_dir / 'ai_raw.txt'
            timestamp = datetime.now(timezone.utc).isoformat()
            with log_path.open('a', encoding='utf-8') as log_file:
                log_file.write(f"\n[{timestamp}] stage={stage} model={self.model_name}\n")
                log_file.write(text)
                if not text.endswith('\n'):
                    log_file.write('\n')
        except Exception:
            # Never fail the request because logging failed.
            return

    def _merge_minimal_into_full(self, minimal: Dict[str, Any]) -> Dict[str, Any]:
        """Merge a minimal analysis-only response into a full schema."""
        base = self._build_fallback_response().get('data', {})
        if not base:
            return minimal

        for key in ['meta', 'analysis', 'progress_tracking', 'alerts']:
            if key in minimal:
                base[key] = minimal[key]

        return base

    def _build_friendly_alert_message(self, error_message: Optional[str]) -> str:
        """Return a user-facing alert message based on the error."""
        if not error_message:
            return 'Analysis unavailable. Please re-upload with a clear full-face photo.'

        normalized = error_message.upper()
        if '503' in normalized or 'UNAVAILABLE' in normalized:
            return 'High demand detected. Retrying analysis, please wait a moment.'
        if '429' in normalized:
            return 'Rate limit reached. Please try again in a moment.'

        return 'Analysis unavailable. Please re-upload with a clear full-face photo.'

    def get_last_model_used(self) -> str:
        """Return the last model used for a Gemini request."""
        return self._last_model_used

    def _normalize_json_text(self, text: str) -> str:
        """Normalize model output to improve JSON parsing odds."""
        if not text:
            return ''

        cleaned = text.strip()

        # Strip fenced code blocks
        if cleaned.startswith('```'):
            cleaned = re.sub(r'^```(?:json)?\s*', '', cleaned, flags=re.IGNORECASE)
            cleaned = re.sub(r'```\s*$', '', cleaned)

        cleaned = self._escape_newlines_in_strings(cleaned)
        return cleaned.strip()

    def _escape_newlines_in_strings(self, text: str) -> str:
        """Escape raw newlines that appear inside JSON strings."""
        if not text:
            return ''

        chars = list(text)
        in_string = False
        escape = False

        for i, char in enumerate(chars):
            if in_string:
                if escape:
                    escape = False
                    continue
                if char == '\\':
                    escape = True
                    continue
                if char == '"':
                    in_string = False
                    continue
                if char == '\n':
                    chars[i] = '\\n'
            else:
                if char == '"':
                    in_string = True

        return ''.join(chars)

    def _cleanup_json(self, text: str) -> str:
        """Remove common JSON issues such as trailing commas."""
        cleaned = text.strip()
        # Convert single-quoted object keys to double quotes.
        cleaned = re.sub(r"([{,]\s*)'([^']+)'\s*:", r'\1"\2":', cleaned)
        # Quote unquoted object keys.
        cleaned = re.sub(r'([{,]\s*)([A-Za-z_][A-Za-z0-9_\-]*)\s*:', r'\1"\2":', cleaned)
        cleaned = re.sub(r',\s*([}\]])', r'\1', cleaned)
        return cleaned

    def _extract_json(self, text: str) -> Optional[str]:
        """Extract the first JSON object from a response string."""
        if not text:
            return None

        start = text.find('{')
        if start == -1:
            return None

        in_string = False
        escape = False
        depth = 0

        for i in range(start, len(text)):
            char = text[i]

            if in_string:
                if escape:
                    escape = False
                elif char == '\\':
                    escape = True
                elif char == '"':
                    in_string = False
                continue

            if char == '"':
                in_string = True
            elif char == '{':
                depth += 1
            elif char == '}':
                depth -= 1
                if depth == 0:
                    return text[start:i + 1]

        return None

    def _generate_content_with_rate_limit(self, contents, config):
        """Enforce a minimum delay between Gemini API calls."""
        retries = int(os.getenv('AI_RETRY_COUNT', '3'))
        delay = float(os.getenv('AI_RETRY_DELAY_SEC', '2'))

        for attempt in range(retries):
            now = time.time()
            wait_time = self._min_call_interval - (now - self._last_call_time)
            if wait_time > 0:
                time.sleep(wait_time)

            try:
                response = self.client.models.generate_content(
                    model=self.primary_model,
                    contents=contents,
                    config=config
                )
                self._last_call_time = time.time()
                self._last_model_used = self.primary_model
                return response
            except Exception as e:
                error_str = str(e)
                normalized = error_str.upper()

                if '503' in normalized or 'UNAVAILABLE' in normalized:
                    if os.getenv('DEBUG'):
                        print(f"Retry {attempt + 1}/{retries} due to overload")
                    time.sleep(delay * (attempt + 1))
                    continue

                if '429' in normalized:
                    if os.getenv('DEBUG'):
                        print("Rate limit hit, waiting before retry")
                    time.sleep(max(delay * (attempt + 1), 10))
                    continue

                if os.getenv('DEBUG'):
                    print("Switching to fallback model due to error:", error_str)
                try:
                    response = self.client.models.generate_content(
                        model=self.fallback_model,
                        contents=contents,
                        config=config
                    )
                    self._last_call_time = time.time()
                    self._last_model_used = self.fallback_model
                    return response
                except Exception as fallback_error:
                    raise RuntimeError(
                        f"Gemini API failed: {str(fallback_error)}"
                    )

        if os.getenv('DEBUG'):
            print("All retries failed, using fallback model")
        try:
            response = self.client.models.generate_content(
                model=self.fallback_model,
                contents=contents,
                config=config
            )
            self._last_call_time = time.time()
            self._last_model_used = self.fallback_model
            return response
        except Exception as e:
            raise RuntimeError(f"Gemini API failed: {str(e)}")


# Singleton instance
_gemini_client = None


def get_gemini_client() -> GeminiClient:
    """Get or create Gemini client instance"""
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client
