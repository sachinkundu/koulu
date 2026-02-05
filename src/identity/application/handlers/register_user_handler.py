"""Register user command handler."""

import structlog

from src.identity.application.commands.register_user import RegisterUserCommand
from src.identity.domain.entities import User
from src.identity.domain.repositories import IUserRepository, IVerificationTokenRepository
from src.identity.domain.services import IPasswordHasher, ITokenGenerator
from src.identity.domain.value_objects import EmailAddress, UserId
from src.shared.infrastructure import event_bus

logger = structlog.get_logger()


class RegisterUserHandler:
    """Handler for user registration."""

    def __init__(
        self,
        user_repository: IUserRepository,
        verification_token_repository: IVerificationTokenRepository,
        password_hasher: IPasswordHasher,
        token_generator: ITokenGenerator,
    ) -> None:
        """Initialize with dependencies."""
        self._user_repository = user_repository
        self._verification_token_repository = verification_token_repository
        self._password_hasher = password_hasher
        self._token_generator = token_generator

    async def handle(self, command: RegisterUserCommand) -> UserId | None:
        """
        Handle user registration.

        Returns UserId on success, None if email already exists
        (to prevent email enumeration).
        """
        logger.info("register_user_attempt", email=command.email)

        # Validate email format
        try:
            email = EmailAddress(command.email)
        except Exception:
            logger.warning("register_user_invalid_email", email=command.email)
            return None

        # Validate password strength
        try:
            User.validate_password_strength(command.password)
        except Exception as e:
            logger.warning("register_user_weak_password", error=str(e))
            raise

        # Check if user already exists (silently ignore for security)
        if await self._user_repository.exists_by_email(email):
            logger.info("register_user_email_exists", email=command.email)
            # Return None but don't raise error to prevent email enumeration
            return None

        # Hash password
        hashed_password = self._password_hasher.hash(command.password)

        # Create user
        user = User.register(email=email, hashed_password=hashed_password)

        # Save user
        await self._user_repository.save(user)

        # Generate and save verification token
        token = self._token_generator.generate_verification_token()
        expires_at = self._token_generator.get_verification_token_expiry()
        await self._verification_token_repository.save(
            user_id=user.id,
            token=token,
            expires_at=expires_at,
        )

        # Publish domain events (triggers email sending)
        await event_bus.publish_all(user.clear_events())

        logger.info("register_user_success", user_id=str(user.id))
        return user.id
