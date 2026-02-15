"""FastAPI application entry point."""

import logging
from collections.abc import AsyncGenerator, Callable
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

import structlog
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from src.classroom.interface.api import (
    courses_router,
    lessons_router,
    modules_router,
    progress_router,
)
from src.community.domain.events import (
    CommentAdded,
    CommentLiked,
    CommentUnliked,
    PostCreated,
    PostLiked,
    PostUnliked,
)
from src.community.interface.api import (
    categories_router,
    comments_router,
    members_router,
    post_comments_router,
    posts_router,
    search_router,
)
from src.config import settings
from src.gamification.application.event_handlers.community_event_handlers import (
    handle_comment_added,
    handle_comment_liked,
    handle_comment_unliked,
    handle_post_created,
    handle_post_liked,
    handle_post_unliked,
)
from src.gamification.interface.api.gamification_controller import (
    router as gamification_router,
)
from src.identity.domain.exceptions import RateLimitExceededError
from src.identity.infrastructure.services import limiter
from src.identity.interface.api import auth_router, user_router

# Configure structlog
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.StackInfoRenderer(),
        structlog.dev.set_exc_info,
        structlog.processors.TimeStamper(fmt="iso"),
        (
            structlog.dev.ConsoleRenderer()
            if settings.is_development
            else structlog.processors.JSONRenderer()
        ),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(
        logging.INFO if not settings.app_debug else logging.DEBUG
    ),
    context_class=dict,
    logger_factory=structlog.PrintLoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()


@asynccontextmanager
async def lifespan(_app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler."""
    logger.info("application_startup", env=settings.app_env)

    # Register gamification event handlers
    from src.shared.infrastructure.event_bus import event_bus

    event_bus.register_handler(PostCreated, handle_post_created)  # type: ignore[arg-type]
    event_bus.register_handler(PostLiked, handle_post_liked)  # type: ignore[arg-type]
    event_bus.register_handler(PostUnliked, handle_post_unliked)  # type: ignore[arg-type]
    event_bus.register_handler(CommentAdded, handle_comment_added)  # type: ignore[arg-type]
    event_bus.register_handler(CommentLiked, handle_comment_liked)  # type: ignore[arg-type]
    event_bus.register_handler(CommentUnliked, handle_comment_unliked)  # type: ignore[arg-type]

    yield
    logger.info("application_shutdown")


# Create FastAPI application
app = FastAPI(
    title="Koulu API",
    description="Community platform API",
    version="0.1.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.is_development else None,
    redoc_url="/redoc" if settings.is_development else None,
)

# Add rate limiter
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)  # type: ignore[arg-type]

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url] if settings.is_production else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Security headers middleware
@app.middleware("http")
async def add_security_headers(
    request: Request,
    call_next: Callable[[Request], Any],
) -> Any:
    """Add security headers to all responses."""
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    if settings.is_production:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


# Request logging middleware
@app.middleware("http")
async def log_requests(
    request: Request,
    call_next: Callable[[Request], Any],
) -> Any:
    """Log all requests."""
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        request_id=request.headers.get("X-Request-ID", ""),
        path=request.url.path,
        method=request.method,
    )

    logger.info("request_started")
    response = await call_next(request)
    logger.info("request_completed", status_code=response.status_code)

    return response


# Global exception handler
@app.exception_handler(RateLimitExceededError)
async def rate_limit_handler(_request: Request, exc: RateLimitExceededError) -> JSONResponse:
    """Handle rate limit exceeded errors."""
    return JSONResponse(
        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
        content={"code": exc.code, "message": exc.message},
        headers={"Retry-After": str(exc.retry_after)} if exc.retry_after else {},
    )


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}


# Mount routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")
app.include_router(categories_router, prefix="/api/v1")
app.include_router(members_router, prefix="/api/v1")
app.include_router(posts_router, prefix="/api/v1")
app.include_router(post_comments_router, prefix="/api/v1")
app.include_router(comments_router, prefix="/api/v1")
app.include_router(search_router, prefix="/api/v1")
app.include_router(courses_router, prefix="/api/v1")
app.include_router(modules_router, prefix="/api/v1")
app.include_router(lessons_router, prefix="/api/v1")
app.include_router(progress_router, prefix="/api/v1")
app.include_router(gamification_router, prefix="/api/v1")

# Serve React SPA in production (static/ directory exists from Docker build)
_static_dir = Path(__file__).resolve().parent.parent / "static"
if _static_dir.exists():
    app.mount("/assets", StaticFiles(directory=_static_dir / "assets"), name="static-assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str) -> FileResponse:
        """Serve SPA index.html for client-side routing."""
        file_path = _static_dir / full_path
        if file_path.exists() and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(_static_dir / "index.html")
