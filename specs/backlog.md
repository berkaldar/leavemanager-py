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
- **B-9** — debug=True hard-coded in app.run — Source: bootstrap 2026-11-21 (app.py:182) — Severity: high
  — Recommendation: FLASK_DEBUG env var, off by default — Deferred by: Berk, 2026-11-21, characterization tests first
- **B-10** — New-request page has no input validation and no proper error responses: an end date before the start date is stored; invalid input (bad date, missing field, unknown employee) is swallowed by a redirect; the balance error returns HTTP 200 with an internal code and a phone extension — Source: spec 0002 clarify, 2026-11-21 (app.py:157-171) — Severity: medium
  — Recommendation: validate at the route boundary, HTTP 400 with a plain message (docs/security.md, Input & output) — Deferred by: Berk, 2026-11-21, characterization tests first (spec 0003 pins it)
- **B-11** — Sign-in hardening: no rate limiting or account lockout; sessions are client-side signed cookies accepted for up to 31 days, with no idle timeout, and signing out does not revoke a copied cookie; a failed sign-in for a known username takes ~100 ms against ~1 ms for an unknown one (usernames can be told apart by timing) — Source: spec 0004 clarify and review round 1 (M-2, L-2), 2026-11-21 — Severity: medium (internal network only)
  — Recommendation: a later hardening spec once real accounts exist; throttle failed sign-ins per username and per address, add a session lifetime and server-side revocation, check unknown usernames against a dummy hash — Deferred by: Berk, 2026-11-21, kept out of the first authentication spec to keep it reviewable
- **B-12** — No security headers: the pages send no Content-Security-Policy (a second layer against script injection), and no other hardening headers (frame, content-type sniffing, referrer) — Source: spec 0005 clarify, 2026-11-21 — Severity: medium (internal network only)
  — Recommendation: a later spec that adds the headers and proves the three pages still work under them; the escaping fix (spec 0005) does not depend on it — Deferred by: Berk, 2026-11-21, new behavior with its own risks, kept out of the escaping fix
- **B-13** — The page headings ("Personel Bakiyeleri", "Izin Talepleri", "Yeni Talep" and the sign-in "Giris") are not pinned by any characterization test: changing one turns nothing red — Source: spec 0005 VERIFY, finding F-1, 2026-11-21 — Severity: low
  — Recommendation: pin each heading in the page tests of the next spec that touches those pages, so a refactor cannot rename one unnoticed — Deferred by: Berk, 2026-11-21, predates spec 0005 and is outside its scope
