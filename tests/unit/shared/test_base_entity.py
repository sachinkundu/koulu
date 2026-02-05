"""Unit tests for BaseEntity and shared domain utilities."""

from dataclasses import dataclass
from uuid import UUID

from src.shared.domain.base_entity import BaseEntity, generate_uuid
from src.shared.domain.base_event import DomainEvent


@dataclass(frozen=True, kw_only=True)
class TestEvent(DomainEvent):
    """Test event for testing."""

    message: str


@dataclass(kw_only=True, eq=False)
class TestEntity(BaseEntity[UUID]):
    """Concrete test entity for testing BaseEntity.

    eq=False allows BaseEntity's __eq__ to be used (compare by ID only).
    """

    name: str

    def __hash__(self) -> int:
        """Hash based on entity ID (required when eq=False)."""
        return hash(self.id)


class TestBaseEntityEventManagement:
    """Tests for BaseEntity event management."""

    def test_add_event_stores_event(self) -> None:
        """add_event() should store the event."""
        entity = TestEntity(id=generate_uuid(), name="test")
        event = TestEvent(message="test event")

        entity.add_event(event)

        assert len(entity.events) == 1
        assert entity.events[0] == event

    def test_clear_events_returns_and_removes_events(self) -> None:
        """clear_events() should return events and empty the list."""
        entity = TestEntity(id=generate_uuid(), name="test")
        event = TestEvent(message="test event")
        entity.add_event(event)

        cleared = entity.clear_events()

        assert len(cleared) == 1
        assert cleared[0] == event
        assert len(entity.events) == 0

    def test_events_property_returns_copy(self) -> None:
        """events property should return a copy, not the original list."""
        entity = TestEntity(id=generate_uuid(), name="test")
        entity.add_event(TestEvent(message="test"))

        events = entity.events
        events.clear()

        assert len(entity.events) == 1  # Original unchanged


class TestBaseEntityEquality:
    """Tests for BaseEntity equality and hashing."""

    def test_entities_with_same_id_are_equal(self) -> None:
        """Entities with the same ID should be equal."""
        entity_id = generate_uuid()
        entity1 = TestEntity(id=entity_id, name="first")
        entity2 = TestEntity(id=entity_id, name="second")  # Different name, same ID

        assert entity1 == entity2

    def test_entities_with_different_ids_are_not_equal(self) -> None:
        """Entities with different IDs should not be equal."""
        entity1 = TestEntity(id=generate_uuid(), name="test")
        entity2 = TestEntity(id=generate_uuid(), name="test")  # Same name, different ID

        assert entity1 != entity2

    def test_entity_not_equal_to_non_entity(self) -> None:
        """Entity should not be equal to non-entity objects."""
        entity = TestEntity(id=generate_uuid(), name="test")

        result = entity.__eq__("not an entity")

        assert result is NotImplemented

    def test_entities_can_be_used_in_sets(self) -> None:
        """Entities should be hashable and usable in sets."""
        entity_id = generate_uuid()
        entity1 = TestEntity(id=entity_id, name="first")
        entity2 = TestEntity(id=entity_id, name="second")

        entity_set = {entity1, entity2}

        assert len(entity_set) == 1  # Same ID = same entity


class TestBaseEntityTimestamps:
    """Tests for BaseEntity timestamp management."""

    def test_update_timestamp_changes_updated_at(self) -> None:
        """_update_timestamp() should update the updated_at field."""
        entity = TestEntity(id=generate_uuid(), name="test")
        original_updated_at = entity.updated_at

        entity._update_timestamp()

        assert entity.updated_at >= original_updated_at


class TestGenerateUuid:
    """Tests for generate_uuid utility."""

    def test_generates_uuid_v4(self) -> None:
        """generate_uuid() should return a valid UUID."""
        result = generate_uuid()

        assert isinstance(result, UUID)
        assert result.version == 4

    def test_generates_unique_uuids(self) -> None:
        """Each call should generate a unique UUID."""
        uuid1 = generate_uuid()
        uuid2 = generate_uuid()

        assert uuid1 != uuid2
