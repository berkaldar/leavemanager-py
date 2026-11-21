# Domain

> The shared language between business, humans, and agents.
> If a term isn't here, expect the AI to invent its own meaning for it.

LeaveManager is an internal HR tool: staff leave requests, their approval status, and each
employee's annual leave balance. Rules below describe the code **as it behaves today**
(bootstrap 2026-11-21); rules marked **OPEN** are disputed and change only through their own spec
(`specs/backlog.md`).

## Ubiquitous language

| Term | Meaning | Notes / not to be confused with |
|---|---|---|
| Employee (`Db.employees`) | A staff member: id, name, department, hire date | Departments are free text (`IT`, `Muhasebe`, `IK`, `Satis`) |
| User (`Db.users`) | A sign-in account for one employee: username, password hash, role | One user per employee; usernames are first names in lowercase |
| Role | `employee`, `manager` or `hr` | Stored per user; no page behaves differently by role until spec 0005 |
| Leave request (`Db.requests`) | A period of leave: employee, start date, end date (both inclusive), reason, status | "Talep" in the UI |
| Status | `Beklemede` (pending) · `Onaylandi` (approved) · `Reddedildi` (rejected) | Stored values, Turkish, without diacritics, case-sensitive |
| Seniority | Whole years of service, derived from hire date and today | See BR-2 (OPEN) |
| Entitlement ("Hak") | Annual leave days an employee is entitled to, by seniority | See BR-1 |
| Used days ("Kullanilan") | Sum of the days of the employee's **approved** requests | Pending and rejected requests do not count (BR-4) |
| Remaining ("Kalan") | Entitlement − used days | Can be negative today; no rule forbids it |
| Request length | Days of a request: `end − start + 1` (calendar days) | See BR-3 (OPEN) |

## Business rules
- **BR-1** Entitlement by seniority: < 1 year → 0 · 1–5 years → **14** · 6–15 years → 20 ·
  > 15 years → 26 days. **OPEN:** the code comment and the 2014 HR handbook reference say 15 for
  1–5 years (B-1).
- **BR-2** Seniority = current calendar year − hire calendar year (month and day ignored).
  **OPEN:** likely wrong; an anniversary-based count needs HR's answer (B-2).
- **BR-3** Request length counts calendar days, both ends inclusive. **OPEN:** the code comment
  says working days; weekends and public holidays undecided (B-3).
- **BR-4** Pending requests do not reduce the remaining balance. **OPEN:** undecided since 2018
  (B-4).
- **BR-5** A new request is created with status `Beklemede`. It is refused when the balance is
  insufficient. **OPEN:** the route refuses when remaining < length, the service when
  remaining ≤ length — "exactly enough" is allowed by one and refused by the other (B-5).
- **BR-6** Back-dated requests (start before today) are allowed: HR enters them retroactively.
- **BR-7** No approve/reject action exists in the app; statuses change only in the seed data.

## Key domain invariants
- Every leave request belongs to an existing employee.
- A request's end date is never before its start date. (Not enforced today — see
  `docs/security.md`, Input & output.)
- Used days count only approved requests.

## Sensitive areas
- **Leave balance calculation** (BR-1…BR-5): a mistake changes what employees are entitled to.
- **Employee personal data**: names, departments, hire dates.
- **Authentication**: sign-in, sessions, CSRF protection and (spec 0005) the role rules decide who
  can read or change leave data; a mistake exposes everyone's balances.
- **Year-end carry-over**: commented-out code in `LeaveService` (max 5 days carried). Not active;
  enabling it is new behavior and needs a spec.
