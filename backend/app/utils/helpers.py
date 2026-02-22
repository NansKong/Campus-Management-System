import random
import string
from datetime import datetime

def generate_unique_code(length: int = 6) -> str:
    """Generate a random alphanumeric code"""
    characters = string.ascii_uppercase + string.digits
    return ''.join(random.choices(characters, k=length))

def is_code_expired(expiry_time: datetime) -> bool:
    """Check if a code has expired"""
    return datetime.utcnow() > expiry_time