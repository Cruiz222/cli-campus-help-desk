
"""Knowledge Quiz Simulation for CampusFlow Pro."""

from dataclasses import dataclass


@dataclass(frozen=True)
class Question:
    prompt: str
    options: tuple[str, str, str, str]
    correct_answer: str
    explanation: str


QUESTIONS = (
    Question(
        "Q1 | Critical SLA: A critical ticket is created at "
        "10:00 UTC. At 11:00 UTC, is it overdue?",
        (
            "Yes",
            "No, only strictly after 11:00",
            "Only if assigned",
            "Only if reopened",
        ),
        "B",
        "At 11:00 UTC the ticket is due, not overdue. "
        "Overdue means the current time is strictly later "
        "than due_at.",
    ),
    Question(
        "Q2 | Priority order: urgency=low and "
        "affected_users=10. What priority?",
        ("Critical", "High", "Medium", "Low"),
        "B",
        "The critical rule requires high urgency and at "
        "least 10 affected users. The next rule assigns "
        "high priority when affected_users >= 10, even "
        "if urgency is low.",
    ),
    Question(
        "Q3 | Illegal transition: an unassigned open ticket "
        "moves directly to in_progress. What should happen?",
        (
            "Transition succeeds",
            "Status changes but history stays",
            "Reject without changing ticket or events",
            "Delete the ticket",
        ),
        "C",
        "An open ticket must be assigned before moving "
        "to in_progress. A rejected transition must not "
        "change the ticket or append an audit event.",
    ),
    Question(
        "Q4 | Reopening: a resolved high-priority ticket "
        "is reopened. Which SLA behavior is correct?",
        (
            "Keep old due_at always",
            "Start a fresh SLA cycle while preserving created_at",
            "Reset created_at to today's date",
            "Delete previous events",
        ),
        "B",
        "Reopening increments the SLA cycle and sets "
        "a new deadline while preserving the original "
        "created_at and historical audit events.",
    ),
    Question(
        "Q5 | Escalation repeated: an overdue ticket is "
        "checked three times within one SLA cycle. "
        "How many new ESCALATE events?",
        ("Three", "Two", "One", "Zero"),
        "C",
        "Escalation is idempotent within a cycle. "
        "Once escalated_cycle matches escalation_cycle, "
        "repeated checks cannot add another event.",
    ),
    Question(
        "Q6 | JSON corrupted: the saved file has invalid "
        "JSON. What is the safest action?",
        (
            "Replace data with empty list",
            "Use eval()",
            "Ignore and keep running with partial data",
            "Reject load and preserve existing valid state",
        ),
        "D",
        "Invalid JSON must cause loading to fail safely. "
        "The application must not overwrite the file "
        "with empty data or accept partial state.",
    ),
    Question(
        "Q7 | Code review: a PR changes SLA calculations "
        "but adds no boundary tests. What should a "
        "reviewer do?",
        (
            "Approve because it runs locally",
            "Request focused tests and explanation",
            "Merge and test next week",
            "Ask AI to approve automatically",
        ),
        "B",
        "SLA boundaries affect correctness. Reviewers "
        "should request tests for exactly due, before "
        "due, and strictly after due, plus a clear "
        "explanation of the change.",
    ),
    Question(
        "Q8 | AI suggestion: an assistant says 'use eval() "
        "to parse stored JSON'. What should you do?",
        (
            "Copy it",
            "Disable tests",
            "Reject and use JSON parsing with validation",
            "Share the whole file publicly",
        ),
        "C",
        "eval() executes Python expressions and is unsafe "
        "for parsing untrusted data. Use json.load() or "
        "json.loads(), validate the resulting document, "
        "and verify behavior with tests.",
    ),
    Question(
        "Q9 | Duplicate warning: titles ' Wi-Fi   Down ' "
        "and 'wi-fi down' share category, both unresolved. "
        "What should the CLI do?",
        (
            "Silently delete original",
            "Warn and require confirmation",
            "Silently block forever",
            "Ignore normalization",
        ),
        "B",
        "Whitespace and case normalization reveal "
        "possible duplicates. Warn the user and request "
        "confirmation, since similar tickets can still "
        "represent separate incidents.",
    ),
    Question(
        "Q10 | Audit log: an invalid return/status "
        "operation is rejected. What should happen "
        "to event count?",
        (
            "Increase by one",
            "Increase twice",
            "Reset to zero",
            "Stay unchanged",
        ),
        "D",
        "Only successful operations create audit events. "
        "Rejected operations must leave both ticket state "
        "and event count unchanged.",
    ),
)


def grade_quiz(answers):
    """Return the score for a complete answer sequence."""
    if len(answers) != len(QUESTIONS):
        raise ValueError("Exactly 10 answers are required.")

    return sum(
        str(answer).strip().upper() == question.correct_answer
        for answer, question in zip(answers, QUESTIONS)
    )


def run_quiz(input_fn=input, output_fn=print):
    """Run the interactive quiz and return the final score."""
    output_fn("\n========== ENGINEER KNOWLEDGE QUIZ ==========")
    output_fn("Answer all 10 questions using A, B, C, or D.")

    answers = []

    for number, question in enumerate(QUESTIONS, start=1):
        output_fn(f"\n{question.prompt}")

        for letter, option in zip("ABCD", question.options):
            output_fn(f"{letter}. {option}")

        while True:
            answer = input_fn(
                f"Your answer for Q{number} (A/B/C/D): "
            ).strip().upper()

            if answer in {"A", "B", "C", "D"}:
                break

            output_fn("Invalid answer. Choose A, B, C, or D.")

        answers.append(answer)

        if answer == question.correct_answer:
            output_fn("Correct!")
        else:
            output_fn(
                f"Incorrect. Correct answer: "
                f"{question.correct_answer}"
            )

        output_fn(f"Explanation: {question.explanation}")

    score = grade_quiz(answers)
    percentage = score * 100 // len(QUESTIONS)

    output_fn("\n========== QUIZ RESULTS ==========")
    output_fn(f"Score: {score}/10")
    output_fn(f"Percentage: {percentage}%")

    return score
