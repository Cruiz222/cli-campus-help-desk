# CampusFlow — Design Decisions

**Project:** CampusFlow — Campus Helpdesk Ticket Management System  
**Language:** Python  
**Application Type:** Command-Line Interface (CLI)  
**Testing Framework:** unittest  
**Team:** Engineer A and Engineer B

## 1. Project Overview

CampusFlow is a Python-based campus helpdesk system designed to help institutions record, prioritize, assign, track, and manage support tickets.

The system addresses a common problem in campus environments: technical complaints may be difficult to track when they are handled informally.

CampusFlow provides a structured process for managing issues from creation to resolution.

### Project Objectives

- Allow users to create support tickets.
- Validate ticket information before storing it.
- Automatically calculate ticket priority.
- Assign tickets to responsible staff members.
- Control ticket status transitions.
- Display outstanding tickets in priority order.
- Generate ticket summary reports.
- Save and retrieve tickets using JSON files.

## 2. Team Responsibilities

The project was divided into two main development areas to allow parallel implementation.

| Engineer | Responsibilities |
|---|---|
| Engineer A | Ticket creation, input validation, priority calculation, ticket ID generation, ticket retrieval, and listing |
| Engineer B | Ticket assignment, status workflow, work queue, reporting, JSON persistence, and related validation |

Both engineers contributed unit tests, code review, debugging, and integration.

**Design decision:** Divide development responsibilities by feature rather than having both engineers modify the same functions.

**Reason:** This reduces conflicting changes, improves accountability, and makes collaboration easier.

## 3. Modular Project Architecture

**Decision:** Organize the application into separate modules based on responsibilities.

```text
cli-campus-help-desk/
├── campusflow/
│   ├── __init__.py
│   ├── tickets.py
│   └── workflow/
│       ├── __init__.py
│       ├── assign_ticket.py
│       ├── ticket_status.py
│       ├── work_queue.py
│       ├── reports.py
│       └── storage.py
├── tests/
│   ├── test_tickets.py
│   ├── test_workflow.py
│   ├── test_work_queue.py
│   ├── test_reports.py
│   └── test_storage.py
├── docs/
│   ├── ai-learning-log.md
│   └── design-decisions.md
├── main.py
└── README.md
```

**Reason:** Each module has a clear responsibility, making it easier to test and maintain independently.

**Trade-off:** Multiple modules require imports and coordination, but this is preferable to placing all application logic in one file.

## 4. Ticket Data Structure

**Decision:** Represent each ticket using a Python dictionary and store tickets in a list.

A ticket contains the following fields:

```python
{
    "id": "T001",
    "title": "Campus Wi-Fi not working",
    "category": "Network",
    "urgency": "high",
    "affected_users": 12,
    "priority": "critical",
    "status": "open",
    "assigned_to": None
}
```

**Reason:** Dictionaries provide a simple way to associate field names with values. Lists allow multiple tickets to be stored and processed.

**Trade-off:** Dictionaries do not enforce a fixed schema automatically, so the application must validate data explicitly.

## 5. Ticket Creation and Input Validation — Engineer A

**Decision:** Validate all required inputs before creating and storing a ticket.

The validation rules include:

- Ticket titles must be nonempty strings.
- Categories must match supported categories: Network, Hardware, Software, or Other.
- Urgency must be low, medium, or high.
- Affected-user counts must be positive integers.
- Unsupported values, including boolean and `None` inputs for affected users, are rejected.
- Valid category and urgency values are normalized to consistent formats.

**Reason:** Invalid input could create incomplete records, affect priority calculations, or cause errors in other modules.

**Trade-off:** Strict validation rejects some user inputs, but it improves consistency and reliability.

The application validates ticket details before appending a new record, preventing invalid tickets from being partially stored.

## 6. Automatic Ticket ID Generation — Engineer A

**Decision:** Generate unique ticket identifiers using a sequential format.

Examples:

`T001`, `T002`, `T003`

The next ticket number is calculated from the highest existing numeric ticket ID rather than the length of the ticket list.

**Reason:** Using the highest existing ID prevents reuse when ticket records have gaps or are stored out of order.

For example, if existing tickets are `T001` and `T004`, the next generated ID is `T005`.

**Trade-off:** This approach is suitable for a small local application, but a database-generated identifier would be preferable in a concurrent system.

## 7. Automatic Priority Calculation — Engineer A

**Decision:** Calculate ticket priority automatically using urgency and the number of affected users.

The implemented rules are evaluated in the following order:

| Condition | Priority |
|---|---|
| High urgency and at least 10 affected users | Critical |
| High urgency or at least 10 affected users | High |
| Medium urgency or at least 3 affected users | Medium |
| Otherwise | Low |

**Reason:** Priority should be determined consistently instead of depending entirely on a user's subjective judgment.

**Trade-off:** A rule-based approach is easy to understand and test but does not account for every possible real-world emergency or service-level requirement.

## 8. Ticket Retrieval and Safe Listing — Engineer A

**Decision:** Provide separate operations for retrieving an individual ticket and listing tickets.

Individual ticket retrieval supports normalized ID lookup and returns the matching ticket record for operations that need to modify it.

Ticket listing returns an independent deep copy of the records.

**Reason:** A read-only listing should not accidentally modify the original ticket data.

**Trade-off:** Deep copying requires additional memory, but this is acceptable for a small application.

## 9. Ticket Assignment — Engineer B

**Decision:** Allow tickets to be assigned to staff members while enforcing validation rules.

The system rejects:
- Unknown ticket IDs.
- Empty staff names.
- Assignment attempts involving resolved tickets.

**Reason:** Assignment establishes responsibility for resolving a reported issue.

**Trade-off:** Staff members are represented by names rather than dedicated staff accounts, keeping the project simple but limiting identity verification.

## 10. Ticket Status Workflow — Engineer B

**Decision:** Enforce a controlled ticket lifecycle.

```text
OPEN
  |
  v
IN_PROGRESS
  |
  v
RESOLVED
```

A separate reopening operation allows a resolved ticket to return to the open state.

### Business Rules

- New tickets begin with an `open` status.
- A ticket must be assigned before moving to `in_progress`.
- An open ticket cannot move directly to `resolved`.
- An `in_progress` ticket can be resolved.
- Resolved tickets cannot be modified through the normal status update operation.
- Only resolved tickets can be reopened.

**Reason:** These rules prevent invalid transitions and ensure that tickets follow a predictable process.

**Trade-off:** The workflow is deliberately restrictive, but that improves consistency and makes it easier to test.

## 11. Priority-Based Work Queue — Engineer B

**Decision:** Display open tickets in priority order.

The sorting order is:

1. Critical
2. High
3. Medium
4. Low

When two tickets share the same priority, their numeric ticket IDs determine their order.

The queue is created using sorting without changing the original ticket list.

**Reason:** Staff should see the most important outstanding issues first.

**Trade-off:** The queue does not currently consider ticket age, deadlines, or staff workload.

## 12. Ticket Reporting — Engineer B

**Decision:** Generate summary reports from the existing ticket records.

Reports include:
- Total number of tickets.
- Number of tickets by status.
- Number of tickets by priority.

**Reason:** Summary reports provide a quick overview of workload and ticket progress.

**Trade-off:** Counts are calculated when reports are requested rather than maintained as separate counters. This reduces the risk of stored counters becoming inconsistent.

## 13. JSON Persistence — Engineer B

**Decision:** Use JSON files for storing ticket records.

Python's built-in `json` module handles serialization and deserialization.

The storage module provides:

- `save_tickets()` — saves ticket records to a JSON file.
- `load_tickets()` — reads ticket records from a JSON file.

**Reason:** JSON is human-readable, easy to inspect, and does not require external dependencies or database setup.

**Trade-off:** JSON is appropriate for a small CLI application but has limitations involving concurrent updates, large datasets, and crash-safe writes.

## 14. Storage Validation and Error Handling — Engineer B

**Decision:** Validate stored data when loading it rather than assuming that every JSON file is correct.

The implementation handles:
- Missing storage files by returning an empty ticket list.
- Malformed JSON by raising a `ValueError`.
- JSON documents whose top-level structure is not a list.
- Ticket records that are not dictionaries.
- Missing or invalid ticket IDs.
- Duplicate ticket IDs.

Duplicate IDs are detected using a Python set.

**Reason:** Duplicate or malformed records could cause incorrect ticket updates or unexpected application errors.

**Trade-off:** Validation adds processing during loading but improves data integrity.

Full validation of every saved ticket field remains a possible improvement.

## 15. Testing Strategy — Both Engineers

**Decision:** Use Python's built-in `unittest` framework to test features independently.

Engineer A wrote tests for ticket creation, validation, priority calculation, ID generation, retrieval, and listing.

Engineer B wrote tests for assignment, status transitions, reopening, queue ordering, reporting, and persistence.

Tests cover both expected operations and invalid scenarios.

The team used the command:

```bash
python3 -m unittest discover -s tests -v
```

### Integration Results

After combining both engineers' branches, the project produced:

**92 tests passed, 0 failures, 0 errors.**

**Reason:** Automated tests help detect defects and regressions when multiple engineers contribute to the same codebase.

**Trade-off:** Writing tests requires development time, but it improves confidence and makes integration safer.

Passing unit tests does not replace manual or automated testing of the complete CLI.

## 16. Version Control and Collaboration — Both Engineers

**Decision:** Use Git feature branches and pull requests.

Engineer A worked on the ticket creation branch, while Engineer B worked on the status workflow branch.

Both branches were combined on an integration branch.

The team reviewed code, identified validation and copying issues, and added tests for important edge cases.

**Reason:** Branch-based collaboration allows independent development while keeping changes reviewable.

**Trade-off:** Branches require coordination and can introduce merge conflicts, but they support a clearer development process.

## 17. Command-Line Interface

**Decision:** Use a text-based interactive menu as the application's user interface.

The CLI is intended to connect the ticket creation, workflow, reporting, and persistence modules.

**Reason:** A CLI is suitable for a time-limited Python challenge and avoids the complexity of building a web frontend.

**Trade-off:** A CLI is less accessible to nontechnical users and does not provide multi-user access.

At the time of the 92-test integration run, the CLI entry point had not yet been verified end to end. Full CLI testing is therefore a separate completion requirement.

## 18. Limitations and Future Improvements

With additional development time, the team would consider:

- Replacing JSON storage with SQLite or PostgreSQL.
- Introducing staff accounts and authentication.
- Adding timestamps and ticket history.
- Implementing atomic file writes.
- Supporting concurrent users safely.
- Validating every field in saved ticket records.
- Adding search and filtering.
- Supporting ticket reassignment and escalation.
- Writing automated CLI integration tests.
- Providing a web-based interface.

## 19. Conclusion

CampusFlow was designed around simplicity, modularity, validation, and predictable workflows.

Engineer A implemented the ticket creation and priority management foundation, while Engineer B developed the workflow, reporting, and persistence capabilities.

The modular structure allowed both engineers to work independently, test their features, review each other's contributions, and integrate their work successfully.

The project demonstrates how Python fundamentals, automated testing, Git collaboration, and clear business rules can be combined to build a functional ticket management system.