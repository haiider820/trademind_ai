from fastapi import APIRouter

from app.api.v1.endpoints.ai import router as ai_router
from app.api.v1.endpoints.devices import router as devices_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.market import router as market_router
from app.api.v1.endpoints.news import router as news_router
from app.api.v1.endpoints.scanner import router as scanner_router
from app.api.v1.endpoints.signals import router as signals_router

api_router = APIRouter()
api_router.include_router(health_router, tags=["health"])
api_router.include_router(market_router, prefix="/market", tags=["market"])
api_router.include_router(news_router, prefix="/news", tags=["news"])
api_router.include_router(signals_router, prefix="/signals", tags=["signals"])
api_router.include_router(ai_router, prefix="/ai", tags=["ai"])
api_router.include_router(scanner_router, prefix="/scanner", tags=["scanner"])
api_router.include_router(devices_router, prefix="/devices", tags=["devices"])
