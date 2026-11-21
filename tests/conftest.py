from datetime import date, datetime

import pytest

import app

TODAY = date(2026, 11, 21)


class FrozenDatetime(datetime):
    """datetime whose now() is TODAY; strptime and the rest behave as usual."""

    @classmethod
    def now(cls, tz=None):
        return cls(TODAY.year, TODAY.month, TODAY.day, 12, 0, 0, tzinfo=tz)


@pytest.fixture(autouse=True)
def leave_state(monkeypatch):
    # Db is global module state: reset it so no test sees another's data (docs/conventions.md).
    app.seed()
    # The rules read datetime.now() directly; the clock is not injectable yet (docs/testing.md).
    monkeypatch.setattr(app, "datetime", FrozenDatetime)
