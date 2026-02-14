"""add search vectors and username to profiles and posts

Revision ID: c2cd28a5f95b
Revises: d51610573516
Create Date: 2026-02-14 08:50:35.488118
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import TSVECTOR

# revision identifiers, used by Alembic.
revision: str = "c2cd28a5f95b"
down_revision: str | None = "d51610573516"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 1. Add username column to profiles
    op.add_column("profiles", sa.Column("username", sa.String(100), nullable=True))
    op.create_unique_constraint("uq_profiles_username", "profiles", ["username"])
    op.create_index("idx_profiles_username", "profiles", ["username"])

    # 2. Add search_vector columns
    op.add_column("profiles", sa.Column("search_vector", TSVECTOR, nullable=True))
    op.add_column("posts", sa.Column("search_vector", TSVECTOR, nullable=True))

    # 3. Create GIN indexes
    op.create_index(
        "idx_profiles_search_vector",
        "profiles",
        ["search_vector"],
        postgresql_using="gin",
    )
    op.create_index(
        "idx_posts_search_vector",
        "posts",
        ["search_vector"],
        postgresql_using="gin",
    )

    # 4. Create trigger functions
    op.execute("""
        CREATE OR REPLACE FUNCTION profiles_search_vector_update() RETURNS trigger AS $$
        BEGIN
          NEW.search_vector := to_tsvector(
            'english',
            coalesce(NEW.display_name, '') || ' ' || coalesce(NEW.bio, '')
          );
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    op.execute("""
        CREATE OR REPLACE FUNCTION posts_search_vector_update() RETURNS trigger AS $$
        BEGIN
          NEW.search_vector := to_tsvector(
            'english',
            coalesce(NEW.title, '') || ' ' || coalesce(NEW.content, '')
          );
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    """)

    # 5. Create triggers
    op.execute("""
        CREATE TRIGGER profiles_search_vector_trigger
          BEFORE INSERT OR UPDATE OF display_name, bio ON profiles
          FOR EACH ROW EXECUTE FUNCTION profiles_search_vector_update();
    """)

    op.execute("""
        CREATE TRIGGER posts_search_vector_trigger
          BEFORE INSERT OR UPDATE OF title, content ON posts
          FOR EACH ROW EXECUTE FUNCTION posts_search_vector_update();
    """)

    # 6. Backfill existing rows
    op.execute("""
        UPDATE profiles
        SET search_vector = to_tsvector(
          'english',
          coalesce(display_name, '') || ' ' || coalesce(bio, '')
        );
    """)

    op.execute("""
        UPDATE posts
        SET search_vector = to_tsvector(
          'english',
          coalesce(title, '') || ' ' || coalesce(content, '')
        );
    """)

    # 7. Generate usernames for existing profiles
    op.execute("""
        UPDATE profiles
        SET username = lower(replace(coalesce(display_name, 'user'), ' ', '-'))
            || '-' || substr(user_id::text, 1, 4)
        WHERE username IS NULL;
    """)


def downgrade() -> None:
    # Drop triggers
    op.execute("DROP TRIGGER IF EXISTS posts_search_vector_trigger ON posts;")
    op.execute("DROP TRIGGER IF EXISTS profiles_search_vector_trigger ON profiles;")

    # Drop trigger functions
    op.execute("DROP FUNCTION IF EXISTS posts_search_vector_update();")
    op.execute("DROP FUNCTION IF EXISTS profiles_search_vector_update();")

    # Drop indexes
    op.drop_index("idx_posts_search_vector", table_name="posts")
    op.drop_index("idx_profiles_search_vector", table_name="profiles")
    op.drop_index("idx_profiles_username", table_name="profiles")

    # Drop constraints
    op.drop_constraint("uq_profiles_username", "profiles", type_="unique")

    # Drop columns
    op.drop_column("posts", "search_vector")
    op.drop_column("profiles", "search_vector")
    op.drop_column("profiles", "username")
