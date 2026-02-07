"""Create courses table for Classroom context.

Revision ID: 008_create_classroom_courses
Revises: 007_seed_default_categories
Create Date: 2026-02-07 15:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "008_create_classroom_courses"
down_revision: str | None = "007_seed_default_categories"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "courses",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("instructor_id", UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("cover_image_url", sa.String(length=500), nullable=True),
        sa.Column("estimated_duration", sa.String(length=100), nullable=True),
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

    # Create indexes
    op.create_index(
        op.f("ix_courses_instructor_id"),
        "courses",
        ["instructor_id"],
        unique=False,
    )
    op.create_index(
        "idx_course_instructor",
        "courses",
        ["instructor_id"],
        unique=False,
    )
    op.create_index(
        "idx_course_created",
        "courses",
        ["created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_course_created", table_name="courses")
    op.drop_index("idx_course_instructor", table_name="courses")
    op.drop_index(op.f("ix_courses_instructor_id"), table_name="courses")
    op.drop_table("courses")
