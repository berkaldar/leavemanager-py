# Spec 0004 — Authentication (sign-in, sign-out, sessions, CSRF)

- Status: In progress
- Mode: lite
- Plan: `specs/plans/0004-plan.md`
- Self-critique: done

## Intent
Today anyone who can reach LeaveManager can read every employee's leave balance and file a request
for anyone. Staff, managers and HR need to sign in before they see or do anything. Success means an
anonymous visitor reaches nothing but the sign-in page, a signed-in user sees and does exactly what
anyone could before, and a forged form post from another site cannot file a request. Roles are
recorded for every user but do not yet change what a user sees — that is spec 0005. Approving
requests, password changes, rate limiting and a real database are deliberately not part of this
work.

## Requirements
- R-1 Every page requires a signed-in user; the sign-in page is the only exception.
- R-2 Users sign in with a username and a password and can sign out.
- R-3 Passwords are never stored or logged in clear text, and never appear in the repository.
- R-4 Every form post carries a check that proves it came from the application's own page.
- R-5 The application does not serve anything unless its secrets are configured.
- R-6 For a signed-in user the three pages behave exactly as before (specs 0001–0003 stay true).
- R-7 Every user carries a role (employee, manager, HR); the role has no effect yet (spec 0005).

## User experience
- Flow: an anonymous visitor opens any page and lands on the sign-in page; enters a username and a
  password and presses "Giris"; lands on the dashboard; "Cikis" in the navigation signs out and
  returns to the sign-in page. After signing in the user always lands on the dashboard (no
  "return to the page I wanted").
- States: sign-in page (empty) · sign-in page after a failed attempt · signed in (navigation shows
  the username and "Cikis") · signed out. There is no loading state and no no-permission state
  (roles are spec 0005).
- Design reference: none — the flow above is the design. UI text is Turkish like the rest of the
  application: "Giris", "Cikis", "Kullanici adi", "Sifre", "Kullanici adi veya sifre hatali".
- Accessibility: none today (fields have no associated labels); not changed by this spec.
- Screenshots for SHIP (docs/testing.md, Evidence for UI criteria): the sign-in page, the sign-in
  page after a wrong password, the dashboard right after signing in — captured by VERIFY,
  headless, outside the repo, deleted after the SHIP gate.

## Constraints & out of scope
- Sensitive area: Leave balance calculation; Employee personal data; Authentication.
- No new dependency: password hashing and signed session cookies come from Flask and Werkzeug,
  which are already installed.
- Users are seeded in memory for the five fictional employees, one user per employee, username =
  first name in lowercase (ayse, mehmet, zeynep, ahmet, elif). Roles: zeynep = hr, ahmet =
  manager, ayse, mehmet and elif = employee. All five share one demo password that comes from the
  environment; real user and password management is a later spec. Known limit, documented in
  `docs/security.md`.
- Configuration comes from the environment: `SECRET_KEY` (signs the session cookie) and
  `LEAVE_DEMO_PASSWORD` (the demo password). Neither is ever committed.
- The session cookie is `HttpOnly` and `SameSite=Lax`. It is not marked `Secure`, because the
  application runs over plain HTTP on the internal network (known limit, `docs/security.md`).
- Out of scope: what each role may see or do (spec 0005); approving or rejecting requests;
  password change or reset; rate limiting, lockout and session expiry (B-11); debug mode (B-9);
  output escaping (B-8); validation and error responses (B-10); a "return to the page I wanted"
  redirect.
- Resolves backlog items B-7 and B-6; their entries are deleted in the ship commit.
- Supersedes: 0002/AC-7 (the exact list of pages and methods now includes `/login` and
  `/logout`; the request list may carry the sign-out form and its "Cikis" button, but still no
  other form or button and still no per-request link) and 0003/AC-4 (the error page has no form
  except the sign-out form; the user's input is still not kept). BR-7 stays fully pinned: no page
  can change a request's status. The other shipped tests keep their values; they run signed in.
- Split: proposed 0004 authentication → 0005 roles; accepted — Berk, 2026-11-21, size (≈15
  criteria as one spec).

## Acceptance criteria
"Today" is 2026-11-21 and the data is the seed data. `SECRET_KEY` and `LEAVE_DEMO_PASSWORD` are
set by the test setup.
- [ ] AC-1 — An anonymous visitor to the dashboard, the request list or the new-request page is
  redirected to `/login`; an anonymous post to `/new` or `/logout` is redirected to `/login` and
  nothing is stored — the redirect comes first, whatever the `csrf_token` (AC-6).
- [ ] AC-2 — The sign-in page answers HTTP 200 to an anonymous visitor and shows a form that
  posts to `/login` with a text field `username`, a password field `password`, a hidden field
  `csrf_token`, and a "Giris" button.
- [ ] AC-3 — Signing in with a seed username and the demo password redirects to `/`; from then on
  the dashboard, the request list and the new-request page answer HTTP 200 and the navigation
  shows the username and a "Cikis" button. The session cookie is `HttpOnly` and `SameSite=Lax`
  and is not marked `Secure`. Signing in discards any earlier session data.
- [ ] AC-4 — Usernames and passwords are matched exactly (no trimming, no case folding). A wrong
  password and an unknown username each answer HTTP 200 with the sign-in page
  and the same message "Kullanici adi veya sifre hatali"; no session is started and the
  protected pages still redirect to `/login`.
- [ ] AC-5 — Signing out (a post to `/logout`) ends the session: the protected pages redirect to
  `/login` again, and the sign-in page is shown. A signed-in user who opens `/login` is
  redirected to `/`.
- [ ] AC-6 — A post to `/login` (anonymous), or to `/logout` or `/new` (signed in), whose
  `csrf_token` is missing or wrong answers HTTP 400; no session is started or ended and nothing is
  stored. There is one token per session: it is created when the session starts and replaced when
  signing in. With a correct token the post behaves as in AC-3, AC-5 and spec 0003.
- [ ] AC-7 — Passwords are stored only as salted hashes (the stored value is never the demo
  password, and the demo password checks against it), and the demo password appears nowhere in
  the repository. Each seed user carries the role given in Constraints; the dashboard, the
  request list and the new-request page give identical responses to an employee, a manager and
  HR (OPEN, spec 0005).
- [ ] AC-8 — Starting the application (`python app.py`) without `SECRET_KEY`, or without
  `LEAVE_DEMO_PASSWORD`, exits with an error message that names the missing variable and serves
  nothing.
- [ ] AC-9 — For a user signed in as any seed user, the dashboard, the request list and the
  new-request page behave exactly as pinned by specs 0001–0003: the existing 59 tests pass with
  the same values and the same assertions, run signed in. The only edits to those test files are
  the sign-in fixture, the exact route list (AC-10), the removal of the B-7 notes in their
  docstrings, and two narrowed assertions (see Supersedes): on the request list, no form except
  the sign-out form, no button except "Cikis", exactly three navigation links and none per
  request; on the error page, no form except the sign-out form.
- [ ] AC-10 — The application answers exactly these pages and methods: `/` GET, `/requests`
  GET, `/new` GET and POST, `/login` GET and POST, `/logout` POST, and static files GET. Static
  files need no sign-in (there are none today).

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
