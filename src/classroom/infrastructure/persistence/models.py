"""SQLAlchemy models for Classroom context."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
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


class ProgressModel(Base):
    """SQLAlchemy model for progress table."""

    __tablename__ = "progress"

    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        nullable=False,
        index=True,
    )
    course_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("courses.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    last_accessed_lesson_id: Mapped[UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("lessons.id", ondelete="SET NULL"),
        nullable=True,
    )
    last_accessed_at: Mapped[datetime | None] = mapped_column(
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
    completions: Mapped[list["LessonCompletionModel"]] = relationship(
        "LessonCompletionModel",
        back_populates="progress",
        cascade="all, delete-orphan",
    )

    __table_args__ = (
        UniqueConstraint("user_id", "course_id", name="uq_progress_user_course"),
        Index("idx_progress_user", "user_id"),
        Index("idx_progress_course", "course_id"),
    )


class LessonCompletionModel(Base):
    """SQLAlchemy model for lesson_completions table."""

    __tablename__ = "lesson_completions"

    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
    )
    progress_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("progress.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    lesson_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("lessons.id", ondelete="CASCADE"),
        nullable=False,
    )
    completed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Relationships
    progress: Mapped["ProgressModel"] = relationship(
        "ProgressModel",
        back_populates="completions",
    )

    __table_args__ = (
        UniqueConstraint("progress_id", "lesson_id", name="uq_completion_progress_lesson"),
        Index("idx_completion_progress", "progress_id", "lesson_id"),
    )
