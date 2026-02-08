# Database Seeding Guide

## Overview

The `seed_db.py` script populates your development database with realistic test data for all existing tables in the Koulu application.

## What Gets Seeded

### Identity Context
- **20 users** with complete profiles (verified accounts)
- User profiles with display names, bios, locations, avatars
- All users use password: `Password123!`

### Community Context
- **5 communities** with realistic names and descriptions:
  - Python Mastery
  - Web3 Builders
  - Fitness Warriors
  - Indie Makers
  - Creative Writers
- **4 categories per community** (General, topic-specific categories)
- **Community memberships** (10-15 members per community)
- **10-20 posts per community** with varied content
- **Comments** (0-10 per post, including threaded replies)
- **Reactions** on posts and comments

### Classroom Context
- **3-5 courses** with instructors
- **Modules and lessons** (if tables exist - currently pending migrations)

## Usage

### Running the Seed Script

```bash
# Make sure database is running
docker compose up -d postgres

# Run migrations first
set -a && source .env && set +a && alembic upgrade head

# Seed the database
python scripts/seed_db.py
```

Or use the shorthand:

```bash
set -a && source .env && set +a && python scripts/seed_db.py
```

### Idempotency

The script is **idempotent** - it checks for a marker user (`seed.marker@koulu.dev`) before seeding:

- ✅ **First run**: Creates all seed data
- ⚠️ **Subsequent runs**: Skips seeding (warns that data already exists)

### Re-seeding

To re-seed the database:

```bash
# Option 1: Drop and recreate the database
docker compose down -v
docker compose up -d postgres
alembic upgrade head
python scripts/seed_db.py

# Option 2: Manual cleanup
# Delete the marker user and related data via SQL
```

## Test Credentials

After seeding, credentials for all users are saved to **local files** (not tracked by git):

### Credentials Files

1. **`scripts/.seed-credentials.json`** - Machine-readable JSON format
   - Contains all user data including communities and roles
   - Useful for automated testing or scripting

2. **`scripts/.seed-credentials.txt`** - Human-readable text format
   - Formatted list of all users with their communities
   - Shows admin badges (👑) and member badges (👤)
   - Easy to reference during development

**⚠️ These files are automatically gitignored and will never be committed to the repository.**

### Quick Test Login

```
Email: seed.marker@koulu.dev
Password: Password123!
```

This user is:
- Admin of the first community (Python Mastery)
- Member of all other communities
- Has a complete profile

**Note**: All 20 seeded users share the same password (`Password123!`) for development convenience.

## Data Characteristics

### Realistic Data
- Names, emails, bios generated with Faker
- Varied post content using templates and topics
- Random timestamps (created in the past 1-365 days)
- Distributed engagement (comments, reactions)

### Community Distribution
- Each community has 10-15 members (random selection from 20 users)
- One admin per community (plus the marker user as global admin)
- Posts authored by different community members
- Comments can be top-level or threaded replies

### Engagement Patterns
- 30-70% of members react to posts
- 10-30% of members react to comments
- 0-10 comments per post
- 5% of posts are pinned

## Adding New Tables

When new features are added with new database tables:

1. **Create migrations** for the new tables
2. **Update `scripts/seed_db.py`**:
   - Import the new models
   - Create a seed function (e.g., `async def create_feature_data()`)
   - Add table existence check if optional
   - Call the function in `seed_database()`
3. **Use the `table_exists()` helper** for optional tables
4. **Follow existing patterns**:
   - Realistic data with Faker
   - Maintain referential integrity
   - Add to summary output

### Example: Adding Calendar Events

```python
async def create_events(session: AsyncSession, communities: list[CommunityModel]) -> None:
    """Create calendar events."""
    if not await table_exists(session, "events"):
        print("⚠️  Events table doesn't exist, skipping")
        return

    print("Creating calendar events...")

    for community in communities:
        # Create 3-5 events per community
        for _ in range(random.randint(3, 5)):
            event = EventModel(
                id=uuid4(),
                community_id=community.id,
                title=fake.sentence(),
                # ... more fields
            )
            session.add(event)

    await session.flush()
    print("✅ Created events")

# Then call it in seed_database():
async def seed_database() -> None:
    # ... existing code ...
    await create_events(session, communities)
    # ... rest of code ...
```

## Troubleshooting

### "relation does not exist" error
**Cause**: Migrations haven't been run for that table
**Fix**: Run `alembic upgrade head` or remove seeding for that table

### "Database already seeded" when you want fresh data
**Cause**: Marker user exists
**Fix**: Drop and recreate the database, or delete the marker user

### No output / hangs
**Cause**: Database not running or DATABASE_URL not set
**Fix**:
- Start database: `docker compose up -d postgres`
- Load .env: `set -a && source .env && set +a`

## Architecture Notes

- **Direct ORM inserts**: Bypasses domain layer for speed (domain logic is tested elsewhere)
- **Async SQLAlchemy**: Uses async/await for database operations
- **Transaction safety**: All operations in a single transaction (rollback on error)
- **Flush strategy**: Strategic `flush()` calls to get generated IDs for foreign keys
