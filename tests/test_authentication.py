"""Authentication: sign-in, sign-out, sessions and CSRF (spec 0004).

These tests use `anon_client`, a plain client that starts anonymous and carries no csrf_token of
its own: every sign-in goes through the real form, the way a browser does it. The demo password is
the throwaway one the test setup puts in the environment (tests/conftest.py).
"""
import os
import re

import pytest
from werkzeug.security import check_password_hash, generate_password_hash

from app import Db
from app import app as flask_app

pytestmark = pytest.mark.http

VALID_REQUEST = {"employee_id": "1", "start": "2026-12-01", "end": "2026-12-01", "reason": "Tatil"}


def password():
    return os.environ["LEAVE_DEMO_PASSWORD"]


def page_token(client, path="/login"):
    html = client.get(path).get_data(as_text=True)
    return re.search(r'name="csrf_token" value="([0-9a-f]+)"', html).group(1)


def login(client, username="zeynep", secret=None):
    """Sign in through the form, like a browser: fetch the page, then post it."""
    return client.post("/login", data={"username": username,
                                       "password": password() if secret is None else secret,
                                       "csrf_token": page_token(client)})


def session_value(client, key):
    with client.session_transaction() as sess:
        return sess.get(key)


def nothing_stored(before, next_id):
    return Db.requests == before and Db.next_id == next_id


# --- AC-1: anonymous visitors ----------------------------------------------------------------

@pytest.mark.parametrize("path", ["/", "/requests", "/new"])
def test_anonymous_pages_redirect_to_login(anon_client, path):
    resp = anon_client.get(path)
    assert resp.status_code == 302
    assert resp.headers["Location"] == "/login"


@pytest.mark.parametrize("path", ["/new", "/logout"])
@pytest.mark.parametrize("with_token", [False, True], ids=["no-token", "real-token"])
def test_anonymous_post_redirects_and_stores_nothing(anon_client, path, with_token):
    before, next_id = list(Db.requests), Db.next_id
    data = dict(VALID_REQUEST)
    if with_token:  # the redirect comes first, even with a genuine token of this session
        data["csrf_token"] = page_token(anon_client)
    resp = anon_client.post(path, data=data)
    assert resp.status_code == 302
    assert resp.headers["Location"] == "/login"
    assert nothing_stored(before, next_id)


def test_static_files_need_no_sign_in(anon_client):
    # AC-10: there are no static files today, so the answer is 404 — not a redirect to /login
    resp = anon_client.get("/static/x")
    assert resp.status_code == 404


# --- AC-2: the sign-in page ------------------------------------------------------------------

def test_login_page_form(anon_client):
    resp = anon_client.get("/login")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert html.count("<form") == 1  # no sign-out form for an anonymous visitor
    assert '<form method="post" action="/login">' in html
    assert '<input type="text" name="username">' in html
    assert '<input type="password" name="password">' in html
    assert re.search(r'<input type="hidden" name="csrf_token" value="[0-9a-f]{32}">', html)
    assert '<input type="submit" value="Giris">' in html


# --- AC-3: signing in ------------------------------------------------------------------------

def test_login_success_starts_session(anon_client):
    resp = login(anon_client)
    assert resp.status_code == 302
    assert resp.headers["Location"] == "/"
    cookie = next(c for c in resp.headers.getlist("Set-Cookie") if c.startswith("session="))
    assert "HttpOnly" in cookie
    assert "SameSite=Lax" in cookie
    assert "Secure" not in cookie  # plain HTTP on the internal network, a known limit
    for path in ("/", "/requests", "/new"):
        assert anon_client.get(path).status_code == 200
    html = anon_client.get("/").get_data(as_text=True)
    assert "zeynep" in html
    assert '<button type="submit">Cikis</button>' in html


def test_login_discards_earlier_session_data(anon_client):
    token = page_token(anon_client)
    with anon_client.session_transaction() as sess:
        sess["junk"] = "left over"
    anon_client.post("/login", data={"username": "zeynep", "password": password(),
                                     "csrf_token": token})
    with anon_client.session_transaction() as sess:
        assert "junk" not in sess
        assert sess["user"] == "zeynep"


# --- AC-4: failed sign-ins are generic and exact ---------------------------------------------

CASES = {
    "wrong-password": ("zeynep", lambda p: "wrong-password"),
    "unknown-user": ("nobody", lambda p: p),
    "case-differs": ("Zeynep", lambda p: p),
    "leading-space": (" zeynep", lambda p: p),
    "password-with-space": ("zeynep", lambda p: p + " "),
}


def failure_page(client, case):
    username, make_password = CASES[case]
    resp = login(client, username, make_password(password()))
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    return html, re.sub(r'value="[0-9a-f]{32}"', 'value="TOKEN"', html)


@pytest.mark.parametrize("case", CASES)
def test_failed_login_is_generic(anon_client, case):
    html, normalized = failure_page(anon_client, case)
    # the whole page is the same for every case, not only the message
    assert normalized == failure_page(flask_app.test_client(), "wrong-password")[1]
    assert html.count("Kullanici adi veya sifre hatali") == 1  # the same message for every case
    assert '<input type="password" name="password">' in html  # the sign-in page again
    assert session_value(anon_client, "user") is None
    assert anon_client.get("/").headers["Location"] == "/login"


# --- AC-5: signing out -----------------------------------------------------------------------

def test_logout_ends_session(anon_client):
    login(anon_client)
    resp = anon_client.post("/logout", data={"csrf_token": session_value(anon_client, "csrf")})
    assert resp.status_code == 302
    assert resp.headers["Location"] == "/login"
    assert session_value(anon_client, "user") is None
    for path in ("/", "/requests", "/new"):
        assert anon_client.get(path).headers["Location"] == "/login"
    assert anon_client.get("/login").status_code == 200


def test_signed_in_user_is_redirected_from_login(anon_client):
    login(anon_client)
    resp = anon_client.get("/login")
    assert resp.status_code == 302
    assert resp.headers["Location"] == "/"


# --- AC-6: CSRF ------------------------------------------------------------------------------

@pytest.mark.parametrize("token", [None, "wrong"], ids=["missing", "wrong"])
def test_login_rejects_bad_csrf_token(anon_client, token):
    anon_client.get("/login")  # starts the session and its token
    data = {"username": "zeynep", "password": password()}
    if token is not None:
        data["csrf_token"] = token
    assert anon_client.post("/login", data=data).status_code == 400
    assert session_value(anon_client, "user") is None


def test_login_without_a_session_token_gives_400(anon_client):
    data = {"username": "zeynep", "password": password(), "csrf_token": ""}
    assert anon_client.post("/login", data=data).status_code == 400  # no session, empty token
    assert session_value(anon_client, "user") is None


@pytest.mark.parametrize("token", [None, "wrong"], ids=["missing", "wrong"])
@pytest.mark.parametrize("path", ["/logout", "/new"])
def test_signed_in_post_rejects_bad_csrf_token(anon_client, path, token):
    login(anon_client)
    before, next_id = list(Db.requests), Db.next_id
    data = dict(VALID_REQUEST)
    if token is not None:
        data["csrf_token"] = token
    assert anon_client.post(path, data=data).status_code == 400
    assert session_value(anon_client, "user") == "zeynep"  # still signed in
    assert anon_client.get("/").status_code == 200
    assert nothing_stored(before, next_id)


def test_csrf_token_is_replaced_at_sign_in(anon_client):
    before_login = page_token(anon_client)
    token = anon_client.get("/login").get_data(as_text=True)
    assert before_login in token  # one token per session: the page shows the same one again
    login(anon_client)
    after_login = session_value(anon_client, "csrf")
    assert after_login != before_login
    assert anon_client.post("/logout", data={"csrf_token": before_login}).status_code == 400
    assert anon_client.post("/logout", data={"csrf_token": after_login}).status_code == 302


# --- AC-7: passwords and roles ---------------------------------------------------------------

def test_passwords_are_stored_hashed():
    secret = password()
    for user in Db.users:
        stored = user["password_hash"]
        assert stored != secret
        assert secret not in stored
        assert stored.count("$") == 2  # method$salt$hash
        assert check_password_hash(stored, secret)
        assert not check_password_hash(stored, "wrong-password")
    assert generate_password_hash(secret) != generate_password_hash(secret)  # salted


def test_seed_users_and_roles():
    assert [(u["username"], u["employee_id"], u["role"]) for u in Db.users] == [
        ("ayse", 1, "employee"),
        ("mehmet", 2, "employee"),
        ("zeynep", 3, "hr"),
        ("ahmet", 4, "manager"),
        ("elif", 5, "employee"),
    ]


def test_pages_are_identical_for_every_role():  # OPEN: roles change what is shown in spec 0005
    def pages_seen_by(username):
        client = flask_app.test_client()
        login(client, username)
        bodies = []
        for path in ("/", "/requests", "/new"):
            html = client.get(path).get_data(as_text=True)
            html = html.replace(username + " <input", "USER <input")  # the navigation's name
            bodies.append(re.sub(r'value="[0-9a-f]{32}"', 'value="TOKEN"', html))  # per-session
        return bodies

    assert pages_seen_by("elif") == pages_seen_by("ahmet") == pages_seen_by("zeynep")
