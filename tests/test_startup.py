"""Start-up configuration (spec 0004, AC-8): the application serves nothing without its secrets.

The cases that must fail are run as a real subprocess (`python app.py`); each exits at once, so no
server is ever started. They are in the fast profile on purpose (no `http` marker).
"""
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
VARIABLES = ("SECRET_KEY", "LEAVE_DEMO_PASSWORD")


def start_app(**given):
    env = {k: v for k, v in os.environ.items() if k not in VARIABLES}
    env.update(given)
    # FLASK_RUN_FROM_CLI makes app.run() return without serving, so a regression of the start-up
    # check fails this test instead of hanging it with a debug server left running (on Windows a
    # timeout kills only the venv launcher, and the server child keeps the pipes open).
    env["FLASK_RUN_FROM_CLI"] = "true"
    return subprocess.run([sys.executable, "-B", "app.py"], cwd=ROOT, env=env,
                          stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=30)


@pytest.mark.parametrize(
    ("given", "named", "not_named"),
    [
        ({}, ["SECRET_KEY", "LEAVE_DEMO_PASSWORD"], []),
        ({"SECRET_KEY": "test-only-secret"}, ["LEAVE_DEMO_PASSWORD"], ["SECRET_KEY"]),
        ({"LEAVE_DEMO_PASSWORD": "test-only-password"}, ["SECRET_KEY"], ["LEAVE_DEMO_PASSWORD"]),
    ],
    ids=["neither", "no-password", "no-secret-key"],
)
def test_startup_requires_configuration(given, named, not_named):
    result = start_app(**given)
    assert result.returncode != 0
    assert result.stdout == ""
    for name in named:
        assert name in result.stderr
    for name in not_named:
        assert name not in result.stderr
    assert "Running on" not in result.stderr  # nothing was served
