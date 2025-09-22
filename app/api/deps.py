from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.redis_client import get_redis_client
from app.services.url_service import URLService


def get_url_service(
    db: Session = Depends(get_db),
    redis_client = Depends(get_redis_client)
) -> URLService:
    return URLService(db, redis_client)