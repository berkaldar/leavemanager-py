# Spec 0003 — New-request page characterization

- Status: In progress
- Mode: lite
- Plan: `specs/plans/0003-plan.md`
- Self-critique: done

## Intent
Specs 0001 and 0002 pinned the leave rules and the read-only pages. The page where people create a
request is still unprotected, and it holds most of the known bugs. Success means automated tests
that pin what the new-request page shows and what **every way of submitting it** does today, with
each bug marked by its backlog item (B-5, B-8, B-10) — including the cases where a request is
silently lost or stored with impossible dates. Nothing about the application changes: no bug is
fixed and the application code is not edited. With this spec shipped the characterization is
complete and fix work can start.

## Requirements
- R-1 The new-request form is pinned: its fields, their names and the employee choices.
- R-2 Every outcome of submitting the form is pinned by both the response and the stored data —
  a redirect alone does not tell a saved request from a lost one.
- R-3 The balance boundaries around the submit check are pinned.
- R-4 Every pinned behavior that a backlog item disputes names that item (OPEN B-n).
- R-5 "Today" is 2026-11-21 and every test starts from the seed data (as in specs 0001–0002).
- R-6 The tests run inside the single verification command.

## User experience
- Flow: a user opens "Yeni Talep" from the navigation, picks an employee, enters a start date, an
  end date and a reason, and presses "Kaydet". On success the request list opens; on insufficient
  balance an error page is shown instead.
- States: empty form · success (request list after the redirect) · insufficient balance (error
  page). Invalid input has no message of its own: the user lands on the request list with nothing
  saved (OPEN B-10). There is no loading state and no no-permission state (no authentication —
  B-7).
- Design reference: none — the current page is the design being pinned.
- Accessibility: none today (fields have no associated labels); not changed by this spec.
- Screenshots for SHIP (docs/testing.md, Evidence for UI criteria): the empty form, the
  insufficient-balance error page, and the request list after a successful submit — captured by
  VERIFY, headless, outside the repo, deleted after the SHIP gate.

## Constraints & out of scope
- Sensitive area: Leave balance calculation (the page runs its own balance check).
- The application code (`app.py`) stays byte-for-byte unchanged. A behavior that cannot be pinned
  without editing it is reported as a finding, not fixed.
- "Today" is fixed at 2026-11-21.
- Out of scope: fixing any backlog item (B-5, B-8, B-10); the exact text of the error message
  beyond its stable part (its internal code and phone extension are not pinned — B-10); the
  browser-side date picker; debug mode (B-9); the dashboard and request list themselves (spec
  0002).
- Split: considered 0003 form / 0004 outcomes; kept as one — Berk, 2026-11-21, one page, one
  shared setup.

## Acceptance criteria
"Today" is 2026-11-21 and the data is the seed data unless a criterion says otherwise. "Stored"
means `Db.requests` and `Db.next_id`; "nothing stored" means both unchanged.
- [ ] AC-1 — The page shows a form that submits with POST, with: an employee dropdown named
  `employee_id` listing the five employees in seed order (value = id); date inputs named `start`
  and `end`; a text input named `reason`; and a "Kaydet" submit button. The page answers with
  HTTP 200.
- [ ] AC-2 — A valid request is accepted and the user is redirected to the request list: Ayse
  Yilmaz (14 remaining) for 13 days (2026-12-01…2026-12-13) is stored as pending (`Beklemede`)
  with the next id, and then appears on the request list.
- [ ] AC-3 — A one-day request is accepted and stored as pending.
- [ ] AC-4 — Insufficient balance: Ayse Yilmaz (14 remaining) for 15 days returns HTTP 200 with
  an error message that contains "HATA" and "bakiye yetersiz", and nothing is stored. The error
  page keeps the navigation links but has no form, so the user's input is not kept. An
  employee with 0 days remaining (Elif Sahin) and a one-day request gets the same message and
  nothing is stored. The message also exposes an internal error code and a phone extension
  (OPEN B-10; their text is not pinned).
- [ ] AC-5 — Exactly enough balance (OPEN B-5, B-3): Ayse Yilmaz (14 remaining) for 14 days
  redirects to the request list as if saved, but **nothing is stored**.
- [ ] AC-6 — An end date before the start date is accepted and stored, with a negative length
  (OPEN B-10): start 2026-12-10, end 2026-12-08 redirects to the request list, the request is
  stored pending, and the request list shows its length as −1.
- [ ] AC-7 — Invalid input redirects to the request list and nothing is stored, with no error
  message (OPEN B-10): a missing start date; a missing end date; a malformed date; a missing
  employee field; a non-numeric employee id; an employee id that does not exist.
- [ ] AC-8 — A missing reason is accepted: the request is stored with an empty reason.
- [ ] AC-9 — Markup in the reason is stored as given and shown unescaped on the request list
  (OPEN B-8): `<b>x</b>` appears as `<b>x</b>`, not as `&lt;b&gt;x&lt;/b&gt;`; when an employee's name is
  `<b>x</b>`, the dropdown option text is `<b>x</b>`, unescaped.

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
