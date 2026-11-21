# Conventions

> Only rules that are real: every rule here is enforced by tooling or checked in review.
> They apply to **new and changed code**; existing code follows them when a spec touches it.

## Language
- Chat language (interviews, sessions): English
- Document language (docs/, specs, plans, ADRs, review and verify reports): English
- Always English (protocol, not prose): ANEW core files, template headings and field labels,
  `Status:` values (Draft / Approved / In progress / Shipped), `Approved by / on:`, `Source:`.
- Code identifiers, branch names, commit messages: English.
- UI text shown to users: Turkish (the product language) — separate from the document language.
- Agent messages (handoff summaries, refusals, `Next:` lines): chat language; command names, file
  paths and protocol fields verbatim.

## Language & framework versions
- Python 3.14 (3.14.6 on the development machine), in the project venv `.venv/`.
- Flask 3.1 — pinned in `requirements.txt`; dev tools (pytest, ruff) pinned in
  `requirements-dev.txt`.
- Always run tools through `.venv/Scripts/python -m <tool>` (see Known traps).

## Naming
- PEP 8, snake_case functions and variables, English identifiers for new code.
- Existing Turkish identifiers are not renamed in bulk — only inside a spec that touches them.
- Tests: `tests/test_<area>.py`, test functions `test_<behavior>`.

## Error handling
- No silent failure: never `except: pass`, never `return True` (or a success redirect) after a
  failure.
- Invalid user input → a visible message and HTTP 400. Unexpected errors propagate (Flask 500)
  and are logged; internals (stack traces, error codes, phone extensions) never reach the page.
- Catch the specific exception you expect (`ValueError` from date parsing), not `Exception`.

## Data rules
- Dates are `datetime.date`; business rules receive "today" as a parameter (injectable clock).
- Day counts are integers; request periods are inclusive at both ends (`docs/domain.md`).
- Status values are compared through named constants, never string literals or `.lower()`.
- HTML output is escaped (Jinja autoescape); `|safe` only on markup built from escaped parts.

## Known traps
- `Db` is class-level global state shared by every request and test — call `seed()` before each
  test; never rely on test order — from bootstrap 2026-11-21.
- `datetime.now()` inside rules makes results depend on the run date — freeze or inject the clock
  in tests — from bootstrap 2026-11-21.
- Leap-day hire date (employee 4, 2020-02-29) — any anniversary-based seniority must handle
  Feb 28/29 in non-leap years — from bootstrap 2026-11-21.
- `render_template_string(PAGE, body=...)` renders `body` with `|safe` — everything put into
  `body` must already be escaped — from bootstrap 2026-11-21.
- Status strings are Turkish without diacritics and case-sensitive (`Onaylandi`, not
  `Onaylandı`) — use the constants — from bootstrap 2026-11-21.
- On this Windows machine `python` resolves to the Microsoft Store stub — always call
  `.venv/Scripts/python` — from bootstrap 2026-11-21.
- `app.run(debug=True)` exposes the Werkzeug debugger (remote code execution) — tests never call
  `app.run`; use `app.test_client()` — from bootstrap 2026-11-21.
- A redirect to `/requests` after POST does not mean the request was saved: exceptions are
  swallowed today — assert on the stored data — from bootstrap 2026-11-21.

## Enforced by tooling
- `ruff check --isolated --select E4,E7,E9,F` (syntax errors, undefined names, unused imports
  and variables) — in `scripts/check`. `--isolated` ignores any machine-level ruff config and
  `--select` pins the rules, so every machine and ruff version lints the same. ruff 0.17's wider
  default set (UP, RUF, BLE…) reports 14 style findings on the legacy `app.py`; adopting it is a
  later decision (proposed, not imposed).
