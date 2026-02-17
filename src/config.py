"""Application configuration using pydantic-settings."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",  # Ignore extra env vars not defined in model (e.g., port isolation vars)
    )

    # Application
    app_env: str = "development"
    app_debug: bool = False
    app_secret_key: str = "dev-secret-key-change-in-production"

    # Database
    database_url: str = "postgresql+asyncpg://koulu:koulu_dev_password@localhost:5432/koulu"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    jwt_secret_key: str = "jwt-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    jwt_refresh_token_expire_days: int = 7
    jwt_refresh_token_remember_me_days: int = 30

    # Email (Resend HTTP API)
    resend_api_key: str = ""
    mail_from: str = "onboarding@resend.dev"
    mail_from_name: str = "Koulu"

    # SMTP (for local dev / E2E with MailHog — used when smtp_host is set)
    smtp_host: str = ""
    smtp_port: int = 1025

    # Frontend URL (for email links)
    frontend_url: str = "http://localhost:5173"

    # Database pool
    db_pool_size: int = 5
    db_max_overflow: int = 10

    # Rate Limiting
    rate_limit_enabled: bool = True

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.app_env == "development"

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.app_env == "production"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Global settings instance
settings = get_settings()
