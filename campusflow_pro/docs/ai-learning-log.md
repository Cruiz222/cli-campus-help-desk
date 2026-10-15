cat > campusflow_pro/docs/ai-learning-log.md << 'EOF'
# Engineer B AI-Learning Log

## Cycle 1: Naive timestamps in the SLA queue (suggestion modified)

- **Problem:** The SLA attention queue needs each ticket's `created_at` to work out deadlines.
- **AI suggestion:** The first version of `attention_queue.py` required timezone-aware timestamps and rejected naive ones.
- **Verification:** I read `campusflow/tickets.py` and found that `current_timestamp()` uses `datetime.now()`, so every ticket created by the original app has a naive `created_at`. The AI's version would have rejected all of them.
- **Evidence:** After the change, the old test `test_naive_timestamp_rejected` failed, as expected, because the behaviour had changed on purpose. My manual edit also joined two lines and caused a `SyntaxError`, which the test run caught. I replaced the whole file instead of patching it.
- **Decision:** A naive `created_at` is treated as local time, while a naive `now` is still rejected. I replaced the old test with two tests, one for each rule.

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
EOF