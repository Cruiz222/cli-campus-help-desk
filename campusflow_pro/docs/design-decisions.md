# CampusFlow Pro — Architecture and Design Decisions

**Project:** CampusFlow Pro
**Team:** Engineer A and Engineer B
**Date:** October 15, 2026
**Status:** Implementation merged; final documentation and requirements review ongoing
**GitHub Issue:** #8

## Introduction

CampusFlow Pro is an improvement on our original CampusFlow helpdesk application. The first version already allowed users to create tickets, assign them, update their status, and generate reports.

For this project, we needed to add more features, including SLA deadlines, overdue escalation, audit history, duplicate-ticket detection, safer JSON storage, an attention queue, and an Engineer Knowledge Quiz.

As a junior developer, I found that one of the biggest challenges was not just writing the new features but making sure they worked together without affecting the existing application.

This document explains the main design decisions we made, why we chose them, and some of the things we would improve in the future.

---

## ADR-001: Keeping CampusFlow Pro Separate from the Original Application

### The problem

The original CampusFlow application was already working and had 106 passing tests before we started the Pro extension.

Adding all the new features directly into the existing modules could make the code harder to maintain and increase the chances of breaking something.

### Our decision

We created a separate package called `campusflow_pro` for the new features.

The original `campusflow` package remains available, while the Pro package contains the additional functionality.

The main entry point for the integrated version is `main_pro.py`.

### Why we chose this

This made it easier for both engineers to work on different parts of the project.

It also helped us organize the code. For example, the SLA logic is kept separate from the persistence logic, and the CLI does not need to handle every business rule directly.

### What I learned

I learned that organizing code properly becomes more important as a project grows. Even when two features are related, they do not always need to be written in the same file.

---

## ADR-002: Preserving the Original Business Rules

### The problem

CampusFlow Pro was meant to extend the original system, not replace it.

The original application already had rules for ticket priorities, assignments, and status transitions.

If we created different versions of those rules without considering the existing behavior, the two applications could produce inconsistent results.

### Our decision

We kept the original functionality available and used regression tests to check that the new work did not break it.

We also made sure that ticket operations in the Pro application followed the required status transitions.

For example, a ticket must be assigned before it can be started, and only a resolved ticket can be reopened.

### Why we chose this

It would not make sense to introduce new features if the existing ones stopped working.

Keeping the old tests passing gave us more confidence during development.

### Trade-off

Supporting older behavior sometimes required extra compatibility logic, especially when working with ticket timestamps and SLA calculations.

---

## ADR-003: Using UTC Timestamps

### The problem

The SLA system depends on time, so we needed a reliable way to calculate deadlines.

Using local timestamps could cause confusion if the application was run on computers with different timezone settings.

### Our decision

We used timezone-aware UTC timestamps for new CampusFlow Pro operations.

We also designed the SLA functions to support fixed clocks during testing.

### Why we chose this

UTC gives us a consistent reference for comparing timestamps.

Fixed clocks are useful because we can test a ticket's deadline without waiting for real time to pass.

For example, we can create a ticket at 10:00 AM UTC and check its behavior at exactly 11:00 AM UTC.

### What I learned

I learned that time-related bugs can be difficult to notice if tests depend on the actual system clock.

Using controlled timestamps made the SLA tests more predictable.

---

## ADR-004: Keeping SLA Rules in One Place

### The problem

Different ticket priorities have different response deadlines.

If every part of the application calculates deadlines independently, it becomes easy for the results to disagree.

### Our decision

We used a central SLA policy with these durations:

| Priority | SLA duration |
|---|---|
| Critical | 1 hour |
| High | 4 hours |
| Medium | 24 hours |
| Low | 48 hours |

New tickets store their deadline in the `due_at` field.

A ticket is overdue only when the current time is strictly later than its deadline and the ticket is not resolved.

### Why we chose this

Having one policy makes it easier to understand and test how deadlines are calculated.

It also prevents different parts of the application from using different SLA durations for the same new ticket.

### What I learned

The exact deadline is an important boundary.

For example, a critical ticket created at 10:00 AM UTC is not overdue at exactly 11:00 AM UTC. It becomes overdue only after that time.

That is why we used `now > due_at` instead of `now >= due_at`.

---

## ADR-005: Preventing Duplicate Escalations

### The problem

An overdue ticket might be checked more than once.

Without proper tracking, the application could create a new escalation event every time the same ticket was checked.

That would make the audit history misleading.

### Our decision

We introduced two fields:

- `escalation_cycle` tracks the ticket's current SLA cycle.
- `escalated_cycle` records the cycle in which the ticket was last escalated.

A new ticket starts at cycle `0`.

When a resolved ticket is reopened, its SLA cycle increases and a fresh deadline is calculated.

### Why we chose this

It allows the application to recognize when a ticket has already been escalated during its current cycle.

For example, checking the same overdue ticket three times should create only one escalation event.

If the ticket is later resolved and reopened, it can be escalated again during the new cycle.

### What I learned

This helped me understand **idempotency**.

An operation is idempotent when repeating it does not keep producing additional changes after the intended result has already been achieved.

We also tested this behavior across application restarts, not just during one running session.

---

## ADR-006: Using Versioned JSON Storage

### The problem

The original application used JSON for persistence.

For CampusFlow Pro, we needed to store additional information, including SLA deadlines, escalation cycles, and audit events.

We also needed to handle invalid or corrupted data safely.

### Our decision

We introduced schema-v2 JSON persistence.

The application validates the stored document and uses atomic file replacement when saving changes.

### Why we chose this

JSON was suitable for the project requirements because we were expected to work with Python's standard library.

However, writing directly to the main file could leave it partially written if something failed during the operation.

Using a temporary file and replacing the original after a successful write reduces that risk.

### What I learned

I initially thought of persistence mainly as saving and loading information.

This part of the project helped me understand that persistence also involves protecting data from invalid updates and failed operations.

### Limitation

Atomic file replacement does not fully solve concurrent access.

If two separate application processes read and update the same file, one process could overwrite changes made by the other.

A future version could use file locking or a database with transaction support.

---

## ADR-007: Recording Audit History

### The problem

A helpdesk system should be able to explain what happened to a ticket.

For example, we should be able to tell when a ticket was created, who assigned it, and when its status changed.

### Our decision

We added audit events for successful ticket operations:

- CREATE
- ASSIGN
- START
- RESOLVE
- REOPEN
- ESCALATE

Each event includes information such as its unique ID, ticket ID, event type, actor, timestamp, status changes, and additional details.

The event history is append-only through the application's normal operations.

### Why we chose this

Audit events make it easier to understand a ticket's history and investigate unexpected behavior.

We also decided that failed operations should not produce successful-operation audit events.

For example, if someone tries to start an unassigned ticket, the application should reject the operation without changing the ticket or adding a START event.

### What I learned

An audit log should describe what actually happened, not just what someone attempted to do.

This made me pay more attention to the order in which validation, state changes, and persistence happen.

---

## ADR-008: Separating the CLI from Application Logic

### The problem

If all the business rules were written directly inside the CLI menu, the code would become difficult to test and maintain.

Every test might require simulating user input, even when we only wanted to check a ticket rule.

### Our decision

We used `ProApplication` to coordinate ticket operations.

The CLI in `main_pro.py` handles interaction with the user, while the application layer handles the operations behind the menu.

### Why we chose this

It made it easier to test the application logic separately.

We could test creating, assigning, resolving, reopening, and escalating tickets without always running the interactive CLI.

It also helped us handle invalid input and keyboard interruptions more safely.

### What I learned

I learned that separating responsibilities makes code easier to understand.

The CLI should mainly deal with what the user sees and enters. It should not be responsible for implementing every ticket rule.

---

## ADR-009: Maintaining One Consistent Ticket State

### The problem

Ticket operations often involve more than one change.

For example, resolving a ticket changes its status and should also create an audit event.

If only one of those changes is saved, the ticket history and current state could disagree.

### Our decision

We made the application validate the proposed changes and persist the ticket data and audit events together.

The updated in-memory state is published only after the save succeeds.

### Why we chose this

This reduces the risk of an operation appearing successful when its required information was not properly saved.

### What I learned

This was one of the areas that helped me understand consistency.

A ticket operation is not complete just because one field has changed. All the changes required by that operation need to agree.

---

## ADR-010: Sharing Responsibilities Between Two Engineers

### The problem

We were working on the same project, but we needed to avoid constantly changing each other's files without coordination.

### Our decision

We divided the major responsibilities between Engineer A and Engineer B.

**Engineer A** focused mainly on the SLA engine, escalation behavior, persistence, and data integrity.

**Engineer B** focused mainly on audit history, duplicate detection, attention queues, reporting, and the CLI and Knowledge Lab work.

Some parts, especially integration and testing, required both engineers to coordinate.

### Why we chose this

It allowed us to work on different features while keeping the responsibilities clear.

We also needed to agree on shared fields and interfaces, especially where the SLA engine interacted with audit events and persistence.

### What I learned

Working with another engineer showed me that communication is part of software development.

Even when two pieces of code work separately, they can still have problems when integrated if both developers made different assumptions.

---

## ADR-011: Using Git Branches and Pull Requests

### The problem

We needed a way to work on separate features without constantly changing the stable `main` branch.

We also needed to review each other's work before merging.

### Our decision

We used feature branches, commits, and pull requests.

The project history includes PRs for the audit and queue work, data integrity, and the final Pro integration.

For example:

- PR #10 — Audit and queue work
- PR #11 — Data integrity
- PR #12 — CampusFlow Pro integration

### Why we chose this

Pull requests gave us a way to review changes before adding them to `main`.

They also helped us track which commits introduced particular features.

### What I learned

I became more comfortable with Git branches, checking changes, running tests before committing, and merging work through pull requests.

I also learned that passing tests does not replace code review. Another developer may notice risks that the existing tests do not cover.

---

## ADR-012: Writing Deterministic Tests and Preserving Regression Coverage

### The problem

We needed to confirm that the new features worked without breaking the original application.

Some features, especially SLA deadlines and escalation, also had edge cases that were difficult to test manually.

### Our decision

We used Python's built-in `unittest` framework.

For time-dependent behavior, we used fixed UTC timestamps.

For persistence tests, we used temporary files so tests would not depend on or modify real application data.

We also kept the original tests running alongside the new tests.

### Why we chose this

Fixed inputs make tests easier to repeat.

Testing boundary conditions helped us catch problems that might not appear during ordinary use.

### Verification

After the integration PR was merged, we ran:

`python3 -m unittest discover -s . -p "test_*.py"`

The result was:

**303 tests passed with no failures or errors.**

We also manually tested the CLI workflows after the merge.

### What I learned

I learned that tests are not only for checking whether a feature works. They also help explain what the expected behavior should be.

---

## ADR-013: Keeping the Engineer Knowledge Lab Separate

### The problem

The Engineer Knowledge Lab was introduced to check whether engineers understood important parts of the project.

It needed to run without changing actual helpdesk tickets.

### Our decision

We implemented the Engineer Knowledge Quiz separately from the ticket-management logic.

The integrated CLI provides a ten-question multiple-choice quiz covering SLA deadlines, ticket transitions, escalation, persistence, code review, and safe AI usage.

The quiz includes scoring and explanations.

### Why we chose this

Learning activities should not accidentally change ticket records or interfere with helpdesk operations.

Keeping the quiz separate also made it easier to test.

### What still needs checking

Issue #8 requires more than multiple-choice questions.

It also requires written explanations, saved participant sessions, and a way for mentors to inspect those sessions.

Although we manually tested the quiz and its existing tests passed, we still need to verify these additional requirements before considering the Knowledge Lab fully complete.

---

## ADR-014: Using AI as a Learning Tool

### The problem

We used AI assistance during development, but the purpose of the project was to improve our own engineering understanding.

Simply copying a suggested solution would not prove that we understood it.

### Our decision

We used AI to discuss problems, understand possible approaches, and identify cases worth testing.

We then used the implementation and tests to check whether those approaches were suitable.

Each engineer is expected to document at least three learning cycles, including a case where AI advice was modified or rejected based on evidence.

### Why we chose this

AI can help explain unfamiliar concepts, but it can also suggest approaches that do not fully match an existing codebase.

The developer still needs to understand the problem and verify the result.

### What I learned

One of my biggest lessons was that I should not accept a solution just because it looks correct.

The SLA attention-queue integration was a useful example. We had to adjust the approach so the new stored deadlines worked correctly without breaking legacy behavior.

---

## Final Integration Decisions

During development, we resolved several decisions that were originally left open.

### Ticket schema

The new schema includes fields such as `due_at`, `escalation_cycle`, and `escalated_cycle`.

These fields allow the SLA system and escalation workflow to share the same ticket information.

### Escalation and audit events

A successful escalation updates the ticket's escalation marker and records an audit event.

Repeated escalation checks during the same cycle do not create duplicate events.

### Persistence and state consistency

The application validates and saves the updated document before publishing the new in-memory state.

Rejected operations should leave ticket data and audit history unchanged.

### Legacy compatibility

For schema-v2 tickets, the attention queue uses the stored `due_at` deadline.

For older tickets without `due_at`, the queue retains legacy calculation behavior.

This was necessary because the existing queue and the new SLA engine originally used different deadline rules.

### CLI integration

The completed Pro CLI is available through `main_pro.py`.

It provides ticket operations, history, SLA attention queue, escalation, reporting, and the Engineer Knowledge Quiz.

### Error handling

Invalid operations are rejected without saving partial changes.

The CLI also handles ordinary input errors and interruptions without unexpectedly crashing.

---

## Remaining Limitations and Improvements

Although the main application has been integrated and tested, there are still some areas that could be improved.

**Concurrent access:** The JSON persistence layer does not currently provide shared locking across multiple processes. This could become a problem if several application instances tried to update the same file.

**Authentication:** The application uses actor names supplied through input. A real helpdesk system would need authentication and role-based permissions.

**Knowledge Lab requirements:** We still need to verify written-answer collection, session persistence, and mentor inspection against the GitHub issue.

**Documentation:** Both engineers need to complete and verify their individual learning evidence and reflections.

These limitations should be documented clearly rather than treated as features that have already been completed.

---

## Conclusion

Working on CampusFlow Pro helped me understand that building an application involves more than writing functions that work individually.

We had to consider how different components share information, how the application behaves when something fails, and how to preserve existing functionality while adding new features.

Some of the most useful lessons came from problems we discovered during integration, especially around SLA deadlines, persistence, and compatibility.

The project also gave me more experience working with another engineer, reviewing code, using Git, and writing tests.

The main application has been merged and passed its automated tests, but we still need to finish the remaining documentation and verify all the requirements in Issue #8 before closing the project.