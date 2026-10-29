"""KrishiMitra FastAPI application."""

from __future__ import annotations

from fastapi import FastAPI

from krishimitra_api.api.router import api_router
from krishimitra_api.errors.handlers import register_exception_handlers
from krishimitra_api.middleware.logging import LoggingMiddleware
from krishimitra_api.middleware.rate_limit import RateLimitMiddleware
from krishimitra_api.middleware.request_id import RequestIDMiddleware
from krishimitra_api.middleware.security import SecurityHeadersMiddleware

app = FastAPI(
    title="KrishiMitra-AI API",
    description="AI-powered agricultural advisory platform",
    version="0.1.0",
)

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(RequestIDMiddleware)

register_exception_handlers(app)

app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
async def root_health() -> dict:
    return {"status": "ok"}
