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
    assert '<input type="date" name="start">' in html
    assert '<input type="date" name="end">' in html
    assert '<input type="text" name="reason">' in html
    assert '<input type="submit" value="Kaydet">' in html


# --- AC-2: a valid request -------------------------------------------------------------------

def test_valid_request_is_stored_and_listed(client):
    resp, before, next_id = submit(client, employee_id=AYSE, start="2026-12-01",
                                   end="2026-12-13", reason="Tatil")  # 13 days, 14 remaining
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
