"""add gamification tables

Revision ID: a1b2c3d4e5f6
Revises: c2cd28a5f95b
Create Date: 2026-02-15 10:00:00.000000
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a1b2c3d4e5f6"
down_revision: str | None = "c2cd28a5f95b"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # member_points table
    op.create_table(
        "member_points",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("community_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("total_points", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("current_level", sa.SmallInteger(), nullable=False, server_default="1"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("community_id", "user_id", name="uq_member_points_community_user"),
    )
    op.create_index(
        "ix_member_points_community_level", "member_points", ["community_id", "current_level"]
    )
    op.create_index(
        "ix_member_points_community_total",
        "member_points",
        ["community_id", sa.text("total_points DESC")],
    )

    # point_transactions table
    op.create_table(
        "point_transactions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("member_points_id", sa.UUID(), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.Column("source", sa.String(30), nullable=False),
        sa.Column("source_id", sa.UUID(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["member_points_id"], ["member_points.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_point_transactions_member_created",
        "point_transactions",
        ["member_points_id", sa.text("created_at DESC")],
    )

    # level_configurations table
    op.create_table(
        "level_configurations",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("community_id", sa.UUID(), nullable=False),
        sa.Column("levels", sa.JSON(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("community_id", name="uq_level_configurations_community"),
    )


def downgrade() -> None:
    op.drop_table("level_configurations")
    op.drop_index("ix_point_transactions_member_created", table_name="point_transactions")
    op.drop_table("point_transactions")
    op.drop_index("ix_member_points_community_total", table_name="member_points")
    op.drop_index("ix_member_points_community_level", table_name="member_points")
    op.drop_table("member_points")
