# CampusFlow — Architecture and Design Decisions

## Project: CampusFlow Pro

**Status:** Approved for implementation  
**Date:** October 14, 2026  
**Team:** Engineer A and Engineer B  
**Baseline:** CampusFlow v1 — 106 passing tests

---

## ADR-001: Separate CampusFlow Pro from the Existing Application

### Context

CampusFlow currently supports ticket creation, priority calculation, mentor assignment, ticket status transitions, work queues, reporting, and JSON persistence.

The CampusFlow Pro challenge introduces several new requirements, including SLA deadlines, overdue escalation, audit history, duplicate detection, enhanced analytics, versioned persistence, and an Engineering Knowledge Lab.

Introducing all these features directly into the existing modules could increase coupling and make regressions more difficult to isolate.

### Decision

Create a new Python package named `campusflow_pro/` to contain the additional functionality.

The original `campusflow/` package will remain the authoritative implementation of existing ticket and workflow rules.

The Pro package will extend and integrate with those rules rather than duplicate them.

### Proposed Structure

```text
cli-campus-help-desk/
├── campusflow/
│   ├── __init__.py
│   ├── tickets.py
│   └── workflow/
│       ├── assign_ticket.py
│       ├── mentor_assignment.py
│       ├── ticket_status.py
│       ├── work_queue.py
│       ├── reports.py
│       └── storage.py
│
├── campusflow_pro/
│   ├── __init__.py
│   ├── sla/
│   │   ├── __init__.py
│   │   ├── clock.py
│   │   ├── policy.py
│   │   ├── overdue.py
│   │   └── escalation.py
│   ├── persistence/
│   │   ├── __init__.py
│   │   ├── schema.py
│   │   └── json_store.py
│   ├── audit/
│   │   ├── __init__.py
│   │   └── history.py
│   ├── duplicates.py
│   ├── attention_queue.py
│   ├── analytics.py
│   ├── knowledge_lab.py
│   └── commands.py
│
├── tests/
├── tests_pro/
├── main.py
├── main_pro.py
└── docs/
    └── design-decisions.md
```

### Rationale

1. Protect existing functionality from unnecessary modifications.
2. Allow engineers to work on separate modules.
3. Improve test isolation.
4. Make the integration boundary explicit.
5. Preserve the existing 106-test regression baseline.
6. Keep the new features organized by responsibility.

### Consequences

**Positive:**
- New features are easier to locate and maintain.
- Existing tests remain useful as regression protection.
- Parallel development becomes more manageable.

**Trade-offs:**
- Some original modules may require integration changes.
- The command layer must coordinate both packages.
- Duplicate implementations of priority, assignment, or status rules must be avoided.

---

## ADR-002: Preserve Existing Business Rules

### Decision

The existing CampusFlow business rules remain authoritative.

These include:

- Priority calculation based on urgency and affected users.
- Ticket ID generation.
- Assignment requirements.
- Legal status transitions.
- Mentor assignment restrictions.
- Original Open Work Queue ordering.

CampusFlow Pro must reuse existing functions where possible.

For example:

```python
from campusflow.tickets import calculate_priority
```

### Rationale

Reimplementing existing rules would create multiple sources of business logic and increase the risk of inconsistent behavior.

### Consequences

Any necessary changes to original modules must preserve existing behavior and be supported by regression tests.

---

## ADR-003: Use Timezone-Aware UTC Timestamps

### Context

The original application uses timezone-naive timestamps generated through `datetime.now()`.

CampusFlow Pro requires reliable SLA calculations.

### Decision

All new CampusFlow Pro timestamps must be timezone-aware UTC values.

Use Python's standard-library `datetime` module.

The SLA engine must support injected timestamps so tests can run deterministically.

### Rules

- Store timestamps using ISO-8601 format.
- Include explicit UTC timezone information.
- Reject invalid or unsupported datetime inputs.
- Do not silently interpret historical naive timestamps as UTC.
- Preserve original creation timestamps when reopening tickets.

### Rationale

Timezone-aware timestamps prevent ambiguity and make SLA calculations reliable.

---

## ADR-004: Centralize SLA Business Rules

### Decision

All SLA calculations will be implemented within `campusflow_pro/sla/`.

Required SLA durations:

| Priority | Duration |
|---|---|
| Critical | 60 minutes |
| High | 240 minutes |
| Medium | 1,440 minutes |
| Low | 2,880 minutes |

A ticket is overdue only when:

- Its status is not `resolved`.
- The current time is strictly later than `due_at`.

At the exact deadline, a ticket is not overdue.

### Reopening Rule

When a resolved ticket is reopened:

1. Preserve `created_at`.
2. Increment `escalation_cycle`.
3. Calculate a new deadline.
4. Update `updated_at`.
5. Reset the escalation marker.

### Rationale

Centralizing these rules prevents different modules from calculating deadlines inconsistently.

---

## ADR-005: Escalation Must Be Idempotent

### Context

Repeated manual escalation checks must not create duplicate escalation records for the same SLA cycle.

### Decision

A ticket may be escalated at most once per SLA cycle.

Escalation must not automatically change:

- Ticket priority.
- Ticket assignment.
- Ticket status.

Reopening starts a new cycle, making the ticket eligible for escalation again if the new deadline is exceeded.

### Implementation Consideration

The system must track whether the current SLA cycle has already been escalated.

Possible strategies include:

- A per-cycle marker on the ticket.
- Deriving escalation state from recorded audit events.

The final strategy must be agreed upon before implementation.

### Rationale

Idempotency ensures repeated operations do not produce duplicate business effects.

---

## ADR-006: Use Versioned JSON Persistence

### Context

The original application stores tickets as a JSON list.

CampusFlow Pro requires tickets and audit events to be persisted together.

### Decision

The canonical CampusFlow Pro persistence format will be:

```json
{
  "schema_version": 2,
  "tickets": [],
  "events": []
}
```

### Persistence Requirements

- Validate the entire document before accepting loaded data.
- Reject unsupported schema versions.
- Reject duplicate ticket IDs.
- Validate event-to-ticket relationships.
- Reject malformed timestamps and invalid required fields.
- Save through a temporary file in the same directory.
- Replace the destination using `os.replace()`.
- Preserve existing valid data when loading fails.
- Avoid fabricating missing historical data.

### Compatibility

The original list-style JSON storage functions may remain available for legacy functionality.

Legacy migration must be explicit rather than automatic.

### Rationale

Versioned persistence makes the data contract explicit and supports safer future changes.

### Limitation

Atomic replacement prevents partial destination-file replacement but does not independently solve concurrent-write conflicts.

---

## ADR-007: Maintain Append-Only Logical Audit History

### Decision

CampusFlow Pro must record successful operations using audit events.

Required event types:

- CREATE
- ASSIGN
- START
- RESOLVE
- REOPEN
- ESCALATE

Each event contains:

```text
event_id
ticket_id
event_type
actor
timestamp
before_status
after_status
details
```

Events must remain unchanged after creation during normal application operations.

### Transaction Consistency

A successful ticket operation must produce a consistent ticket state and corresponding audit event.

Rejected operations must not modify either.

The application command layer will coordinate validation, state changes, event creation, and persistence.

### Rationale

Audit events provide traceability and support ticket-history inspection.

### Limitation

Append-only logical history does not make a JSON file tamper-proof against external editing.

---

## ADR-008: Separate Domain Logic from CLI Interaction

### Decision

Business rules must not depend on interactive input or output.

The CLI is responsible for:

- Collecting user input.
- Displaying results.
- Confirming duplicate warnings.
- Showing validation errors.
- Navigating menus.

Domain and application modules are responsible for:

- Validating operations.
- Enforcing business rules.
- Calculating SLA deadlines.
- Recording successful operations.
- Coordinating persistence.

### Entry Points

During development:

- `main.py` remains the original CampusFlow entry point.
- `main_pro.py` provides the CampusFlow Pro interface.

Before final submission, the documented primary entry point must expose the complete required CampusFlow Pro functionality.

### Rationale

Separating CLI and business logic improves testability and reduces coupling.

---

## ADR-009: Maintain One Authoritative Ticket State

### Decision

The original and Pro applications must not independently maintain conflicting copies of the same ticket records.

CampusFlow Pro will use one canonical version-2 document for active ticket state and audit history.

The original modules may be reused as business-rule helpers, but the Pro command layer must control how changes are committed.

### Rationale

Multiple independent ticket stores could produce inconsistent statuses, assignments, and history.

### Consequences

The team must carefully coordinate the integration between existing ticket functions and the Pro persistence layer.

---

## ADR-010: Establish Clear Engineering Ownership

### Engineer A — SLA and Data Integrity

Responsible for:

- UTC clock.
- SLA policies and deadline calculations.
- Overdue detection.
- Escalation and SLA cycles.
- Version-2 schema validation.
- Atomic JSON persistence.
- Ticket ID continuity.
- SLA and persistence tests.

### Engineer B — Audit, Queues, CLI, and Knowledge Lab

Responsible for:

- Audit-event recording.
- Ticket history.
- Duplicate detection.
- SLA Attention Queue.
- Enhanced analytics.
- CLI integration.
- Engineering Knowledge Lab.
- Audit, queue, CLI, and quiz tests.

### Shared Responsibilities

- Agree on function contracts.
- Preserve original business rules.
- Review pull requests.
- Resolve integration conflicts.
- Maintain documentation.
- Verify end-to-end workflows.

### Rationale

Clear ownership enables parallel development without unnecessary duplication.

---

## ADR-011: Use Feature Branches and Peer-Reviewed Pull Requests

### Decision

Development will take place through feature branches.

Planned branches:

| Branch | Owner | Scope |
|---|---|---|
| `feat/11-sla-engine` | Engineer A | SLA and escalation |
| `feat/12-data-integrity` | Engineer A | Version-2 persistence |
| `feat/13-audit-queues` | Engineer B | Audit, duplicates, queues |
| `feat/14-cli-knowledge-lab` | Engineer B | CLI and Knowledge Lab |

Each engineer must contribute at least two pull requests and review the other engineer's work.

Direct feature commits to `main` are prohibited.

### Review Requirements

- At least two substantive review observations per PR.
- Partner approval before merging.
- Tests must pass before merging.
- Integration decisions must be documented.

---

## ADR-012: Preserve Regression Coverage and Add Deterministic Tests

### Decision

The existing 106 passing tests form the regression baseline.

CampusFlow Pro must introduce at least 16 meaningful new tests, with at least six authored by each engineer.

### Test Organization

- `tests/` — existing CampusFlow tests.
- `tests_pro/` — CampusFlow Pro tests.

### Test Principles

- Use fixed UTC clocks.
- Use temporary files.
- Test boundary conditions.
- Test failed operations.
- Verify no unintended state mutation.
- Avoid real-time delays and sleeps.
- Run both test suites before merging.

### Verification Command

```bash
python3 -m unittest discover -s . -p "test_*.py"
```

### Rationale

Deterministic tests improve reliability and make regressions easier to identify.

---

## ADR-013: Keep the Engineering Knowledge Lab Independent

### Decision

The Engineering Knowledge Lab will be implemented separately from ticket-management operations.

It must:

- Present ten multiple-choice questions.
- Accept answers A/B/C/D.
- Re-prompt invalid answers.
- Collect at least three free-text explanations.
- Score responses out of ten.
- Show topics needing revision.
- Save participant sessions in JSON.
- Allow mentors to inspect sessions.
- Never modify ticket state.

### Rationale

The Knowledge Lab evaluates engineering understanding without affecting helpdesk operations.

---

## ADR-014: Record and Verify AI-Assisted Engineering Decisions

### Decision

Each engineer must document at least three substantive AI-learning cycles.

Every cycle should include:

1. Engineering problem or uncertainty.
2. AI suggestion or explanation.
3. Independent verification.
4. Test or experimental evidence.
5. Final engineering decision.

At least one documented cycle must show an AI suggestion being rejected or modified based on evidence.

### Rationale

AI assistance must support engineering understanding rather than replace independent verification.

---

## Outstanding Integration Decisions

The following must be finalized before dependent implementation begins:

- [ ] Exact shared ticket schema, including escalation marker representation.
- [ ] Function signatures for SLA and audit integration.
- [ ] Atomicity strategy for ticket and event updates in memory.
- [ ] Legacy timestamp compatibility.
- [ ] Whether legacy JSON migration will be implemented.
- [ ] Final CampusFlow Pro CLI entry point.
- [ ] Error and exception contracts between modules.

These decisions should be resolved jointly by Engineer A and Engineer B and recorded here before implementation.

---

## Final Architectural Principle

**CampusFlow Pro extends the existing CampusFlow system without duplicating its core business rules.**

The original package remains responsible for established ticket behavior.

The new `campusflow_pro/` package introduces advanced functionality through clearly defined interfaces.

Both engineers are responsible for ensuring that the integrated system remains reliable, testable, auditable, and maintainable.