# Security

> Baseline rules agents must honor in every plan and review. Set at bootstrap 2026-11-21.

## Exposure
LeaveManager runs on an internal network only, over plain HTTP. Every page requires a signed-in
user (spec 0004); what each role may see or do is spec 0005 (roles are stored, not yet enforced:
any signed-in user sees everything). Do not expose it beyond the intranet before B-9 (debug mode)
and B-11 (no rate limiting) are closed and the demo accounts below are replaced.

## Secrets
- Secrets never enter the repo, specs, prompts, or chat. `.env` is gitignored; provide `.env.example`.
- Agents never print secret values, even when debugging.
- Two values come from the environment and are required to start the app (`python app.py` exits
  with an error naming the missing one): `SECRET_KEY` (signs the session cookie) and
  `LEAVE_DEMO_PASSWORD` (the shared password of the five seed accounts). `.env.example` lists the
  names only; the app does not read a `.env` file, set them in the shell.
- Tests use throwaway fake values (`tests/conftest.py`), never the real ones.

## Input & output
- Validate at the route boundary (the trust boundary): dates parsed strictly as `YYYY-MM-DD`,
  end ≥ start, the employee must exist, reason length limited. Invalid input → HTTP 400 with a
  plain message.
- **All output is escaped.** User-supplied text (reason) and stored data (names, departments,
  statuses) are HTML-escaped before rendering, with `esc()` in `app.py` (the standard library's
  `html.escape`, all five special characters); `|safe` only on markup built from escaped parts.
  Every new place that puts stored text into page markup must call `esc()` — a test per place
  (`tests/test_escaping.py`) is the proof. The navigation username is escaped by the template.
- Error pages never show stack traces, internal error codes or contact details.
- Debug mode is off by default; it is enabled only through the `FLASK_DEBUG` environment variable,
  never in code.

## Known findings (bootstrap 2026-11-21)
- **Medium — no security headers (B-12):** no Content-Security-Policy, which would be a second layer
  against script injection, and no other hardening headers. The escaping above does not depend on it.
- **High — debug mode in code:** `app.run(debug=True)` (`app.py:273`) exposes the Werkzeug
  debugger (B-9); the debugger's console sits outside the sign-in guard and is protected only by
  its PIN.
- **Medium — sign-in hardening missing (B-11):** no rate limiting or lockout; failed sign-ins for a
  known username take ~100 ms and for an unknown one ~1 ms, so usernames can be told apart by
  timing (they are public anyway).
- **Medium — sessions are client-side signed cookies:** the server accepts one for up to 31 days
  after sign-in (Flask's default permanent-session lifetime), and **signing out does not revoke a
  copy of the cookie** (a replayed pre-logout cookie still works). Over plain HTTP a sniffed cookie
  is therefore valid for up to 31 days. A session lifetime and server-side revocation belong to
  B-11.
- `python app.py` is the only supported way to serve the app: it checks `SECRET_KEY` and
  `LEAVE_DEMO_PASSWORD` first. Served some other way without them, the app answers no data:
  without `SECRET_KEY` the sign-in page fails with a 500, and without `LEAVE_DEMO_PASSWORD` the
  page works but every sign-in fails.
- **Limits of the first authentication (spec 0004):** the five demo accounts share one password
  (real user and password management is a later spec); the session cookie is not `Secure`
  because the app runs over plain HTTP; sign-in always lands on the dashboard (no "return to the
  page I wanted", so there is no open-redirect surface).

## Personal data
- Employee names and hire dates are personal data (KVKK / GDPR). Seed and test data stay
  fictional; personal data never goes into logs, specs or chat.

## AuthN / AuthZ
- Sign-in with a username and password (Werkzeug salted hashes, exact match); the generic message
  "Kullanici adi veya sifre hatali" for every failure; the session cookie is `HttpOnly` and
  `SameSite=Lax`. Default: deny unauthenticated requests to every route except `/login` and static
  files; an anonymous visitor is redirected before any other check.
- **CSRF:** one token per session (replaced at sign-in), a hidden `csrf_token` in every form, checked
  on every POST (HTTP 400 when missing or wrong).
- Roles (`employee`, `manager`, `hr`) are stored per user; enforcing them is spec 0005.

## Dependencies
- Exact pinned versions in `requirements.txt` / `requirements-dev.txt`.
- A new dependency needs a spec and human approval; check license, maintenance and known CVEs.
  No dependency for a few lines of code.
- `pip-audit` in `scripts/check` is a suggested later addition, not adopted at bootstrap.

## Review lens
Security is a mandatory dimension of every independent review (see `prompts/review.md`), not a
separate afterthought phase.
