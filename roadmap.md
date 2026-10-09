# CampusFlow — Team Roadmap

**Project:** CampusFlow command-line helpdesk ticket manager  
**Team:** Two fellows (Engineer A and Engineer B)  
**Duration:** Six-hour sprint  
**Stack:** Python 3, standard-library `unittest` and `json`, Git and GitHub

## 1. Mission and definition of done

Build a CLI that creates, lists, views, assigns, progresses, prioritizes, reports on, and persists support tickets. The menu must continue until Exit. Both teammates must contribute real Python code **and** automated tests, open their own pull requests, review and approve each other's PRs, and demonstrate the integrated application.

Required ticket fields: `id`, `title`, `category`, `urgency`, `affected_users`, `priority`, `status`, `assigned_to`.

- IDs: unique, sequential-looking `T001`, `T002`, ...; never duplicate after reload.
- Categories: `Network`, `Hardware`, `Software`, `Other`.
- Urgency: `low`, `medium`, `high`; normalize valid case variations.
- Title: nonblank; affected users: positive integer (reject zero, negatives, decimals, text, and booleans).
- Priority rules, **first match wins**: high + at least 10 users → critical; high OR at least 10 → high; medium OR at least 3 → medium; otherwise low.
- Statuses: `open` → `in_progress` → `resolved`; entering `in_progress` requires assignment. Resolved tickets cannot be modified unless explicitly reopened to `open`.
- Queue: only `open` tickets, ordered critical → high → medium → low, then ascending numeric ID.
- Reports: total count, breakdown by status and priority, including an empty collection.
- Persistence: JSON save/load; missing file starts empty, malformed file raises a clear error without silently erasing data.

## 2. Ownership and deliverables

### Engineer A — Ticket creation, validation, priority and viewing

**Primary files:** `campusflow/tickets.py`, `tests/test_tickets.py`; coordinate CLI wiring in `main.py` during integration.

| Feature | Proposed functions | Acceptance requirements |
|---|---|---|
| F1 — Create | `create_ticket(tickets, title, category, urgency, affected_users)` | Validate before mutating; calculate priority; assign unique ID; default status `open` and `assigned_to=None`; store and return ticket. |
| Input validation | `validate_title`, `validate_category`, `validate_urgency`, `validate_affected_users` | Normalize supported case variants; reject invalid values with useful errors; no partial ticket stored. |
| Priority | `calculate_priority(urgency, affected_users)` | Implement ordered four-rule engine exactly; no AI call for priority. |
| IDs | `generate_ticket_id(tickets)` | Return `T001` etc.; numeric progression survives reload; no collision. |
| F2 — List/view | `list_tickets(tickets)`, `get_ticket_by_id(tickets, ticket_id)` | Show all records or locate a specific ID; handle unknown IDs explicitly. |

**Engineer A tests (minimum proposed coverage):**

- High urgency + 12 users → critical.
- High urgency + 2 users → high.
- Low urgency + 4 users → medium.
- Low urgency + 1 user → low.
- Zero, negative, non-integer or boolean affected users rejected.
- Blank title, invalid category and urgency rejected; valid case variants normalized.
- Ticket has all required fields and initial defaults.
- IDs are unique, including when created from previously loaded records (with Engineer B).
- Unknown ID lookup produces agreed error behavior.

**Engineer A completion evidence:** application code, passing tests, meaningful commits, feature branch, PR description with test output, review of Engineer B's PR, at least two substantive review comments, final approval, three verified AI learning entries, and ability to explain one design decision and one test.

### Engineer B — Assignment, workflow, queue, reporting and storage

**Primary files:** `campusflow/workflow.py`, `campusflow/reports.py`, `campusflow/storage.py`, `tests/test_workflow.py`, `tests/test_reports.py`, `tests/test_storage.py`.

| Feature | Proposed functions | Acceptance requirements |
|---|---|---|
| F3 — Assign | `assign_ticket(tickets, ticket_id, staff_name)`, `validate_staff_name` | Reject blank staff names, unknown IDs, and changes to resolved tickets. |
| F4 — Workflow | `update_ticket_status(tickets, ticket_id, new_status)`, `validate_status_transition`, `reopen_ticket` | Enforce `open → in_progress → resolved`; cannot start work before assignment; explicit reopen required for resolved ticket. |
| F5 — Queue | `get_work_queue(tickets)`, `priority_rank(priority)` | Only open tickets; priority order then numeric ID; do not mutate underlying ticket order. |
| F6 — Reports | `generate_report(tickets)`, `count_by_status`, `count_by_priority` | Total and complete status/priority breakdowns; zero-ticket case works. |
| F7 — Storage | `save_tickets(tickets, filepath)`, `load_tickets(filepath)` | Valid JSON round trip; fresh start on missing file; clear malformed JSON error; no silent data loss. |

**Engineer B tests (minimum proposed coverage):**

- Reject assigning a blank name and an unknown ticket ID.
- Unassigned ticket cannot enter `in_progress`.
- Assigned ticket progresses `open → in_progress → resolved`.
- Invalid transitions rejected without corrupting ticket data.
- Resolved ticket cannot be modified until explicitly reopened.
- Queue sorts by priority and then numeric ID (`T002` before `T010`).
- Queue excludes `in_progress` and `resolved` tickets.
- Reports handle nonempty and empty collections.
- JSON save/load preserves tickets; missing file is safe; malformed JSON gives a clear error.
- After reload, newly created IDs do not duplicate existing IDs (with Engineer A).

**Engineer B completion evidence:** application code, passing tests, meaningful commits, feature branch, PR description with test output, review of Engineer A's PR, at least two substantive review comments, final approval, three verified AI learning entries, and ability to explain one design decision and one test.

### Shared responsibilities

1. Agree on data representation, function signatures, error conventions, return values, mutation policy, and JSON file path; record in `docs/design-decisions.md`.
2. Integrate the CLI menu in `main.py` with create, list/view, assign, status update/reopen, queue, reports, and exit.
3. Integrate saving/loading and check that ticket IDs remain unique across restarts.
4. Use separate branches and cross-review each other's PRs; do not merge without approval.
5. Run the full suite on `main`, fix integration problems through reviewed changes, and prepare the demo.
6. Each fellow must independently document **at least three verified AI learning interactions**, including one AI suggestion corrected, improved, or rejected based on evidence.

## 3. Suggested shared function contracts

These are **team proposals**, not prescribed names in the challenge guide. Confirm them before coding.

```python
# tickets.py
create_ticket(tickets, title, category, urgency, affected_users) -> dict
calculate_priority(urgency, affected_users) -> str
get_ticket_by_id(tickets, ticket_id) -> dict
list_tickets(tickets) -> list[dict]

# workflow.py
assign_ticket(tickets, ticket_id, staff_name) -> dict
update_ticket_status(tickets, ticket_id, new_status) -> dict
reopen_ticket(tickets, ticket_id) -> dict
get_work_queue(tickets) -> list[dict]

# reports.py
generate_report(tickets) -> dict

# storage.py
save_tickets(tickets, filepath) -> None
load_tickets(filepath) -> list[dict]
```

**Suggested conventions:** a `list[dict]` stores tickets; pure calculation/validation functions avoid `input()` and `print()`; CLI handles interaction and catches domain errors; changes are validated before mutation. For a six-hour sprint, prefer straightforward modules to a complex framework. Agree whether storage is saved after every successful change or on explicit exit (and ensure it is not lost).

## 4. Project layout

```text
campusflow/
├── main.py
├── README.md
├── .gitignore
├── campusflow/
│   ├── __init__.py
│   ├── tickets.py              # Engineer A
│   ├── workflow.py             # Engineer B
│   ├── reports.py              # Engineer B
│   └── storage.py              # Engineer B; shared integration
├── tests/
│   ├── test_tickets.py         # Engineer A
│   ├── test_workflow.py        # Engineer B
│   ├── test_reports.py         # Engineer B
│   └── test_storage.py         # Engineer B; shared ID test
├── docs/
│   ├── design-decisions.md
│   └── ai-learning-log.md
└── data/
    └── tickets.json           # runtime only; gitignored
```

Use `.gitignore` for `.venv/`, `__pycache__/`, `*.pyc`, `.env`, and `data/tickets.json`. No web framework, database, AI SDK, or API key is required.

## 5. Six-hour sprint checkpoints

| Time | Team milestone | Engineer A | Engineer B | Evidence |
|---|---|---|---|---|
| 00:00–00:20 | Repository setup | Create/clone repo and branch | Join/clone repo and branch | GitHub URL, collaborators, initial commit |
| 00:20–00:50 | Design | Specify ticket schema, validations, IDs | Specify transitions, storage and reports | Issues, `design-decisions.md` |
| 00:50–01:30 | AI learning | Two verified topic experiments | Two verified topic experiments | Two learning entries each |
| 01:30–03:55 | Build/test | F1/F2 and matching tests | F3–F7 and matching tests | Commits, tests, third learning entry each |
| 03:55–05:00 | PR review | Open A PR; review B PR | Open B PR; review A PR | Two substantive comments per reviewer, approvals |
| 05:00–05:40 | Integrate | CLI, ID/persistence checks | Storage, queue/report integration | Green full suite on main, docs |
| 05:40–06:00 | Demo/defence | Explain creation/priority and tests | Explain workflow/storage and tests | Live demo, PR links, test output |

**Git workflow:** create one shared repo; each teammate works on a separate `feat/<issue-number>-<description>` branch. Commit focused changes, push, open a descriptive PR, review partner's code and tests, address blockers, and merge only after partner approval. If `main` moves, update the outstanding branch and rerun tests.

## 6. Minimum acceptance and test checklist

- [ ] All seven features accessible from a CLI menu that runs until Exit.
- [ ] Ticket validation, normalization, required fields and IDs correct.
- [ ] Four priority examples produce critical, high, medium, and low respectively.
- [ ] Unassigned ticket cannot enter `in_progress`.
- [ ] Assigned ticket can progress to `resolved`; explicit reopen works.
- [ ] Invalid input and transitions do not corrupt existing records.
- [ ] Queue orders only open tickets by priority and numeric ID.
- [ ] Reports include totals and status/priority breakdowns; empty report works.
- [ ] JSON persists tickets across restart; malformed JSON is not silently discarded.
- [ ] IDs remain unique after reload.
- [ ] At least eight meaningful `unittest` tests pass on integrated `main` (target more).
- [ ] Both fellows authored code and tests and each has a reviewed, approved PR.
- [ ] Each reviewer left at least two substantive review observations.
- [ ] Each fellow has three verified AI learning interactions, one critically evaluated.
- [ ] README, design decisions, learning log and final demonstration ready.

**Test command:**

```bash
python -m unittest discover -s tests -v
```

## 7. Final demonstration sequence

1. Start CLI; create several tickets with different urgency and affected-user counts.
2. Show correct priority and unique IDs; reject an invalid input.
3. List/view tickets; assign a ticket to staff.
4. Show rejected unassigned/invalid status transition, then valid progression and reopening.
5. Show sorted open queue and status/priority report.
6. Exit and restart; demonstrate JSON reload and next unique ID.
7. Run `python -m unittest discover -s tests -v` on latest `main`.
8. Show both PRs, cross-reviews, and each fellow's AI learning evidence.

## 8. Submission deliverables

- Main GitHub repository URL.
- Engineer A's approved PR URL and Engineer B's approved PR URL.
- Actual passing test output from latest `main`.
- `README.md` with setup, run/test commands, features, limitations and contribution summary.
- `docs/design-decisions.md` with shared contracts and ownership.
- `docs/ai-learning-log.md` with three truthful, verified interactions per fellow.
- A live demonstration and individual explanation of implementation, testing, AI verification and partner review.

---

**Scope note:** This roadmap follows the uploaded *Fellows' Engineering Guide — AI-Native Engineering Sprint: CampusFlow*. The named functions, exact file ownership and extra tests are recommended team decisions; the seven features, collaboration process, minimum testing, learning logs and six-hour checkpoints are challenge requirements.