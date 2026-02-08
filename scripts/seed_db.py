#!/usr/bin/env python3
"""
Database seeding script for Koulu development.

Seeds the database with realistic test data:
- 20 users with profiles
- 5 communities with categories
- Community memberships (users distributed across communities)
- 10-20 posts per community with comments and reactions
- Courses with modules and lessons

This script is IDEMPOTENT - it checks for existing seed data and skips if present.
"""

import asyncio
import json
import os
import random
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import uuid4

from faker import Faker
from pwdlib import PasswordHash
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from src.classroom.infrastructure.persistence.models import (
    CourseModel,
    LessonModel,
    ModuleModel,
)
from src.community.domain.value_objects import MemberRole
from src.community.infrastructure.persistence.models import (
    CategoryModel,
    CommentModel,
    CommunityMemberModel,
    CommunityModel,
    PostModel,
    ReactionModel,
)
from src.identity.infrastructure.persistence.models import ProfileModel, UserModel
from src.shared.infrastructure.database import Database

fake = Faker()
password_hasher = PasswordHash.recommended()

# Seed marker email - if this user exists, we assume DB is already seeded
SEED_MARKER_EMAIL = "seed.marker@koulu.dev"

# Common password for all seeded users (development only)
SEED_PASSWORD = "Password123!"

# Credentials file path
CREDENTIALS_FILE = Path(__file__).parent / ".seed-credentials.json"
CREDENTIALS_TXT_FILE = Path(__file__).parent / ".seed-credentials.txt"

# Sample data pools
COMMUNITY_NAMES = [
    "Python Mastery",
    "Web3 Builders",
    "Fitness Warriors",
    "Indie Makers",
    "Creative Writers",
]

CATEGORY_DATA = {
    "Python Mastery": [
        ("💬", "General", "general"),
        ("🚀", "Projects", "projects"),
        ("❓", "Help", "help"),
        ("📚", "Resources", "resources"),
    ],
    "Web3 Builders": [
        ("💬", "General", "general"),
        ("🔗", "Smart Contracts", "smart-contracts"),
        ("🎨", "NFTs", "nfts"),
        ("💰", "DeFi", "defi"),
    ],
    "Fitness Warriors": [
        ("💬", "General", "general"),
        ("🏋️", "Workouts", "workouts"),
        ("🥗", "Nutrition", "nutrition"),
        ("🏆", "Wins", "wins"),
    ],
    "Indie Makers": [
        ("💬", "General", "general"),
        ("🚀", "Launches", "launches"),
        ("💡", "Ideas", "ideas"),
        ("📊", "Growth", "growth"),
    ],
    "Creative Writers": [
        ("💬", "General", "general"),
        ("✍️", "Short Stories", "short-stories"),
        ("📖", "Poetry", "poetry"),
        ("💭", "Feedback", "feedback"),
    ],
}

POST_TEMPLATES = [
    "Just finished {topic}! Here's what I learned: {content}",
    "Quick tip: {content}",
    "Has anyone tried {topic}? Would love to hear your thoughts.",
    "Sharing my experience with {topic}: {content}",
    "PSA: {content}",
    "Struggling with {topic}. Any advice?",
    "Amazing resource I found: {content}",
    "Week {num} update: {content}",
    "Hot take: {content}",
    "What do you think about {topic}?",
]

TOPICS = [
    "async/await patterns",
    "database optimization",
    "API design",
    "testing strategies",
    "deployment automation",
    "code review practices",
    "project architecture",
    "performance tuning",
    "security best practices",
    "CI/CD pipelines",
]


async def check_already_seeded(session: AsyncSession) -> bool:
    """Check if database is already seeded by looking for marker user."""
    result = await session.execute(select(UserModel).where(UserModel.email == SEED_MARKER_EMAIL))
    return result.scalar_one_or_none() is not None


async def create_users(
    session: AsyncSession, count: int = 20
) -> tuple[list[UserModel], list[dict]]:
    """Create users with profiles. Returns (users, credentials)."""
    print(f"Creating {count} users with profiles...")

    users = []
    credentials = []
    # First user is the seed marker
    hashed_password = password_hasher.hash(SEED_PASSWORD)

    for i in range(count):
        user_id = uuid4()
        email = SEED_MARKER_EMAIL if i == 0 else fake.email()
        display_name = fake.name()

        user = UserModel(
            id=user_id,
            email=email,
            hashed_password=hashed_password,
            is_active=True,
            is_verified=True,  # All seed users are verified
            created_at=datetime.now(UTC) - timedelta(days=random.randint(1, 365)),
        )

        profile = ProfileModel(
            user_id=user_id,
            display_name=display_name,
            bio=fake.text(max_nb_chars=200) if random.random() > 0.3 else None,
            location_city=fake.city() if random.random() > 0.5 else None,
            location_country=fake.country() if random.random() > 0.5 else None,
            avatar_url=f"https://api.dicebear.com/7.x/avataaars/svg?seed={user_id}",
            is_complete=random.random() > 0.2,  # 80% have complete profiles
            created_at=user.created_at,
        )

        session.add(user)
        session.add(profile)
        users.append(user)

        # Track credentials
        credentials.append(
            {
                "email": email,
                "password": SEED_PASSWORD,
                "display_name": display_name,
                "is_verified": True,
                "user_id": str(user_id),
            }
        )

    await session.flush()
    print(f"✅ Created {count} users")
    return users, credentials


async def create_communities(session: AsyncSession) -> list[CommunityModel]:
    """Create communities with categories."""
    print(f"Creating {len(COMMUNITY_NAMES)} communities with categories...")

    communities = []

    for name in COMMUNITY_NAMES:
        community = CommunityModel(
            id=uuid4(),
            name=name,
            slug=name.lower().replace(" ", "-"),
            description=fake.text(max_nb_chars=300),
            created_at=datetime.now(UTC) - timedelta(days=random.randint(30, 365)),
        )
        session.add(community)
        await session.flush()  # Flush to get community.id for categories

        # Create categories for this community
        for emoji, cat_name, slug in CATEGORY_DATA[name]:
            category = CategoryModel(
                id=uuid4(),
                community_id=community.id,
                name=cat_name,
                slug=slug,
                emoji=emoji,
                description=f"Discuss {cat_name.lower()} topics" if random.random() > 0.5 else None,
                created_at=community.created_at,
            )
            session.add(category)

        communities.append(community)

    await session.flush()
    print(f"✅ Created {len(communities)} communities with categories")
    return communities


async def create_memberships(
    session: AsyncSession, users: list[UserModel], communities: list[CommunityModel]
) -> dict[str, list[dict]]:
    """Create community memberships - users distributed across communities.

    Returns dict mapping user_id -> list of {community_name, role}
    """
    print("Creating community memberships...")

    membership_count = 0
    user_memberships: dict[str, list[dict]] = {}

    for community in communities:
        # First user is always admin of first community, member of others
        is_first_community = community == communities[0]

        # Pick 10-15 random members per community
        num_members = random.randint(10, 15)
        member_users = random.sample(users, num_members)

        # Ensure first user is in every community
        if users[0] not in member_users:
            member_users.append(users[0])

        for i, user in enumerate(member_users):
            # First user gets admin role in first community, member elsewhere
            if user == users[0] and is_first_community:
                role = MemberRole.ADMIN.value
            elif i == 0 and user != users[0]:
                # Each community has one other admin besides the first user
                role = MemberRole.ADMIN.value
            else:
                role = MemberRole.MEMBER.value

            membership = CommunityMemberModel(
                user_id=user.id,
                community_id=community.id,
                role=role,
                joined_at=community.created_at + timedelta(days=random.randint(0, 30)),
                is_active=True,
            )
            session.add(membership)
            membership_count += 1

            # Track for credentials file
            user_id_str = str(user.id)
            if user_id_str not in user_memberships:
                user_memberships[user_id_str] = []
            user_memberships[user_id_str].append({"community_name": community.name, "role": role})

    await session.flush()
    print(f"✅ Created {membership_count} community memberships")
    return user_memberships


async def create_posts_and_engagement(
    session: AsyncSession, communities: list[CommunityModel]
) -> None:
    """Create posts with comments and reactions for each community."""
    print("Creating posts with comments and reactions...")

    total_posts = 0
    total_comments = 0
    total_reactions = 0

    for community in communities:
        # Get community members
        result = await session.execute(
            select(CommunityMemberModel).where(CommunityMemberModel.community_id == community.id)
        )
        members = list(result.scalars().all())

        if not members:
            continue

        # Get community categories
        result = await session.execute(
            select(CategoryModel).where(CategoryModel.community_id == community.id)
        )
        categories = list(result.scalars().all())

        if not categories:
            continue

        # Create 10-20 posts per community
        num_posts = random.randint(10, 20)

        for _ in range(num_posts):
            author = random.choice(members)
            category = random.choice(categories)
            topic = random.choice(TOPICS)
            template = random.choice(POST_TEMPLATES)

            post = PostModel(
                id=uuid4(),
                community_id=community.id,
                author_id=author.user_id,
                category_id=category.id,
                title=f"{topic.title()}: {fake.sentence(nb_words=6)}",
                content=template.format(
                    topic=topic, content=fake.text(max_nb_chars=500), num=random.randint(1, 52)
                ),
                image_url=(
                    f"https://picsum.photos/seed/{uuid4()}/800/400"
                    if random.random() > 0.7
                    else None
                ),
                is_pinned=random.random() > 0.95,  # 5% pinned
                pinned_at=(
                    datetime.now(UTC) - timedelta(days=random.randint(1, 7))
                    if random.random() > 0.95
                    else None
                ),
                is_locked=False,
                is_deleted=False,
                created_at=community.created_at + timedelta(days=random.randint(1, 60)),
            )
            session.add(post)
            await session.flush()  # Get post.id for comments/reactions
            total_posts += 1

            # Create 0-10 comments per post
            num_comments = random.randint(0, 10)
            post_comments = []

            for _ in range(num_comments):
                commenter = random.choice(members)
                # 20% chance of being a reply to existing comment
                parent_comment = (
                    random.choice(post_comments)
                    if post_comments and random.random() > 0.8
                    else None
                )

                comment = CommentModel(
                    id=uuid4(),
                    post_id=post.id,
                    author_id=commenter.user_id,
                    parent_comment_id=parent_comment.id if parent_comment else None,
                    content=fake.text(max_nb_chars=200),
                    is_deleted=False,
                    created_at=post.created_at + timedelta(hours=random.randint(1, 48)),
                )
                session.add(comment)
                post_comments.append(comment)
                total_comments += 1

            await session.flush()  # Get comment IDs for reactions

            # Create reactions on post (30-70% of members react)
            num_post_reactions = random.randint(int(len(members) * 0.3), int(len(members) * 0.7))
            post_reactors = random.sample(members, min(num_post_reactions, len(members)))

            for reactor in post_reactors:
                reaction = ReactionModel(
                    id=uuid4(),
                    user_id=reactor.user_id,
                    target_type="post",
                    target_id=post.id,
                    created_at=post.created_at + timedelta(hours=random.randint(1, 72)),
                )
                session.add(reaction)
                total_reactions += 1

            # Create reactions on comments (10-30% of members react)
            for comment in post_comments:
                num_comment_reactions = random.randint(
                    int(len(members) * 0.1), int(len(members) * 0.3)
                )
                comment_reactors = random.sample(members, min(num_comment_reactions, len(members)))

                for reactor in comment_reactors:
                    reaction = ReactionModel(
                        id=uuid4(),
                        user_id=reactor.user_id,
                        target_type="comment",
                        target_id=comment.id,
                        created_at=comment.created_at + timedelta(hours=random.randint(1, 24)),
                    )
                    session.add(reaction)
                    total_reactions += 1

    await session.flush()
    print(f"✅ Created {total_posts} posts, {total_comments} comments, {total_reactions} reactions")


async def table_exists(session: AsyncSession, table_name: str) -> bool:
    """Check if a table exists in the database."""
    result = await session.execute(
        text(
            "SELECT EXISTS (SELECT FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_name = :table_name)"
        ),
        {"table_name": table_name},
    )
    return result.scalar()


async def create_courses(session: AsyncSession, users: list[UserModel]) -> None:
    """Create courses with modules and lessons (if tables exist)."""
    print("Creating courses...")

    # Check if classroom tables exist
    courses_exist = await table_exists(session, "courses")
    modules_exist = await table_exists(session, "modules")
    lessons_exist = await table_exists(session, "lessons")

    if not courses_exist:
        print("⚠️  Courses table doesn't exist, skipping classroom seeding")
        return

    # Create 3-5 courses
    num_courses = random.randint(3, 5)
    total_modules = 0
    total_lessons = 0

    course_topics = [
        ("Python Fundamentals", "Learn Python from scratch"),
        ("Web Development Bootcamp", "Build modern web applications"),
        ("Data Structures & Algorithms", "Master CS fundamentals"),
        ("Machine Learning Basics", "Introduction to ML concepts"),
        ("FastAPI Masterclass", "Build production-ready APIs"),
        ("React Deep Dive", "Modern React patterns and hooks"),
    ]

    for _ in range(num_courses):
        instructor = random.choice(users[:5])  # Pick from first 5 users as instructors
        title, description = random.choice(course_topics)

        course = CourseModel(
            id=uuid4(),
            instructor_id=instructor.id,
            title=title,
            description=description,
            cover_image_url=f"https://picsum.photos/seed/{uuid4()}/800/400",
            estimated_duration=f"{random.randint(4, 20)} hours",
            is_deleted=False,
            created_at=datetime.now(UTC) - timedelta(days=random.randint(30, 180)),
        )
        session.add(course)
        await session.flush()

        # Only create modules/lessons if tables exist
        if modules_exist and lessons_exist:
            # Create 3-6 modules per course
            num_modules = random.randint(3, 6)

            for module_pos in range(1, num_modules + 1):
                module = ModuleModel(
                    id=uuid4(),
                    course_id=course.id,
                    title=f"Module {module_pos}: {fake.sentence(nb_words=4)}",
                    description=fake.text(max_nb_chars=200),
                    position=module_pos,
                    is_deleted=False,
                    created_at=course.created_at,
                )
                session.add(module)
                await session.flush()
                total_modules += 1

                # Create 4-8 lessons per module
                num_lessons = random.randint(4, 8)

                for lesson_pos in range(1, num_lessons + 1):
                    lesson_types = ["video", "text", "quiz"]
                    content_type = random.choice(lesson_types)

                    if content_type == "video":
                        content = f"https://www.youtube.com/watch?v={fake.lexify('???????????')}"
                    elif content_type == "text":
                        content = fake.text(max_nb_chars=1000)
                    else:  # quiz
                        content = fake.text(max_nb_chars=300)

                    lesson = LessonModel(
                        id=uuid4(),
                        module_id=module.id,
                        title=f"Lesson {lesson_pos}: {fake.sentence(nb_words=5)}",
                        content_type=content_type,
                        content=content,
                        position=lesson_pos,
                        is_deleted=False,
                        created_at=module.created_at,
                    )
                    session.add(lesson)
                    total_lessons += 1

    await session.flush()

    if modules_exist and lessons_exist:
        print(f"✅ Created {num_courses} courses, {total_modules} modules, {total_lessons} lessons")
    else:
        print(f"✅ Created {num_courses} courses (modules/lessons tables don't exist yet, skipped)")


def write_credentials_files(credentials: list[dict], memberships: dict) -> None:
    """Write credentials to JSON and TXT files for local reference."""
    # Enhance credentials with community memberships
    enhanced_credentials = []
    for cred in credentials:
        user_id = cred["user_id"]
        user_memberships = memberships.get(user_id, [])

        enhanced_cred = {
            **cred,
            "communities": [
                {"name": m["community_name"], "role": m["role"]} for m in user_memberships
            ],
        }
        enhanced_credentials.append(enhanced_cred)

    # Write JSON file
    with open(CREDENTIALS_FILE, "w") as f:
        json.dump(
            {
                "generated_at": datetime.now(UTC).isoformat(),
                "password": SEED_PASSWORD,
                "note": "⚠️  DEVELOPMENT ONLY - All users share the same password",
                "users": enhanced_credentials,
            },
            f,
            indent=2,
        )

    # Write human-readable TXT file
    with open(CREDENTIALS_TXT_FILE, "w") as f:
        f.write("=" * 80 + "\n")
        f.write("KOULU - SEEDED USER CREDENTIALS (DEVELOPMENT ONLY)\n")
        f.write("=" * 80 + "\n\n")
        f.write("⚠️  WARNING: All users share the same password for development convenience\n")
        f.write(f"Password: {SEED_PASSWORD}\n\n")
        f.write(f"Generated: {datetime.now(UTC).strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
        f.write("=" * 80 + "\n\n")

        for i, cred in enumerate(enhanced_credentials, 1):
            f.write(f"{i}. {cred['display_name']}\n")
            f.write(f"   Email: {cred['email']}\n")
            f.write(f"   User ID: {cred['user_id']}\n")

            if cred["communities"]:
                f.write("   Communities:\n")
                for membership in cred["communities"]:
                    role_badge = "👑" if membership["role"].upper() == "ADMIN" else "👤"
                    f.write(f"      {role_badge} {membership['name']} ({membership['role']})\n")
            else:
                f.write("   Communities: None\n")

            f.write("\n")

        f.write("=" * 80 + "\n")
        f.write(f"Total users: {len(enhanced_credentials)}\n")
        f.write("=" * 80 + "\n")

    print(f"\n📝 Credentials saved to:")
    print(f"   - {CREDENTIALS_FILE} (JSON)")
    print(f"   - {CREDENTIALS_TXT_FILE} (human-readable)")


async def seed_database() -> None:
    """Main seeding function."""
    # Load DATABASE_URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        return

    print("🌱 Starting database seeding...")
    print(f"📦 Database: {database_url.split('@')[-1]}")  # Hide credentials

    # Create database connection
    db = Database(database_url, echo=False)

    try:
        async with db.session() as session:
            # Check if already seeded
            if await check_already_seeded(session):
                print("⚠️  Database already seeded (marker user exists)")
                print("   To re-seed, manually delete data or drop/recreate the database")
                return

            # Create all seed data
            users, credentials = await create_users(session, count=20)
            communities = await create_communities(session)
            memberships = await create_memberships(session, users, communities)
            await create_posts_and_engagement(session, communities)
            await create_courses(session, users)

            # Commit all changes
            await session.commit()

            print("\n✅ Database seeding completed successfully!")
            print("\n📊 Summary:")
            print(f"   - {len(users)} users with profiles")
            print(f"   - {len(communities)} communities with categories")
            print("   - Posts with comments and reactions")
            print("   - Courses with modules and lessons")

            # Write credentials files
            write_credentials_files(credentials, memberships)

            print("\n🔑 Quick test login:")
            print(f"   Email: {SEED_MARKER_EMAIL}")
            print(f"   Password: {SEED_PASSWORD}")

    finally:
        await db.close()


if __name__ == "__main__":
    asyncio.run(seed_database())
