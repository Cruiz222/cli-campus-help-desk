
import unittest

from campusflow_pro.knowledge_quiz import (
    QUESTIONS,
    grade_quiz,
    run_quiz,
)


class TestKnowledgeQuiz(unittest.TestCase):

    def test_exactly_ten_questions(self):
        self.assertEqual(len(QUESTIONS), 10)

    def test_every_question_has_four_options(self):
        for question in QUESTIONS:
            self.assertEqual(len(question.options), 4)
            self.assertIn(question.correct_answer, "ABCD")
            self.assertTrue(question.explanation)

    def test_correct_answer_key(self):
        self.assertEqual(
            [question.correct_answer for question in QUESTIONS],
            ["B", "B", "C", "B", "C", "D", "B", "C", "B", "D"],
        )

    def test_all_correct_scores_ten(self):
        answers = [
            question.correct_answer for question in QUESTIONS
        ]
        self.assertEqual(grade_quiz(answers), 10)

    def test_all_wrong_scores_zero(self):
        self.assertEqual(grade_quiz(["A"] * 10), 0)

    def test_incomplete_answers_rejected(self):
        with self.assertRaises(ValueError):
            grade_quiz(["A"] * 9)

    def test_quiz_displays_explanations(self):
        answers = iter(
            question.correct_answer for question in QUESTIONS
        )
        output = []

        score = run_quiz(
            input_fn=lambda prompt: next(answers),
            output_fn=output.append,
        )

        self.assertEqual(score, 10)
        self.assertEqual(
            sum("Explanation:" in line for line in output),
            10,
        )
        self.assertIn("Score: 10/10", output)

    def test_invalid_answer_is_retried(self):
        answers = iter(
            ["X", "B"] +
            [question.correct_answer for question in QUESTIONS[1:]]
        )
        output = []

        score = run_quiz(
            input_fn=lambda prompt: next(answers),
            output_fn=output.append,
        )

        self.assertEqual(score, 10)
        self.assertTrue(
            any("Invalid answer" in line for line in output)
        )


if __name__ == "__main__":
    unittest.main()
