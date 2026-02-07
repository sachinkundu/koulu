"""Create comments table.

Revision ID: 008_create_comments
Revises: 007_seed_default_categories
Create Date: 2026-02-08 10:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "008_create_comments"
down_revision: str | None = "007_seed_default_categories"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "comments",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("post_id", UUID(as_uuid=True), nullable=False),
        sa.Column("author_id", UUID(as_uuid=True), nullable=True),
        sa.Column("parent_comment_id", UUID(as_uuid=True), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
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
            ["post_id"],
            ["posts.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["author_id"],
            ["users.id"],
            ondelete="SET NULL",
        ),
        sa.ForeignKeyConstraint(
            ["parent_comment_id"],
            ["comments.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create indexes
    op.create_index(
        op.f("ix_comments_post_id"),
        "comments",
        ["post_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_comments_author_id"),
        "comments",
        ["author_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_comments_parent_comment_id"),
        "comments",
        ["parent_comment_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_comments_created_at"),
        "comments",
        ["created_at"],
        unique=False,
    )

    # Create composite indexes for comment queries
    op.create_index(
        "idx_comment_post_created",
        "comments",
        ["post_id", "created_at"],
        unique=False,
    )
    op.create_index(
        "idx_comment_parent",
        "comments",
        ["parent_comment_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("idx_comment_parent", table_name="comments")
    op.drop_index("idx_comment_post_created", table_name="comments")
    op.drop_index(op.f("ix_comments_created_at"), table_name="comments")
    op.drop_index(op.f("ix_comments_parent_comment_id"), table_name="comments")
    op.drop_index(op.f("ix_comments_author_id"), table_name="comments")
    op.drop_index(op.f("ix_comments_post_id"), table_name="comments")
    op.drop_table("comments")
