from datetime import date, datetime

import pytest
from flask.testing import FlaskClient

import app

TODAY = date(2026, 11, 21)
# Throwaway test values; the running app takes its real ones from the environment (docs/security.md).
TEST_PASSWORD = "test-only-password"
TEST_SECRET = "test-only-secret-key"
TEST_CSRF = "test-only-csrf-token"


class FrozenDatetime(datetime):
    """datetime whose now() is TODAY; strptime and the rest behave as usual."""

    @classmethod
    def now(cls, tz=None):
        return cls(TODAY.year, TODAY.month, TODAY.day, 12, 0, 0, tzinfo=tz)


class TokenClient(FlaskClient):
    """Signed-in client for the page tests: form posts carry the session's csrf_token."""

    def open(self, *args, **kwargs):
        data = kwargs.get("data")
        if kwargs.get("method") == "POST" and isinstance(data, dict) and "csrf_token" not in data:
            with self.session_transaction() as sess:
                kwargs["data"] = {**data, "csrf_token": sess.get("csrf", "")}
        return super().open(*args, **kwargs)


@pytest.fixture(autouse=True)
def leave_state(monkeypatch):
    monkeypatch.setenv("LEAVE_DEMO_PASSWORD", TEST_PASSWORD)
    monkeypatch.setattr(app.app, "secret_key", TEST_SECRET)
    # Db is global module state: reset it so no test sees another's data (docs/conventions.md).
    app.seed()
    # The rules read datetime.now() directly; the clock is not injectable yet (docs/testing.md).
    monkeypatch.setattr(app, "datetime", FrozenDatetime)


@pytest.fixture
def client():
    """Signed in as the HR user (set through the session, no password hashing per test)."""
    signed_in = TokenClient(app.app, app.app.response_class)
    with signed_in.session_transaction() as sess:
        sess["user"] = "zeynep"
        sess["csrf"] = TEST_CSRF
    return signed_in


@pytest.fixture
def anon_client():
    return app.app.test_client()
