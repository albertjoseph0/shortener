from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.db.database import Base


class URL(Base):
    __tablename__ = "urls"
    
    id = Column(Integer, primary_key=True, index=True)
    original_url = Column(Text, nullable=False)
    short_code = Column(String(50), unique=True, index=True, nullable=False)
    custom_alias = Column(String(50), unique=True, index=True, nullable=True)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    
    # Analytics relationship
    clicks = relationship("URLClick", back_populates="url", cascade="all, delete-orphan")
    
    # Indexes for performance
    __table_args__ = (
        Index('idx_urls_short_code', 'short_code'),
        Index('idx_urls_custom_alias', 'custom_alias'),
        Index('idx_urls_expires_at', 'expires_at'),
        Index('idx_urls_created_at', 'created_at'),
    )


class URLClick(Base):
    __tablename__ = "url_clicks"
    
    id = Column(Integer, primary_key=True, index=True)
    url_id = Column(Integer, nullable=False, index=True)
    ip_address = Column(String(45), nullable=True)  # IPv6 support
    user_agent = Column(Text, nullable=True)
    referer = Column(Text, nullable=True)
    country = Column(String(2), nullable=True)  # ISO country code
    city = Column(String(100), nullable=True)
    clicked_at = Column(DateTime, default=func.now(), nullable=False)
    
    # Relationship
    url = relationship("URL", back_populates="clicks")
    
    # Indexes for analytics queries
    __table_args__ = (
        Index('idx_clicks_url_id_clicked_at', 'url_id', 'clicked_at'),
        Index('idx_clicks_clicked_at', 'clicked_at'),
    )


class Counter(Base):
    __tablename__ = "counters"
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    value = Column(Integer, default=0, nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)