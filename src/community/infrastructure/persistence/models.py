"""SQLAlchemy models for Community context."""

from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text, func
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.community.domain.value_objects import MemberRole
from src.shared.infrastructure import Base


class CommunityModel(Base):
    """SQLAlchemy model for communities table."""

    __tablename__ = "communities"

    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Relationships
    categories: Mapped[list["CategoryModel"]] = relationship(
        "CategoryModel",
        back_populates="community",
        cascade="all, delete-orphan",
    )
    members: Mapped[list["CommunityMemberModel"]] = relationship(
        "CommunityMemberModel",
        back_populates="community",
        cascade="all, delete-orphan",
    )
    posts: Mapped[list["PostModel"]] = relationship(
        "PostModel",
        back_populates="community",
        cascade="all, delete-orphan",
    )


class CategoryModel(Base):
    """SQLAlchemy model for categories table."""

    __tablename__ = "categories"

    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
    )
    community_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("communities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    name: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    slug: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )
    emoji: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )

    # Unique constraint: (community_id, name)
    __table_args__ = (Index("idx_category_community_name", "community_id", "name", unique=True),)

    # Relationships
    community: Mapped["CommunityModel"] = relationship(
        "CommunityModel",
        back_populates="categories",
    )
    posts: Mapped[list["PostModel"]] = relationship(
        "PostModel",
        back_populates="category",
    )


class CommunityMemberModel(Base):
    """SQLAlchemy model for community_members table."""

    __tablename__ = "community_members"

    user_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    )
    community_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("communities.id", ondelete="CASCADE"),
        primary_key=True,
    )
    role: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default=MemberRole.MEMBER.value,
    )
    joined_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )

    # Relationships
    community: Mapped["CommunityModel"] = relationship(
        "CommunityModel",
        back_populates="members",
    )


class PostModel(Base):
    """SQLAlchemy model for posts table."""

    __tablename__ = "posts"

    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
    )
    community_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("communities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    author_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    category_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    title: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    image_url: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    is_pinned: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    pinned_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )
    is_locked: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    edited_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Indexes for feed queries
    __table_args__ = (
        Index("idx_post_community_created", "community_id", "created_at"),
        Index("idx_post_community_pinned", "community_id", "is_pinned"),
        Index("idx_post_category_created", "category_id", "created_at"),
    )

    # Relationships
    community: Mapped["CommunityModel"] = relationship(
        "CommunityModel",
        back_populates="posts",
    )
    category: Mapped["CategoryModel"] = relationship(
        "CategoryModel",
        back_populates="posts",
    )
    comments: Mapped[list["CommentModel"]] = relationship(
        "CommentModel",
        back_populates="post",
        cascade="all, delete-orphan",
    )


class CommentModel(Base):
    """SQLAlchemy model for comments table."""

    __tablename__ = "comments"

    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
    )
    post_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("posts.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    author_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    parent_comment_id: Mapped[UUID | None] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("comments.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    content: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        index=True,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
    edited_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    # Indexes for comment queries
    __table_args__ = (
        Index("idx_comment_post_created", "post_id", "created_at"),
        Index("idx_comment_parent", "parent_comment_id"),
    )

    # Relationships
    post: Mapped["PostModel"] = relationship(
        "PostModel",
        back_populates="comments",
    )
    parent: Mapped["CommentModel | None"] = relationship(
        "CommentModel",
        remote_side=[id],
        back_populates="replies",
    )
    replies: Mapped[list["CommentModel"]] = relationship(
        "CommentModel",
        back_populates="parent",
        cascade="all, delete-orphan",
    )


class ReactionModel(Base):
    """SQLAlchemy model for reactions table."""

    __tablename__ = "reactions"

    id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        primary_key=True,
    )
    user_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
    )
    target_id: Mapped[UUID] = mapped_column(
        PgUUID(as_uuid=True),
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    # Unique constraint: one reaction per user per target
    # Composite index for target lookups
    __table_args__ = (
        Index(
            "idx_reaction_user_target",
            "user_id",
            "target_type",
            "target_id",
            unique=True,
        ),
        Index("idx_reaction_target", "target_type", "target_id"),
    )
