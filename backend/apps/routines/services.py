"""
Weather Service and Routine Adaptation Logic
Integrates with OpenWeatherMap API for weather-based routine suggestions.
"""

import os
import logging
import requests
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

OPENWEATHER_API_KEY = os.getenv('OPENWEATHER_API_KEY', '')
WEATHER_CACHE = {}
CACHE_TTL = 1800  # 30 minutes


def get_weather(city: str = 'Mumbai', lat: float = None, lon: float = None) -> Dict[str, Any]:
    """
    Get current weather conditions from OpenWeatherMap.
    Falls back to reasonable defaults if API is unavailable.
    """
    cache_key = f"{city or f'{lat},{lon}'}"
    import time
    now = time.time()
    
    if cache_key in WEATHER_CACHE:
        cached = WEATHER_CACHE[cache_key]
        if now - cached['timestamp'] < CACHE_TTL:
            return cached['data']
    
    if not OPENWEATHER_API_KEY or OPENWEATHER_API_KEY == 'your-openweather-api-key':
        return _default_weather(city)
    
    try:
        if lat and lon:
            url = f'https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric'
        else:
            url = f'https://api.openweathermap.org/data/2.5/weather?q={city}&appid={OPENWEATHER_API_KEY}&units=metric'
        
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            result = _parse_weather_response(data)
            WEATHER_CACHE[cache_key] = {'data': result, 'timestamp': now}
            return result
    
    except Exception as e:
        logger.warning(f'Weather API error: {e}')
    
    return _default_weather(city)


def _parse_weather_response(data: Dict) -> Dict[str, Any]:
    """Parse OpenWeatherMap response into our format."""
    main = data.get('main', {})
    wind = data.get('wind', {})
    weather = data.get('weather', [{}])[0]
    
    temp = main.get('temp', 25)
    humidity = main.get('humidity', 50)
    weather_id = weather.get('id', 800)
    description = weather.get('description', 'clear sky')
    wind_speed = wind.get('speed', 0)
    
    # Determine weather condition category
    condition = _classify_weather(temp, humidity, weather_id)
    
    uv_index = data.get('uvi', 0) if 'uvi' in data else _estimate_uv(weather_id, description)
    
    return {
        'temperature': round(temp, 1),
        'humidity': humidity,
        'condition': condition,
        'description': description,
        'wind_speed': wind_speed,
        'uv_index': uv_index,
        'city': data.get('name', 'Unknown'),
        'source': 'openweathermap',
    }


def _classify_weather(temp: float, humidity: int, weather_id: int) -> str:
    """Classify weather into our adaptation categories."""
    if weather_id >= 800 and weather_id < 900:
        if weather_id == 800:
            if temp > 35:
                return 'hot_dry'
            elif temp > 25:
                if humidity > 60:
                    return 'hot_humid'
                return 'sunny'
            elif temp < 10:
                if humidity > 60:
                    return 'cold_humid'
                return 'cold_dry'
        elif weather_id in [801, 802, 803]:
            if temp > 30:
                return 'hot_humid' if humidity > 60 else 'hot_dry'
            return 'normal'
        elif weather_id == 804:
            if temp > 25 and humidity > 70:
                return 'hot_humid'
            return 'normal'
    
    if weather_id >= 500 and weather_id < 600:
        return 'rainy'
    
    if weather_id >= 200 and weather_id < 300:
        return 'rainy'
    
    if weather_id >= 700 and weather_id < 800:
        return 'polluted'
    
    if temp > 30:
        return 'hot_dry' if humidity < 40 else 'hot_humid'
    elif temp < 10:
        return 'cold_dry' if humidity < 50 else 'cold_humid'
    
    return 'normal'


def _estimate_uv(weather_id: int, description: str) -> int:
    """Estimate UV index from weather conditions."""
    if weather_id == 800:
        return 8  # Clear sky
    elif weather_id in [801, 802]:
        return 5  # Partly cloudy
    elif weather_id in [803, 804]:
        return 2  # Cloudy
    elif weather_id >= 500 and weather_id < 600:
        return 1  # Rain
    return 3


def _default_weather(city: str = 'Mumbai') -> Dict[str, Any]:
    """Return reasonable default weather when API is unavailable."""
    return {
        'temperature': 28.0,
        'humidity': 65,
        'condition': 'normal',
        'description': 'Weather service unavailable - using defaults',
        'wind_speed': 0,
        'uv_index': 5,
        'city': city,
        'source': 'default',
    }


def get_routine_adaptation(weather_condition: str) -> Dict[str, Any]:
    """Get routine adjustments based on weather condition."""
    adaptations = {
        'hot_humid': {
            'focus': 'Oil control, lightweight hydration, SPF',
            'add': ['cleanser', 'sunscreen'],
            'remove': ['heavy_moisturizer'],
            'tips': ['Use gel-based moisturizers', 'Apply water-resistant SPF 50+', 'Consider a mattifying toner'],
        },
        'hot_dry': {
            'focus': 'Hydration, barrier protection, SPF',
            'add': ['moisturizer', 'sunscreen'],
            'remove': [],
            'tips': ['Layer hydrating toners', 'Use ceramide-rich moisturizers', 'Reapply SPF every 2 hours'],
        },
        'cold_dry': {
            'focus': 'Barrier repair, rich hydration',
            'add': ['moisturizer'],
            'remove': ['exfoliator'],
            'tips': ['Switch to cream-based cleansers', 'Use overnight sleeping masks', 'Reduce exfoliation to 1x/week'],
        },
        'cold_humid': {
            'focus': 'Barrier protection, light moisture',
            'add': ['moisturizer'],
            'remove': [],
            'tips': ['Use barrier repair creams', 'Avoid over-cleansing', 'Focus on gentle hydration'],
        },
        'polluted': {
            'focus': 'Antioxidant protection, deep cleansing',
            'add': ['cleanser', 'serum'],
            'remove': [],
            'tips': ['Double cleanse in evening', 'Use vitamin C serum in AM', 'Apply antioxidant-rich moisturizer'],
        },
        'sunny': {
            'focus': 'UV protection, antioxidant defense',
            'add': ['sunscreen', 'serum'],
            'remove': [],
            'tips': ['Apply SPF 50+ PA++++', 'Use vitamin C under sunscreen', 'Wear protective accessories'],
        },
        'rainy': {
            'focus': 'Lightweight routine, barrier support',
            'add': [],
            'remove': ['heavy_moisturizer'],
            'tips': ['Use lighter textures', 'Focus on barrier repair at night', 'Consider humidifier for indoors'],
        },
        'normal': {
            'focus': 'Maintain balanced routine',
            'add': [],
            'remove': [],
            'tips': ['Continue your regular routine', 'Maintain SPF habit', 'Listen to your skin daily'],
        },
    }
    
    return adaptations.get(weather_condition, adaptations['normal'])
