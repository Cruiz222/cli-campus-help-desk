# AI LEARNING LOG FOR ENGINEER A - OFFORBUZOR OSINAKE DIVINE

### Entry 1: Validating Affected Users

- **Problem:** My validation function rejected valid integers and numeric strings.
- **My initial understanding:** I thought my type check was correct.
- **Prompt to AI:** Why are my affected-user validation tests failing?
- **Useful AI guidance:** The `or` condition caused both valid types to be rejected.
- **My independent experiment/test:** Ran `python -m unittest discover -s tests -v`.
- **Verification source or result:** The traceback pointed to `validate_affected_users`; multiple ticket-creation tests failed.
- **Decision:** Improved my validation logic based on the explanation.
- **Related file/commit:** `campusflow/tickets.py`, `tests/test_tickets.py`.
- **What I can now explain without AI:** How `or` and `isinstance()` affect type validation.

### Entry 2: Boolean Validation

- **Problem:** Python treats booleans as integers.
- **My initial understanding:** I needed to distinguish `True` and `False` from ordinary integers.
- **Prompt to AI:** How should I reject booleans while accepting integers?
- **Useful AI guidance:** `bool` is a subclass of `int` in Python.
- **My independent experiment/test:** Boolean rejection is covered by my test suite; I have not recorded a separate experiment here.
- **Verification source or result:** The roadmap requires booleans to be rejected.
- **Decision:** Included an explicit boolean check in validation.
- **Related file/commit:** `campusflow/tickets.py`, `tests/test_tickets.py`.
- **What I can now explain without AI:** Why `isinstance(True, int)` returns `True`.

### Entry 3: Protecting Stored Tickets

- **Problem:** Returning ticket data could allow callers to modify stored records unintentionally.
- **My initial understanding:** A new list alone might be enough to protect the original data.
- **Prompt to AI:** Why use `deepcopy()` when listing tickets?
- **Useful AI guidance:** A shallow copy still shares the dictionaries inside the list.
- **My independent experiment/test:** My test suite includes `test_modifying_listed_ticket_status_does_not_affect_storage`; it was blocked by an earlier validation error.
- **Verification source or result:** The test appeared in the test output, but its assertion has not yet been verified as passing.
- **Decision:** Used `deepcopy()` to provide independent ticket dictionaries.
- **Related file/commit:** `campusflow/tickets.py`, `tests/test_tickets.py`.
- **What I can now explain without AI:** The difference between a shallow copy and a deep copy.

### Entry 4: Generating Ticket IDs

- **Problem:** I needed ticket IDs that remain unique when creating new tickets.
- **My initial understanding:** I needed a way to generate the next sequential ID.
- **Prompt to AI:** How can I generate ticket IDs automatically?
- **Useful AI guidance:** AI suggested using `itertools` to generate sequential IDs.
- **My independent experiment/test:** I considered how the counter would behave when the program restarts and existing tickets are loaded.
- **Verification source or result:** The approach did not fit my need to continue numbering from existing tickets after a restart.
- **Decision:** Rejected the `itertools` approach in favour of finding the highest existing numeric ticket ID and adding one.
- **Related file/commit:** `campusflow/tickets.py` — `generate_ticket_id`.
- **What I can now explain without AI:** Why a counter that starts from its initial value may generate duplicate IDs when existing tickets are loaded.


--------------------------------------------------------------------------------------------------------

# AI Learning Log — Engineer B John Abah

**Project:** CampusFlow — Campus Helpdesk Ticket Management System  
**Role:** Engineer B — Workflow, Reporting, and Persistence  
**Language:** Python  
**Testing Framework:** unittest

## 1. How I Used AI

I used ChatGPT as a programming assistant while developing my assigned features for CampusFlow.

Initially, I asked AI to guide me step by step rather than provide complete implementations. I wrote the code myself, tested it, and shared errors for review.

As the project deadline approached, I changed my approach and requested complete code solutions followed by explanations to help finish the implementation on time.

AI assisted with:
- Understanding Python functions, dictionaries, lists, and sets.
- Designing ticket assignment and status transition rules.
- Writing and debugging unit tests.
- Implementing ticket queues and summary reports.
- Reading and writing JSON files.
- Identifying edge cases and improving validation.
- Reviewing my teammate's pull request.
- Preparing the integration of both engineers' implementations.

## 2. Features I Implemented

### F3 — Ticket Assignment

Implemented the ability to assign tickets to staff members.

The implementation handles invalid staff names, unknown ticket IDs, and attempts to assign resolved tickets.

### F4 — Ticket Status Workflow

Implemented controlled status transitions:

`open → in_progress → resolved`

A ticket must be assigned before work can begin. A resolved ticket cannot be modified through the normal status update process, but it can be reopened through a separate operation.

### F5 — Work Queue

Implemented a queue that displays open tickets in priority order:

`critical → high → medium → low`

When tickets have equal priority, they are sorted by their numeric ticket IDs. The sorting operation does not modify the original ticket list.

### F6 — Reporting

Implemented a reporting function that summarizes:
- Total number of tickets.
- Number of tickets in each status.
- Number of tickets in each priority category.

### F7 — JSON Persistence

Implemented functions to save tickets to a JSON file and load them when needed.

The implementation also handles missing files, malformed JSON, invalid top-level data structures, invalid ticket IDs, and duplicate ticket IDs.

## 3. Challenges and Lessons Learned

### Challenge 1 — Understanding JSON File Operations

While implementing persistence, I initially confused reading and writing operations.

I learned that `json.dump()` writes Python data to a file, while `json.load()` reads JSON data from a file.

I corrected the implementation and verified that tickets could be saved and loaded successfully.

**Lesson:** File modes and JSON functions must match the operation being performed.

### Challenge 2 — Detecting Duplicate Ticket IDs

My first test attempted to represent duplicate IDs by repeating the `"id"` key inside a single dictionary.

I learned that dictionary keys must be unique, so repeating a key does not create two separate tickets.

I corrected the test by creating two ticket dictionaries with the same ID.

The test initially failed because the storage implementation did not detect duplicates. I then added validation using a Python set to track previously encountered IDs.

**Lesson:** Sets are useful for checking uniqueness, and tests can reveal missing validation rules.

### Challenge 3 — Preventing Invalid Status Changes

Ticket statuses must follow specific business rules.

For example, an unassigned ticket should not move to `in_progress`, and an open ticket should not be resolved directly.

I implemented validation and unit tests to ensure invalid transitions were rejected.

**Lesson:** Business rules should be enforced in the application logic, not left to users to follow manually.

### Challenge 4 — Reviewing Another Engineer's Code

During code review, I identified issues involving validation of `None` as an affected-user count and shallow copying of ticket dictionaries.

The affected-user validation was improved to reject unsupported input types. The ticket listing implementation was changed to use deep copying, preventing modifications to returned ticket dictionaries from changing the original records.

**Lesson:** Code review helps identify edge cases that may be missed during initial implementation.

## 4. Testing and Debugging

I used Python's built-in `unittest` framework.

The main command was:

```bash
python3 -m unittest discover -s tests -v
```

I followed a test-driven approach for several features:

1. Write a test describing the expected behavior.
2. Run the test and observe the failure.
3. Implement or correct the function.
4. Run the tests again.
5. Check that existing functionality still works.

Before integration, my assigned modules passed 29 tests.

After integrating both engineers' branches, the combined project passed **92 tests with zero failures and zero errors**.

These tests provided confidence in the individual features, although the complete interactive CLI still required end-to-end verification.

## 5. Collaboration and Version Control

We divided the project into two areas of responsibility.

Engineer A handled ticket creation, input validation, priority calculation, and ticket listing.

I handled assignment, status management, work queues, reporting, and persistence.

We developed on separate Git branches and used pull requests for collaboration.

I also participated in reviewing Engineer A's implementation before integrating both branches.

## 6. What I Learned

This project improved my understanding of:

- Writing modular Python programs.
- Using dictionaries and lists to represent records.
- Using sets to detect duplicates.
- Implementing business rules through validation.
- Writing unit tests and understanding expected test failures.
- Working with JSON files.
- Reviewing code and collaborating through Git.
- Integrating independently developed modules.

## 7. What I Would Improve

With more time, I would:

- Add stronger validation for all fields in loaded ticket records.
- Use atomic file writes to reduce the risk of corrupting saved data.
- Add automated tests for the complete CLI workflow.
- Improve error handling and user-facing messages.
- Consider a database if the system needed to support many users or concurrent updates.

## Conclusion

AI helped me learn, debug, and complete my assigned features, but testing and reviewing the generated solutions remained important.

The most valuable lesson was understanding why a solution works rather than relying only on whether it runs successfully.