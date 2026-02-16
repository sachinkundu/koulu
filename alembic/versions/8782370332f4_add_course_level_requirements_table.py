"""add course_level_requirements table

Revision ID: 8782370332f4
Revises: a1b2c3d4e5f6
Create Date: 2026-02-16 13:24:37.041366
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8782370332f4"
down_revision: str | None = "a1b2c3d4e5f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "course_level_requirements",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("community_id", sa.UUID(), nullable=False),
        sa.Column("course_id", sa.UUID(), nullable=False),
        sa.Column("minimum_level", sa.SmallInteger(), nullable=False, server_default="1"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "community_id", "course_id", name="uq_course_level_req_community_course"
        ),
    )


def downgrade() -> None:
    op.drop_table("course_level_requirements")
