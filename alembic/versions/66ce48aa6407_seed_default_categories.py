"""seed_default_categories

Revision ID: 66ce48aa6407
Revises: 8295c6c51028
Create Date: 2026-02-08 09:26:09.769605
"""

from typing import Sequence, Union
from uuid import uuid4

from alembic import op
import sqlalchemy as sa
from sqlalchemy import text


# revision identifiers, used by Alembic.
revision: str = '66ce48aa6407'
down_revision: Union[str, None] = '8295c6c51028'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# Default community ID (consistent across environments)
DEFAULT_COMMUNITY_ID = "00000000-0000-0000-0000-000000000001"


def upgrade() -> None:
    """Create default community and categories."""
    conn = op.get_bind()

    # Check if default community already exists
    result = conn.execute(
        text("SELECT id FROM communities WHERE id = :id"),
        {"id": DEFAULT_COMMUNITY_ID}
    )

    if result.fetchone() is None:
        # Create default community
        conn.execute(
            text("""
                INSERT INTO communities (id, name, slug, description, created_at, updated_at)
                VALUES (:id, :name, :slug, :description, NOW(), NOW())
            """),
            {
                "id": DEFAULT_COMMUNITY_ID,
                "name": "Koulu Community",
                "slug": "koulu",
                "description": "The main Koulu community space"
            }
        )

    # Define default categories
    categories = [
        {
            "id": str(uuid4()),
            "community_id": DEFAULT_COMMUNITY_ID,
            "name": "General",
            "slug": "general",
            "emoji": "💬",
            "description": "General discussion and announcements"
        },
        {
            "id": str(uuid4()),
            "community_id": DEFAULT_COMMUNITY_ID,
            "name": "Q&A",
            "slug": "qa",
            "emoji": "❓",
            "description": "Questions and answers"
        },
        {
            "id": str(uuid4()),
            "community_id": DEFAULT_COMMUNITY_ID,
            "name": "Roast",
            "slug": "roast",
            "emoji": "🔥",
            "description": "Constructive feedback and critiques"
        },
        {
            "id": str(uuid4()),
            "community_id": DEFAULT_COMMUNITY_ID,
            "name": "Wins",
            "slug": "wins",
            "emoji": "🏆",
            "description": "Celebrate your achievements"
        },
        {
            "id": str(uuid4()),
            "community_id": DEFAULT_COMMUNITY_ID,
            "name": "Tools & Resources",
            "slug": "tools-resources",
            "emoji": "🛠️",
            "description": "Share helpful tools and resources"
        },
        {
            "id": str(uuid4()),
            "community_id": DEFAULT_COMMUNITY_ID,
            "name": "Meet & Greet",
            "slug": "meet-greet",
            "emoji": "👋",
            "description": "Introduce yourself to the community"
        }
    ]

    # Insert categories (only if they don't exist)
    for category in categories:
        result = conn.execute(
            text("SELECT id FROM categories WHERE slug = :slug AND community_id = :community_id"),
            {"slug": category["slug"], "community_id": category["community_id"]}
        )

        if result.fetchone() is None:
            conn.execute(
                text("""
                    INSERT INTO categories (id, community_id, name, slug, emoji, description, created_at, updated_at)
                    VALUES (:id, :community_id, :name, :slug, :emoji, :description, NOW(), NOW())
                """),
                category
            )


def downgrade() -> None:
    """Remove default categories and community."""
    conn = op.get_bind()

    # Delete categories associated with default community
    conn.execute(
        text("DELETE FROM categories WHERE community_id = :community_id"),
        {"community_id": DEFAULT_COMMUNITY_ID}
    )

    # Delete default community
    conn.execute(
        text("DELETE FROM communities WHERE id = :id"),
        {"id": DEFAULT_COMMUNITY_ID}
    )
