"""Rate limiter service."""

from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address

from src.config import settings

# Create rate limiter instance
# Uses Redis if REDIS_URL is set, otherwise in-memory
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["100/minute"],
    enabled=settings.rate_limit_enabled,
    storage_uri=settings.redis_url if settings.rate_limit_enabled else None,
)


def get_email_key(request: Request) -> str:
    """
    Get rate limit key based on email from request body.

    Used for per-email rate limiting on login, forgot password, etc.
    """
    # This is a placeholder - actual implementation depends on request parsing
    # In the actual endpoint, we'll parse the email from the request body
    return get_remote_address(request)


# Rate limit decorators for auth endpoints
# These are applied in the FastAPI routes

# Registration: 5 requests per 15 minutes per IP
REGISTER_LIMIT = "5/15 minutes"

# Login: 5 requests per 15 minutes per email
LOGIN_LIMIT = "5/15 minutes"

# Password reset request: 3 requests per 15 minutes per email
PASSWORD_RESET_LIMIT = "3/15 minutes"

# Verification resend: 3 requests per 15 minutes per email
RESEND_VERIFICATION_LIMIT = "3/15 minutes"

# Profile update: 10 requests per hour per IP
PROFILE_UPDATE_LIMIT = "10/hour"
