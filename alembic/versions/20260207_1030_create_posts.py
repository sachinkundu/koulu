"""Create posts table.

Revision ID: 006_create_posts
Revises: 005_create_community_members
Create Date: 2026-02-07 10:30:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "006_create_posts"
down_revision: str | None = "005_create_community_members"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "posts",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("community_id", UUID(as_uuid=True), nullable=False),
        sa.Column("author_id", UUID(as_uuid=True), nullable=True),
        sa.Column("category_id", UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("image_url", sa.String(length=500), nullable=True),
        sa.Column(
            "is_pinned",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
        sa.Column("pinned_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "is_locked",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
        sa.Column(
            "is_deleted",
            sa.Boolean(),
            nullable=False,
            server_default="false",
        ),
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
        sa.Column("edited_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ["community_id"],
            ["communities.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["author_id"],
            ["users.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["category_id"],
            ["categories.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes
    op.create_index(
        op.f("ix_posts_community_id"),
        "posts",
        ["community_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_posts_author_id"),
        "posts",
        ["author_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_posts_category_id"),
        "posts",
        ["category_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_posts_is_deleted"),
        "posts",
        ["is_deleted"],
        unique=False,
    )
    op.create_index(
        op.f("ix_posts_created_at"),
        "posts",
        ["created_at"],
        unique=False,
    )

    # Create composite indexes for feed queries
    op.create_index(
        "idx_post_community_created",
        "posts",
        ["community_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "idx_post_community_pinned",
        "posts",
        ["community_id", "is_pinned"],
        unique=False,
    )
    op.create_index(
        "idx_post_category_created",
        "posts",
        ["category_id", "created_at"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_post_category_created", table_name="posts")
    op.drop_index("idx_post_community_pinned", table_name="posts")
    op.drop_index("idx_post_community_created", table_name="posts")
    op.drop_index(op.f("ix_posts_created_at"), table_name="posts")
    op.drop_index(op.f("ix_posts_is_deleted"), table_name="posts")
    op.drop_index(op.f("ix_posts_category_id"), table_name="posts")
    op.drop_index(op.f("ix_posts_author_id"), table_name="posts")
    op.drop_index(op.f("ix_posts_community_id"), table_name="posts")
    op.drop_table("posts")
