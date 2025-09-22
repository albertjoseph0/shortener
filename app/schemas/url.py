from pydantic import BaseModel, HttpUrl, validator
from typing import Optional
from datetime import datetime


class URLBase(BaseModel):
    original_url: str
    custom_alias: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    expires_at: Optional[datetime] = None
    
    @validator('original_url')
    def validate_url(cls, v):
        from app.utils.url_encoder import validate_url
        if not validate_url(v):
            raise ValueError('Invalid URL format')
        return v
    
    @validator('custom_alias')
    def validate_custom_alias(cls, v):
        if v is not None:
            from app.utils.url_encoder import URLEncoder
            if not URLEncoder.is_valid_custom_alias(v):
                raise ValueError('Custom alias can only contain alphanumeric characters')
            if len(v) < 3:
                raise ValueError('Custom alias must be at least 3 characters long')
        return v


class URLCreate(URLBase):
    pass


class URLResponse(URLBase):
    id: int
    short_code: str
    short_url: str
    is_active: bool
    created_at: datetime
    updated_at: datetime
    click_count: int = 0
    
    class Config:
        from_attributes = True


class URLUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None
    expires_at: Optional[datetime] = None


class URLClickCreate(BaseModel):
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    referer: Optional[str] = None
    country: Optional[str] = None
    city: Optional[str] = None


class URLClickResponse(BaseModel):
    id: int
    url_id: int
    ip_address: Optional[str]
    user_agent: Optional[str]
    referer: Optional[str]
    country: Optional[str]
    city: Optional[str]
    clicked_at: datetime
    
    class Config:
        from_attributes = True


class URLAnalytics(BaseModel):
    total_clicks: int
    unique_clicks: int
    clicks_by_day: list
    clicks_by_country: list
    clicks_by_referer: list
    recent_clicks: list[URLClickResponse]