from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import Optional, List
from datetime import datetime, timedelta
from app.models.url import URL, URLClick, Counter
from app.schemas.url import URLCreate, URLUpdate, URLClickCreate
from app.utils.url_encoder import generate_short_code, URLEncoder
from app.core.config import settings
from app.db.redis_client import RedisClient


class URLService:
    def __init__(self, db: Session, redis_client: RedisClient):
        self.db = db
        self.redis = redis_client
    
    def create_url(self, url_data: URLCreate) -> URL:
        """Create a new shortened URL"""
        
        # Check if custom alias is provided and available
        if url_data.custom_alias:
            existing_url = self.db.query(URL).filter(
                URL.custom_alias == url_data.custom_alias
            ).first()
            if existing_url:
                raise ValueError("Custom alias already exists")
        
        # Generate short code
        if url_data.custom_alias:
            short_code = url_data.custom_alias
        else:
            # Get next counter value
            counter = self.db.query(Counter).filter(Counter.name == "url_counter").first()
            if not counter:
                counter = Counter(name="url_counter", value=0)
                self.db.add(counter)
            
            counter.value += 1
            short_code = generate_short_code(counter.value)
        
        # Create URL record
        url = URL(
            original_url=url_data.original_url,
            short_code=short_code,
            custom_alias=url_data.custom_alias,
            title=url_data.title,
            description=url_data.description,
            expires_at=url_data.expires_at
        )
        
        self.db.add(url)
        self.db.commit()
        self.db.refresh(url)
        
        # Cache the URL in Redis
        self._cache_url(url)
        
        return url
    
    def get_url_by_short_code(self, short_code: str) -> Optional[URL]:
        """Get URL by short code with Redis caching"""
        
        # Try Redis cache first
        cache_key = f"url:{short_code}"
        cached_url = self.redis.get(cache_key)
        
        if cached_url:
            # Parse cached data and return URL object
            import json
            url_data = json.loads(cached_url)
            url = URL(**url_data)
            return url
        
        # Fallback to database
        url = self.db.query(URL).filter(URL.short_code == short_code).first()
        
        if url:
            # Cache for future requests
            self._cache_url(url)
        
        return url
    
    def get_url_by_id(self, url_id: int) -> Optional[URL]:
        """Get URL by ID"""
        return self.db.query(URL).filter(URL.id == url_id).first()
    
    def update_url(self, url_id: int, url_data: URLUpdate) -> Optional[URL]:
        """Update URL"""
        url = self.get_url_by_id(url_id)
        if not url:
            return None
        
        for field, value in url_data.dict(exclude_unset=True).items():
            setattr(url, field, value)
        
        self.db.commit()
        self.db.refresh(url)
        
        # Update cache
        self._cache_url(url)
        
        return url
    
    def delete_url(self, url_id: int) -> bool:
        """Delete URL"""
        url = self.get_url_by_id(url_id)
        if not url:
            return False
        
        # Remove from cache
        cache_key = f"url:{url.short_code}"
        self.redis.delete(cache_key)
        
        self.db.delete(url)
        self.db.commit()
        return True
    
    def record_click(self, url_id: int, click_data: URLClickCreate) -> URLClick:
        """Record a click on a URL"""
        click = URLClick(
            url_id=url_id,
            ip_address=click_data.ip_address,
            user_agent=click_data.user_agent,
            referer=click_data.referer,
            country=click_data.country,
            city=click_data.city
        )
        
        self.db.add(click)
        self.db.commit()
        self.db.refresh(click)
        
        # Update click counter in Redis
        click_key = f"clicks:{url_id}"
        self.redis.increment(click_key)
        
        return click
    
    def get_url_analytics(self, url_id: int) -> dict:
        """Get analytics for a URL"""
        url = self.get_url_by_id(url_id)
        if not url:
            return {}
        
        # Get total clicks
        total_clicks = self.db.query(URLClick).filter(URLClick.url_id == url_id).count()
        
        # Get unique clicks (by IP)
        unique_clicks = self.db.query(URLClick.ip_address).filter(
            URLClick.url_id == url_id
        ).distinct().count()
        
        # Get clicks by day (last 30 days)
        thirty_days_ago = datetime.utcnow() - timedelta(days=30)
        clicks_by_day = self.db.query(
            func.date(URLClick.clicked_at).label('date'),
            func.count(URLClick.id).label('count')
        ).filter(
            URLClick.url_id == url_id,
            URLClick.clicked_at >= thirty_days_ago
        ).group_by(
            func.date(URLClick.clicked_at)
        ).all()
        
        # Get clicks by country
        clicks_by_country = self.db.query(
            URLClick.country,
            func.count(URLClick.id).label('count')
        ).filter(
            URLClick.url_id == url_id,
            URLClick.country.isnot(None)
        ).group_by(URLClick.country).all()
        
        # Get recent clicks
        recent_clicks = self.db.query(URLClick).filter(
            URLClick.url_id == url_id
        ).order_by(URLClick.clicked_at.desc()).limit(10).all()
        
        return {
            "total_clicks": total_clicks,
            "unique_clicks": unique_clicks,
            "clicks_by_day": [{"date": str(day.date), "count": day.count} for day in clicks_by_day],
            "clicks_by_country": [{"country": country.country, "count": country.count} for country in clicks_by_country],
            "recent_clicks": recent_clicks
        }
    
    def _cache_url(self, url: URL):
        """Cache URL in Redis"""
        cache_key = f"url:{url.short_code}"
        url_data = {
            "id": url.id,
            "original_url": url.original_url,
            "short_code": url.short_code,
            "custom_alias": url.custom_alias,
            "title": url.title,
            "description": url.description,
            "is_active": url.is_active,
            "expires_at": url.expires_at.isoformat() if url.expires_at else None,
            "created_at": url.created_at.isoformat(),
            "updated_at": url.updated_at.isoformat()
        }
        
        import json
        self.redis.set(cache_key, json.dumps(url_data), ex=3600)  # Cache for 1 hour
    
    def is_url_expired(self, url: URL) -> bool:
        """Check if URL has expired"""
        if not url.expires_at:
            return False
        return datetime.utcnow() > url.expires_at