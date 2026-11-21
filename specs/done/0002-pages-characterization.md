# Spec 0002 — Read-only pages characterization (dashboard, request list, BR-7)

- Status: Shipped
- Mode: lite
- Plan: `specs/plans/0002-plan.md`
- Self-critique: done

## Intent
Spec 0001 pinned the leave rules; the pages people actually look at are still unprotected. Success
means automated tests that pin what the dashboard and the request list show **today** — the status
counts, the balance table, the request rows and their colored status labels, the empty state — and
that no page can approve or reject a request (BR-7). Known bugs are pinned and marked with their
backlog item, including the unescaped output (B-8). Nothing about the application changes: no bug
is fixed and the application code is not edited. The new-request page is pinned separately in
spec 0003.

## Requirements
- R-1 What the dashboard and the request list show for the seed data is pinned, value by value.
- R-2 The empty state of both pages is pinned.
- R-3 BR-7 is pinned: the application offers no way to change a request's status.
- R-4 Every pinned behavior that a backlog item disputes names that item (OPEN B-n).
- R-5 "Today" is 2026-11-21 and every test starts from the seed data (as in spec 0001).
- R-6 The tests run inside the single verification command.

## User experience
- Flow: a user opens the dashboard (home page) or the request list, through the links at the top
  of every page; both pages only display data.
- States: populated (seed data) and empty (no requests). There is no loading state (server-rendered
  pages), no error state reachable from these pages, and no no-permission state (no
  authentication — B-7).
- Design reference: none — the current pages are the design being pinned.
- Accessibility: none today (plain tables, no labels or landmarks); not changed by this spec.
- Screenshots for SHIP (docs/testing.md, Evidence for UI criteria): dashboard populated, dashboard
  empty, request list populated, request list empty — captured by VERIFY, headless, outside the
  repo, deleted after the SHIP gate.

## Constraints & out of scope
- Sensitive area: Leave balance calculation (the dashboard shows every employee's balance).
- The application code (`app.py`) stays byte-for-byte unchanged. A behavior that cannot be pinned
  without editing it is reported as a finding, not fixed.
- "Today" is fixed at 2026-11-21.
- Out of scope: the new-request page and its outcomes (spec 0003, B-10); fixing any backlog item;
  a request that points to a missing employee (the request list fails, but no page can create one);
  debug mode (B-9, not reachable through the pages); the status label matching "beklemede"
  case-insensitively while the dashboard count needs the exact value (no page can store another
  spelling).
- Split: proposed 0002 read-only pages → 0003 new-request page; accepted — Berk, 2026-11-21,
  size (≈13 criteria as one spec).

## Acceptance criteria
"Today" is 2026-11-21 and the data is the seed data unless a criterion says otherwise.
- [x] AC-1 — The dashboard shows the number of requests per status: pending (Bekleyen) 4,
  approved (Onaylanan) 1, rejected (Reddedilen) 3.
- [x] AC-2 — The dashboard's balance table has one row per employee, in seed order, with name,
  department, entitlement, used days and remaining: Ayse Yilmaz · IT · 26 · 12 · 14 (OPEN B-3,
  B-4); Mehmet Demir · Muhasebe · 20 · 0 · 20 (OPEN B-4); Zeynep Kaya · IK · 14 · 0 · 14 (OPEN
  B-1, B-4); Ahmet Celik · IT · 20 · 0 · 20 (OPEN B-4); Elif Sahin · Satis · 0 · 0 · 0.
- [x] AC-3 — The request list has one row per request, in stored order, with employee name, start,
  end, length in calendar days (OPEN B-3), reason and status — the eight seed requests:
  1. Ayse Yilmaz · 2026-07-06 · 2026-07-17 · 12 · Yaz tatili · Onaylandi
  2. Mehmet Demir · 2026-11-02 · 2026-11-04 · 3 · Aile ziyareti · Beklemede
  3. Zeynep Kaya · 2026-11-09 · 2026-11-09 · 1 · Saglik · Beklemede
  4. Ahmet Celik · 2026-12-21 · 2026-12-25 · 5 · Yilbasi oncesi · Beklemede
  5. Ayse Yilmaz · 2026-12-28 · 2026-12-30 · 3 · Yil sonu · Beklemede
  6. Elif Sahin · 2026-10-05 · 2026-10-07 · 3 · Tasinma · Reddedildi
  7. Zeynep Kaya · 2026-09-14 · 2026-09-25 · 12 · Uzun tatil · Reddedildi
  8. Mehmet Demir · 2026-08-03 · 2026-08-03 · 1 · Ozel is · Reddedildi
- [x] AC-4 — Each status label is colored through its inline style: Onaylandi `green`,
  Beklemede `orange`, Reddedildi `red`; any other status value `#999` (gray).
- [x] AC-5 — Empty state: with no requests stored, the dashboard counts are 0 / 0 / 0 and its
  balance table still lists all five employees with 0 used days; the request list shows its
  header row and no request rows.
- [x] AC-6 — Output is not escaped (OPEN B-8): text containing `<b>x</b>` appears in the page as
  `<b>x</b>`, not as `&lt;b&gt;x&lt;/b&gt;` — an employee name on the dashboard and on the
  request list, a department on the dashboard, and a reason on the request list.
- [x] AC-7 — No page can change a request's status (BR-7): the application answers only the
  dashboard, the request list and the new-request page (plus static files), and the request list
  offers no form, button or link per request.
- [x] AC-8 — Both pages answer with HTTP 200 and carry the page title "LeaveManager" and the
  links to the dashboard (Ana Sayfa), the request list (Talepler) and the new-request page
  (Yeni Talep).

## Definition of Done
- [x] Every acceptance criterion mapped to proof (test or reproducible observation)
- [x] `scripts/check` green
- [x] Independent review done; real findings fixed, noise rejected with written rationale, deferred ones in `specs/backlog.md`
- [x] Docs / ADRs updated if behavior or architecture changed
- [x] Spec moved to `specs/done/` (it becomes immutable there)

## Scorecard (fill at ship — honest numbers make the process improvable)
| Metric | Value |
|---|---|
| Spec revisions | 0 |
| Fix rounds | 1 |
| Review findings: real / noise / deferred | 2 / 0 / 0 |
| Regressions introduced | 0 |
| Bugs escaped to production | 0 |
