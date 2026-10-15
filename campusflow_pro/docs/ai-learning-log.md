# CampusFlow Pro — AI Learning Log

## Engineer B — Learning Cycles

## Cycle 1: Naive timestamps in the SLA queue (suggestion modified)

- **Problem:** The SLA attention queue needs each ticket's `created_at` to work out deadlines.
- **AI suggestion:** The first version of `attention_queue.py` required timezone-aware timestamps and rejected naive ones.
- **Verification:** I read `campusflow/tickets.py` and found that `current_timestamp()` uses `datetime.now()`, so every ticket created by the original app has a naive `created_at`. The AI's version would have rejected all of them.
- **Evidence:** After the change, the old test `test_naive_timestamp_rejected` failed, as expected, because the behaviour had changed on purpose. My manual edit also joined two lines and caused a `SyntaxError`, which the test run caught. I replaced the whole file instead of patching it.
- **Decision:** A naive `created_at` is treated as local time, while a naive `now` is still rejected. I replaced the old test with two tests, one for each rule. After the schema-v2 merge, this rule applies only to legacy tickets that have no `due_at`; schema-v2 tickets use their authoritative `due_at` deadline, and the other Pro modules reject naive timestamps.

## Cycle 2: Integrating audit logging without changing original code (suggestion accepted after checking)

- **Problem:** Audit events had to be recorded for create, assign, start, resolve and reopen without touching the original `campusflow/` functions or its 106 tests.
- **AI suggestion:** Add a `TicketService` wrapper that calls the original function first and records the audit event only if it succeeds.
- **Verification:** I checked that the original functions raise `ValueError` on failure, so a failure skips the recording step.
- **Evidence:** `test_failed_operations_record_nothing` checks that an unassigned start, a missing ticket and a non-resolved reopen add no events. `test_full_lifecycle_events_in_order` checks the order CREATE, ASSIGN, START, RESOLVE, REOPEN. All 106 original tests still passed.
- **Decision:** Keep the wrapper design.

## Cycle 3: Checking an AI checklist against the repository (claim not trusted)

- **Problem:** I needed to know what was left for Engineer B.
- **AI suggestion:** A chatbot produced a generic checklist and said it could not confirm the repository's state.
- **Verification:** I ran `git log` on `main` and the full test suite.
- **Evidence:** The log showed PR #10 (`feat/13-audit-queues`) already merged, along with the persistence and CLI/quiz PRs. All 303 tests passed.
- **Decision:** I did not build more features. I used the remaining time to answer the integration contract and write the documentation.

## Cycle 4: Contract wording checked against the code (suggestion rejected)

- **Problem:** I needed to reply to the escalation contract with the exact audit event format.
- **AI suggestion:** The draft reply said the ESCALATE event stores `{"sla_cycle": <n>}` in `details`.
- **Verification:** I searched the code with `grep` for the field names.
- **Evidence:** `sla_cycle` appears nowhere in the code. `campusflow_pro/sla/escalation.py` compares the event details to exactly `{"escalation_cycle": cycle}`.
- **Decision:** I corrected the contract to use `escalation_cycle` as the only key in `details`.


---
**Project:** CampusFlow Pro
**Repository:** https://github.com/Cruiz222/cli-campus-help-desk
**GitHub Issue:** #8
**Engineer:** Engineer A

---

## Engineer A — Learning Cycles
## Introduction

While working on CampusFlow Pro, I used AI mainly to help me understand some of the problems I encountered and think through possible solutions.

One thing I learned during this project is that getting code to work is not always the same as getting it to work correctly in every situation. Some features seemed straightforward at first, but when I started considering things like exact deadlines, failed file operations, and compatibility between different parts of the application, I realized there was more to them.

Below are three important areas where AI helped me understand a problem, but I still had to use tests and the actual application behavior to decide what worked.

---

## Learning Cycle 1: Understanding SLA Deadlines

### What I was trying to understand

One of my responsibilities was implementing the SLA system. The application needed to calculate how long an engineer had to attend to a ticket based on its priority.

My main concern was how to handle the exact deadline. For example, if a critical ticket was created at 10:00 AM and had a one-hour SLA, should it be considered overdue at exactly 11:00 AM or only after 11:00 AM?

It seemed like a small detail, but I realized it could affect escalation and how the application reports overdue tickets.

### How AI helped

I discussed the difference between using `>` and `>=` when comparing the current time with the SLA deadline.

The explanation helped me understand why the exact boundary matters. I also learned why using timezone-aware UTC timestamps is safer than depending on the computer's local time.

### What I tested

I worked with tests that used fixed timestamps instead of the actual system clock.

The important cases were:

- A critical ticket reaching its deadline exactly.
- The same ticket being checked after the deadline.
- A resolved ticket being checked for overdue status.

This allowed the behavior to be tested consistently without waiting for real time to pass.

### What I found and decided

The tests confirmed the intended behavior: a ticket should only be considered overdue when the current time is strictly greater than its deadline.

I used:

`now > due_at`

rather than:

`now >= due_at`

I also kept the SLA deadline in the ticket's `due_at` field so other parts of the application could use the same deadline.

This taught me that boundary conditions are important, especially when working with time-sensitive features. A difference of one second can change the outcome of an operation.

**Evidence:** SLA boundary tests and the passing integration test suite.

**Related work:** Commit `4e2aa96`, PR #12.

---

## Learning Cycle 2: Making JSON Persistence Safer

### What I was trying to understand

Another major part of my work was implementing JSON persistence.

At first, saving data to a JSON file seemed simple. But I started thinking about what would happen if the application failed while saving a ticket or if the existing JSON file contained invalid data.

I wanted to avoid a situation where a ticket was updated but its audit event was missing, or where a failed operation left the application with inconsistent information.

### How AI helped

AI helped me understand the importance of validating data before saving it and why writing directly to the main JSON file can be risky.

I explored the idea of writing the updated data to a temporary file first and then replacing the original file only when the write was successful.

I also learned that the application should not immediately treat an operation as successful just because the in-memory ticket object has changed.

### What I tested

I worked with tests covering different persistence situations, including:

- Saving and loading ticket information.
- Rejecting corrupted JSON.
- Validating the schema before accepting stored data.
- Checking that application state remains consistent when persistence fails.

These tests helped me check more than just whether a JSON file could be created.

### What I found and decided

I decided to use schema validation and atomic file replacement.

The application also needed to save successfully before publishing the updated in-memory state.

One important lesson for me was that a successful operation should not leave only part of the required changes behind.

This changed how I thought about persistence. I now see saving data as part of maintaining the correctness of the application, not just writing information to a file.

**Evidence:** Persistence tests, schema-v2 validation, and the passing test suite.

**Related work:** Commit `6796b2e`, PR #11.

---

## Learning Cycle 3: Integrating the SLA Attention Queue

### What I was trying to understand

This was one of the more challenging parts of the integration work.

Engineer B had already worked on the attention queue, while I had implemented the SLA policy and deadline calculations.

When we brought the components together, I had to consider how the queue should handle both the older ticket format and the new schema-v2 tickets.

The older behavior and the new SLA policy were not completely aligned. I was concerned that a ticket could have one deadline in the application but be classified differently by the attention queue.

### How AI helped

During the integration discussion, AI helped me examine the difference between recalculating deadlines and using a deadline that had already been stored.

The important point was that the new tickets already contained a `due_at` value. Recalculating that deadline using a different set of SLA durations could produce inconsistent results.

However, completely removing the old behavior could also break existing functionality.

### What I tested

I ran the existing attention-queue tests alongside the new integration tests.

I checked how the queue handled SLA classifications, deadlines, and ticket records using the newer schema.

I also ran the full project test suite to check whether the integration had affected previously working features.

The final merged version passed all 303 automated tests.

### What I found and decided

I chose to modify the integration approach rather than force all tickets through one calculation.

For schema-v2 tickets, the queue uses the stored `due_at` deadline.

For older tickets without that field, it retains the legacy calculation behavior.

This was an important learning experience because I realized that integrating two working components does not automatically mean they will work correctly together.

I also learned that sometimes the better solution is not to replace existing code completely, but to understand why it behaves differently and make the components compatible.

**This is an example of modifying the initial approach based on the integration tests and the behavior of the existing system.**

**Evidence:** Attention-queue integration tests and 303 passing automated tests.

**Related work:** Commits `8be318c` and `4e2aa96`, PR #12.

---

## My Overall Reflection

Working on CampusFlow Pro helped me become more careful about how I approach software development.

Before this project, I might have focused mainly on implementing a feature and checking that it worked under normal conditions. This project made me pay more attention to what happens when something goes wrong or when different parts of the application interact.

The SLA work taught me to think about boundary conditions. The persistence work helped me understand why data consistency matters. The integration work showed me why existing behavior and compatibility should be considered before making changes.

AI was useful because I could ask questions, explore different approaches, and understand concepts that were not immediately clear to me. However, I also learned that an explanation or suggestion is not enough on its own. I still needed to check the code, run tests, and understand the result before deciding what to implement.

One area I would improve in the future is handling multiple application processes writing to the same JSON file. The current implementation uses atomic file replacement, but that does not completely solve concurrent access. I would also like to introduce proper authentication and role-based authorization instead of relying only on actor names.

Overall, I feel more confident working with tests, reviewing integration problems, and making decisions based on evidence rather than assumptions.

---

## Final Verification

The integrated application was merged into `main` through PR #12.

The full automated test suite was executed using:

`python3 -m unittest discover -s . -p "test_*.py"`

**Result:** 303 tests passed, with no failures or errors.

I also manually checked the main CLI workflows, including ticket creation, assignment, starting and resolving tickets, reopening, ticket history, the SLA attention queue, reporting, and the Engineer Knowledge Quiz.

These checks helped confirm that the integrated features were working together as expected.