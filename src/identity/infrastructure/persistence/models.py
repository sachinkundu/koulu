"""SQLAlchemy models for Identity context."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import TSVECTOR
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.infrastructure import Base


class UserModel(Base):
    """SQLAlchemy model for users table."""

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
    )
    email: Mapped[str] = mapped_column(
        String(254),
        unique=True,
        nullable=False,
        index=True,
    )
    hashed_password: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    profile: Mapped["ProfileModel"] = relationship(
        "ProfileModel",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    verification_tokens: Mapped[list["VerificationTokenModel"]] = relationship(
        "VerificationTokenModel",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    reset_tokens: Mapped[list["ResetTokenModel"]] = relationship(
        "ResetTokenModel",
        back_populates="user",
        cascade="all, delete-orphan",
    )


class ProfileModel(Base):
    """SQLAlchemy model for profiles table."""

    __tablename__ = "profiles"

    user_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    display_name: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
    )
    avatar_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    bio: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    username: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        unique=True,
    )
    search_vector: Mapped[str | None] = mapped_column(TSVECTOR, nullable=True)
    location_city: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    location_country: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    twitter_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    linkedin_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    instagram_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    website_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    is_complete: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="profile",
    )


class VerificationTokenModel(Base):
    """SQLAlchemy model for verification tokens."""

    __tablename__ = "verification_tokens"

    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    token: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Relationships
    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="verification_tokens",
    )

    # Indexes
    __table_args__ = (
        Index("idx_verification_tokens_token", "token"),
        Index("idx_verification_tokens_user_id", "user_id"),
    )


class ResetTokenModel(Base):
    """SQLAlchemy model for password reset tokens."""

    __tablename__ = "reset_tokens"

    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    token: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )
    used_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Relationships
    user: Mapped["UserModel"] = relationship(
        "UserModel",
        back_populates="reset_tokens",
    )

    # Indexes
    __table_args__ = (
        Index("idx_reset_tokens_token", "token"),
        Index("idx_reset_tokens_user_id", "user_id"),
    )
