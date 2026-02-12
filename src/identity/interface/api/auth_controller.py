"""Authentication API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status

from src.identity.application.commands import (
    LoginCommand,
    LogoutCommand,
    RefreshTokenCommand,
    RegisterUserCommand,
    RequestPasswordResetCommand,
    ResendVerificationCommand,
    ResetPasswordCommand,
    VerifyEmailCommand,
)
from src.identity.application.handlers import (
    LoginHandler,
    LogoutHandler,
    RefreshTokenHandler,
    RegisterUserHandler,
    RequestPasswordResetHandler,
    ResendVerificationHandler,
    ResetPasswordHandler,
    VerifyEmailHandler,
)
from src.identity.domain.exceptions import (
    IdentityDomainError,
    InvalidCredentialsError,
    InvalidTokenError,
    PasswordTooShortError,
    UserAlreadyVerifiedError,
    UserDisabledError,
    UserNotVerifiedError,
)
from src.identity.infrastructure.services import (
    LOGIN_LIMIT,
    PASSWORD_RESET_LIMIT,
    REGISTER_LIMIT,
    RESEND_VERIFICATION_LIMIT,
    limiter,
)
from src.identity.interface.api.dependencies import (
    SessionDep,
    get_login_handler,
    get_logout_handler,
    get_refresh_token_handler,
    get_register_handler,
    get_request_password_reset_handler,
    get_resend_verification_handler,
    get_reset_password_handler,
    get_verify_email_handler,
)
from src.identity.interface.api.schemas import (
    ErrorResponse,
    ForgotPasswordRequest,
    LoginRequest,
    LogoutRequest,
    MessageResponse,
    RefreshTokenRequest,
    RegisterRequest,
    RegisterResponse,
    ResendVerificationRequest,
    ResetPasswordRequest,
    TokenResponse,
    VerifyEmailRequest,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=RegisterResponse,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        400: {"model": ErrorResponse, "description": "Validation error"},
        429: {"model": ErrorResponse, "description": "Rate limited"},
    },
)
@limiter.limit(REGISTER_LIMIT)
async def register(
    request: Request,  # noqa: ARG001
    body: RegisterRequest,
    handler: Annotated[RegisterUserHandler, Depends(get_register_handler)],
    session: SessionDep,
) -> RegisterResponse:
    """
    Register a new user.

    Returns 202 Accepted regardless of whether email exists (security).
    """
    try:
        command = RegisterUserCommand(email=body.email, password=body.password)
        await handler.handle(command)
    except PasswordTooShortError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": e.code, "message": e.message},
        ) from e
    except IdentityDomainError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": e.code, "message": e.message},
        ) from e

    await session.commit()
    # Always return success message (prevents email enumeration)
    return RegisterResponse()


@router.post(
    "/verify",
    response_model=TokenResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid or expired token"},
    },
)
async def verify_email(
    body: VerifyEmailRequest,
    handler: Annotated[VerifyEmailHandler, Depends(get_verify_email_handler)],
    session: SessionDep,
) -> TokenResponse:
    """Verify email with token from verification link."""
    try:
        command = VerifyEmailCommand(token=body.token)
        tokens = await handler.handle(command)
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": e.code, "message": e.message},
        ) from e
    except UserAlreadyVerifiedError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": e.code, "message": e.message},
        ) from e

    await session.commit()
    return TokenResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type=tokens.token_type,
        expires_at=tokens.expires_at,
    )


@router.post(
    "/verify/resend",
    response_model=MessageResponse,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        429: {"model": ErrorResponse, "description": "Rate limited"},
    },
)
@limiter.limit(RESEND_VERIFICATION_LIMIT)
async def resend_verification(
    request: Request,  # noqa: ARG001
    body: ResendVerificationRequest,
    handler: Annotated[ResendVerificationHandler, Depends(get_resend_verification_handler)],
    session: SessionDep,
) -> MessageResponse:
    """
    Resend verification email.

    Always returns success (prevents email enumeration).
    """
    command = ResendVerificationCommand(email=body.email)
    await handler.handle(command)
    await session.commit()
    return MessageResponse(message="If the email exists, a verification link has been sent")


@router.post(
    "/login",
    response_model=TokenResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
        429: {"model": ErrorResponse, "description": "Rate limited"},
    },
)
@limiter.limit(LOGIN_LIMIT)
async def login(
    request: Request,  # noqa: ARG001
    body: LoginRequest,
    handler: Annotated[LoginHandler, Depends(get_login_handler)],
) -> TokenResponse:
    """Log in with email and password."""
    try:
        command = LoginCommand(
            email=body.email,
            password=body.password,
            remember_me=body.remember_me,
        )
        tokens = await handler.handle(command)
    except InvalidCredentialsError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": e.code, "message": e.message},
        ) from e
    except UserNotVerifiedError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": e.code, "message": e.message},
        ) from e
    except UserDisabledError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": e.code, "message": e.message},
        ) from e

    return TokenResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type=tokens.token_type,
        expires_at=tokens.expires_at,
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid token"},
    },
)
async def refresh_token(
    body: RefreshTokenRequest,
    handler: Annotated[RefreshTokenHandler, Depends(get_refresh_token_handler)],
) -> TokenResponse:
    """Refresh access token using refresh token."""
    try:
        command = RefreshTokenCommand(refresh_token=body.refresh_token)
        tokens = await handler.handle(command)
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"code": e.code, "message": e.message},
        ) from e

    return TokenResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
        token_type=tokens.token_type,
        expires_at=tokens.expires_at,
    )


@router.post(
    "/logout",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
)
async def logout(
    body: LogoutRequest,
    handler: Annotated[LogoutHandler, Depends(get_logout_handler)],
) -> MessageResponse:
    """Log out (invalidate refresh token)."""
    command = LogoutCommand(refresh_token=body.refresh_token)
    await handler.handle(command)
    return MessageResponse(message="Successfully logged out")


@router.post(
    "/password/forgot",
    response_model=MessageResponse,
    status_code=status.HTTP_202_ACCEPTED,
    responses={
        429: {"model": ErrorResponse, "description": "Rate limited"},
    },
)
@limiter.limit(PASSWORD_RESET_LIMIT)
async def forgot_password(
    request: Request,  # noqa: ARG001
    body: ForgotPasswordRequest,
    handler: Annotated[RequestPasswordResetHandler, Depends(get_request_password_reset_handler)],
    session: SessionDep,
) -> MessageResponse:
    """
    Request password reset email.

    Always returns success (prevents email enumeration).
    """
    command = RequestPasswordResetCommand(email=body.email)
    await handler.handle(command)
    await session.commit()
    return MessageResponse(message="If the email exists, a password reset link has been sent")


@router.post(
    "/password/reset",
    response_model=MessageResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Invalid token or password"},
    },
)
async def reset_password(
    body: ResetPasswordRequest,
    handler: Annotated[ResetPasswordHandler, Depends(get_reset_password_handler)],
    session: SessionDep,
) -> MessageResponse:
    """Reset password using reset token."""
    try:
        command = ResetPasswordCommand(
            token=body.token,
            new_password=body.new_password,
        )
        await handler.handle(command)
    except InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": e.code, "message": e.message},
        ) from e
    except PasswordTooShortError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"code": e.code, "message": e.message},
        ) from e

    await session.commit()
    return MessageResponse(message="Password successfully reset")
