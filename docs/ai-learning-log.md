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

