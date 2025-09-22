from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql://user:password@localhost:5432/urlshortener"
    redis_url: str = "redis://localhost:6379/0"
    
    # Security
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Application
    debug: bool = True
    host: str = "0.0.0.0"
    port: int = 8000
    base_url: str = "http://localhost:8000"
    
    # Rate Limiting
    rate_limit_per_minute: int = 100
    rate_limit_burst: int = 200
    
    # URL Shortener
    default_domain: str = "short.ly"
    max_custom_alias_length: int = 50
    max_url_length: int = 2048
    
    class Config:
        env_file = ".env"


settings = Settings()