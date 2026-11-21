"""Characterization of the read-only pages and BR-7 as they behave today (spec 0002).

These pin current behavior, bugs included. A test marked "OPEN B-n" changes on purpose in the
spec that resolves backlog item B-n — never to get to green.
"""
from html.parser import HTMLParser

import pytest

from app import Db

pytestmark = pytest.mark.http


class _TableReader(HTMLParser):
    """Collects every table row as a list of its cells' text."""

    def __init__(self):
        super().__init__()
        self.rows = []
        self._row = None
        self._cell = None

    def handle_starttag(self, tag, attrs):
        if tag == "tr":
            self._row = []
        elif tag in ("td", "th") and self._row is not None:
            self._cell = []

    def handle_endtag(self, tag):
        if tag in ("td", "th") and self._cell is not None:
            self._row.append("".join(self._cell).strip())
            self._cell = None
        elif tag == "tr" and self._row is not None:
            self.rows.append(self._row)
            self._row = None

    def handle_data(self, data):
        if self._cell is not None:
            self._cell.append(data)


def page(client, path):
    resp = client.get(path)
    assert resp.status_code == 200
    return resp.get_data(as_text=True)


def table_rows(html):
    reader = _TableReader()
    reader.feed(html)
    return reader.rows


DASHBOARD_HEADER = ["Ad", "Birim", "Hak", "Kullanilan", "Kalan"]
LIST_HEADER = ["Personel", "Baslangic", "Bitis", "Gun", "Neden", "Durum"]


# --- AC-1: counts per status ----------------------------------------------------------------

def test_dashboard_counts_requests_per_status(client):
    html = page(client, "/")
    assert "Bekleyen: <b>4</b>" in html
    assert "Onaylanan: <b>1</b>" in html
    assert "Reddedilen: <b>3</b>" in html


# --- AC-2: balance table --------------------------------------------------------------------

def test_dashboard_balance_table(client):
    assert table_rows(page(client, "/")) == [
        DASHBOARD_HEADER,
        ["Ayse Yilmaz", "IT", "26", "12", "14"],  # OPEN B-3, B-4
        ["Mehmet Demir", "Muhasebe", "20", "0", "20"],  # OPEN B-4
        ["Zeynep Kaya", "IK", "14", "0", "14"],  # OPEN B-1, B-4
        ["Ahmet Celik", "IT", "20", "0", "20"],  # OPEN B-4
        ["Elif Sahin", "Satis", "0", "0", "0"],
    ]


# --- AC-5: empty state (dashboard) ----------------------------------------------------------

def test_dashboard_empty_state(client):
    Db.requests = []
    html = page(client, "/")
    assert "Bekleyen: <b>0</b>" in html
    assert "Onaylanan: <b>0</b>" in html
    assert "Reddedilen: <b>0</b>" in html
    assert table_rows(html) == [
        DASHBOARD_HEADER,
        ["Ayse Yilmaz", "IT", "26", "0", "26"],
        ["Mehmet Demir", "Muhasebe", "20", "0", "20"],
        ["Zeynep Kaya", "IK", "14", "0", "14"],  # OPEN B-1
        ["Ahmet Celik", "IT", "20", "0", "20"],
        ["Elif Sahin", "Satis", "0", "0", "0"],
    ]


# --- AC-3: request rows ---------------------------------------------------------------------

def test_request_list_rows(client):
    assert table_rows(page(client, "/requests")) == [
        LIST_HEADER,
        # length column: calendar days, OPEN B-3
        ["Ayse Yilmaz", "2026-07-06", "2026-07-17", "12", "Yaz tatili", "Onaylandi"],
        ["Mehmet Demir", "2026-11-02", "2026-11-04", "3", "Aile ziyareti", "Beklemede"],
        ["Zeynep Kaya", "2026-11-09", "2026-11-09", "1", "Saglik", "Beklemede"],
        ["Ahmet Celik", "2026-12-21", "2026-12-25", "5", "Yilbasi oncesi", "Beklemede"],
        ["Ayse Yilmaz", "2026-12-28", "2026-12-30", "3", "Yil sonu", "Beklemede"],
        ["Elif Sahin", "2026-10-05", "2026-10-07", "3", "Tasinma", "Reddedildi"],
        ["Zeynep Kaya", "2026-09-14", "2026-09-25", "12", "Uzun tatil", "Reddedildi"],
        ["Mehmet Demir", "2026-08-03", "2026-08-03", "1", "Ozel is", "Reddedildi"],
    ]


# --- AC-4: status label colors --------------------------------------------------------------

@pytest.mark.parametrize(
    ("status", "color"),
    [("Onaylandi", "green"), ("Beklemede", "orange"), ("Reddedildi", "red"), ("Iptal", "#999")],
)
def test_status_label_colors(client, status, color):
    Db.requests = [{"id": 1, "employee_id": 1, "start": Db.requests[0]["start"],
                    "end": Db.requests[0]["end"], "reason": "Test", "status": status}]
    assert f"<b style='color:{color}'>{status}</b>" in page(client, "/requests")


# --- AC-5: empty state (request list) -------------------------------------------------------

def test_request_list_empty_state(client):
    Db.requests = []
    assert table_rows(page(client, "/requests")) == [LIST_HEADER]


# --- AC-6: output is not escaped (OPEN B-8) -------------------------------------------------

@pytest.mark.parametrize(
    ("path", "record", "field"),
    [
        ("/", "employee", "name"),
        ("/requests", "employee", "name"),
        ("/", "employee", "department"),
        ("/requests", "request", "reason"),
    ],
)
def test_markup_is_not_escaped(client, path, record, field):
    target = Db.employees[0] if record == "employee" else Db.requests[0]
    target[field] = "<b>x</b>"
    html = page(client, path)
    assert "<b>x</b>" in html  # OPEN B-8: rendered as markup
    assert "&lt;b&gt;x&lt;/b&gt;" not in html


# --- AC-7: no page changes a status (BR-7) --------------------------------------------------

def test_only_three_pages_exist():
    from app import app

    assert sorted(rule.rule for rule in app.url_map.iter_rules()) == [
        "/", "/new", "/requests", "/static/<path:filename>",
    ]


def test_request_list_has_no_actions(client):
    html = page(client, "/requests")
    assert "<form" not in html
    assert "<button" not in html
    assert html.count("<a ") == 3  # the three navigation links only


# --- AC-8: title and navigation -------------------------------------------------------------

@pytest.mark.parametrize("path", ["/", "/requests"])
def test_page_has_title_and_navigation(client, path):
    html = page(client, path)  # asserts HTTP 200
    assert "<title>LeaveManager</title>" in html
    assert '<a href="/">Ana Sayfa</a>' in html
    assert '<a href="/requests">Talepler</a>' in html
    assert '<a href="/new">Yeni Talep</a>' in html
