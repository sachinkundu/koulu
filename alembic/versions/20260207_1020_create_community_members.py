"""Create community_members table.

Revision ID: 005_create_community_members
Revises: 004_create_categories
Create Date: 2026-02-07 10:20:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "005_create_community_members"
down_revision: str | None = "004_create_categories"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "community_members",
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("community_id", UUID(as_uuid=True), nullable=False),
        sa.Column(
            "role",
            sa.String(length=20),
            nullable=False,
        ),
        sa.Column(
            "joined_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            nullable=False,
            server_default="true",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["community_id"],
            ["communities.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("user_id", "community_id"),
    )


def downgrade() -> None:
    op.drop_table("community_members")
