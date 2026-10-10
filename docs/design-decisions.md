# CampusFlow Design Decisions

## 1. Shared Conventions

The following conventions are based on the team roadmap and documented for confirmation during integration with Engineer B.

- Tickets are stored as a `list` of `dict` objects, passed into functions as arguments.
- Pure logic functions do not use `input()` or `print()`; the CLI handles interaction.
- Invalid input and unknown ticket IDs raise `ValueError` with clear messages.
- Functions validate inputs before modifying ticket data to prevent partial changes.
- Shared function contracts follow Section 3 of the team roadmap.

## 2. Engineer A — `tickets.py`

- `validate_affected_users` accepts integers and numeric strings, returns a positive integer, and rejects booleans, floats, and invalid values.
- Validators return cleaned and normalized values.
- `calculate_priority` expects validated inputs; `create_ticket` validates before calculating priority.
- `generate_ticket_id` uses the highest existing numeric ID plus one to avoid collisions after reload.
- `create_ticket` appends and returns the new ticket with all required fields and default values.
- `get_ticket_by_id` returns the actual ticket dictionary for workflow modifications.
- `list_tickets` returns independent deep copies to protect stored tickets.

## 3. Function Contracts

| Function | Return value |
|---|---|
| `validate_title`, `validate_category`, `validate_urgency` | Cleaned, normalized values |
| `validate_affected_users` | Positive integer |
| `calculate_priority` | Priority string |
| `generate_ticket_id` | Next ticket ID |
| `create_ticket` | Created ticket dictionary |
| `get_ticket_by_id` | Actual matching ticket dictionary |
| `list_tickets` | List of deep-copied tickets |

Invalid inputs raise `ValueError` where applicable.

## 4. Ownership

- **Engineer A:** `campusflow/tickets.py`, `tests/test_tickets.py`; coordinates CLI integration in `main.py`.
- **Engineer B:** Workflow, reports, storage, and their corresponding tests.
- **Shared:** Integration, persistence verification, and cross-review.

## 5. Pending Decisions

To be agreed with Engineer B:

- JSON storage path.
- Whether saving occurs after every successful change or on exit.
- Any necessary changes to shared interfaces and integration tests.

