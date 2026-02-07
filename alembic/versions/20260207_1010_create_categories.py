"""Create categories table.

Revision ID: 004_create_categories
Revises: 003_create_communities
Create Date: 2026-02-07 10:10:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "004_create_categories"
down_revision: str | None = "003_create_communities"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "categories",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column(
            "community_id",
            UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=50), nullable=False),
        sa.Column("slug", sa.String(length=50), nullable=False),
        sa.Column("emoji", sa.String(length=10), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
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
        sa.ForeignKeyConstraint(
            ["community_id"],
            ["communities.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_categories_community_id"),
        "categories",
        ["community_id"],
        unique=False,
    )
    op.create_index(
        "idx_category_community_name",
        "categories",
        ["community_id", "name"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("idx_category_community_name", table_name="categories")
    op.drop_index(op.f("ix_categories_community_id"), table_name="categories")
    op.drop_table("categories")
