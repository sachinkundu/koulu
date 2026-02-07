"""Create reactions table.

Revision ID: 009_create_reactions
Revises: 008_create_comments
Create Date: 2026-02-08 10:10:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "009_create_reactions"
down_revision: str | None = "008_create_comments"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "reactions",
        sa.Column("id", UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("target_type", sa.String(length=20), nullable=False),
        sa.Column("target_id", UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    # Create unique index for one reaction per user per target
    op.create_index(
        "idx_reaction_user_target",
        "reactions",
        ["user_id", "target_type", "target_id"],
        unique=True,
    )

    # Create composite index for target lookups
    op.create_index(
        "idx_reaction_target",
        "reactions",
        ["target_type", "target_id"],
        unique=False,
    )

    # Create single-column index for user_id
    op.create_index(
        op.f("ix_reactions_user_id"),
        "reactions",
        ["user_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_reactions_user_id"), table_name="reactions")
    op.drop_index("idx_reaction_target", table_name="reactions")
    op.drop_index("idx_reaction_user_target", table_name="reactions")
    op.drop_table("reactions")
