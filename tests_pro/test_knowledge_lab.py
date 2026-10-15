import json
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

from campusflow_pro.knowledge_lab import (
    WRITTEN_QUESTIONS,
    create_session,
    load_sessions,
    review_sessions,
    run_knowledge_lab,
    save_session,
)
from campusflow_pro.knowledge_quiz import QUESTIONS


class TestKnowledgeLab(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.path = Path(self.temp_dir.name) / "sessions.json"

        self.answers = [
            question.correct_answer for question in QUESTIONS
        ]

        self.responses = [
            "The deadline must be strictly exceeded.",
            "Reject corrupted data without overwriting it.",
            "Rejected operations must not create events.",
        ]

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_three_written_questions_exist(self):
        self.assertEqual(len(WRITTEN_QUESTIONS), 3)

    def test_create_session(self):
        session = create_session(
            "Engineer A",
            self.answers,
            self.responses,
        )

        self.assertEqual(session["participant"], "Engineer A")
        self.assertEqual(session["score"], 10)
        self.assertEqual(len(session["answers"]), 10)
        self.assertEqual(len(session["written_responses"]), 3)

        submitted_at = datetime.fromisoformat(
            session["submitted_at"]
        )
        self.assertEqual(
            submitted_at.utcoffset(),
            timezone.utc.utcoffset(submitted_at),
        )

    def test_empty_participant_rejected(self):
        with self.assertRaises(ValueError):
            create_session("", self.answers, self.responses)

    def test_invalid_answer_rejected(self):
        answers = self.answers.copy()
        answers[0] = "X"

        with self.assertRaises(ValueError):
            create_session("Engineer A", answers, self.responses)

    def test_missing_written_response_rejected(self):
        with self.assertRaises(ValueError):
            create_session(
                "Engineer A",
                self.answers,
                self.responses[:2],
            )

    def test_save_and_load_session(self):
        session = create_session(
            "Engineer A",
            self.answers,
            self.responses,
        )

        save_session(session, self.path)

        self.assertEqual(load_sessions(self.path), [session])

    def test_multiple_sessions_preserved(self):
        first = create_session(
            "Engineer A", self.answers, self.responses
        )
        second = create_session(
            "Engineer B", self.answers, self.responses
        )

        save_session(first, self.path)
        save_session(second, self.path)

        self.assertEqual(len(load_sessions(self.path)), 2)

    def test_missing_file_returns_empty_list(self):
        self.assertEqual(load_sessions(self.path), [])

    def test_corrupted_json_is_not_overwritten(self):
        original = "{invalid json"
        self.path.write_text(original, encoding="utf-8")

        session = create_session(
            "Engineer A", self.answers, self.responses
        )

        with self.assertRaises(json.JSONDecodeError):
            save_session(session, self.path)

        self.assertEqual(
            self.path.read_text(encoding="utf-8"),
            original,
        )

    def test_interactive_lab_saves_session(self):
        inputs = iter(
            ["Engineer A"] + self.answers + self.responses
        )
        output = []

        session = run_knowledge_lab(
            input_fn=lambda prompt: next(inputs),
            output_fn=output.append,
            path=self.path,
        )

        self.assertEqual(session["score"], 10)
        self.assertEqual(len(load_sessions(self.path)), 1)
        self.assertIn("Your session has been saved.", output)

    def test_mentor_can_review_written_responses(self):
        session = create_session(
            "Engineer A", self.answers, self.responses
        )
        save_session(session, self.path)

        output = []
        sessions = review_sessions(
            output_fn=output.append,
            path=self.path,
        )

        self.assertEqual(len(sessions), 1)
        self.assertIn("Participant: Engineer A", output)
        self.assertIn(
            "Response: Rejected operations must not create events.",
            output,
        )

    def test_missing_session_fields_rejected(self):
        self.path.write_text(
            '[{"participant": "Engineer A"}]',
            encoding="utf-8",
        )

        with self.assertRaises(ValueError):
            load_sessions(self.path)

    def test_invalid_written_responses_rejected(self):
        session = create_session(
            "Engineer A",
            self.answers,
            self.responses,
        )

        session["written_responses"] = ["invalid", "data", "here"]

        self.path.write_text(
            json.dumps([session]),
            encoding="utf-8",
        )

        with self.assertRaises(ValueError):
            load_sessions(self.path)


if __name__ == "__main__":
    unittest.main()
