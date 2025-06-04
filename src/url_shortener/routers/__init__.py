from fastapi import APIRouter

from src.url_shortener.routers.shortener_router import router as shortener_router
from src.url_shortener.routers.info_router import router as info_router

url_router = APIRouter()
url_router.include_router(shortener_router)
url_router.include_router(info_router)
