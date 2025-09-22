import string
from typing import Optional


class URLEncoder:
    """Base62 URL encoder for generating short URLs"""
    
    # Base62 alphabet: 0-9, a-z, A-Z
    ALPHABET = string.digits + string.ascii_lowercase + string.ascii_uppercase
    BASE = len(ALPHABET)
    
    @classmethod
    def encode(cls, num: int) -> str:
        """Encode a number to base62 string"""
        if num == 0:
            return cls.ALPHABET[0]
        
        encoded = ""
        while num > 0:
            encoded = cls.ALPHABET[num % cls.BASE] + encoded
            num //= cls.BASE
        
        return encoded
    
    @classmethod
    def decode(cls, encoded: str) -> int:
        """Decode a base62 string to number"""
        num = 0
        for char in encoded:
            if char not in cls.ALPHABET:
                raise ValueError(f"Invalid character '{char}' in encoded string")
            num = num * cls.BASE + cls.ALPHABET.index(char)
        return num
    
    @classmethod
    def is_valid_custom_alias(cls, alias: str) -> bool:
        """Check if custom alias contains only valid characters"""
        return all(char in cls.ALPHABET for char in alias)


def generate_short_code(counter: int) -> str:
    """Generate a short code from a counter value"""
    return URLEncoder.encode(counter)


def validate_url(url: str) -> bool:
    """Basic URL validation"""
    import re
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain...
        r'localhost|'  # localhost...
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE)
    return bool(url_pattern.match(url))