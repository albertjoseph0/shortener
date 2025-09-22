from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session
from typing import List
from app.schemas.url import URLCreate, URLResponse, URLUpdate, URLClickCreate
from app.services.url_service import URLService
from app.api.deps import get_url_service
from app.core.config import settings

router = APIRouter()


@router.post("/", response_model=URLResponse)
async def create_short_url(
    url_data: URLCreate,
    url_service: URLService = Depends(get_url_service)
):
    """Create a new shortened URL"""
    try:
        url = url_service.create_url(url_data)
        
        # Build short URL
        short_url = f"{settings.base_url}/{url.short_code}"
        
        return URLResponse(
            id=url.id,
            original_url=url.original_url,
            short_code=url.short_code,
            short_url=short_url,
            custom_alias=url.custom_alias,
            title=url.title,
            description=url.description,
            is_active=url.is_active,
            expires_at=url.expires_at,
            created_at=url.created_at,
            updated_at=url.updated_at,
            click_count=0
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{short_code}")
async def redirect_to_original_url(
    short_code: str,
    request: Request,
    url_service: URLService = Depends(get_url_service)
):
    """Redirect to the original URL"""
    url = url_service.get_url_by_short_code(short_code)
    
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")
    
    if not url.is_active:
        raise HTTPException(status_code=410, detail="URL is no longer active")
    
    if url_service.is_url_expired(url):
        raise HTTPException(status_code=410, detail="URL has expired")
    
    # Record the click
    click_data = URLClickCreate(
        ip_address=request.client.host,
        user_agent=request.headers.get("user-agent"),
        referer=request.headers.get("referer")
    )
    url_service.record_click(url.id, click_data)
    
    # Redirect to original URL
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url=url.original_url, status_code=302)


@router.get("/{short_code}/info", response_model=URLResponse)
async def get_url_info(
    short_code: str,
    url_service: URLService = Depends(get_url_service)
):
    """Get information about a shortened URL"""
    url = url_service.get_url_by_short_code(short_code)
    
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")
    
    # Get click count
    click_count = url_service.redis.get(f"clicks:{url.id}")
    click_count = int(click_count) if click_count else 0
    
    short_url = f"{settings.base_url}/{url.short_code}"
    
    return URLResponse(
        id=url.id,
        original_url=url.original_url,
        short_code=url.short_code,
        short_url=short_url,
        custom_alias=url.custom_alias,
        title=url.title,
        description=url.description,
        is_active=url.is_active,
        expires_at=url.expires_at,
        created_at=url.created_at,
        updated_at=url.updated_at,
        click_count=click_count
    )


@router.put("/{url_id}", response_model=URLResponse)
async def update_url(
    url_id: int,
    url_data: URLUpdate,
    url_service: URLService = Depends(get_url_service)
):
    """Update a shortened URL"""
    url = url_service.update_url(url_id, url_data)
    
    if not url:
        raise HTTPException(status_code=404, detail="URL not found")
    
    short_url = f"{settings.base_url}/{url.short_code}"
    
    return URLResponse(
        id=url.id,
        original_url=url.original_url,
        short_code=url.short_code,
        short_url=short_url,
        custom_alias=url.custom_alias,
        title=url.title,
        description=url.description,
        is_active=url.is_active,
        expires_at=url.expires_at,
        created_at=url.created_at,
        updated_at=url.updated_at,
        click_count=0
    )


@router.delete("/{url_id}")
async def delete_url(
    url_id: int,
    url_service: URLService = Depends(get_url_service)
):
    """Delete a shortened URL"""
    success = url_service.delete_url(url_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="URL not found")
    
    return {"message": "URL deleted successfully"}


@router.get("/{url_id}/analytics")
async def get_url_analytics(
    url_id: int,
    url_service: URLService = Depends(get_url_service)
):
    """Get analytics for a shortened URL"""
    analytics = url_service.get_url_analytics(url_id)
    
    if not analytics:
        raise HTTPException(status_code=404, detail="URL not found")
    
    return analytics