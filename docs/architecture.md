# Architecture

> Describes the architecture decided at bootstrap (2026-11-21): the current state and the target
> layering it moves toward. Agents read this file before planning.

## System overview
LeaveManager is a small server-rendered Flask monolith in one file, `app.py`. Data lives in memory
(`Db`, filled by `seed()` at import), so nothing persists across restarts. The target is three
layers — web → service → store — reached **incrementally**, one `/refactor` spec at a time and only
under characterization tests; there is no big-bang rewrite. Splitting `app.py` into files is itself
a later refactor spec, not a bootstrap decision.

## Modules / components and ownership

| Module | Single responsibility | Owns |
|---|---|---|
| web (Flask routes, `PAGE` template) | HTTP: parse and validate input, call the service, render HTML | Routes, templates, UI text (Turkish) |
| service (`LeaveService`) | Leave rules: seniority, entitlement, request length, balance, request creation | Business rules BR-1…BR-7 (`docs/domain.md`) |
| store (`Db`, `seed()`) | Holding employees, requests and users | Employee, request and user records (a user: username, role, password hash, linked employee), id sequence |

## Communication rules
- web → service → store, by direct function calls.
- web may read from store directly only to list records (dropdowns, tables); every calculation
  goes through the service.
- "Today" enters the service as a value (injectable clock), never from `datetime.now()` inside a
  rule — target state; see Known current violations.

## Forbidden dependencies (make them testable)
- The service never imports Flask, reads `request`, or returns HTML/markup.
- The store never imports the service or web.
- Routes never re-implement a business rule (day count, balance check, entitlement).

## Known current violations (debt, fixed by `/refactor` specs after characterization tests)
- `LeaveService.status_badge` returns HTML from the service.
- `new_request` repeats the day count and the balance check of the service (`app.py:241-243`).
- Routes do their own employee lookups.
- Rules call `datetime.now()` internally.

## Deliberately out of scope
- Persistence (a real database) — a future spec.
- Role enforcement (who may see or do what, spec 0005) and everything in `docs/security.md`
  marked as a later spec. Sign-in, sessions and CSRF protection exist since spec 0004 (a
  `before_request` guard in the web layer).
- Approve/reject workflow, year-end carry-over.
- Any JavaScript front end or API.
