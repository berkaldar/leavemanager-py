# LeaveManager (Python/Flask)

Internal staff leave tracker. Project rules: `AGENTS.md`.

Setup (Windows; `python` here may be the Store stub, so use the full interpreter path once):

    <path-to-python-3.14>\python.exe -m venv .venv
    .venv\Scripts\python -m pip install -r requirements-dev.txt

Run (set the two required variables first, see `.env.example`; the app refuses to start without
them):

    $env:SECRET_KEY = "<a long random string>"
    $env:LEAVE_DEMO_PASSWORD = "<the demo password>"
    .venv\Scripts\python app.py

Address: http://localhost:5000 — sign in as `ayse`, `mehmet`, `zeynep` (HR), `ahmet` (manager) or
`elif`, all with the demo password.

Verify (the single check command, from Git Bash):

    ./scripts/check
