import pytest
from app.utils.url_encoder import URLEncoder, generate_short_code, validate_url


class TestURLEncoder:
    def test_encode_decode(self):
        """Test encoding and decoding numbers"""
        test_cases = [0, 1, 10, 100, 1000, 10000, 100000, 1000000]
        
        for num in test_cases:
            encoded = URLEncoder.encode(num)
            decoded = URLEncoder.decode(encoded)
            assert decoded == num, f"Failed for {num}: {encoded} -> {decoded}"
    
    def test_encode_edge_cases(self):
        """Test edge cases for encoding"""
        assert URLEncoder.encode(0) == "0"
        assert URLEncoder.encode(1) == "1"
        assert URLEncoder.encode(61) == "Z"  # Last character in base62
        assert URLEncoder.encode(62) == "10"  # First two-character code
    
    def test_decode_invalid_characters(self):
        """Test decoding with invalid characters"""
        with pytest.raises(ValueError):
            URLEncoder.decode("invalid@")
        
        with pytest.raises(ValueError):
            URLEncoder.decode("test#")
    
    def test_is_valid_custom_alias(self):
        """Test custom alias validation"""
        assert URLEncoder.is_valid_custom_alias("abc123") == True
        assert URLEncoder.is_valid_custom_alias("test-alias") == True
        assert URLEncoder.is_valid_custom_alias("test_alias") == True
        assert URLEncoder.is_valid_custom_alias("Test123") == True
        
        assert URLEncoder.is_valid_custom_alias("test@alias") == False
        assert URLEncoder.is_valid_custom_alias("test.alias") == False
        assert URLEncoder.is_valid_custom_alias("test alias") == False
        assert URLEncoder.is_valid_custom_alias("") == True  # Empty is valid


class TestGenerateShortCode:
    def test_generate_short_code(self):
        """Test short code generation"""
        assert generate_short_code(0) == "0"
        assert generate_short_code(1) == "1"
        assert generate_short_code(61) == "Z"
        assert generate_short_code(62) == "10"


class TestValidateURL:
    def test_valid_urls(self):
        """Test valid URL validation"""
        valid_urls = [
            "https://example.com",
            "http://example.com",
            "https://www.example.com/path",
            "https://subdomain.example.com/path?query=value",
            "https://example.com:8080/path",
        ]
        
        for url in valid_urls:
            assert validate_url(url) == True, f"URL should be valid: {url}"
    
    def test_invalid_urls(self):
        """Test invalid URL validation"""
        invalid_urls = [
            "not-a-url",
            "ftp://example.com",
            "file:///path/to/file",
            "javascript:alert('xss')",
            "data:text/html,<script>alert('xss')</script>",
            "example.com",  # Missing protocol
            "https://",  # Missing domain
        ]
        
        for url in invalid_urls:
            assert validate_url(url) == False, f"URL should be invalid: {url}"