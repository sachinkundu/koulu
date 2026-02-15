# Points & Levels Phase 1 — Task Plan

> **For Claude:** Use `/implement-feature gamification/points --phase=1` to execute this plan.

**Phase goal:** Members earn points from engagement actions and automatically level up through a 9-level progression. Level badges appear on avatars.
**Files to create/modify:** ~30
**BDD scenarios to enable:** 15
**Estimated time:** 4-5 hours
**Task count:** 18

---

### Dependency Graph

```
Task 1 (Value Objects + Exceptions) ─────┬──► Task 2 (PointTransaction)
           │                              ├──► Task 3 (Domain Events)
           │                              ├──► Task 4 (LevelConfiguration)
           │                              │         │
           │                              │         ▼
           │                              └──► Task 5 (MemberPoints) ◄── Task 2, 3, 4
           │                                        │
           │                                        ▼
           │                                  Task 6 (Repo Interfaces)
           │                                        │
           ▼                                        │
Task 8 (Models + Migration) ────────────────────────┤
           │                                        │
           ▼                                        ▼
Task 9 (Repo Implementations) ◄──────────── Task 6, Task 8
           │
           ▼
Task 10 (Award+Deduct Handlers) ◄── Task 5, 6
Task 11 (GetMemberLevel Query) ◄── Task 6
           │           │
           ▼           │
Task 12 (Event Handlers) ◄── Task 7 (Community Enrichment, independent)
           │           │
           ▼           ▼
Task 13 (API Routes + Schemas)
           │
           ▼
Task 14 (App Wiring)

Task 15 (TS Types + API) ──► Task 16 (LevelBadge) ──► Task 17 (Avatar Enhancement)

Task 18 (BDD + Verification) ◄── ALL TASKS
```

### Parallel Execution Summary

| Batch | Tasks | Mode | Rationale |
|-------|-------|------|-----------|
| 1 | Task 1, Task 7, Task 15, Task 16 | Parallel | Independent foundations (backend VOs, community enrichment, frontend types, LevelBadge) |
| 2 | Task 2, Task 3, Task 4, Task 8, Task 17 | Parallel | Task 2-4 depend on Task 1; Task 8 depends on Task 1; Task 17 depends on Task 16 |
| 3 | Task 5 | Sequential | Depends on Tasks 1-4 |
| 4 | Task 6 | Sequential | Depends on Tasks 4, 5 |
| 5 | Task 9, Task 10, Task 11 | Parallel | Task 9 depends on 6+8; Tasks 10-11 depend on 5+6 |
| 6 | Task 12 | Sequential | Depends on Tasks 7, 10 |
| 7 | Task 13 | Sequential | Depends on Tasks 10, 11 |
| 8 | Task 14 | Sequential | Depends on Tasks 12, 13 |
| 9 | Task 18 | Sequential | Final verification, depends on all |

**Sequential execution:** 18 tasks
**Parallel execution:** 9 batches (estimated ~40% time savings)

### Agent Execution Plan

> Used by `/implement-phase-team` to assign tasks to team agents.

| Agent | Tasks | Starts | Blocked Until |
|-------|-------|--------|---------------|
| backend | Task 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14 | Immediately | — |
| frontend | Task 15, 16, 17 | Immediately | — |
| testing | Task 18 | After backend + frontend | All implementation tasks complete |

**File ownership boundaries (no overlap allowed):**
- `backend` owns: `src/gamification/`, `src/community/domain/events.py` (enrichment), `tests/unit/gamification/`, `alembic/versions/`
- `frontend` owns: `frontend/src/features/gamification/`, `frontend/src/components/Avatar.tsx`
- `testing` owns: `tests/features/gamification/`

---

### Task 1: Value Objects + Domain Exceptions

**Owner:** backend
**Depends on:** none

**Files:**
- Create: `src/gamification/__init__.py`
- Create: `src/gamification/domain/__init__.py`
- Create: `src/gamification/domain/value_objects/__init__.py`
- Create: `src/gamification/domain/value_objects/point_source.py`
- Create: `src/gamification/domain/value_objects/level_number.py`
- Create: `src/gamification/domain/value_objects/level_name.py`
- Create: `src/gamification/domain/exceptions.py`
- Test: `tests/unit/gamification/__init__.py`
- Test: `tests/unit/gamification/domain/__init__.py`
- Test: `tests/unit/gamification/domain/test_value_objects.py`

**Step 1: Write the failing tests**

```python
# tests/unit/gamification/domain/test_value_objects.py
"""Tests for gamification value objects."""

import pytest

from src.gamification.domain.exceptions import (
    GamificationDomainError,
    InvalidLevelNameError,
    InvalidLevelNumberError,
)
from src.gamification.domain.value_objects.level_name import LevelName
from src.gamification.domain.value_objects.level_number import LevelNumber
from src.gamification.domain.value_objects.point_source import PointSource


class TestPointSource:
    """Tests for PointSource enum."""

    def test_post_created_awards_2_points(self) -> None:
        assert PointSource.POST_CREATED.points == 2

    def test_comment_created_awards_1_point(self) -> None:
        assert PointSource.COMMENT_CREATED.points == 1

    def test_post_liked_awards_1_point(self) -> None:
        assert PointSource.POST_LIKED.points == 1

    def test_comment_liked_awards_1_point(self) -> None:
        assert PointSource.COMMENT_LIKED.points == 1

    def test_lesson_completed_awards_5_points(self) -> None:
        assert PointSource.LESSON_COMPLETED.points == 5


class TestLevelNumber:
    """Tests for LevelNumber value object."""

    def test_valid_level_1(self) -> None:
        level = LevelNumber(1)
        assert level.value == 1

    def test_valid_level_9(self) -> None:
        level = LevelNumber(9)
        assert level.value == 9

    def test_level_0_raises(self) -> None:
        with pytest.raises(InvalidLevelNumberError):
            LevelNumber(0)

    def test_level_10_raises(self) -> None:
        with pytest.raises(InvalidLevelNumberError):
            LevelNumber(10)

    def test_negative_level_raises(self) -> None:
        with pytest.raises(InvalidLevelNumberError):
            LevelNumber(-1)


class TestLevelName:
    """Tests for LevelName value object."""

    def test_valid_name(self) -> None:
        name = LevelName("Student")
        assert name.value == "Student"

    def test_empty_name_raises(self) -> None:
        with pytest.raises(InvalidLevelNameError, match="required"):
            LevelName("")

    def test_name_too_long_raises(self) -> None:
        with pytest.raises(InvalidLevelNameError, match="30 characters"):
            LevelName("A" * 31)

    def test_html_stripped(self) -> None:
        name = LevelName("<script>alert('xss')</script>Beginner")
        assert "<script>" not in name.value
        assert "Beginner" in name.value

    def test_whitespace_only_raises(self) -> None:
        with pytest.raises(InvalidLevelNameError, match="required"):
            LevelName("   ")
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/unit/gamification/domain/test_value_objects.py -v`
Expected: FAIL (modules not found)

**Step 3: Write minimal implementation**

`src/gamification/domain/exceptions.py`:
```python
"""Gamification domain exceptions."""


class GamificationDomainError(Exception):
    """Base exception for all gamification domain errors."""


class InvalidLevelNumberError(GamificationDomainError):
    """Raised when level number is not 1-9."""

    def __init__(self, value: int) -> None:
        super().__init__(f"Level number must be between 1 and 9, got {value}")
        self.value = value


class InvalidLevelNameError(GamificationDomainError):
    """Raised when level name is invalid."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)


class InvalidThresholdError(GamificationDomainError):
    """Raised when point thresholds are invalid."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)


class DuplicateLessonCompletionError(GamificationDomainError):
    """Raised when lesson completion points already awarded."""

    def __init__(self, lesson_id: str) -> None:
        super().__init__(f"Points already awarded for lesson: {lesson_id}")
        self.lesson_id = lesson_id
```

`src/gamification/domain/value_objects/point_source.py`:
```python
"""PointSource enum — defines engagement actions and their point values."""

from enum import Enum


class PointSource(Enum):
    """Engagement actions that award points."""

    POST_CREATED = ("post_created", 2)
    COMMENT_CREATED = ("comment_created", 1)
    POST_LIKED = ("post_liked", 1)
    COMMENT_LIKED = ("comment_liked", 1)
    LESSON_COMPLETED = ("lesson_completed", 5)

    def __init__(self, source_name: str, points: int) -> None:
        self.source_name = source_name
        self._points = points

    @property
    def points(self) -> int:
        return self._points
```

`src/gamification/domain/value_objects/level_number.py`:
```python
"""LevelNumber value object."""

from dataclasses import dataclass

from src.gamification.domain.exceptions import InvalidLevelNumberError
from src.shared.domain.base_value_object import BaseValueObject


@dataclass(frozen=True)
class LevelNumber(BaseValueObject):
    """Level number (1-9)."""

    value: int

    def _validate(self) -> None:
        if not isinstance(self.value, int) or self.value < 1 or self.value > 9:
            raise InvalidLevelNumberError(self.value)
```

`src/gamification/domain/value_objects/level_name.py`:
```python
"""LevelName value object."""

from dataclasses import dataclass

import bleach

from src.gamification.domain.exceptions import InvalidLevelNameError
from src.shared.domain.base_value_object import BaseValueObject

MAX_LEVEL_NAME_LENGTH = 30


@dataclass(frozen=True)
class LevelName(BaseValueObject):
    """Level name (1-30 chars, sanitized)."""

    value: str

    def _validate(self) -> None:
        sanitized = bleach.clean(self.value, tags=[], strip=True).strip()
        object.__setattr__(self, "value", sanitized)

        if not sanitized:
            raise InvalidLevelNameError("Level name is required")

        if len(sanitized) > MAX_LEVEL_NAME_LENGTH:
            raise InvalidLevelNameError(
                f"Level name must be {MAX_LEVEL_NAME_LENGTH} characters or less"
            )
```

`src/gamification/domain/value_objects/__init__.py`:
```python
"""Gamification domain value objects."""

from src.gamification.domain.value_objects.level_name import LevelName
from src.gamification.domain.value_objects.level_number import LevelNumber
from src.gamification.domain.value_objects.point_source import PointSource

__all__ = ["LevelName", "LevelNumber", "PointSource"]
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/unit/gamification/domain/test_value_objects.py -v`
Expected: PASS (all tests)

**Step 5: Commit**

```bash
git add src/gamification/__init__.py src/gamification/domain/__init__.py \
  src/gamification/domain/value_objects/ src/gamification/domain/exceptions.py \
  tests/unit/gamification/
git commit -m "feat(gamification): add value objects (PointSource, LevelNumber, LevelName) and domain exceptions"
```

---

### Task 2: PointTransaction Value Object

**Owner:** backend
**Depends on:** Task 1

**Files:**
- Create: `src/gamification/domain/value_objects/point_transaction.py`
- Modify: `src/gamification/domain/value_objects/__init__.py`
- Test: `tests/unit/gamification/domain/test_point_transaction.py`

**Step 1: Write the failing tests**

```python
# tests/unit/gamification/domain/test_point_transaction.py
"""Tests for PointTransaction value object."""

from uuid import uuid4

from src.gamification.domain.value_objects.point_source import PointSource
from src.gamification.domain.value_objects.point_transaction import PointTransaction


class TestPointTransaction:
    """Tests for PointTransaction value object."""

    def test_create_award_transaction(self) -> None:
        source_id = uuid4()
        txn = PointTransaction(
            points=2,
            source=PointSource.POST_CREATED,
            source_id=source_id,
        )
        assert txn.points == 2
        assert txn.source == PointSource.POST_CREATED
        assert txn.source_id == source_id
        assert txn.created_at is not None

    def test_create_deduction_transaction(self) -> None:
        txn = PointTransaction(
            points=-1,
            source=PointSource.POST_LIKED,
            source_id=uuid4(),
        )
        assert txn.points == -1

    def test_immutable(self) -> None:
        txn = PointTransaction(
            points=1,
            source=PointSource.COMMENT_CREATED,
            source_id=uuid4(),
        )
        import pytest
        with pytest.raises(AttributeError):
            txn.points = 5  # type: ignore[misc]
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/unit/gamification/domain/test_point_transaction.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

`src/gamification/domain/value_objects/point_transaction.py`:
```python
"""PointTransaction value object."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID

from src.gamification.domain.value_objects.point_source import PointSource


@dataclass(frozen=True)
class PointTransaction:
    """Represents a single point change (positive or negative)."""

    points: int
    source: PointSource
    source_id: UUID
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
```

Update `__init__.py` to export `PointTransaction`.

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/unit/gamification/domain/test_point_transaction.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/gamification/domain/value_objects/point_transaction.py \
  src/gamification/domain/value_objects/__init__.py \
  tests/unit/gamification/domain/test_point_transaction.py
git commit -m "feat(gamification): add PointTransaction value object"
```

---

### Task 3: Domain Events

**Owner:** backend
**Depends on:** Task 1

**Files:**
- Create: `src/gamification/domain/events/__init__.py`
- Create: `src/gamification/domain/events/gamification_events.py`
- Test: `tests/unit/gamification/domain/test_events.py`

**Step 1: Write the failing tests**

```python
# tests/unit/gamification/domain/test_events.py
"""Tests for gamification domain events."""

from uuid import uuid4

from src.gamification.domain.events.gamification_events import (
    MemberLeveledUp,
    PointsAwarded,
    PointsDeducted,
)
from src.shared.domain.base_event import DomainEvent


class TestPointsAwarded:
    def test_is_domain_event(self) -> None:
        event = PointsAwarded(
            member_id=uuid4(),
            community_id=uuid4(),
            points=2,
            new_total=12,
            source="post_created",
        )
        assert isinstance(event, DomainEvent)

    def test_event_type(self) -> None:
        event = PointsAwarded(
            member_id=uuid4(), community_id=uuid4(),
            points=1, new_total=5, source="post_liked",
        )
        assert event.event_type == "PointsAwarded"


class TestPointsDeducted:
    def test_event_type(self) -> None:
        event = PointsDeducted(
            member_id=uuid4(), community_id=uuid4(),
            points=1, new_total=4, source="post_liked",
        )
        assert event.event_type == "PointsDeducted"


class TestMemberLeveledUp:
    def test_event_type(self) -> None:
        event = MemberLeveledUp(
            member_id=uuid4(), community_id=uuid4(),
            old_level=1, new_level=2, new_level_name="Practitioner",
        )
        assert event.event_type == "MemberLeveledUp"
        assert event.old_level == 1
        assert event.new_level == 2
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/unit/gamification/domain/test_events.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

`src/gamification/domain/events/gamification_events.py`:
```python
"""Gamification domain events."""

from dataclasses import dataclass
from uuid import UUID

from src.shared.domain.base_event import DomainEvent


@dataclass(frozen=True)
class PointsAwarded(DomainEvent):
    """Published when points are awarded to a member."""

    member_id: UUID
    community_id: UUID
    points: int
    new_total: int
    source: str

    @property
    def event_type(self) -> str:
        return "PointsAwarded"


@dataclass(frozen=True)
class PointsDeducted(DomainEvent):
    """Published when points are deducted from a member."""

    member_id: UUID
    community_id: UUID
    points: int
    new_total: int
    source: str

    @property
    def event_type(self) -> str:
        return "PointsDeducted"


@dataclass(frozen=True)
class MemberLeveledUp(DomainEvent):
    """Published when a member reaches a new level."""

    member_id: UUID
    community_id: UUID
    old_level: int
    new_level: int
    new_level_name: str

    @property
    def event_type(self) -> str:
        return "MemberLeveledUp"
```

`src/gamification/domain/events/__init__.py`:
```python
"""Gamification domain events."""

from src.gamification.domain.events.gamification_events import (
    MemberLeveledUp,
    PointsAwarded,
    PointsDeducted,
)

__all__ = ["MemberLeveledUp", "PointsAwarded", "PointsDeducted"]
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/unit/gamification/domain/test_events.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/gamification/domain/events/ tests/unit/gamification/domain/test_events.py
git commit -m "feat(gamification): add domain events (PointsAwarded, PointsDeducted, MemberLeveledUp)"
```

---

### Task 4: LevelConfiguration Entity

**Owner:** backend
**Depends on:** Task 1

**Files:**
- Create: `src/gamification/domain/entities/__init__.py`
- Create: `src/gamification/domain/entities/level_configuration.py`
- Test: `tests/unit/gamification/domain/test_level_configuration.py`

**Step 1: Write the failing tests**

```python
# tests/unit/gamification/domain/test_level_configuration.py
"""Tests for LevelConfiguration entity."""

import pytest
from uuid import uuid4

from src.gamification.domain.entities.level_configuration import LevelConfiguration


class TestLevelConfigurationDefaults:
    """Tests for default level configuration."""

    def test_create_default_has_9_levels(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        assert len(config.levels) == 9

    def test_default_level_1_is_student_at_0(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        assert config.levels[0].name == "Student"
        assert config.levels[0].threshold == 0

    def test_default_level_9_is_icon_at_360(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        assert config.levels[8].name == "Icon"
        assert config.levels[8].threshold == 360


class TestGetLevelForPoints:
    """Tests for level calculation from points."""

    def test_zero_points_is_level_1(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        assert config.get_level_for_points(0) == 1

    def test_exactly_at_threshold_is_that_level(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        assert config.get_level_for_points(10) == 2

    def test_one_below_threshold_stays_at_lower_level(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        assert config.get_level_for_points(9) == 1

    def test_high_points_is_level_9(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        assert config.get_level_for_points(500) == 9

    def test_mid_range_points(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        assert config.get_level_for_points(45) == 3  # threshold for 3 is 30, for 4 is 60


class TestThresholdForLevel:
    """Tests for getting threshold of a specific level."""

    def test_threshold_for_level_1_is_0(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        assert config.threshold_for_level(1) == 0

    def test_threshold_for_level_2_is_10(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        assert config.threshold_for_level(2) == 10

    def test_threshold_for_level_9_is_360(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        assert config.threshold_for_level(9) == 360


class TestPointsToNextLevel:
    """Tests for points-to-next-level calculation."""

    def test_level_1_with_0_points(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        assert config.points_to_next_level(current_level=1, total_points=0) == 10

    def test_level_2_with_15_points(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        assert config.points_to_next_level(current_level=2, total_points=15) == 15

    def test_level_9_returns_none(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        assert config.points_to_next_level(current_level=9, total_points=400) is None
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/unit/gamification/domain/test_level_configuration.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

`src/gamification/domain/entities/level_configuration.py`:
```python
"""LevelConfiguration aggregate root."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from src.shared.domain.base_entity import BaseEntity


@dataclass
class LevelDefinition:
    """A single level's configuration."""

    level: int
    name: str
    threshold: int


DEFAULT_LEVELS = [
    LevelDefinition(level=1, name="Student", threshold=0),
    LevelDefinition(level=2, name="Practitioner", threshold=10),
    LevelDefinition(level=3, name="Builder", threshold=30),
    LevelDefinition(level=4, name="Leader", threshold=60),
    LevelDefinition(level=5, name="Mentor", threshold=100),
    LevelDefinition(level=6, name="Empire Builder", threshold=150),
    LevelDefinition(level=7, name="Ruler", threshold=210),
    LevelDefinition(level=8, name="Legend", threshold=280),
    LevelDefinition(level=9, name="Icon", threshold=360),
]


@dataclass
class LevelConfiguration(BaseEntity[UUID]):
    """Per-community level configuration (9 levels)."""

    community_id: UUID
    levels: list[LevelDefinition] = field(default_factory=list)

    @classmethod
    def create_default(cls, community_id: UUID) -> LevelConfiguration:
        """Create a default configuration with standard levels."""
        return cls(
            id=uuid4(),
            community_id=community_id,
            levels=[
                LevelDefinition(level=ld.level, name=ld.name, threshold=ld.threshold)
                for ld in DEFAULT_LEVELS
            ],
        )

    def get_level_for_points(self, points: int) -> int:
        """Return the level number for a given point total."""
        current_level = 1
        for ld in self.levels:
            if points >= ld.threshold:
                current_level = ld.level
        return current_level

    def threshold_for_level(self, level: int) -> int:
        """Return the point threshold for a given level number."""
        for ld in self.levels:
            if ld.level == level:
                return ld.threshold
        raise ValueError(f"Invalid level: {level}")

    def name_for_level(self, level: int) -> str:
        """Return the name for a given level number."""
        for ld in self.levels:
            if ld.level == level:
                return ld.name
        raise ValueError(f"Invalid level: {level}")

    def points_to_next_level(self, current_level: int, total_points: int) -> int | None:
        """Return points needed to reach the next level, or None if max."""
        if current_level >= 9:
            return None
        next_threshold = self.threshold_for_level(current_level + 1)
        return max(0, next_threshold - total_points)
```

`src/gamification/domain/entities/__init__.py`:
```python
"""Gamification domain entities."""

from src.gamification.domain.entities.level_configuration import (
    LevelConfiguration,
    LevelDefinition,
)

__all__ = ["LevelConfiguration", "LevelDefinition"]
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/unit/gamification/domain/test_level_configuration.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/gamification/domain/entities/ tests/unit/gamification/domain/test_level_configuration.py
git commit -m "feat(gamification): add LevelConfiguration entity with defaults and level calculation"
```

---

### Task 5: MemberPoints Aggregate

**Owner:** backend
**Depends on:** Task 1, Task 2, Task 3, Task 4

**Files:**
- Create: `src/gamification/domain/entities/member_points.py`
- Modify: `src/gamification/domain/entities/__init__.py`
- Test: `tests/unit/gamification/domain/test_member_points.py`

**Step 1: Write the failing tests**

```python
# tests/unit/gamification/domain/test_member_points.py
"""Tests for MemberPoints aggregate root."""

import pytest
from uuid import uuid4

from src.gamification.domain.entities.level_configuration import LevelConfiguration
from src.gamification.domain.entities.member_points import MemberPoints
from src.gamification.domain.events.gamification_events import (
    MemberLeveledUp,
    PointsAwarded,
    PointsDeducted,
)
from src.gamification.domain.exceptions import DuplicateLessonCompletionError
from src.gamification.domain.value_objects.point_source import PointSource


class TestMemberPointsCreation:
    def test_create_starts_at_level_1_with_0_points(self) -> None:
        mp = MemberPoints.create(community_id=uuid4(), user_id=uuid4())
        assert mp.total_points == 0
        assert mp.current_level == 1

    def test_create_has_no_transactions(self) -> None:
        mp = MemberPoints.create(community_id=uuid4(), user_id=uuid4())
        assert len(mp.transactions) == 0


class TestAwardPoints:
    def test_award_increases_total(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        mp = MemberPoints.create(community_id=config.community_id, user_id=uuid4())
        mp.award_points(
            source=PointSource.POST_CREATED,
            source_id=uuid4(),
            level_config=config,
        )
        assert mp.total_points == 2

    def test_award_creates_transaction(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        mp = MemberPoints.create(community_id=config.community_id, user_id=uuid4())
        mp.award_points(
            source=PointSource.POST_LIKED,
            source_id=uuid4(),
            level_config=config,
        )
        assert len(mp.transactions) == 1
        assert mp.transactions[0].points == 1

    def test_award_publishes_points_awarded_event(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        mp = MemberPoints.create(community_id=config.community_id, user_id=uuid4())
        mp.award_points(
            source=PointSource.POST_CREATED,
            source_id=uuid4(),
            level_config=config,
        )
        events = [e for e in mp.events if isinstance(e, PointsAwarded)]
        assert len(events) == 1
        assert events[0].points == 2
        assert events[0].new_total == 2


class TestLevelUp:
    def test_level_up_when_threshold_reached(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        mp = MemberPoints.create(community_id=config.community_id, user_id=uuid4())
        # Award enough to reach level 2 (threshold=10): 5 lessons = 25 points
        for _ in range(2):
            mp.award_points(
                source=PointSource.LESSON_COMPLETED,
                source_id=uuid4(),
                level_config=config,
            )
        assert mp.current_level == 2
        assert mp.total_points == 10

    def test_level_up_publishes_event(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        mp = MemberPoints.create(community_id=config.community_id, user_id=uuid4())
        for _ in range(2):
            mp.award_points(
                source=PointSource.LESSON_COMPLETED,
                source_id=uuid4(),
                level_config=config,
            )
        level_events = [e for e in mp.events if isinstance(e, MemberLeveledUp)]
        assert len(level_events) == 1
        assert level_events[0].old_level == 1
        assert level_events[0].new_level == 2

    def test_can_skip_levels(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        mp = MemberPoints.create(community_id=config.community_id, user_id=uuid4())
        # Award 35 points at once (6 lessons + 1 post = 32, or use multiple)
        # Simpler: set up with 8 points, then award 25 (lesson x5) => 33 points => level 3
        for _ in range(5):
            mp.award_points(
                source=PointSource.POST_CREATED,
                source_id=uuid4(),
                level_config=config,
            )
        # 10 points = level 2
        for _ in range(4):
            mp.award_points(
                source=PointSource.LESSON_COMPLETED,
                source_id=uuid4(),
                level_config=config,
            )
        # 10 + 20 = 30 points = level 3
        assert mp.total_points == 30
        assert mp.current_level == 3


class TestDeductPoints:
    def test_deduct_decreases_total(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        mp = MemberPoints.create(community_id=config.community_id, user_id=uuid4())
        mp.award_points(source=PointSource.POST_CREATED, source_id=uuid4(), level_config=config)
        mp.deduct_points(source=PointSource.POST_LIKED, source_id=uuid4(), level_config=config)
        assert mp.total_points == 1  # 2 - 1

    def test_deduct_cannot_go_below_zero(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        mp = MemberPoints.create(community_id=config.community_id, user_id=uuid4())
        mp.deduct_points(source=PointSource.POST_LIKED, source_id=uuid4(), level_config=config)
        assert mp.total_points == 0

    def test_deduct_publishes_points_deducted_event(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        mp = MemberPoints.create(community_id=config.community_id, user_id=uuid4())
        mp.award_points(source=PointSource.POST_CREATED, source_id=uuid4(), level_config=config)
        mp.clear_events()  # Clear award event
        mp.deduct_points(source=PointSource.POST_LIKED, source_id=uuid4(), level_config=config)
        events = [e for e in mp.events if isinstance(e, PointsDeducted)]
        assert len(events) == 1


class TestRatchetBehavior:
    def test_level_does_not_decrease_on_deduction(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        mp = MemberPoints.create(community_id=config.community_id, user_id=uuid4())
        # Reach level 2 (10 points)
        for _ in range(2):
            mp.award_points(
                source=PointSource.LESSON_COMPLETED,
                source_id=uuid4(),
                level_config=config,
            )
        assert mp.current_level == 2
        # Deduct a point
        mp.deduct_points(source=PointSource.POST_LIKED, source_id=uuid4(), level_config=config)
        assert mp.total_points == 9
        assert mp.current_level == 2  # Ratchet: stays at 2


class TestLessonDeduplication:
    def test_duplicate_lesson_raises(self) -> None:
        config = LevelConfiguration.create_default(community_id=uuid4())
        mp = MemberPoints.create(community_id=config.community_id, user_id=uuid4())
        lesson_id = uuid4()
        mp.award_points(
            source=PointSource.LESSON_COMPLETED,
            source_id=lesson_id,
            level_config=config,
        )
        with pytest.raises(DuplicateLessonCompletionError):
            mp.award_points(
                source=PointSource.LESSON_COMPLETED,
                source_id=lesson_id,
                level_config=config,
            )
        assert mp.total_points == 5  # Only first completion counted
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/unit/gamification/domain/test_member_points.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

`src/gamification/domain/entities/member_points.py`:
```python
"""MemberPoints aggregate root."""

from __future__ import annotations

from dataclasses import dataclass, field
from uuid import UUID, uuid4

from src.gamification.domain.events.gamification_events import (
    MemberLeveledUp,
    PointsAwarded,
    PointsDeducted,
)
from src.gamification.domain.exceptions import DuplicateLessonCompletionError
from src.gamification.domain.value_objects.point_source import PointSource
from src.gamification.domain.value_objects.point_transaction import PointTransaction
from src.shared.domain.base_entity import BaseEntity


@dataclass
class MemberPoints(BaseEntity[UUID]):
    """
    Aggregate root: a member's point balance and level in a community.

    Invariants:
    - total_points >= 0
    - current_level never decreases (ratchet)
    - Lesson completion points awarded once per lesson
    """

    community_id: UUID
    user_id: UUID
    total_points: int = 0
    current_level: int = 1
    transactions: list[PointTransaction] = field(default_factory=list)

    @classmethod
    def create(cls, community_id: UUID, user_id: UUID) -> MemberPoints:
        """Create a new MemberPoints with 0 points at level 1."""
        return cls(
            id=uuid4(),
            community_id=community_id,
            user_id=user_id,
            total_points=0,
            current_level=1,
        )

    def award_points(
        self,
        source: PointSource,
        source_id: UUID,
        level_config: "LevelConfiguration",  # noqa: F821 — forward ref
    ) -> None:
        """Award points from an engagement action."""
        # Lesson deduplication
        if source == PointSource.LESSON_COMPLETED:
            for txn in self.transactions:
                if txn.source == PointSource.LESSON_COMPLETED and txn.source_id == source_id:
                    raise DuplicateLessonCompletionError(str(source_id))

        amount = source.points
        self.total_points += amount

        self.transactions.append(
            PointTransaction(points=amount, source=source, source_id=source_id)
        )

        self.add_event(
            PointsAwarded(
                member_id=self.user_id,
                community_id=self.community_id,
                points=amount,
                new_total=self.total_points,
                source=source.source_name,
            )
        )

        self._recalculate_level(level_config)
        self._update_timestamp()

    def deduct_points(
        self,
        source: PointSource,
        source_id: UUID,
        level_config: "LevelConfiguration",  # noqa: F821
    ) -> None:
        """Deduct points (e.g., unlike). Floor at 0, level never decreases."""
        amount = source.points
        self.total_points = max(0, self.total_points - amount)

        self.transactions.append(
            PointTransaction(points=-amount, source=source, source_id=source_id)
        )

        self.add_event(
            PointsDeducted(
                member_id=self.user_id,
                community_id=self.community_id,
                points=amount,
                new_total=self.total_points,
                source=source.source_name,
            )
        )

        # No level recalculation needed — ratchet rule means level can't go down
        self._update_timestamp()

    def recalculate_level(self, level_config: "LevelConfiguration") -> None:  # noqa: F821
        """Public recalculation (for admin threshold changes)."""
        self._recalculate_level(level_config)

    def _recalculate_level(self, level_config: "LevelConfiguration") -> None:  # noqa: F821
        """Recalculate level from points — ratchet: only goes up."""
        from src.gamification.domain.entities.level_configuration import LevelConfiguration

        calculated_level = level_config.get_level_for_points(self.total_points)
        if calculated_level > self.current_level:
            old_level = self.current_level
            self.current_level = calculated_level
            self.add_event(
                MemberLeveledUp(
                    member_id=self.user_id,
                    community_id=self.community_id,
                    old_level=old_level,
                    new_level=self.current_level,
                    new_level_name=level_config.name_for_level(self.current_level),
                )
            )
```

Update `src/gamification/domain/entities/__init__.py` to export `MemberPoints`.

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/unit/gamification/domain/test_member_points.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/gamification/domain/entities/ tests/unit/gamification/domain/test_member_points.py
git commit -m "feat(gamification): add MemberPoints aggregate with award, deduct, ratchet, and lesson dedup"
```

---

### Task 6: Repository Interfaces

**Owner:** backend
**Depends on:** Task 4, Task 5

**Files:**
- Create: `src/gamification/domain/repositories/__init__.py`
- Create: `src/gamification/domain/repositories/member_points_repository.py`
- Create: `src/gamification/domain/repositories/level_config_repository.py`

**Step 1: Write the interfaces** (no test needed — ABCs have no logic)

`src/gamification/domain/repositories/member_points_repository.py`:
```python
"""MemberPoints repository interface."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.gamification.domain.entities.member_points import MemberPoints


class IMemberPointsRepository(ABC):
    """Interface for MemberPoints persistence."""

    @abstractmethod
    async def save(self, member_points: MemberPoints) -> None: ...

    @abstractmethod
    async def get_by_community_and_user(
        self, community_id: UUID, user_id: UUID
    ) -> MemberPoints | None: ...

    @abstractmethod
    async def list_by_community(self, community_id: UUID) -> list[MemberPoints]: ...
```

`src/gamification/domain/repositories/level_config_repository.py`:
```python
"""LevelConfiguration repository interface."""

from abc import ABC, abstractmethod
from uuid import UUID

from src.gamification.domain.entities.level_configuration import LevelConfiguration


class ILevelConfigRepository(ABC):
    """Interface for LevelConfiguration persistence."""

    @abstractmethod
    async def get_by_community(self, community_id: UUID) -> LevelConfiguration | None: ...

    @abstractmethod
    async def save(self, config: LevelConfiguration) -> None: ...
```

`src/gamification/domain/repositories/__init__.py`:
```python
"""Gamification repository interfaces."""

from src.gamification.domain.repositories.level_config_repository import ILevelConfigRepository
from src.gamification.domain.repositories.member_points_repository import IMemberPointsRepository

__all__ = ["ILevelConfigRepository", "IMemberPointsRepository"]
```

**Step 2: Commit**

```bash
git add src/gamification/domain/repositories/
git commit -m "feat(gamification): add repository interfaces (IMemberPointsRepository, ILevelConfigRepository)"
```

---

### Task 7: Community Event Enrichment

**Owner:** backend
**Depends on:** none

**Files:**
- Modify: `src/community/domain/events.py`
- Test: Existing community tests should still pass

**Step 1: Add `author_id` field to like/unlike events**

In `src/community/domain/events.py`, add `author_id: UserId` to:
- `PostLiked` (after `user_id`)
- `PostUnliked` (after `user_id`)
- `CommentLiked` (after `user_id`)
- `CommentUnliked` (after `user_id`)

Example change for `PostLiked`:
```python
@dataclass(frozen=True)
class PostLiked(DomainEvent):
    """Event published when a post is liked."""

    reaction_id: ReactionId
    post_id: PostId
    user_id: UserId
    author_id: UserId  # NEW: content author (for gamification)
    timestamp: datetime = datetime.now(UTC)

    @property
    def event_type(self) -> str:
        return "PostLiked"
```

**Step 2: Update event publishers**

Find all places that create `PostLiked`, `PostUnliked`, `CommentLiked`, `CommentUnliked` events and add the `author_id` parameter. Search for these event constructors in:
- `src/community/application/handlers/like_post_handler.py`
- `src/community/application/handlers/unlike_post_handler.py`
- `src/community/application/handlers/like_comment_handler.py`
- `src/community/application/handlers/unlike_comment_handler.py`

The handler already has access to the post/comment entity, which contains the `author_id`.

**Step 3: Run existing community tests to verify no breakage**

Run: `python -m pytest tests/features/community/ -v`
Expected: PASS (all existing tests still pass)

**Step 4: Commit**

```bash
git add src/community/domain/events.py src/community/application/handlers/
git commit -m "feat(community): add author_id to like/unlike events for gamification integration"
```

---

### Task 8: SQLAlchemy Models + Alembic Migration

**Owner:** backend
**Depends on:** Task 1

**Files:**
- Create: `src/gamification/infrastructure/__init__.py`
- Create: `src/gamification/infrastructure/persistence/__init__.py`
- Create: `src/gamification/infrastructure/persistence/models.py`
- Create: `alembic/versions/xxx_add_gamification_tables.py` (via `alembic revision`)

**Step 1: Write SQLAlchemy models**

`src/gamification/infrastructure/persistence/models.py`:
```python
"""SQLAlchemy models for Gamification context."""

from datetime import UTC, datetime
from uuid import uuid4

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    String,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSON, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.shared.infrastructure.database import Base


class MemberPointsModel(Base):
    """Stores a member's point total and current level per community."""

    __tablename__ = "member_points"

    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    community_id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), nullable=False)
    user_id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), nullable=False)
    total_points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    current_level: Mapped[int] = mapped_column(SmallInteger, nullable=False, default=1)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    transactions: Mapped[list["PointTransactionModel"]] = relationship(
        back_populates="member_points", cascade="all, delete-orphan"
    )

    __table_args__ = (
        UniqueConstraint("community_id", "user_id", name="uq_member_points_community_user"),
        Index("ix_member_points_community_level", "community_id", "current_level"),
        Index("ix_member_points_community_total", "community_id", total_points.desc()),
    )


class PointTransactionModel(Base):
    """Append-only audit log of point changes."""

    __tablename__ = "point_transactions"

    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    member_points_id: Mapped[uuid4] = mapped_column(
        UUID(as_uuid=True), ForeignKey("member_points.id"), nullable=False
    )
    points: Mapped[int] = mapped_column(Integer, nullable=False)
    source: Mapped[str] = mapped_column(String(30), nullable=False)
    source_id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )

    member_points: Mapped["MemberPointsModel"] = relationship(back_populates="transactions")

    __table_args__ = (
        Index("ix_point_transactions_member_created", "member_points_id", created_at.desc()),
    )


class LevelConfigurationModel(Base):
    """Per-community level configuration (9 levels as JSONB)."""

    __tablename__ = "level_configurations"

    id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    community_id: Mapped[uuid4] = mapped_column(UUID(as_uuid=True), nullable=False, unique=True)
    levels: Mapped[dict] = mapped_column(JSON, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )
```

**Step 2: Generate Alembic migration**

Run: `alembic revision --autogenerate -m "add_gamification_tables"`

**Step 3: Run migration**

Run: `alembic upgrade head`

**Step 4: Verify tables exist**

Run: `alembic current`
Expected: Shows the new migration as current

**Step 5: Commit**

```bash
git add src/gamification/infrastructure/ alembic/versions/*add_gamification*
git commit -m "feat(gamification): add SQLAlchemy models and migration for gamification tables"
```

---

### Task 9: Repository Implementations

**Owner:** backend
**Depends on:** Task 6, Task 8

**Files:**
- Create: `src/gamification/infrastructure/persistence/member_points_repository.py`
- Create: `src/gamification/infrastructure/persistence/level_config_repository.py`
- Modify: `src/gamification/infrastructure/persistence/__init__.py`

**Step 1: Implement MemberPoints repository**

`src/gamification/infrastructure/persistence/member_points_repository.py`:
```python
"""SQLAlchemy implementation of IMemberPointsRepository."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.gamification.domain.entities.member_points import MemberPoints
from src.gamification.domain.repositories.member_points_repository import IMemberPointsRepository
from src.gamification.domain.value_objects.point_source import PointSource
from src.gamification.domain.value_objects.point_transaction import PointTransaction
from src.gamification.infrastructure.persistence.models import (
    MemberPointsModel,
    PointTransactionModel,
)


class SqlAlchemyMemberPointsRepository(IMemberPointsRepository):
    """SQLAlchemy implementation of IMemberPointsRepository."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, member_points: MemberPoints) -> None:
        existing = await self._session.get(MemberPointsModel, member_points.id)

        if existing is None:
            model = MemberPointsModel(
                id=member_points.id,
                community_id=member_points.community_id,
                user_id=member_points.user_id,
                total_points=member_points.total_points,
                current_level=member_points.current_level,
            )
            # Add transactions
            for txn in member_points.transactions:
                model.transactions.append(
                    PointTransactionModel(
                        points=txn.points,
                        source=txn.source.source_name,
                        source_id=txn.source_id,
                        created_at=txn.created_at,
                    )
                )
            self._session.add(model)
        else:
            existing.total_points = member_points.total_points
            existing.current_level = member_points.current_level
            # Add only NEW transactions (those not yet persisted)
            existing_txn_count = len(existing.transactions)
            for txn in member_points.transactions[existing_txn_count:]:
                existing.transactions.append(
                    PointTransactionModel(
                        points=txn.points,
                        source=txn.source.source_name,
                        source_id=txn.source_id,
                        created_at=txn.created_at,
                    )
                )

        await self._session.flush()

    async def get_by_community_and_user(
        self, community_id: UUID, user_id: UUID
    ) -> MemberPoints | None:
        stmt = (
            select(MemberPointsModel)
            .where(
                MemberPointsModel.community_id == community_id,
                MemberPointsModel.user_id == user_id,
            )
            .options(selectinload(MemberPointsModel.transactions))
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._to_entity(model)

    async def list_by_community(self, community_id: UUID) -> list[MemberPoints]:
        stmt = (
            select(MemberPointsModel)
            .where(MemberPointsModel.community_id == community_id)
            .options(selectinload(MemberPointsModel.transactions))
        )
        result = await self._session.execute(stmt)
        return [self._to_entity(m) for m in result.scalars().all()]

    def _to_entity(self, model: MemberPointsModel) -> MemberPoints:
        transactions = [
            PointTransaction(
                points=t.points,
                source=PointSource(t.source) if hasattr(PointSource, t.source.upper())
                else self._source_name_to_enum(t.source),
                source_id=t.source_id,
                created_at=t.created_at,
            )
            for t in model.transactions
        ]
        return MemberPoints(
            id=model.id,
            community_id=model.community_id,
            user_id=model.user_id,
            total_points=model.total_points,
            current_level=model.current_level,
            created_at=model.created_at,
            updated_at=model.updated_at,
            transactions=transactions,
        )

    @staticmethod
    def _source_name_to_enum(source_name: str) -> PointSource:
        """Map source_name string to PointSource enum."""
        for ps in PointSource:
            if ps.source_name == source_name:
                return ps
        raise ValueError(f"Unknown point source: {source_name}")
```

Implement `SqlAlchemyLevelConfigRepository` similarly, converting between `LevelConfigurationModel` (with JSONB `levels`) and `LevelConfiguration` entity.

**Step 2: Verify with existing domain tests**

Run: `python -m pytest tests/unit/gamification/ -v`
Expected: PASS

**Step 3: Commit**

```bash
git add src/gamification/infrastructure/persistence/
git commit -m "feat(gamification): add SQLAlchemy repository implementations"
```

---

### Task 10: AwardPoints + DeductPoints Commands & Handlers

**Owner:** backend
**Depends on:** Task 5, Task 6

**Files:**
- Create: `src/gamification/application/__init__.py`
- Create: `src/gamification/application/commands/__init__.py`
- Create: `src/gamification/application/commands/award_points.py`
- Create: `src/gamification/application/commands/deduct_points.py`
- Test: `tests/unit/gamification/application/__init__.py`
- Test: `tests/unit/gamification/application/test_award_points.py`
- Test: `tests/unit/gamification/application/test_deduct_points.py`

**Step 1: Write the failing tests**

```python
# tests/unit/gamification/application/test_award_points.py
"""Tests for AwardPointsHandler."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.gamification.application.commands.award_points import (
    AwardPointsCommand,
    AwardPointsHandler,
)
from src.gamification.domain.entities.level_configuration import LevelConfiguration
from src.gamification.domain.entities.member_points import MemberPoints
from src.gamification.domain.value_objects.point_source import PointSource


class TestAwardPointsHandler:
    @pytest.fixture
    def member_points_repo(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def level_config_repo(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def handler(self, member_points_repo: AsyncMock, level_config_repo: AsyncMock) -> AwardPointsHandler:
        return AwardPointsHandler(
            member_points_repo=member_points_repo,
            level_config_repo=level_config_repo,
        )

    async def test_creates_member_points_if_not_exists(
        self, handler: AwardPointsHandler, member_points_repo: AsyncMock, level_config_repo: AsyncMock
    ) -> None:
        community_id = uuid4()
        user_id = uuid4()
        config = LevelConfiguration.create_default(community_id=community_id)

        member_points_repo.get_by_community_and_user.return_value = None
        level_config_repo.get_by_community.return_value = config

        command = AwardPointsCommand(
            community_id=community_id,
            user_id=user_id,
            source=PointSource.POST_CREATED,
            source_id=uuid4(),
        )
        await handler.handle(command)

        member_points_repo.save.assert_called_once()
        saved = member_points_repo.save.call_args[0][0]
        assert saved.total_points == 2
        assert saved.user_id == user_id

    async def test_awards_to_existing_member(
        self, handler: AwardPointsHandler, member_points_repo: AsyncMock, level_config_repo: AsyncMock
    ) -> None:
        community_id = uuid4()
        user_id = uuid4()
        config = LevelConfiguration.create_default(community_id=community_id)
        existing = MemberPoints.create(community_id=community_id, user_id=user_id)

        member_points_repo.get_by_community_and_user.return_value = existing
        level_config_repo.get_by_community.return_value = config

        command = AwardPointsCommand(
            community_id=community_id,
            user_id=user_id,
            source=PointSource.POST_LIKED,
            source_id=uuid4(),
        )
        await handler.handle(command)

        member_points_repo.save.assert_called_once()
        saved = member_points_repo.save.call_args[0][0]
        assert saved.total_points == 1

    async def test_creates_default_config_if_not_exists(
        self, handler: AwardPointsHandler, member_points_repo: AsyncMock, level_config_repo: AsyncMock
    ) -> None:
        community_id = uuid4()
        member_points_repo.get_by_community_and_user.return_value = None
        level_config_repo.get_by_community.return_value = None  # No config yet

        command = AwardPointsCommand(
            community_id=community_id,
            user_id=uuid4(),
            source=PointSource.POST_CREATED,
            source_id=uuid4(),
        )
        await handler.handle(command)

        # Should have saved a default config
        level_config_repo.save.assert_called_once()
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/unit/gamification/application/test_award_points.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

`src/gamification/application/commands/award_points.py`:
```python
"""Award points command and handler."""

from dataclasses import dataclass
from uuid import UUID

import structlog

from src.gamification.domain.entities.level_configuration import LevelConfiguration
from src.gamification.domain.entities.member_points import MemberPoints
from src.gamification.domain.repositories import ILevelConfigRepository, IMemberPointsRepository
from src.gamification.domain.value_objects.point_source import PointSource
from src.shared.infrastructure import event_bus

logger = structlog.get_logger()


@dataclass(frozen=True)
class AwardPointsCommand:
    """Command to award points to a member."""

    community_id: UUID
    user_id: UUID
    source: PointSource
    source_id: UUID


class AwardPointsHandler:
    """Handler for awarding points."""

    def __init__(
        self,
        member_points_repo: IMemberPointsRepository,
        level_config_repo: ILevelConfigRepository,
    ) -> None:
        self._member_points_repo = member_points_repo
        self._level_config_repo = level_config_repo

    async def handle(self, command: AwardPointsCommand) -> None:
        # Get or create level config (lazy init)
        config = await self._level_config_repo.get_by_community(command.community_id)
        if config is None:
            config = LevelConfiguration.create_default(command.community_id)
            await self._level_config_repo.save(config)

        # Get or create member points
        mp = await self._member_points_repo.get_by_community_and_user(
            command.community_id, command.user_id
        )
        if mp is None:
            mp = MemberPoints.create(
                community_id=command.community_id, user_id=command.user_id
            )

        # Award points
        mp.award_points(
            source=command.source,
            source_id=command.source_id,
            level_config=config,
        )

        # Persist
        await self._member_points_repo.save(mp)

        # Publish events
        await event_bus.publish_all(mp.clear_events())

        logger.info(
            "points_awarded",
            user_id=str(command.user_id),
            community_id=str(command.community_id),
            source=command.source.source_name,
            points=command.source.points,
            new_total=mp.total_points,
        )
```

Implement `DeductPointsCommand` + `DeductPointsHandler` following the same pattern but calling `mp.deduct_points()`. The handler should silently handle `total_points == 0` (no-op for deduction on zero).

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/unit/gamification/application/ -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/gamification/application/ tests/unit/gamification/application/
git commit -m "feat(gamification): add AwardPoints and DeductPoints commands and handlers"
```

---

### Task 11: GetMemberLevel Query & Handler

**Owner:** backend
**Depends on:** Task 6

**Files:**
- Create: `src/gamification/application/queries/__init__.py`
- Create: `src/gamification/application/queries/get_member_level.py`
- Test: `tests/unit/gamification/application/test_get_member_level.py`

**Step 1: Write the failing tests**

```python
# tests/unit/gamification/application/test_get_member_level.py
"""Tests for GetMemberLevelHandler."""

from unittest.mock import AsyncMock
from uuid import uuid4

import pytest

from src.gamification.application.queries.get_member_level import (
    GetMemberLevelQuery,
    GetMemberLevelHandler,
    MemberLevelResult,
)
from src.gamification.domain.entities.level_configuration import LevelConfiguration
from src.gamification.domain.entities.member_points import MemberPoints


class TestGetMemberLevelHandler:
    @pytest.fixture
    def member_points_repo(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def level_config_repo(self) -> AsyncMock:
        return AsyncMock()

    @pytest.fixture
    def handler(self, member_points_repo: AsyncMock, level_config_repo: AsyncMock) -> GetMemberLevelHandler:
        return GetMemberLevelHandler(
            member_points_repo=member_points_repo,
            level_config_repo=level_config_repo,
        )

    async def test_returns_member_level_for_existing_member(
        self, handler: GetMemberLevelHandler, member_points_repo: AsyncMock, level_config_repo: AsyncMock
    ) -> None:
        community_id = uuid4()
        user_id = uuid4()
        config = LevelConfiguration.create_default(community_id=community_id)
        mp = MemberPoints.create(community_id=community_id, user_id=user_id)
        mp.total_points = 15
        mp.current_level = 2

        member_points_repo.get_by_community_and_user.return_value = mp
        level_config_repo.get_by_community.return_value = config

        query = GetMemberLevelQuery(
            community_id=community_id,
            user_id=user_id,
            requesting_user_id=user_id,  # viewing own profile
        )
        result = await handler.handle(query)

        assert result.level == 2
        assert result.level_name == "Practitioner"
        assert result.total_points == 15
        assert result.points_to_next_level == 15  # 30 - 15

    async def test_new_member_returns_level_1(
        self, handler: GetMemberLevelHandler, member_points_repo: AsyncMock, level_config_repo: AsyncMock
    ) -> None:
        community_id = uuid4()
        config = LevelConfiguration.create_default(community_id=community_id)
        member_points_repo.get_by_community_and_user.return_value = None
        level_config_repo.get_by_community.return_value = config

        query = GetMemberLevelQuery(
            community_id=community_id,
            user_id=uuid4(),
            requesting_user_id=uuid4(),
        )
        result = await handler.handle(query)

        assert result.level == 1
        assert result.level_name == "Student"
        assert result.total_points == 0

    async def test_points_to_next_level_null_for_other_member(
        self, handler: GetMemberLevelHandler, member_points_repo: AsyncMock, level_config_repo: AsyncMock
    ) -> None:
        community_id = uuid4()
        user_id = uuid4()
        other_user_id = uuid4()
        config = LevelConfiguration.create_default(community_id=community_id)
        mp = MemberPoints.create(community_id=community_id, user_id=user_id)

        member_points_repo.get_by_community_and_user.return_value = mp
        level_config_repo.get_by_community.return_value = config

        query = GetMemberLevelQuery(
            community_id=community_id,
            user_id=user_id,
            requesting_user_id=other_user_id,  # different user
        )
        result = await handler.handle(query)

        assert result.points_to_next_level is None  # private to own profile

    async def test_level_9_has_no_points_to_next(
        self, handler: GetMemberLevelHandler, member_points_repo: AsyncMock, level_config_repo: AsyncMock
    ) -> None:
        community_id = uuid4()
        user_id = uuid4()
        config = LevelConfiguration.create_default(community_id=community_id)
        mp = MemberPoints.create(community_id=community_id, user_id=user_id)
        mp.total_points = 400
        mp.current_level = 9

        member_points_repo.get_by_community_and_user.return_value = mp
        level_config_repo.get_by_community.return_value = config

        query = GetMemberLevelQuery(
            community_id=community_id,
            user_id=user_id,
            requesting_user_id=user_id,
        )
        result = await handler.handle(query)

        assert result.is_max_level is True
        assert result.points_to_next_level is None
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/unit/gamification/application/test_get_member_level.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

`src/gamification/application/queries/get_member_level.py`:
```python
"""GetMemberLevel query and handler."""

from dataclasses import dataclass
from uuid import UUID

from src.gamification.domain.entities.level_configuration import LevelConfiguration
from src.gamification.domain.repositories import ILevelConfigRepository, IMemberPointsRepository


@dataclass(frozen=True)
class GetMemberLevelQuery:
    community_id: UUID
    user_id: UUID
    requesting_user_id: UUID


@dataclass
class MemberLevelResult:
    user_id: UUID
    level: int
    level_name: str
    total_points: int
    points_to_next_level: int | None
    is_max_level: bool


class GetMemberLevelHandler:
    def __init__(
        self,
        member_points_repo: IMemberPointsRepository,
        level_config_repo: ILevelConfigRepository,
    ) -> None:
        self._member_points_repo = member_points_repo
        self._level_config_repo = level_config_repo

    async def handle(self, query: GetMemberLevelQuery) -> MemberLevelResult:
        config = await self._level_config_repo.get_by_community(query.community_id)
        if config is None:
            config = LevelConfiguration.create_default(query.community_id)

        mp = await self._member_points_repo.get_by_community_and_user(
            query.community_id, query.user_id
        )

        total_points = mp.total_points if mp else 0
        current_level = mp.current_level if mp else 1
        is_max_level = current_level >= 9
        is_own_profile = query.user_id == query.requesting_user_id

        points_to_next: int | None = None
        if is_own_profile and not is_max_level:
            points_to_next = config.points_to_next_level(current_level, total_points)

        return MemberLevelResult(
            user_id=query.user_id,
            level=current_level,
            level_name=config.name_for_level(current_level),
            total_points=total_points,
            points_to_next_level=points_to_next,
            is_max_level=is_max_level,
        )
```

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/unit/gamification/application/test_get_member_level.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/gamification/application/queries/ tests/unit/gamification/application/test_get_member_level.py
git commit -m "feat(gamification): add GetMemberLevel query and handler"
```

---

### Task 12: Community + Classroom Event Handlers

**Owner:** backend
**Depends on:** Task 7, Task 10

**Files:**
- Create: `src/gamification/application/event_handlers/__init__.py`
- Create: `src/gamification/application/event_handlers/community_event_handlers.py`
- Create: `src/gamification/application/event_handlers/classroom_event_handlers.py`
- Test: `tests/unit/gamification/application/test_event_handlers.py`

**Step 1: Write the failing tests**

```python
# tests/unit/gamification/application/test_event_handlers.py
"""Tests for gamification event handlers."""

from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from src.community.domain.events import CommentAdded, PostCreated, PostLiked, PostUnliked
from src.community.domain.value_objects import CommentId, CommunityId, PostId, ReactionId
from src.gamification.application.event_handlers.community_event_handlers import (
    handle_comment_added,
    handle_post_created,
    handle_post_liked,
    handle_post_unliked,
)
from src.gamification.domain.value_objects.point_source import PointSource
from src.identity.domain.value_objects import UserId


class TestPostCreatedHandler:
    @patch("src.gamification.application.event_handlers.community_event_handlers._get_award_handler")
    async def test_awards_2_points_to_author(self, mock_get_handler: AsyncMock) -> None:
        mock_handler = AsyncMock()
        mock_get_handler.return_value = mock_handler

        event = PostCreated(
            post_id=PostId(uuid4()),
            community_id=CommunityId(uuid4()),
            author_id=UserId(uuid4()),
            category_id=...,  # fill based on actual event fields
            title="Test",
            content="Test content",
        )
        await handle_post_created(event)

        mock_handler.handle.assert_called_once()
        cmd = mock_handler.handle.call_args[0][0]
        assert cmd.source == PointSource.POST_CREATED
        assert cmd.user_id == event.author_id.value


class TestPostLikedHandler:
    @patch("src.gamification.application.event_handlers.community_event_handlers._get_award_handler")
    async def test_awards_1_point_to_author(self, mock_get_handler: AsyncMock) -> None:
        mock_handler = AsyncMock()
        mock_get_handler.return_value = mock_handler

        event = PostLiked(
            reaction_id=ReactionId(uuid4()),
            post_id=PostId(uuid4()),
            user_id=UserId(uuid4()),  # liker
            author_id=UserId(uuid4()),  # content author
        )
        await handle_post_liked(event)

        mock_handler.handle.assert_called_once()
        cmd = mock_handler.handle.call_args[0][0]
        assert cmd.source == PointSource.POST_LIKED
        assert cmd.user_id == event.author_id.value  # points go to author, not liker


class TestPostUnlikedHandler:
    @patch("src.gamification.application.event_handlers.community_event_handlers._get_deduct_handler")
    async def test_deducts_1_point_from_author(self, mock_get_handler: AsyncMock) -> None:
        mock_handler = AsyncMock()
        mock_get_handler.return_value = mock_handler

        event = PostUnliked(
            post_id=PostId(uuid4()),
            user_id=UserId(uuid4()),  # unliker
            author_id=UserId(uuid4()),  # content author
        )
        await handle_post_unliked(event)

        mock_handler.handle.assert_called_once()
        cmd = mock_handler.handle.call_args[0][0]
        assert cmd.user_id == event.author_id.value
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/unit/gamification/application/test_event_handlers.py -v`
Expected: FAIL

**Step 3: Write minimal implementation**

`src/gamification/application/event_handlers/community_event_handlers.py`:
```python
"""Event handlers for Community context events."""

import structlog

from src.community.domain.events import (
    CommentAdded,
    CommentLiked,
    CommentUnliked,
    PostCreated,
    PostLiked,
    PostUnliked,
)
from src.gamification.application.commands.award_points import AwardPointsCommand, AwardPointsHandler
from src.gamification.application.commands.deduct_points import DeductPointsCommand, DeductPointsHandler
from src.gamification.domain.value_objects.point_source import PointSource

logger = structlog.get_logger()


def _get_award_handler() -> AwardPointsHandler:
    """Get an AwardPointsHandler with a fresh DB session."""
    # Wired at app startup — uses dependency injection
    from src.gamification.interface.api.dependencies import create_award_handler
    return create_award_handler()


def _get_deduct_handler() -> DeductPointsHandler:
    """Get a DeductPointsHandler with a fresh DB session."""
    from src.gamification.interface.api.dependencies import create_deduct_handler
    return create_deduct_handler()


async def handle_post_created(event: PostCreated) -> None:
    """Award 2 points to post author."""
    handler = _get_award_handler()
    await handler.handle(AwardPointsCommand(
        community_id=event.community_id.value,
        user_id=event.author_id.value,
        source=PointSource.POST_CREATED,
        source_id=event.post_id.value,
    ))


async def handle_post_liked(event: PostLiked) -> None:
    """Award 1 point to post author (not the liker)."""
    handler = _get_award_handler()
    await handler.handle(AwardPointsCommand(
        community_id=...,  # need to extract from event or context
        user_id=event.author_id.value,
        source=PointSource.POST_LIKED,
        source_id=event.post_id.value,
    ))


async def handle_post_unliked(event: PostUnliked) -> None:
    """Deduct 1 point from post author."""
    handler = _get_deduct_handler()
    await handler.handle(DeductPointsCommand(
        community_id=...,
        user_id=event.author_id.value,
        source=PointSource.POST_LIKED,
        source_id=event.post_id.value,
    ))


async def handle_comment_added(event: CommentAdded) -> None:
    """Award 1 point to comment author."""
    handler = _get_award_handler()
    await handler.handle(AwardPointsCommand(
        community_id=...,
        user_id=event.author_id.value,
        source=PointSource.COMMENT_CREATED,
        source_id=event.comment_id.value,
    ))

# Similarly for handle_comment_liked, handle_comment_unliked
```

**Note:** The exact `community_id` extraction depends on whether the Community events carry `community_id`. Check `PostLiked` — if it doesn't have `community_id`, it may need to be added alongside `author_id` (Task 7), or resolved via the post. Adjust implementation accordingly.

Implement `classroom_event_handlers.py` similarly for `LessonCompleted`.

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/unit/gamification/application/test_event_handlers.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/gamification/application/event_handlers/ tests/unit/gamification/application/test_event_handlers.py
git commit -m "feat(gamification): add event handlers for Community and Classroom events"
```

---

### Task 13: API Routes + Schemas

**Owner:** backend
**Depends on:** Task 10, Task 11

**Files:**
- Create: `src/gamification/infrastructure/api/__init__.py`
- Create: `src/gamification/infrastructure/api/schemas.py`
- Create: `src/gamification/infrastructure/api/routes.py`
- Create: `src/gamification/interface/__init__.py`
- Create: `src/gamification/interface/api/__init__.py`
- Create: `src/gamification/interface/api/dependencies.py`
- Create: `src/gamification/interface/api/gamification_controller.py`

**Step 1: Write schemas**

`src/gamification/infrastructure/api/schemas.py`:
```python
"""Pydantic schemas for Gamification API."""

from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MemberLevelResponse(BaseModel):
    """Response for GET /communities/{id}/members/{user_id}/level."""

    model_config = ConfigDict(from_attributes=True)

    user_id: UUID
    level: int
    level_name: str
    total_points: int
    points_to_next_level: int | None
    is_max_level: bool
```

**Step 2: Write dependencies**

`src/gamification/interface/api/dependencies.py`:
```python
"""FastAPI dependencies for Gamification context."""

from typing import Annotated

from fastapi import Depends

from src.gamification.application.commands.award_points import AwardPointsHandler
from src.gamification.application.commands.deduct_points import DeductPointsHandler
from src.gamification.application.queries.get_member_level import GetMemberLevelHandler
from src.gamification.infrastructure.persistence.level_config_repository import SqlAlchemyLevelConfigRepository
from src.gamification.infrastructure.persistence.member_points_repository import SqlAlchemyMemberPointsRepository
from src.identity.interface.api.dependencies import SessionDep


def get_member_points_repo(session: SessionDep) -> SqlAlchemyMemberPointsRepository:
    return SqlAlchemyMemberPointsRepository(session)


def get_level_config_repo(session: SessionDep) -> SqlAlchemyLevelConfigRepository:
    return SqlAlchemyLevelConfigRepository(session)


MemberPointsRepoDep = Annotated[SqlAlchemyMemberPointsRepository, Depends(get_member_points_repo)]
LevelConfigRepoDep = Annotated[SqlAlchemyLevelConfigRepository, Depends(get_level_config_repo)]


def get_get_member_level_handler(
    mp_repo: MemberPointsRepoDep,
    lc_repo: LevelConfigRepoDep,
) -> GetMemberLevelHandler:
    return GetMemberLevelHandler(member_points_repo=mp_repo, level_config_repo=lc_repo)


def get_award_handler(
    mp_repo: MemberPointsRepoDep,
    lc_repo: LevelConfigRepoDep,
) -> AwardPointsHandler:
    return AwardPointsHandler(member_points_repo=mp_repo, level_config_repo=lc_repo)


def get_deduct_handler(
    mp_repo: MemberPointsRepoDep,
    lc_repo: LevelConfigRepoDep,
) -> DeductPointsHandler:
    return DeductPointsHandler(member_points_repo=mp_repo, level_config_repo=lc_repo)
```

**Step 3: Write controller**

`src/gamification/interface/api/gamification_controller.py`:
```python
"""Gamification API endpoints."""

from typing import Annotated
from uuid import UUID

import structlog
from fastapi import APIRouter, Depends

from src.gamification.application.queries.get_member_level import (
    GetMemberLevelHandler,
    GetMemberLevelQuery,
)
from src.gamification.infrastructure.api.schemas import MemberLevelResponse
from src.gamification.interface.api.dependencies import get_get_member_level_handler

# Import auth dependency from identity context (same pattern as community)
from src.community.interface.api.dependencies import CurrentUserIdDep

logger = structlog.get_logger()

router = APIRouter(prefix="/api/communities", tags=["Gamification"])


@router.get(
    "/{community_id}/members/{user_id}/level",
    response_model=MemberLevelResponse,
)
async def get_member_level(
    community_id: UUID,
    user_id: UUID,
    current_user_id: CurrentUserIdDep,
    handler: Annotated[GetMemberLevelHandler, Depends(get_get_member_level_handler)],
) -> MemberLevelResponse:
    """Get a member's level and points."""
    query = GetMemberLevelQuery(
        community_id=community_id,
        user_id=user_id,
        requesting_user_id=current_user_id,
    )
    result = await handler.handle(query)
    return MemberLevelResponse(
        user_id=result.user_id,
        level=result.level,
        level_name=result.level_name,
        total_points=result.total_points,
        points_to_next_level=result.points_to_next_level,
        is_max_level=result.is_max_level,
    )
```

**Step 4: Verify linting and types**

Run: `ruff check src/gamification/ && mypy src/gamification/`
Expected: PASS

**Step 5: Commit**

```bash
git add src/gamification/infrastructure/api/ src/gamification/interface/
git commit -m "feat(gamification): add API routes, schemas, and dependencies for member level endpoint"
```

---

### Task 14: App Wiring — Register Event Handlers + Include Router

**Owner:** backend
**Depends on:** Task 12, Task 13

**Files:**
- Modify: Main app setup file (find the FastAPI app initialization file — likely `src/main.py` or similar)
- Register gamification event handlers with the global event bus
- Include gamification router in the FastAPI app

**Step 1: Find and read the main app file**

Search for `app = FastAPI` or `include_router` to find where routers are registered.

**Step 2: Register event handlers**

Add to app startup:
```python
from src.shared.infrastructure.event_bus import event_bus
from src.community.domain.events import (
    PostCreated, PostLiked, PostUnliked, CommentAdded, CommentLiked, CommentUnliked,
)
from src.gamification.application.event_handlers.community_event_handlers import (
    handle_post_created, handle_post_liked, handle_post_unliked,
    handle_comment_added, handle_comment_liked, handle_comment_unliked,
)

# Register gamification event handlers
event_bus.subscribe(PostCreated)(handle_post_created)
event_bus.subscribe(PostLiked)(handle_post_liked)
event_bus.subscribe(PostUnliked)(handle_post_unliked)
event_bus.subscribe(CommentAdded)(handle_comment_added)
event_bus.subscribe(CommentLiked)(handle_comment_liked)
event_bus.subscribe(CommentUnliked)(handle_comment_unliked)
```

**Step 3: Include router**

```python
from src.gamification.interface.api.gamification_controller import router as gamification_router
app.include_router(gamification_router)
```

**Step 4: Verify app starts**

Run: `python -c "from src.main import app; print('App loaded successfully')"`
Expected: No import errors

**Step 5: Commit**

```bash
git add src/main.py  # or wherever the app wiring is
git commit -m "feat(gamification): wire event handlers and API router into app startup"
```

---

### Task 15: TypeScript Types + API Client

**Owner:** frontend
**Depends on:** none (codes against API contract from TDD)

**Files:**
- Create: `frontend/src/features/gamification/types/index.ts`
- Create: `frontend/src/features/gamification/api/index.ts`
- Create: `frontend/src/features/gamification/api/gamificationApi.ts`

**Step 1: Write TypeScript types**

`frontend/src/features/gamification/types/index.ts`:
```typescript
export interface MemberLevel {
  user_id: string;
  level: number;
  level_name: string;
  total_points: number;
  points_to_next_level: number | null;
  is_max_level: boolean;
}

export type PointSource =
  | 'post_created'
  | 'comment_created'
  | 'post_liked'
  | 'comment_liked'
  | 'lesson_completed';
```

**Step 2: Write API client**

`frontend/src/features/gamification/api/gamificationApi.ts`:
```typescript
import { apiClient } from '@/lib/api-client';
import type { MemberLevel } from '../types';

/**
 * Get a member's level and points in a community.
 */
export async function getMemberLevel(
  communityId: string,
  userId: string,
): Promise<MemberLevel> {
  const response = await apiClient.get<MemberLevel>(
    `/api/communities/${communityId}/members/${userId}/level`,
  );
  return response.data;
}
```

`frontend/src/features/gamification/api/index.ts`:
```typescript
export { getMemberLevel } from './gamificationApi';
```

**Step 3: Verify TypeScript compiles**

Run: `cd frontend && npx tsc --noEmit`
Expected: PASS

**Step 4: Commit**

```bash
git add frontend/src/features/gamification/
git commit -m "feat(gamification): add TypeScript types and API client for gamification"
```

---

### Task 16: LevelBadge Component

**Owner:** frontend
**Depends on:** none

**Files:**
- Create: `frontend/src/features/gamification/components/LevelBadge.tsx`
- Test: `frontend/src/features/gamification/components/LevelBadge.test.tsx`

**Step 1: Write the failing test**

```typescript
// frontend/src/features/gamification/components/LevelBadge.test.tsx
import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { LevelBadge } from './LevelBadge';

describe('LevelBadge', () => {
  it('renders the level number', () => {
    render(<LevelBadge level={3} />);
    expect(screen.getByText('3')).toBeInTheDocument();
  });

  it('renders level 1', () => {
    render(<LevelBadge level={1} />);
    expect(screen.getByText('1')).toBeInTheDocument();
  });

  it('renders level 9', () => {
    render(<LevelBadge level={9} />);
    expect(screen.getByText('9')).toBeInTheDocument();
  });

  it('applies correct size classes for md', () => {
    const { container } = render(<LevelBadge level={2} size="md" />);
    const badge = container.firstChild as HTMLElement;
    expect(badge.className).toContain('h-5');
    expect(badge.className).toContain('w-5');
  });

  it('has aria-hidden for accessibility', () => {
    const { container } = render(<LevelBadge level={2} />);
    const badge = container.firstChild as HTMLElement;
    expect(badge.getAttribute('aria-hidden')).toBe('true');
  });
});
```

**Step 2: Run test to verify it fails**

Run: `cd frontend && npx vitest run src/features/gamification/components/LevelBadge.test.tsx`
Expected: FAIL

**Step 3: Write minimal implementation**

```typescript
// frontend/src/features/gamification/components/LevelBadge.tsx
interface LevelBadgeProps {
  level: number;
  size?: 'xs' | 'sm' | 'md' | 'lg';
}

const badgeSizeClasses = {
  xs: 'h-4 w-4 text-[10px]',
  sm: 'h-4 w-4 text-[10px]',
  md: 'h-5 w-5 text-xs',
  lg: 'h-6 w-6 text-sm',
};

export function LevelBadge({ level, size = 'md' }: LevelBadgeProps): JSX.Element {
  return (
    <div
      aria-hidden="true"
      className={`${badgeSizeClasses[size]} flex items-center justify-center rounded-full bg-blue-600 border-2 border-white text-white font-semibold`}
    >
      {level}
    </div>
  );
}
```

**Step 4: Run test to verify it passes**

Run: `cd frontend && npx vitest run src/features/gamification/components/LevelBadge.test.tsx`
Expected: PASS

**Step 5: Commit**

```bash
git add frontend/src/features/gamification/components/LevelBadge.tsx \
  frontend/src/features/gamification/components/LevelBadge.test.tsx
git commit -m "feat(gamification): add LevelBadge component with responsive sizing"
```

---

### Task 17: Avatar Enhancement with Level Prop

**Owner:** frontend
**Depends on:** Task 16

**Files:**
- Modify: `frontend/src/components/Avatar.tsx`
- Test: `frontend/src/components/Avatar.test.tsx` (create or modify)

**Step 1: Write the failing test**

```typescript
// frontend/src/components/Avatar.test.tsx
import { render, screen } from '@testing-library/react';
import { describe, expect, it } from 'vitest';
import { Avatar } from './Avatar';

describe('Avatar with level badge', () => {
  it('renders without badge when level is undefined', () => {
    const { container } = render(
      <Avatar src={null} alt="Test" fallback="T" />
    );
    expect(container.querySelector('[aria-hidden="true"]')).toBeNull();
  });

  it('renders level badge when level is provided', () => {
    render(<Avatar src={null} alt="Test" fallback="T" level={3} />);
    expect(screen.getByText('3')).toBeInTheDocument();
  });

  it('wraps in relative container when level is provided', () => {
    const { container } = render(
      <Avatar src={null} alt="Test" fallback="T" level={2} />
    );
    const wrapper = container.firstChild as HTMLElement;
    expect(wrapper.className).toContain('relative');
  });

  it('includes level in alt text when provided', () => {
    render(<Avatar src="test.jpg" alt="John Doe" fallback="J" level={5} />);
    const img = screen.getByAltText('John Doe, Level 5');
    expect(img).toBeInTheDocument();
  });
});
```

**Step 2: Run test to verify it fails**

Run: `cd frontend && npx vitest run src/components/Avatar.test.tsx`
Expected: FAIL

**Step 3: Modify Avatar component**

Add `level?: number` prop to `AvatarProps`. When `level` is provided:
1. Wrap in `<div className="relative inline-block">`
2. Render `<LevelBadge>` with `absolute -bottom-0.5 -right-0.5` positioning
3. Append `, Level {level}` to alt text

```typescript
// Updated Avatar component (key changes)
import { LevelBadge } from '@/features/gamification/components/LevelBadge';

interface AvatarProps {
  src: string | null | undefined;
  alt: string;
  size?: 'xs' | 'sm' | 'md' | 'lg';
  fallback: string;
  level?: number;  // NEW
}

export function Avatar({ src, alt, size = 'md', fallback, level }: AvatarProps): JSX.Element {
  const altText = level != null ? `${alt}, Level ${level}` : alt;

  const avatarElement = src != null && src !== '' ? (
    <img src={src} alt={altText} className={`${sizeClasses[size]} rounded-full object-cover`} />
  ) : (
    <div className={`${sizeClasses[size]} flex items-center justify-center rounded-full bg-primary-100 text-primary-700 font-medium`}>
      {fallback[0]?.toUpperCase() ?? 'U'}
    </div>
  );

  if (level == null) {
    return avatarElement;
  }

  return (
    <div className="relative inline-block">
      {avatarElement}
      <div className="absolute -bottom-0.5 -right-0.5">
        <LevelBadge level={level} size={size} />
      </div>
    </div>
  );
}
```

**Step 4: Run test to verify it passes**

Run: `cd frontend && npx vitest run src/components/Avatar.test.tsx`
Expected: PASS

**Step 5: Run all frontend tests**

Run: `cd frontend && npm run test -- --run`
Expected: PASS (no regressions)

**Step 6: Commit**

```bash
git add frontend/src/components/Avatar.tsx frontend/src/components/Avatar.test.tsx
git commit -m "feat(gamification): enhance Avatar with optional level badge overlay"
```

---

### Task 18: BDD Step Definitions + Full Verification

**Owner:** testing
**Depends on:** ALL previous tasks

**Files:**
- Create: `tests/features/gamification/__init__.py`
- Create: `tests/features/gamification/test_points.py`
- Create: `tests/features/gamification/conftest.py`

**Step 1: Create BDD step definitions**

Create `conftest.py` with fixtures for:
- Community creation with default level config
- User creation with specified roles
- Post creation
- Comment creation
- Like/unlike actions
- Level config initialization
- MemberPoints with pre-set points/level

Create `test_points.py` with `pytest-bdd` step definitions:
- Map all 40 scenarios from `tests/features/gamification/points.feature`
- Implement step definitions for the 15 Phase 1 scenarios
- Mark 25 remaining scenarios as skipped with phase markers

**Step 2: Add skip markers for Phase 2 and Phase 3 scenarios**

For each skipped scenario, add:
```python
@pytest.mark.skip(reason="Phase 2: Requires level definitions query and display components")
```

or:
```python
@pytest.mark.skip(reason="Phase 3: Requires course gating infrastructure")
```

**Phase 1 enabled scenarios (15):**
1. Member earns a point when their post is liked
2. Member earns a point when their comment is liked
3. Point is deducted when a like is removed
4. Member earns points when creating a post
5. Member earns a point when commenting on a post
6. Member earns points when completing a lesson
7. No duplicate points for completing the same lesson twice
8. New member starts at Level 1
9. Member levels up when reaching point threshold
10. Member can skip levels with large point gains
11. Member sees points needed to reach next level
12. Level 9 member sees no level-up progress
13. Level does not decrease when points drop below threshold
14. Points cannot go below zero
15. Multiple point sources accumulate correctly

**Phase 2 skipped scenarios (9):**
- Level badge shown on post author avatar (Phase 2)
- Level badge shown in member directory (Phase 2)
- Level information shown on member profile (Phase 2)
- Member can view all level definitions (Phase 2)
- Level definitions show percentage of members at each level (Phase 2)
- Admin customizes level names (Phase 2)
- Admin customizes point thresholds (Phase 2)
- Threshold change recalculates member levels (Phase 2)
- Level ratchet preserved when thresholds change (Phase 2)

**Phase 3 skipped scenarios (16):**
- Course access scenarios (Phase 3)
- Validation error scenarios (Phase 3)
- Security scenarios (Phase 3)
- Course gating edge cases (Phase 3)

**Step 3: Run Phase 1 BDD tests**

Run: `python -m pytest tests/features/gamification/test_points.py -v`
Expected: 15 passed, 25 skipped, 0 failed

**Step 4: Verify all skips have phase markers**

Run: `grep -r "@pytest.mark.skip" tests/features/gamification/ | grep "Phase [0-9]"`
Expected: 25 lines, each with a Phase marker

**Step 5: Run full verification**

Run: `./scripts/verify.sh`
Expected: All checks pass (ruff check, ruff format, mypy, tests)

**Step 6: Run frontend tests and typecheck**

Run: `cd frontend && npm run test -- --run && npm run typecheck`
Expected: PASS

**Step 7: Commit**

```bash
git add tests/features/gamification/
git commit -m "feat(gamification): complete Phase 1 — core points engine with 15 BDD scenarios passing"
```

---

## Post-Phase 1 Checklist

- [ ] All 15 Phase 1 BDD scenarios passing
- [ ] 25 scenarios skipped with Phase 2/3 markers
- [ ] Unit tests for all value objects, entities, and handlers
- [ ] Frontend LevelBadge and Avatar tests passing
- [ ] `./scripts/verify.sh` green
- [ ] No regressions in Community or Classroom tests
- [ ] Migration applies cleanly
