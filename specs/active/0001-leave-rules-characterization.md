# Spec 0001 — Leave rules characterization (BR-1…BR-6)

- Status: In progress
- Mode: lite
- Plan: `specs/plans/0001-plan.md`
- Self-critique: done

## Intent
The LeaveManager maintainer needs a safety net before any legacy leave rule or security fix is
touched. Success means automated tests that pin how the leave rules behave **today** — warts
included — with every known bug marked by its backlog item (B-1…B-5), so a later fix changes
exactly the tests it should and nothing else. Nothing about the application's behavior changes in
this work: no rule is corrected, no bug is fixed, and the application code is not edited. The
three pages are pinned separately in spec 0002.

## Requirements
- R-1 The leave rules BR-1…BR-6 (`docs/domain.md`) are pinned as they behave today, including
  their boundary values.
- R-2 Every pinned behavior that a backlog item disputes names that item (e.g. "current behavior,
  OPEN B-1"), so the spec that resolves it knows which test it changes.
- R-3 Results do not depend on the date the tests run: "today" is 2026-11-21 for every test.
- R-4 Every test starts from the seed data, so results do not depend on test order.
- R-5 The tests run inside the single verification command, so every later change is checked
  against them.

## User experience
none — no user interface (the pages are spec 0002).

## Constraints & out of scope
- Sensitive area: Leave balance calculation.
- The application code (`app.py`) stays byte-for-byte unchanged. A behavior that cannot be pinned
  without editing it is reported as a finding, not fixed.
- "Today" is fixed at 2026-11-21.
- Out of scope: fixing any backlog item (B-1…B-9); the pages and their own balance check (spec
  0002); BR-7 (no approve/reject action — spec 0002); year-end carry-over (inactive code).
- Split: proposed 0001 leave rules (BR-1…BR-6) → 0002 pages (dashboard, request list, new
  request, BR-7); accepted — Berk, 2026-11-21, size (≈15 criteria as one spec).

## Acceptance criteria
"Today" is 2026-11-21 in every criterion.
- [ ] AC-1 — Seniority is the current calendar year minus the hire year, month and day ignored
  (OPEN B-2): hired 2025-12-31 → 1 year; hired 2026-06-01 → 0 years; hired 2020-02-29 (leap
  day) → 6 years, without error.
- [ ] AC-2 — Entitlement by seniority (OPEN B-1 for 1–5 years), by hire year: 2026 (0 years)
  → 0 days; 2025 (1) → 14; 2021 (5) → 14; 2020 (6) → 20; 2011 (15) → 20; 2010 (16) → 26.
- [ ] AC-3 — Request length counts calendar days with both ends included (OPEN B-3): a one-day
  request → 1; 2026-07-06…2026-07-17 (spans two weekends) → 12; an end date one day before the
  start date → 0, without error.
- [ ] AC-4 — Used days count only approved requests (BR-4): with the seed data, Ayse Yilmaz has
  12 used days (her approved 2026-07-06…17 request; her pending 2026-12-28…30 request does not
  count); Mehmet Demir, Zeynep Kaya and Elif Sahin, who have only pending or rejected requests,
  have 0.
- [ ] AC-5 — Remaining is entitlement minus used days, for the five seed employees: Ayse Yilmaz
  26 − 12 = 14; Mehmet Demir 20 − 0 = 20; Zeynep Kaya 14 − 0 = 14; Ahmet Celik 20 − 0 = 20;
  Elif Sahin 0 − 0 = 0. Remaining has no floor: an employee with 0 entitlement and 3 approved
  days has −3.
- [ ] AC-6 — A request shorter than the remaining balance is accepted — Ayse Yilmaz (14
  remaining) and a 13-day request: it is stored as pending
  (`Beklemede`) with the next id, the id sequence advances by one, and the employee's remaining
  balance is unchanged afterwards (pending requests are not deducted — OPEN B-4).
- [ ] AC-7 — A request is refused, and nothing is stored, when the remaining balance is less
  than **or equal to** its length (OPEN B-5): 14 days remaining and a 14-day request → refused;
  an employee with 0 entitlement and a 1-day request → refused.
- [ ] AC-8 — A request for an employee id that does not exist reports success, and nothing is
  stored (OPEN B-5).
- [ ] AC-9 — A request given directly to the leave rules (not through a page) with its dates
  missing reports success, and nothing is stored: the failure is swallowed (OPEN B-5).
- [ ] AC-10 — A request that starts before today is accepted like any other (BR-6:
  back-dated entries by HR).

## Definition of Done
- [ ] Every acceptance criterion mapped to proof (test or reproducible observation)
- [ ] `scripts/check` green
- [ ] Independent review done; real findings fixed, noise rejected with written rationale, deferred ones in `specs/backlog.md`
- [ ] Docs / ADRs updated if behavior or architecture changed
- [ ] Spec moved to `specs/done/` (it becomes immutable there)

## Scorecard (fill at ship — honest numbers make the process improvable)
| Metric | Value |
|---|---|
| Spec revisions | |
| Fix rounds | |
| Review findings: real / noise / deferred | |
| Regressions introduced | |
| Bugs escaped to production | |
