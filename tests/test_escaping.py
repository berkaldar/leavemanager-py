"""Stored text is shown as text on every page (spec 0005, backlog B-8).

A page is parsed the way a browser parses it: the typed text must come out as text content, and the
page's elements and attributes must be exactly those of the same page holding ordinary text.
"""
from html.parser import HTMLParser

import pytest

from app import Db

pytestmark = pytest.mark.http


class PageParser(HTMLParser):
    """Collects every start tag with its attributes, and the text content."""

    def __init__(self):
        super().__init__()
        self.tags = []
        self._text = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, tuple(attrs)))

    def handle_data(self, data):
        self._text.append(data)

    @property
    def text(self):
        return "".join(self._text)


def parse(html):
    parser = PageParser()
    parser.feed(html)
    parser.close()
    return parser


# where stored text reaches a page: (name, page, how the test stores the text)
PLACES = ["name-dashboard", "name-list", "name-dropdown", "department-dashboard", "reason-list"]
PAGES = {"name-dashboard": "/", "name-list": "/requests", "name-dropdown": "/new",
         "department-dashboard": "/", "reason-list": "/requests"}


def store(place, text):
    if place.startswith("name"):
        Db.employees[0]["name"] = text
    elif place.startswith("department"):
        Db.employees[0]["department"] = text
    else:
        Db.requests[0]["reason"] = text


def page_with(client, place, text):
    store(place, text)
    resp = client.get(PAGES[place])
    assert resp.status_code == 200
    return resp.get_data(as_text=True)


def assert_shown_as_text(client, place, typed):
    plain = parse(page_with(client, place, "plain"))
    html = page_with(client, place, typed)
    shown = parse(html)
    assert typed in shown.text  # exactly as typed
    assert shown.tags == plain.tags  # no element and no attribute comes from it
    return html


# --- AC-2: a status value is text (no page can set one, so the test stores it directly) ----

def test_status_with_markup_is_text(client):
    Db.requests[0]["status"] = "Iptal"
    plain = parse(client.get("/requests").get_data(as_text=True))
    Db.requests[0]["status"] = "<b>x</b>"
    html = client.get("/requests").get_data(as_text=True)
    shown = parse(html)
    assert "<b>x</b>" in shown.text
    assert shown.tags == plain.tags
    assert "<b style='color:#999'>&lt;b&gt;x&lt;/b&gt;</b>" in html  # the gray fallback color


# --- AC-4: all five special characters -------------------------------------------------------

@pytest.mark.parametrize("place", PLACES)
def test_special_characters_are_shown_as_typed(client, place):
    html = assert_shown_as_text(client, place, "<>&\"'")
    # Unescaped, this text would still parse as plain text, so the page source is checked too:
    # each character is written as its entity, however the entity for a quote is spelled.
    assert "&lt;&gt;&amp;" in html
    assert "<>&" not in html
    assert "\"'" not in html


# --- AC-5: a script is text --------------------------------------------------------------------

@pytest.mark.parametrize("place", PLACES)
def test_script_text_creates_no_script_element(client, place):
    typed = "<script>alert(1)</script>"
    html = assert_shown_as_text(client, place, typed)
    assert "script" not in [tag for tag, _ in parse(html).tags]
    assert "<script>" not in html


# --- AC-6: escaped once ------------------------------------------------------------------------

@pytest.mark.parametrize("place", PLACES)
def test_text_is_escaped_once(client, place):
    html = assert_shown_as_text(client, place, "Tom &amp; Jerry")  # shown as typed, not as "Tom & Jerry"
    assert "Tom &amp;amp; Jerry" in html


# --- AC-8: the navigation username is text -----------------------------------------------------

@pytest.mark.parametrize("path", ["/", "/requests", "/new"])
def test_navigation_username_is_text(client, path):
    with client.session_transaction() as sess:
        sess["user"] = "zeynep"
    plain = parse(client.get(path).get_data(as_text=True))
    with client.session_transaction() as sess:
        sess["user"] = "<b>x</b>"
    html = client.get(path).get_data(as_text=True)
    shown = parse(html)
    assert "<b>x</b>" in shown.text
    assert shown.tags == plain.tags
    assert "&lt;b&gt;x&lt;/b&gt; <input" in html  # next to the "Cikis" button
