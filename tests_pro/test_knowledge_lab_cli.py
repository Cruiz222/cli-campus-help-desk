import unittest
from unittest.mock import patch

from main_pro import run_cli


class TestKnowledgeLabCLI(unittest.TestCase):

    def test_option_11_runs_knowledge_lab(self):
        output = []
        answers = iter(["11", "13"])

        with patch("main_pro.run_knowledge_lab") as lab:
            run_cli(
                app=None,
                input_fn=lambda prompt: next(answers),
                output_fn=output.append,
            )

        lab.assert_called_once()

    def test_option_12_runs_mentor_review(self):
        output = []
        answers = iter(["12", "13"])

        with patch("main_pro.review_sessions") as review:
            run_cli(
                app=None,
                input_fn=lambda prompt: next(answers),
                output_fn=output.append,
            )

        review.assert_called_once()


if __name__ == "__main__":
    unittest.main()