"""Characterization of the new-request page as it behaves today (spec 0003).

These pin current behavior, bugs included. A test marked "OPEN B-n" changes on purpose in the
spec that resolves backlog item B-n — never to get to green.

A redirect to /requests follows both a save and a silent loss, so every submission test also
asserts what was stored (Db.requests, Db.next_id).
"""
from datetime import date

import pytest

from app import Db

pytestmark = pytest.mark.http

AYSE, ELIF = "1", "5"


def submit(client, **fields):
    """POST the form; return (response, stored requests before, id sequence before)."""
    before = list(Db.requests)
    next_id = Db.next_id
    resp = client.post("/new", data=fields)
    return resp, before, next_id


def nothing_stored(before, next_id):
    return Db.requests == before and Db.next_id == next_id


# --- AC-1: the form --------------------------------------------------------------------------

def test_form_structure(client):
    resp = client.get("/new")
    assert resp.status_code == 200
    html = resp.get_data(as_text=True)
    assert '<form method="post">' in html
    assert '<select name="employee_id">' in html
    options = [f"<option value='{e['id']}'>{e['name']}</option>" for e in Db.employees]
    assert len(options) == 5
    positions = [html.index(o) for o in options]
    assert positions == sorted(positions)  # seed order
    assert html.count("<option") == 5  # exactly the five employees, no default empty choice
    assert '<input type="date" name="start">' in html
    assert '<input type="date" name="end">' in html
    assert '<input type="text" name="reason">' in html
    assert '<input type="submit" value="Kaydet">' in html


# --- AC-2: a valid request -------------------------------------------------------------------

def test_valid_request_is_stored_and_listed(client):
    resp, before, next_id = submit(client, employee_id=AYSE, start="2026-12-01",
                                   end="2026-12-13", reason="Tatil")
    # 13 calendar days (OPEN B-3) against 14 remaining (OPEN B-3, B-4: pending is not deducted)
    assert resp.status_code == 302
    assert resp.headers["Location"] == "/requests"
    assert Db.requests[:-1] == before
    assert Db.requests[-1] == {"id": next_id, "employee_id": 1, "start": date(2026, 12, 1),
                               "end": date(2026, 12, 13), "reason": "Tatil",
                               "status": "Beklemede"}
    assert Db.next_id == next_id + 1
    listed = client.get("/requests").get_data(as_text=True)
    assert "<td>2026-12-01</td><td>2026-12-13</td><td>13</td><td>Tatil</td>" in listed


# --- AC-3: a one-day request -----------------------------------------------------------------

def test_one_day_request_is_stored(client):
    resp, before, next_id = submit(client, employee_id=AYSE, start="2026-12-01",
                                   end="2026-12-01", reason="Tek gun")
    assert resp.status_code == 302
    assert len(Db.requests) == len(before) + 1
    assert Db.requests[-1]["status"] == "Beklemede"
    assert Db.next_id == next_id + 1


# --- AC-4: insufficient balance --------------------------------------------------------------

@pytest.mark.parametrize(
    ("employee_id", "start", "end"),
    [
        (AYSE, "2026-12-01", "2026-12-15"),  # 15 days, 14 remaining (OPEN B-3, B-4)
        (ELIF, "2026-12-01", "2026-12-01"),  # 0 remaining, 1 day
    ],
)
def test_insufficient_balance_shows_error_and_stores_nothing(client, employee_id, start, end):
    resp, before, next_id = submit(client, employee_id=employee_id, start=start, end=end,
                                   reason="Tatil")
    assert resp.status_code == 200  # OPEN B-10: an error page that is not an error response
    html = resp.get_data(as_text=True)
    assert "HATA" in html
    assert "bakiye yetersiz" in html
    assert nothing_stored(before, next_id)


def test_error_page_keeps_navigation_but_has_no_form(client):
    # 15 calendar days against 14 remaining: the error path depends on OPEN B-3, B-4
    resp, _, _ = submit(client, employee_id=AYSE, start="2026-12-01", end="2026-12-15")
    html = resp.get_data(as_text=True)
    assert '<a href="/">Ana Sayfa</a>' in html
    assert '<a href="/requests">Talepler</a>' in html
    assert '<a href="/new">Yeni Talep</a>' in html
    # no form except the sign-out form: the user's input is not kept (OPEN B-10; spec 0004,
    # Supersedes 0003/AC-4)
    assert html.count("<form") == 1
    assert '<form method="post" action="/logout">' in html


# --- AC-5: exactly enough balance (OPEN B-5, B-3) --------------------------------------------

def test_exactly_enough_balance_is_silently_lost(client):
    # Ayse: 14 remaining (OPEN B-4); 12-01…12-14 is 14 calendar days (OPEN B-3). The page lets it through,
    # the leave rules refuse it (<=), and the page redirects as if it had been saved (OPEN B-5).
    resp, before, next_id = submit(client, employee_id=AYSE, start="2026-12-01",
                                   end="2026-12-14", reason="Tatil")
    assert resp.status_code == 302
    assert resp.headers["Location"] == "/requests"
    assert nothing_stored(before, next_id)


# --- AC-6: end before start (OPEN B-10) ------------------------------------------------------

def test_end_before_start_is_stored_with_negative_length(client):
    resp, before, next_id = submit(client, employee_id=AYSE, start="2026-12-10",
                                   end="2026-12-08", reason="Ters")
    assert resp.status_code == 302
    assert resp.headers["Location"] == "/requests"
    assert Db.requests[-1]["start"] == date(2026, 12, 10)
    assert Db.requests[-1]["end"] == date(2026, 12, 8)
    assert Db.requests[-1]["status"] == "Beklemede"
    assert Db.next_id == next_id + 1
    listed = client.get("/requests").get_data(as_text=True)
    # length -1 is the calendar-day formula (OPEN B-3); rejecting the request is B-10
    assert "<td>2026-12-10</td><td>2026-12-08</td><td>-1</td><td>Ters</td>" in listed


# --- AC-7: invalid input (OPEN B-10) ---------------------------------------------------------

@pytest.mark.parametrize(
    "fields",
    [
        {"employee_id": AYSE, "end": "2026-12-02"},  # missing start
        {"employee_id": AYSE, "start": "2026-12-01"},  # missing end
        {"employee_id": AYSE, "start": "not-a-date", "end": "2026-12-02"},  # malformed date
        {"start": "2026-12-01", "end": "2026-12-02"},  # missing employee field
        {"employee_id": "abc", "start": "2026-12-01", "end": "2026-12-02"},  # non-numeric id
        {"employee_id": "999", "start": "2026-12-01", "end": "2026-12-02"},  # unknown employee
    ],
    ids=["no-start", "no-end", "bad-date", "no-employee", "non-numeric-id", "unknown-employee"],
)
def test_invalid_input_redirects_and_stores_nothing(client, fields):
    resp, before, next_id = submit(client, **fields)
    assert resp.status_code == 302
    assert resp.headers["Location"] == "/requests"  # no error message (OPEN B-10)
    assert nothing_stored(before, next_id)


# --- AC-8: a missing reason ------------------------------------------------------------------

def test_missing_reason_is_stored_empty(client):
    resp, before, _ = submit(client, employee_id=AYSE, start="2026-12-01", end="2026-12-01")
    assert resp.status_code == 302
    assert len(Db.requests) == len(before) + 1
    assert Db.requests[-1]["reason"] == ""


# --- AC-9: output is not escaped (OPEN B-8) --------------------------------------------------

def test_markup_in_reason_is_not_escaped(client):
    submit(client, employee_id=AYSE, start="2026-12-01", end="2026-12-01", reason="<b>x</b>")
    assert Db.requests[-1]["reason"] == "<b>x</b>"  # stored as given
    html = client.get("/requests").get_data(as_text=True)
    assert "<b>x</b>" in html  # OPEN B-8: rendered as markup
    assert "&lt;b&gt;x&lt;/b&gt;" not in html


def test_markup_in_employee_name_is_not_escaped_in_dropdown(client):
    Db.employees[0]["name"] = "<b>x</b>"
    html = client.get("/new").get_data(as_text=True)
    assert "<option value='1'><b>x</b></option>" in html  # OPEN B-8
    assert "&lt;b&gt;x&lt;/b&gt;" not in html
