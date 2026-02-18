"""LeaderboardPeriod — time windows for leaderboard ranking."""

from enum import Enum


class LeaderboardPeriod(Enum):
    """Time window for leaderboard ranking."""

    SEVEN_DAY = ("7-day", 168)
    THIRTY_DAY = ("30-day", 720)
    ALL_TIME = ("All-time", None)

    def __init__(self, display_label: str, interval_hours: int | None) -> None:
        self.display_label = display_label
        self._interval_hours = interval_hours

    @property
    def interval_hours(self) -> int | None:
        return self._interval_hours
