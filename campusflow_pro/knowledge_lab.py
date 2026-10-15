"""Participant sessions and mentor review for CampusFlow Pro."""

import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from campusflow_pro.knowledge_quiz import QUESTIONS, grade_quiz


WRITTEN_QUESTIONS = (
    "Explain why a ticket is not overdue at its exact SLA deadline.",
    "Explain how the application should handle corrupted JSON data.",
    "Explain why rejected ticket operations must not create audit events.",
)

DEFAULT_SESSION_PATH = Path("knowledge_lab_sessions.json")


def create_session(participant, answers, written_responses):
    """Validate participant work and create a session record."""
    if not isinstance(participant, str) or not participant.strip():
        raise ValueError("Participant name is required.")

    if len(answers) != len(QUESTIONS):
        raise ValueError("Exactly 10 MCQ answers are required.")

    normalized_answers = []

    for answer in answers:
        if not isinstance(answer, str):
            raise ValueError("MCQ answers must be letters A, B, C, or D.")

        answer = answer.strip().upper()

        if answer not in "ABCD" or len(answer) != 1:
            raise ValueError("MCQ answers must be letters A, B, C, or D.")

        normalized_answers.append(answer)

    if len(written_responses) != len(WRITTEN_QUESTIONS):
        raise ValueError("Exactly three written responses are required.")

    for response in written_responses:
        if not isinstance(response, str) or not response.strip():
            raise ValueError("Written responses cannot be empty.")

    return {
        "session_id": str(uuid4()),
        "participant": participant.strip(),
        "submitted_at": datetime.now(timezone.utc).isoformat(),
        "answers": normalized_answers,
        "score": grade_quiz(normalized_answers),
        "total_questions": len(QUESTIONS),
        "written_responses": [
            {
                "question": question,
                "answer": response.strip(),
            }
            for question, response in zip(
                WRITTEN_QUESTIONS, written_responses
            )
        ],
    }


def load_sessions(path=DEFAULT_SESSION_PATH):
    """Load and validate saved Knowledge Lab sessions."""
    path = Path(path)

    if not path.exists():
        return []

    with path.open("r", encoding="utf-8") as file:
        sessions = json.load(file)

    if not isinstance(sessions, list):
        raise ValueError("Knowledge Lab storage must contain a list.")

    required_fields = {
        "session_id",
        "participant",
        "submitted_at",
        "answers",
        "score",
        "total_questions",
        "written_responses",
    }

    for session in sessions:
        if not isinstance(session, dict):
            raise ValueError("Invalid Knowledge Lab session record.")

        if not required_fields.issubset(session):
            raise ValueError(
                "Knowledge Lab session is missing required fields."
            )

        if not isinstance(session["participant"], str):
            raise ValueError("Invalid participant name.")

        if not isinstance(session["written_responses"], list):
            raise ValueError("Invalid written responses.")

        if len(session["written_responses"]) != 3:
            raise ValueError("Exactly three written responses are required.")

        for response in session["written_responses"]:
            if not isinstance(response, dict):
                raise ValueError("Invalid written response record.")

            if not isinstance(response.get("question"), str):
                raise ValueError("Invalid written question.")

            if not isinstance(response.get("answer"), str):
                raise ValueError("Invalid written answer.")

    return sessions


def save_session(session, path=DEFAULT_SESSION_PATH):
    """Save a session using an atomic file replacement."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    sessions = load_sessions(path)
    sessions.append(session)

    temporary_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as temporary_file:
            temporary_path = Path(temporary_file.name)

            json.dump(sessions, temporary_file, indent=2)
            temporary_file.flush()
            os.fsync(temporary_file.fileno())

        os.replace(temporary_path, path)

    finally:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)


def run_knowledge_lab(
    input_fn=input,
    output_fn=print,
    path=DEFAULT_SESSION_PATH,
):
    """Collect and save a complete participant session."""
    output_fn("\n========== KNOWLEDGE LAB ==========")

    participant = input_fn("Participant name or ID: ").strip()

    if not participant:
        raise ValueError("Participant name is required.")

    answers = []

    for number, question in enumerate(QUESTIONS, start=1):
        output_fn(f"\n{question.prompt}")

        for letter, option in zip("ABCD", question.options):
            output_fn(f"{letter}. {option}")

        while True:
            answer = input_fn(
                f"Answer for Q{number} (A/B/C/D): "
            ).strip().upper()

            if answer in {"A", "B", "C", "D"}:
                answers.append(answer)
                break

            output_fn("Invalid answer. Choose A, B, C, or D.")

        output_fn(f"Explanation: {question.explanation}")

    output_fn("\n========== WRITTEN EXPLANATIONS ==========")

    written_responses = []

    for number, question in enumerate(WRITTEN_QUESTIONS, start=1):
        output_fn(f"\nWritten question {number}: {question}")

        while True:
            response = input_fn("Your explanation: ").strip()

            if response:
                written_responses.append(response)
                break

            output_fn("Please provide an explanation.")

    session = create_session(
        participant,
        answers,
        written_responses,
    )

    save_session(session, path)

    output_fn("\n========== RESULTS ==========")
    output_fn(f"Participant: {session['participant']}")
    output_fn(f"MCQ score: {session['score']}/10")
    output_fn(f"Session ID: {session['session_id']}")
    output_fn("Your session has been saved.")

    return session


def review_sessions(output_fn=print, path=DEFAULT_SESSION_PATH):
    """Display saved sessions for mentor inspection."""
    sessions = load_sessions(path)

    if not sessions:
        output_fn("\nNo Knowledge Lab sessions found.")
        return sessions

    output_fn("\n========== MENTOR SESSION REVIEW ==========")

    for session in sessions:
        output_fn(f"\nSession: {session['session_id']}")
        output_fn(f"Participant: {session['participant']}")
        output_fn(f"Submitted: {session['submitted_at']}")
        output_fn(
            f"MCQ score: {session['score']}/"
            f"{session['total_questions']}"
        )

        for number, response in enumerate(
            session["written_responses"], start=1
        ):
            output_fn(f"\nWritten question {number}:")
            output_fn(response["question"])
            output_fn(f"Response: {response['answer']}")

    return sessions
