"""FastAPI dependencies for Identity context."""

from collections.abc import AsyncGenerator
from typing import Annotated
from uuid import UUID

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession

from src.config import settings
from src.identity.application.handlers import (
    CompleteProfileHandler,
    LoginHandler,
    LogoutHandler,
    RefreshTokenHandler,
    RegisterUserHandler,
    RequestPasswordResetHandler,
    ResendVerificationHandler,
    ResetPasswordHandler,
    VerifyEmailHandler,
)
from src.identity.application.queries import GetCurrentUserHandler
from src.identity.domain.entities import User
from src.identity.infrastructure.persistence import (
    RedisRefreshTokenRepository,
    SqlAlchemyResetTokenRepository,
    SqlAlchemyUserRepository,
    SqlAlchemyVerificationTokenRepository,
)
from src.identity.infrastructure.services import (
    Argon2PasswordHasher,
    InitialsAvatarGenerator,
    JWTService,
)
from src.shared.infrastructure import Database

# ============================================================================
# Database & Redis Dependencies
# ============================================================================

_database: Database | None = None
_redis: Redis | None = None  # type: ignore[type-arg]


def get_database() -> Database:
    """Get database instance (singleton)."""
    global _database
    if _database is None:
        _database = Database(url=settings.database_url, echo=settings.app_debug)
    return _database


async def get_redis() -> Redis:  # type: ignore[type-arg]
    """Get Redis instance (singleton)."""
    global _redis
    if _redis is None:
        _redis = Redis.from_url(settings.redis_url)
    return _redis


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    """Get database session."""
    database = get_database()
    async with database.session() as session:
        yield session


# Type aliases for dependency injection
SessionDep = Annotated[AsyncSession, Depends(get_session)]
RedisDep = Annotated["Redis[bytes]", Depends(get_redis)]


# ============================================================================
# Service Dependencies
# ============================================================================


def get_password_hasher() -> Argon2PasswordHasher:
    """Get password hasher instance."""
    return Argon2PasswordHasher()


def get_token_generator() -> JWTService:
    """Get JWT service instance."""
    return JWTService(
        secret_key=settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
        access_token_expire_minutes=settings.jwt_access_token_expire_minutes,
        refresh_token_expire_days=settings.jwt_refresh_token_expire_days,
        refresh_token_remember_me_days=settings.jwt_refresh_token_remember_me_days,
    )


def get_avatar_generator() -> InitialsAvatarGenerator:
    """Get avatar generator instance."""
    return InitialsAvatarGenerator()


PasswordHasherDep = Annotated[Argon2PasswordHasher, Depends(get_password_hasher)]
TokenGeneratorDep = Annotated[JWTService, Depends(get_token_generator)]
AvatarGeneratorDep = Annotated[InitialsAvatarGenerator, Depends(get_avatar_generator)]


# ============================================================================
# Repository Dependencies
# ============================================================================


def get_user_repository(session: SessionDep) -> SqlAlchemyUserRepository:
    """Get user repository."""
    return SqlAlchemyUserRepository(session)


def get_verification_token_repository(
    session: SessionDep,
) -> SqlAlchemyVerificationTokenRepository:
    """Get verification token repository."""
    return SqlAlchemyVerificationTokenRepository(session)


def get_reset_token_repository(session: SessionDep) -> SqlAlchemyResetTokenRepository:
    """Get reset token repository."""
    return SqlAlchemyResetTokenRepository(session)


def get_refresh_token_repository(redis: RedisDep) -> RedisRefreshTokenRepository:
    """Get refresh token repository."""
    return RedisRefreshTokenRepository(redis)


UserRepositoryDep = Annotated[SqlAlchemyUserRepository, Depends(get_user_repository)]
VerificationTokenRepositoryDep = Annotated[
    SqlAlchemyVerificationTokenRepository, Depends(get_verification_token_repository)
]
ResetTokenRepositoryDep = Annotated[
    SqlAlchemyResetTokenRepository, Depends(get_reset_token_repository)
]
RefreshTokenRepositoryDep = Annotated[
    RedisRefreshTokenRepository, Depends(get_refresh_token_repository)
]


# ============================================================================
# Handler Dependencies
# ============================================================================


def get_register_handler(
    user_repo: UserRepositoryDep,
    verification_repo: VerificationTokenRepositoryDep,
    password_hasher: PasswordHasherDep,
    token_generator: TokenGeneratorDep,
) -> RegisterUserHandler:
    """Get register user handler."""
    return RegisterUserHandler(
        user_repository=user_repo,
        verification_token_repository=verification_repo,
        password_hasher=password_hasher,
        token_generator=token_generator,
    )


def get_verify_email_handler(
    user_repo: UserRepositoryDep,
    verification_repo: VerificationTokenRepositoryDep,
    token_generator: TokenGeneratorDep,
) -> VerifyEmailHandler:
    """Get verify email handler."""
    return VerifyEmailHandler(
        user_repository=user_repo,
        verification_token_repository=verification_repo,
        token_generator=token_generator,
    )


def get_resend_verification_handler(
    user_repo: UserRepositoryDep,
    verification_repo: VerificationTokenRepositoryDep,
    token_generator: TokenGeneratorDep,
) -> ResendVerificationHandler:
    """Get resend verification handler."""
    return ResendVerificationHandler(
        user_repository=user_repo,
        verification_token_repository=verification_repo,
        token_generator=token_generator,
    )


def get_login_handler(
    user_repo: UserRepositoryDep,
    password_hasher: PasswordHasherDep,
    token_generator: TokenGeneratorDep,
) -> LoginHandler:
    """Get login handler."""
    return LoginHandler(
        user_repository=user_repo,
        password_hasher=password_hasher,
        token_generator=token_generator,
    )


def get_refresh_token_handler(
    user_repo: UserRepositoryDep,
    refresh_repo: RefreshTokenRepositoryDep,
    token_generator: TokenGeneratorDep,
) -> RefreshTokenHandler:
    """Get refresh token handler."""
    return RefreshTokenHandler(
        user_repository=user_repo,
        refresh_token_repository=refresh_repo,
        token_generator=token_generator,
    )


def get_logout_handler(
    refresh_repo: RefreshTokenRepositoryDep,
    token_generator: TokenGeneratorDep,
) -> LogoutHandler:
    """Get logout handler."""
    return LogoutHandler(
        refresh_token_repository=refresh_repo,
        token_generator=token_generator,
    )


def get_request_password_reset_handler(
    user_repo: UserRepositoryDep,
    reset_repo: ResetTokenRepositoryDep,
    token_generator: TokenGeneratorDep,
) -> RequestPasswordResetHandler:
    """Get request password reset handler."""
    return RequestPasswordResetHandler(
        user_repository=user_repo,
        reset_token_repository=reset_repo,
        token_generator=token_generator,
    )


def get_reset_password_handler(
    user_repo: UserRepositoryDep,
    reset_repo: ResetTokenRepositoryDep,
    refresh_repo: RefreshTokenRepositoryDep,
    password_hasher: PasswordHasherDep,
) -> ResetPasswordHandler:
    """Get reset password handler."""
    return ResetPasswordHandler(
        user_repository=user_repo,
        reset_token_repository=reset_repo,
        refresh_token_repository=refresh_repo,
        password_hasher=password_hasher,
    )


def get_complete_profile_handler(
    user_repo: UserRepositoryDep,
    avatar_generator: AvatarGeneratorDep,
) -> CompleteProfileHandler:
    """Get complete profile handler."""
    return CompleteProfileHandler(
        user_repository=user_repo,
        avatar_generator=avatar_generator,
    )


def get_current_user_handler(user_repo: UserRepositoryDep) -> GetCurrentUserHandler:
    """Get current user handler."""
    return GetCurrentUserHandler(user_repository=user_repo)


# ============================================================================
# Authentication Dependencies
# ============================================================================

security = HTTPBearer(auto_error=False)


async def get_current_user_id(
    _request: Request,
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)] = None,
) -> UUID:
    """
    Get current user ID from JWT token.

    Raises HTTPException 401 if not authenticated.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token_generator = get_token_generator()
    user_id = token_generator.validate_access_token(credentials.credentials)

    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id.value


async def get_current_user(
    user_id: Annotated[UUID, Depends(get_current_user_id)],
    handler: Annotated[GetCurrentUserHandler, Depends(get_current_user_handler)],
) -> User:
    """
    Get current authenticated user.

    Raises HTTPException 401 if not authenticated.
    Raises HTTPException 404 if user not found.
    """
    from src.identity.application.queries import GetCurrentUserQuery
    from src.identity.domain.exceptions import UserNotFoundError

    try:
        return await handler.handle(GetCurrentUserQuery(user_id=user_id))
    except UserNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        ) from e


CurrentUserIdDep = Annotated[UUID, Depends(get_current_user_id)]
CurrentUserDep = Annotated[User, Depends(get_current_user)]
