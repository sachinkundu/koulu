"""Tests for PointTransaction value object."""

from uuid import uuid4

import pytest

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
        with pytest.raises(AttributeError):
            txn.points = 5  # type: ignore[misc]
