# Backlog — deferred findings

Findings a human triaged as **defer**: real, but fixed later by decision (`workflows/feature-development.md`,
step 7). Nothing lands here without that decision; noise is rejected in the triage record, not parked here.

- A criterion moved out at the ship gate (R-08, `→ moved to B-<n>`) lands here too, by the
  human's ship decision; the entry names the spec and criterion.
- One entry per finding, newest last. Delete the entry in the commit of the work that closes it.
- An entry that grows into new behavior becomes a spec (`specs/active/`), not a fix.

<!-- Format (labels stay English):
- **B-<n>** — <finding, one line> — Source: spec <NNNN>, review round <n> (<file:line>) — Severity: <…>
  — Recommendation: <the reviewer's action> — Deferred by: <name>, <YYYY-MM-DD>, <why>
  A decision deferred at bootstrap (its REPORT) uses Source: bootstrap <YYYY-MM-DD>.
-->

- **B-1** — Entitlement for 1–5 years is 14 in code, 15 in the comment / HR handbook (BR-1) — Source: bootstrap 2026-11-21 (app.py:51) — Severity: high
  — Recommendation: get HR's table, then a CHANGE spec — Deferred by: Berk, 2026-11-21, needs HR's answer; pin current behavior first
- **B-2** — Seniority ignores month and day (BR-2) — Source: bootstrap 2026-11-21 (app.py:60) — Severity: high
  — Recommendation: anniversary-based years, leap-day hire date covered — Deferred by: Berk, 2026-11-21, needs HR's answer
- **B-3** — Request length counts calendar days; comment says working days (BR-3) — Source: bootstrap 2026-11-21 (app.py:78-80) — Severity: medium
  — Recommendation: decide weekends/public holidays with HR, then a CHANGE spec — Deferred by: Berk, 2026-11-21, needs HR's answer
- **B-4** — Pending requests do not reduce the balance; undecided since 2018 (BR-4) — Source: bootstrap 2026-11-21 (app.py:83) — Severity: medium
  — Recommendation: deduct pending requests, to prevent over-booking — Deferred by: Berk, 2026-11-21, needs HR's answer
- **B-5** — Balance check disagrees: route `<`, service `<=` (BR-5); service also returns success for an unknown employee and on exceptions — Source: bootstrap 2026-11-21 (app.py:93, 96, 106, 165) — Severity: high
  — Recommendation: one check in the service, failures reported — Deferred by: Berk, 2026-11-21, characterization tests first
- **B-6** — No CSRF protection on POST /new — Source: bootstrap 2026-11-21 (app.py:155) — Severity: medium
  — Recommendation: add with the AuthN spec (B-7) — Deferred by: Berk, 2026-11-21, matters once authentication exists
- **B-7** — No authentication or authorization — Source: bootstrap 2026-11-21 — Severity: medium (internal network only)
  — Recommendation: spec before any exposure beyond the intranet — Deferred by: Berk, 2026-11-21, internal use only today
- **B-8** — Stored XSS: reason and names rendered unescaped with |safe — Source: bootstrap 2026-11-21 (app.py:151) — Severity: high
  — Recommendation: escape all output; first spec after the characterization tests — Deferred by: Berk, 2026-11-21, characterization tests first
- **B-9** — debug=True hard-coded in app.run — Source: bootstrap 2026-11-21 (app.py:182) — Severity: high
  — Recommendation: FLASK_DEBUG env var, off by default — Deferred by: Berk, 2026-11-21, characterization tests first
