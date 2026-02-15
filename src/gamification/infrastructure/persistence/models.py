"""SQLAlchemy models for Gamification context."""

from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.infrastructure import Base


class MemberPointsModel(Base):
    """Stores a member's point total and current level per community."""

    __tablename__ = "member_points"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    community_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    user_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    total_points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    current_level: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    transactions: Mapped[list["PointTransactionModel"]] = relationship(
        back_populates="member_points", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("community_id", "user_id", name="uq_member_points_community_user"),
        Index("ix_member_points_community_level", "community_id", "current_level"),
        Index("ix_member_points_community_total", "community_id", total_points.desc()),
    )


class PointTransactionModel(Base):
    """Append-only audit log of point changes."""

    __tablename__ = "point_transactions"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    member_points_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True), ForeignKey("member_points.id"), nullable=False
    )
    points: Mapped[int] = mapped_column(Integer, nullable=False)
    source: Mapped[str] = mapped_column(String(30), nullable=False)
    source_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    member_points: Mapped["MemberPointsModel"] = relationship(back_populates="transactions")

    __table_args__ = (
        Index("ix_point_transactions_member_created", "member_points_id", created_at.desc()),
    )


class LevelConfigurationModel(Base):
    """Per-community level configuration (9 levels as JSONB)."""

    __tablename__ = "level_configurations"

    id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), primary_key=True, default=uuid4)
    community_id: Mapped[UUID] = mapped_column(PgUUID(as_uuid=True), nullable=False, unique=True)
    levels: Mapped[list[dict[str, Any]]] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
