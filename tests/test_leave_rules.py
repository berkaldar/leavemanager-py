"""Characterization of the leave rules BR-1…BR-6 as they behave today (spec 0001).

These pin current behavior, bugs included. A test marked "OPEN B-n" changes on purpose in the
spec that resolves backlog item B-n — never to get to green.
"""
from datetime import date

import pytest

from app import Db, svc

AYSE, MEHMET, ZEYNEP, AHMET, ELIF = 1, 2, 3, 4, 5


def employee(emp_id):
    return next(e for e in Db.employees if e["id"] == emp_id)


def add_employee(hire_date, emp_id=99):
    emp = {"id": emp_id, "name": "Test Kisi", "department": "Test", "hire_date": hire_date}
    Db.employees.append(emp)
    return emp


# --- AC-1: seniority (BR-2, OPEN B-2) -------------------------------------------------------

@pytest.mark.parametrize(
    ("hire_date", "years"),
    [
        (date(2025, 12, 31), 1),  # OPEN B-2: under a month of service counts as a full year
        (date(2026, 6, 1), 0),
    ],
)
def test_seniority_is_calendar_year_difference(hire_date, years):
    assert svc.get_seniority_years(add_employee(hire_date)) == years


def test_seniority_leap_day_hire_date():
    assert svc.get_seniority_years(employee(AHMET)) == 6  # hired 2020-02-29


# --- AC-2: entitlement (BR-1, OPEN B-1 for 1–5 years) ---------------------------------------

@pytest.mark.parametrize(
    ("hire_year", "days"),
    [
        (2026, 0),
        (2025, 14),  # OPEN B-1: the HR handbook says 15
        (2021, 14),  # OPEN B-1
        (2020, 20),
        (2011, 20),
        (2010, 26),
    ],
)
def test_entitlement_by_hire_year(hire_year, days):
    assert svc.get_entitlement(add_employee(date(hire_year, 1, 1))) == days


# --- AC-3: request length (BR-3, OPEN B-3) --------------------------------------------------

@pytest.mark.parametrize(
    ("start", "end", "days"),
    [
        (date(2026, 7, 6), date(2026, 7, 6), 1),
        (date(2026, 7, 6), date(2026, 7, 17), 12),  # OPEN B-3: weekends are counted
        (date(2026, 7, 6), date(2026, 7, 5), 0),  # end before start: no error
    ],
)
def test_request_length_counts_calendar_days_inclusive(start, end, days):
    assert svc.calc_days(start, end) == days


# --- AC-4: used days (BR-4) -----------------------------------------------------------------

def test_used_days_count_only_approved_requests():
    assert svc.get_used_days(AYSE) == 12  # approved 07-06…07-17; pending 12-28…30 not counted
    assert svc.get_used_days(MEHMET) == 0
    assert svc.get_used_days(ZEYNEP) == 0
    assert svc.get_used_days(ELIF) == 0


# --- AC-5: remaining --------------------------------------------------------------------------

@pytest.mark.parametrize(
    ("emp_id", "remaining"),
    [(AYSE, 14), (MEHMET, 20), (ZEYNEP, 14), (AHMET, 20), (ELIF, 0)],
)
def test_remaining_for_seed_employees(emp_id, remaining):
    assert svc.get_remaining(employee(emp_id)) == remaining


def test_remaining_has_no_floor():
    emp = add_employee(date(2026, 1, 1))  # 0 years → 0 days
    Db.requests.append({"id": 100, "employee_id": emp["id"], "start": date(2026, 3, 2),
                        "end": date(2026, 3, 4), "reason": "Test", "status": "Onaylandi"})
    assert svc.get_remaining(emp) == -3


# --- AC-6…AC-10: request creation (BR-5, BR-6) ----------------------------------------------

def test_request_below_balance_is_stored_pending():
    before = len(Db.requests)
    next_id = Db.next_id
    # Ayse: 14 remaining; 2026-12-01…12-13 is 13 days
    assert svc.create_request(AYSE, date(2026, 12, 1), date(2026, 12, 13), "Tatil") is True
    assert len(Db.requests) == before + 1
    assert Db.requests[-1] == {"id": next_id, "employee_id": AYSE, "start": date(2026, 12, 1),
                               "end": date(2026, 12, 13), "reason": "Tatil",
                               "status": "Beklemede"}
    assert Db.next_id == next_id + 1
    assert svc.get_remaining(employee(AYSE)) == 14  # OPEN B-4: pending is not deducted


def test_request_equal_to_balance_is_refused():
    before = list(Db.requests)
    # OPEN B-5: Ayse has exactly 14 remaining; a 14-day request (12-01…12-14) is refused
    assert svc.create_request(AYSE, date(2026, 12, 1), date(2026, 12, 14), "Tatil") is False
    assert Db.requests == before


def test_request_with_zero_entitlement_is_refused():
    before = list(Db.requests)
    assert svc.create_request(ELIF, date(2026, 12, 1), date(2026, 12, 1), "Tatil") is False
    assert Db.requests == before


def test_unknown_employee_reports_success_and_stores_nothing():
    before = list(Db.requests)
    next_id = Db.next_id
    # OPEN B-5: reports success for an employee that does not exist
    assert svc.create_request(999, date(2026, 12, 1), date(2026, 12, 1), "Tatil") is True
    assert Db.requests == before
    assert Db.next_id == next_id


def test_missing_dates_report_success_and_store_nothing():
    before = list(Db.requests)
    next_id = Db.next_id
    # OPEN B-5: the failure is swallowed and reported as success
    assert svc.create_request(AYSE, None, None, "Tatil") is True
    assert Db.requests == before
    assert Db.next_id == next_id


def test_back_dated_request_is_accepted():
    before = len(Db.requests)
    assert svc.create_request(MEHMET, date(2026, 1, 5), date(2026, 1, 6), "Geriye donuk") is True
    assert len(Db.requests) == before + 1
    assert Db.requests[-1]["start"] == date(2026, 1, 5)
    assert Db.requests[-1]["status"] == "Beklemede"
