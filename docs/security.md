# Security

> Baseline rules agents must honor in every plan and review. Set at bootstrap 2026-11-21.

## Exposure
LeaveManager runs on an internal network only. It has **no authentication**: anyone who can reach
it can create a request for any employee. Exposing it beyond the intranet requires the AuthN spec
first (B-7).

## Secrets
- Secrets never enter the repo, specs, prompts, or chat. `.env` is gitignored; provide `.env.example`.
- Agents never print secret values, even when debugging.
- The app has no secrets today. A future `SECRET_KEY` (sessions, CSRF) comes from the environment.

## Input & output
- Validate at the route boundary (the trust boundary): dates parsed strictly as `YYYY-MM-DD`,
  end ≥ start, the employee must exist, reason length limited. Invalid input → HTTP 400 with a
  plain message.
- **All output is escaped.** User-supplied text (reason) and stored data (names, departments) are
  HTML-escaped before rendering; `|safe` only on markup built from escaped parts.
- Error pages never show stack traces, internal error codes or contact details.
- Debug mode is off by default; it is enabled only through the `FLASK_DEBUG` environment variable,
  never in code.

## Known findings (bootstrap 2026-11-21)
- **High — stored XSS:** reason and names are rendered unescaped with `|safe` (`app.py:151`).
  First spec after the characterization tests (B-8).
- **High — debug mode in code:** `app.run(debug=True)` (`app.py:182`) exposes the Werkzeug
  debugger (B-9).
- **Medium — no CSRF protection** on `POST /new`; matters once authentication exists (B-6).

## Personal data
- Employee names and hire dates are personal data (KVKK / GDPR). Seed and test data stay
  fictional; personal data never goes into logs, specs or chat.

## AuthN / AuthZ
- None today (see Exposure). Default when added: deny unauthenticated requests to every route.

## Dependencies
- Exact pinned versions in `requirements.txt` / `requirements-dev.txt`.
- A new dependency needs a spec and human approval; check license, maintenance and known CVEs.
  No dependency for a few lines of code.
- `pip-audit` in `scripts/check` is a suggested later addition, not adopted at bootstrap.

## Review lens
Security is a mandatory dimension of every independent review (see `prompts/review.md`), not a
separate afterthought phase.
