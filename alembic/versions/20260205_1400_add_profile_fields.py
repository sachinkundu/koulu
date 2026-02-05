"""Add profile fields for location and social links.

Revision ID: 002_add_profile_fields
Revises: 001_initial_identity
Create Date: 2026-02-05 14:00:00
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "002_add_profile_fields"
down_revision: str | None = "001_initial_identity"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add location fields
    op.add_column("profiles", sa.Column("location_city", sa.String(length=100), nullable=True))
    op.add_column("profiles", sa.Column("location_country", sa.String(length=100), nullable=True))

    # Add social links
    op.add_column("profiles", sa.Column("twitter_url", sa.String(length=500), nullable=True))
    op.add_column("profiles", sa.Column("linkedin_url", sa.String(length=500), nullable=True))
    op.add_column("profiles", sa.Column("instagram_url", sa.String(length=500), nullable=True))
    op.add_column("profiles", sa.Column("website_url", sa.String(length=500), nullable=True))


def downgrade() -> None:
    # Remove social links
    op.drop_column("profiles", "website_url")
    op.drop_column("profiles", "instagram_url")
    op.drop_column("profiles", "linkedin_url")
    op.drop_column("profiles", "twitter_url")

    # Remove location fields
    op.drop_column("profiles", "location_country")
    op.drop_column("profiles", "location_city")
