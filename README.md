# CampusFlow — Campus Helpdesk Ticket Manager

CampusFlow is a Python command-line application for managing campus technical support tickets. It helps record complaints, prioritize issues, assign staff, track progress, and generate reports.

## Features

- **Ticket Creation:** Create tickets with a title, category, urgency, and number of affected users.
- **Input Validation:** Reject invalid or missing ticket information.
- **Automatic Priority:** Calculate ticket priority as low, medium, high, or critical.
- **Ticket Assignment:** Assign support tickets to staff members.
- **Status Management:** Move tickets through `open → in_progress → resolved`, with an option to reopen resolved tickets.
- **Work Queue:** Display open tickets sorted by priority.
- **Reporting:** View ticket counts by status and priority.
- **JSON Persistence:** Save tickets and load them when the application restarts.

## Requirements

- Python 3.10 or newer
- Git (for cloning the repository)

No external Python packages are required.

## Installation

Clone the repository:

```bash
git clone <https://github.com/Cruiz222/cli-campus-help-desk.git>
```

Navigate into the project directory:

```bash
cd cli-campus-help-desk
```

## How to Run

Run the application from the project root:

```bash
python3 main.py
```

The interactive menu provides options to create tickets, list tickets, assign staff, update ticket statuses, reopen tickets, view the work queue, and generate reports.

Follow the on-screen prompts to select an operation.

Ticket records are stored in a JSON file so they can be loaded again when the application restarts.

## How to Run Tests

Run all unit tests from the project root:

```bash
python3 -m unittest discover -s tests -v
```

The `-v` flag displays individual test results.

The test suite covers ticket creation, validation, priority calculation, assignment, status transitions, work queue ordering, reporting, and JSON persistence.

## Project Structure

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

## Team Contributions

| Team Member | Responsibilities |
|---|---|
| Engineer A | Ticket creation, validation, priority calculation, ticket retrieval, and listing |
| Engineer B | Ticket assignment, status management, work queue, reporting, and JSON persistence |

Both engineers contributed to testing, code review, and integration.

## Documentation

Additional project documentation is available in the `docs/` directory:

- `design-decisions.md` — Architecture and technical design decisions.
- `ai-learning-log.md` — AI-assisted development and learning reflections.

## License

See the `LICENSE` file for licensing information.