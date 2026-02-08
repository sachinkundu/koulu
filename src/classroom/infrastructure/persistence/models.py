"""SQLAlchemy models for Classroom context."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.infrastructure import Base


class CourseModel(Base):
    """SQLAlchemy model for courses table."""

    __tablename__ = "courses"

    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
    )
    instructor_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    cover_image_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    estimated_duration: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
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
    modules: Mapped[list["ModuleModel"]] = relationship(
        "ModuleModel",
        back_populates="course",
        cascade="all, delete-orphan",
        order_by="ModuleModel.position",
    )

    __table_args__ = (
        Index("idx_course_instructor", "instructor_id"),
        Index("idx_course_created", "created_at"),
    )


class ModuleModel(Base):
    """SQLAlchemy model for modules table."""

    __tablename__ = "modules"

    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
    )
    course_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
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
    course: Mapped["CourseModel"] = relationship(
        "CourseModel",
        back_populates="modules",
    )
    lessons: Mapped[list["LessonModel"]] = relationship(
        "LessonModel",
        back_populates="module",
        cascade="all, delete-orphan",
        order_by="LessonModel.position",
    )

    __table_args__ = (
        Index("idx_module_course", "course_id"),
        Index("idx_module_position", "course_id", "position"),
    )


class LessonModel(Base):
    """SQLAlchemy model for lessons table."""

    __tablename__ = "lessons"

    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
    )
    module_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("modules.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    content_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    position: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
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
    module: Mapped["ModuleModel"] = relationship(
        "ModuleModel",
        back_populates="lessons",
    )

    __table_args__ = (
        Index("idx_lesson_module", "module_id"),
        Index("idx_lesson_position", "module_id", "position"),
    )
