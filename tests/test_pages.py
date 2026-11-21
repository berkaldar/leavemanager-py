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


# --- AC-8: title and navigation -------------------------------------------------------------

@pytest.mark.parametrize("path", ["/", "/requests"])
def test_page_has_title_and_navigation(client, path):
    html = page(client, path)  # asserts HTTP 200
    assert "<title>LeaveManager</title>" in html
    assert '<a href="/">Ana Sayfa</a>' in html
    assert '<a href="/requests">Talepler</a>' in html
    assert '<a href="/new">Yeni Talep</a>' in html
