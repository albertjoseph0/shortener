import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timedelta
from app.services.url_service import URLService
from app.schemas.url import URLCreate, URLUpdate, URLClickCreate
from app.models.url import URL, URLClick, Counter


class TestURLService:
    @pytest.fixture
    def mock_db(self):
        return Mock()
    
    @pytest.fixture
    def mock_redis(self):
        return Mock()
    
    @pytest.fixture
    def url_service(self, mock_db, mock_redis):
        return URLService(mock_db, mock_redis)
    
    def test_create_url_with_custom_alias(self, url_service, mock_db):
        """Test creating URL with custom alias"""
        url_data = URLCreate(
            original_url="https://example.com",
            custom_alias="test-alias"
        )
        
        # Mock database queries
        mock_db.query.return_value.filter.return_value.first.return_value = None  # No existing alias
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        
        # Mock the URL object
        mock_url = Mock()
        mock_url.id = 1
        mock_url.short_code = "test-alias"
        mock_url.original_url = "https://example.com"
        mock_url.custom_alias = "test-alias"
        mock_url.title = None
        mock_url.description = None
        mock_url.is_active = True
        mock_url.expires_at = None
        mock_url.created_at = datetime.utcnow()
        mock_url.updated_at = datetime.utcnow()
        
        with patch('app.services.url_service.URL', return_value=mock_url):
            result = url_service.create_url(url_data)
        
        assert result.short_code == "test-alias"
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
    
    def test_create_url_without_custom_alias(self, url_service, mock_db):
        """Test creating URL without custom alias"""
        url_data = URLCreate(original_url="https://example.com")
        
        # Mock counter
        mock_counter = Mock()
        mock_counter.value = 0
        mock_db.query.return_value.filter.return_value.first.return_value = mock_counter
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        
        # Mock the URL object
        mock_url = Mock()
        mock_url.id = 1
        mock_url.short_code = "1"
        mock_url.original_url = "https://example.com"
        mock_url.custom_alias = None
        
        with patch('app.services.url_service.URL', return_value=mock_url):
            result = url_service.create_url(url_data)
        
        assert result.short_code == "1"
        assert mock_counter.value == 1  # Counter should be incremented
    
    def test_get_url_by_short_code_with_cache(self, url_service, mock_redis):
        """Test getting URL from cache"""
        short_code = "test-code"
        cached_data = '{"id": 1, "original_url": "https://example.com", "short_code": "test-code"}'
        
        mock_redis.get.return_value = cached_data
        
        with patch('app.services.url_service.URL') as mock_url_class:
            mock_url = Mock()
            mock_url_class.return_value = mock_url
            
            result = url_service.get_url_by_short_code(short_code)
        
        assert result == mock_url
        mock_redis.get.assert_called_once_with(f"url:{short_code}")
    
    def test_get_url_by_short_code_from_database(self, url_service, mock_db, mock_redis):
        """Test getting URL from database when not in cache"""
        short_code = "test-code"
        
        # Mock cache miss
        mock_redis.get.return_value = None
        
        # Mock database result
        mock_url = Mock()
        mock_url.id = 1
        mock_url.short_code = short_code
        mock_url.original_url = "https://example.com"
        
        mock_db.query.return_value.filter.return_value.first.return_value = mock_url
        
        result = url_service.get_url_by_short_code(short_code)
        
        assert result == mock_url
        mock_redis.get.assert_called_once_with(f"url:{short_code}")
        mock_db.query.assert_called_once()
    
    def test_record_click(self, url_service, mock_db, mock_redis):
        """Test recording a click"""
        url_id = 1
        click_data = URLClickCreate(
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0",
            referer="https://google.com"
        )
        
        mock_db.add = Mock()
        mock_db.commit = Mock()
        mock_db.refresh = Mock()
        mock_redis.increment = Mock()
        
        with patch('app.services.url_service.URLClick') as mock_click_class:
            mock_click = Mock()
            mock_click_class.return_value = mock_click
            
            result = url_service.record_click(url_id, click_data)
        
        assert result == mock_click
        mock_db.add.assert_called_once()
        mock_db.commit.assert_called_once()
        mock_redis.increment.assert_called_once_with(f"clicks:{url_id}")
    
    def test_is_url_expired(self, url_service):
        """Test URL expiration check"""
        # Not expired
        future_time = datetime.utcnow() + timedelta(days=1)
        mock_url_future = Mock()
        mock_url_future.expires_at = future_time
        assert url_service.is_url_expired(mock_url_future) == False
        
        # Expired
        past_time = datetime.utcnow() - timedelta(days=1)
        mock_url_past = Mock()
        mock_url_past.expires_at = past_time
        assert url_service.is_url_expired(mock_url_past) == True
        
        # No expiration
        mock_url_no_expiry = Mock()
        mock_url_no_expiry.expires_at = None
        assert url_service.is_url_expired(mock_url_no_expiry) == False