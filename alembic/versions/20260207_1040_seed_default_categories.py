"""Seed default categories for default community.

Revision ID: 007_seed_default_categories
Revises: 006_create_posts
Create Date: 2026-02-07 10:40:00
"""

from collections.abc import Sequence
from uuid import uuid4

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

revision: str = "007_seed_default_categories"
down_revision: str | None = "006_create_posts"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Create a default community
    default_community_id = uuid4()

    op.execute(
        sa.text(
            """
            INSERT INTO communities (id, name, slug, description, created_at, updated_at)
            VALUES (
                :id,
                'Default Community',
                'default',
                'Welcome to the default community',
                NOW(),
                NOW()
            )
            """
        ).bindparams(
            id=default_community_id,
        )
    )

    # Insert default categories
    categories = [
        {
            "id": uuid4(),
            "community_id": default_community_id,
            "name": "General",
            "slug": "general",
            "emoji": "💬",
            "description": "General discussion and community chat",
        },
        {
            "id": uuid4(),
            "community_id": default_community_id,
            "name": "Q&A",
            "slug": "qa",
            "emoji": "❓",
            "description": "Ask questions and get help from the community",
        },
        {
            "id": uuid4(),
            "community_id": default_community_id,
            "name": "Wins",
            "slug": "wins",
            "emoji": "🎉",
            "description": "Celebrate your achievements and milestones",
        },
        {
            "id": uuid4(),
            "community_id": default_community_id,
            "name": "Introductions",
            "slug": "introductions",
            "emoji": "👋",
            "description": "Introduce yourself to the community",
        },
    ]

    for category in categories:
        op.execute(
            sa.text(
                """
                INSERT INTO categories (id, community_id, name, slug, emoji, description, created_at, updated_at)
                VALUES (
                    :id,
                    :community_id,
                    :name,
                    :slug,
                    :emoji,
                    :description,
                    NOW(),
                    NOW()
                )
                """
            ).bindparams(
                id=category["id"],
                community_id=category["community_id"],
                name=category["name"],
                slug=category["slug"],
                emoji=category["emoji"],
                description=category["description"],
            )
        )


def downgrade() -> None:
    # Delete default categories and community
    op.execute(
        sa.text(
            """
            DELETE FROM categories
            WHERE community_id IN (
                SELECT id FROM communities WHERE slug = 'default'
            )
            """
        )
    )
    op.execute(
        sa.text(
            """
            DELETE FROM communities WHERE slug = 'default'
            """
        )
    )
