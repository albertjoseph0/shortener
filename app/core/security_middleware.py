from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
import re
from typing import List


class SecurityMiddleware:
    """Security middleware for URL shortener"""
    
    # List of potentially malicious patterns
    MALICIOUS_PATTERNS = [
        r'javascript:',
        r'data:',
        r'vbscript:',
        r'onload=',
        r'onerror=',
        r'<script',
        r'</script>',
        r'<iframe',
        r'<object',
        r'<embed',
        r'<form',
        r'<input',
        r'<meta',
        r'<link',
        r'<style',
        r'<img',
        r'<svg',
        r'<video',
        r'<audio',
        r'<source',
        r'<track',
        r'<canvas',
        r'<map',
        r'<area',
        r'<base',
        r'<command',
        r'<details',
        r'<dialog',
        r'<fieldset',
        r'<keygen',
        r'<legend',
        r'<menu',
        r'<menuitem',
        r'<optgroup',
        r'<option',
        r'<output',
        r'<progress',
        r'<select',
        r'<textarea',
        r'<title',
        r'<wbr',
    ]
    
    # Suspicious domains
    SUSPICIOUS_DOMAINS = [
        'localhost',
        '127.0.0.1',
        '0.0.0.0',
        '::1',
        'file://',
        'ftp://',
    ]
    
    @classmethod
    def validate_url(cls, url: str) -> bool:
        """Validate URL for security threats"""
        url_lower = url.lower()
        
        # Check for malicious patterns
        for pattern in cls.MALICIOUS_PATTERNS:
            if re.search(pattern, url_lower, re.IGNORECASE):
                return False
        
        # Check for suspicious domains
        for domain in cls.SUSPICIOUS_DOMAINS:
            if domain in url_lower:
                return False
        
        # Check for valid URL format
        if not url.startswith(('http://', 'https://')):
            return False
        
        return True
    
    @classmethod
    def sanitize_input(cls, input_str: str) -> str:
        """Sanitize user input"""
        if not input_str:
            return input_str
        
        # Remove potentially dangerous characters
        sanitized = re.sub(r'[<>"\']', '', input_str)
        
        # Limit length
        return sanitized[:1000]
    
    @classmethod
    def check_custom_alias(cls, alias: str) -> bool:
        """Check if custom alias is safe"""
        if not alias:
            return True
        
        # Only allow alphanumeric, hyphens, and underscores
        if not re.match(r'^[a-zA-Z0-9_-]+$', alias):
            return False
        
        # Check for reserved words
        reserved_words = [
            'admin', 'api', 'www', 'mail', 'ftp', 'blog', 'shop',
            'app', 'dev', 'test', 'staging', 'prod', 'production',
            'secure', 'login', 'logout', 'register', 'signup',
            'dashboard', 'analytics', 'stats', 'help', 'support',
            'about', 'contact', 'privacy', 'terms', 'legal'
        ]
        
        if alias.lower() in reserved_words:
            return False
        
        return True


def security_middleware(request: Request, call_next):
    """Security middleware for all requests"""
    # Add security headers
    response = call_next(request)
    
    # Security headers
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Content-Security-Policy"] = "default-src 'self'"
    
    return response