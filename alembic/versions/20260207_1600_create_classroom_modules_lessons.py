"""Create modules and lessons tables for Classroom context.

Revision ID: 009_create_classroom_modules_lessons
Revises: 008_create_classroom_courses
Create Date: 2026-02-07 16:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "009_modules_lessons"
down_revision: str | None = "008_create_classroom_courses"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create modules table
    op.create_table(
        "modules",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column(
            "course_id",
            UUID(as_uuid=True),
            sa.ForeignKey("courses.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("position", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("idx_module_course", "modules", ["course_id"], unique=False)
    op.create_index("idx_module_position", "modules", ["course_id", "position"], unique=False)

    # Create lessons table
    op.create_table(
        "lessons",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column(
            "module_id",
            UUID(as_uuid=True),
            sa.ForeignKey("modules.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("content_type", sa.String(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False, server_default="1"),
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index("idx_lesson_module", "lessons", ["module_id"], unique=False)
    op.create_index("idx_lesson_position", "lessons", ["module_id", "position"], unique=False)


def downgrade() -> None:
    op.drop_index("idx_lesson_position", table_name="lessons")
    op.drop_index("idx_lesson_module", table_name="lessons")
    op.drop_table("lessons")

    op.drop_index("idx_module_position", table_name="modules")
    op.drop_index("idx_module_course", table_name="modules")
    op.drop_table("modules")
