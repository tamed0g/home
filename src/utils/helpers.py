import os
import json
import hashlib
import uuid
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

def generate_device_id(name: str, device_type: str) -> str:
    """Generate a unique device ID based on name and type"""
    unique_string = f"{name}_{device_type}_{datetime.now().isoformat()}"
    return hashlib.md5(unique_string.encode()).hexdigest()[:16]

def generate_uuid() -> str:
    """Generate a UUID string"""
    return str(uuid.uuid4())

def validate_ip_address(ip: str) -> bool:
    """Validate IP address format"""
    try:
        parts = ip.split('.')
        if len(parts) != 4:
            return False
        
        for part in parts:
            if not 0 <= int(part) <= 255:
                return False
        
        return True
    except (ValueError, AttributeError):
        return False

def validate_port(port: Union[str, int]) -> bool:
    """Validate port number"""
    try:
        port_num = int(port)
        return 1 <= port_num <= 65535
    except (ValueError, TypeError):
        return False

def safe_json_load(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Safely load JSON file, return empty dict if file doesn't exist or is invalid"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def safe_json_save(data: Dict[str, Any], file_path: Union[str, Path]) -> bool:
    """Safely save data to JSON file"""
    try:
        file_path = Path(file_path)
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception:
        return False

def parse_voice_command(text: str) -> Dict[str, Any]:
    """Parse voice command and extract action and parameters"""
    text = text.lower().strip()
    
    # Basic command patterns
    patterns = {
        'greeting': ['привет', 'hello', 'здравствуй'],
        'time': ['время', 'time', 'который час'],
        'weather': ['погода', 'weather'],
        'light_on': ['включи свет', 'включить свет', 'turn on light'],
        'light_off': ['выключи свет', 'выключить свет', 'turn off light'],
        'music_on': ['включи музыку', 'включить музыку', 'play music'],
        'music_off': ['выключи музыку', 'выключить музыку', 'stop music'],
        'volume_up': ['громче', 'volume up', 'увеличь громкость'],
        'volume_down': ['тише', 'volume down', 'уменьши громкость'],
    }
    
    # Find matching pattern
    for action, keywords in patterns.items():
        for keyword in keywords:
            if keyword in text:
                return {
                    'action': action,
                    'original_text': text,
                    'confidence': 1.0,
                    'parameters': {}
                }
    
    # No pattern matched
    return {
        'action': 'unknown',
        'original_text': text,
        'confidence': 0.0,
        'parameters': {}
    }

def clamp(value: Union[int, float], min_value: Union[int, float], max_value: Union[int, float]) -> Union[int, float]:
    """Clamp value between min and max"""
    return max(min_value, min(value, max_value))

def format_duration(seconds: float) -> str:
    """Format duration in seconds to human-readable string"""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"

def format_timestamp(timestamp: Union[datetime, str, float, int]) -> str:
    """Format timestamp to standard string representation"""
    try:
        if isinstance(timestamp, str):
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
        elif isinstance(timestamp, (int, float)):
            dt = datetime.fromtimestamp(timestamp)
        elif isinstance(timestamp, datetime):
            dt = timestamp
        else:
            return str(timestamp)
        
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return str(timestamp)

def ensure_directory(path: Union[str, Path]) -> Path:
    """Ensure directory exists, create if it doesn't"""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)
    return path

def get_file_age(file_path: Union[str, Path]) -> Optional[timedelta]:
    """Get age of a file"""
    try:
        file_path = Path(file_path)
        if not file_path.exists():
            return None
        
        modification_time = datetime.fromtimestamp(file_path.stat().st_mtime)
        return datetime.now() - modification_time
    except Exception:
        return None

class AsyncCache:
    """Simple cache implementation for testing"""
    
    def __init__(self, ttl_seconds: int = 300):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl_seconds
    
    def _is_expired(self, entry: Dict[str, Any]) -> bool:
        """Check if cache entry is expired"""
        age = datetime.now() - entry['timestamp']
        return age.total_seconds() > self.ttl
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if key in self.cache:
            entry = self.cache[key]
            if not self._is_expired(entry):
                return entry['value']
            else:
                del self.cache[key]
        
        return None
    
    def set(self, key: str, value: Any):
        """Set value in cache"""
        self.cache[key] = {
            'value': value,
            'timestamp': datetime.now()
        }
    
    def clear(self):
        """Clear all cache entries"""
        self.cache.clear()