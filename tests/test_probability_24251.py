"""Structure and presentation checks for the imported 24251 probability exam."""
import json
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
PAPER = "24251 概率论与数理统计 A卷"
IDS = [f"24251_A卷-T{number}" for number in range(1, 20)]
FIELDS = [
    "id", "fileId", "source", "paper", "num", "chapter", "type",
    "subtype", "desc", "options", "images", "answer", "analysis",
]


def selected(questions):
    return [question for question in questions if question.get("paper") == PAPER]


class Probability24251Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        snapshot = json.loads(
            (ROOT / "bank-data/probability.json").read_text(encoding="utf-8")
        )
        cls.snapshot = selected(snapshot["questions"])

        html = (ROOT / "web/exam/probability.html").read_text(encoding="utf-8")
        match = re.search(
            r'<script id="probability-data" type="application/json">(.*?)</script>',
            html,
            re.DOTALL,
        )
        if not match:
            raise AssertionError("probability-data JSON not found")
        cls.embedded = selected(json.loads(match.group(1))["questions"])

    def test_snapshot_matches_embedded_exam(self):
        self.assertEqual(self.snapshot, self.embedded)

    def test_exam_uses_existing_question_schema_and_numbering(self):
        self.assertEqual([question["id"] for question in self.snapshot], IDS)
        for number, question in enumerate(self.snapshot, 1):
            self.assertEqual(list(question), FIELDS)
            self.assertEqual(question["fileId"], "24251_A卷")
            self.assertEqual(question["source"], f"{PAPER} T{number}")
            self.assertEqual(question["num"], number)
            self.assertEqual(set(question["chapter"]), {"label", "section", "raw"})
            self.assertIsInstance(question["images"], list)

    def test_answers_and_analysis_follow_neighboring_exam_style(self):
        for question in self.snapshot:
            self.assertTrue(question["desc"].strip())
            self.assertTrue(question["answer"].strip())
            self.assertIn("易错点：", question["analysis"])
            self.assertEqual(question["desc"].count("$") % 2, 0)
            self.assertEqual(question["analysis"].count("$") % 2, 0)
            if question["type"] == "choice":
                self.assertEqual(
                    [option["letter"] for option in question["options"]],
                    ["A", "B", "C", "D"],
                )
                self.assertIn(question["answer"], "ABCD")
            else:
                self.assertEqual(question["type"], "open")
                self.assertEqual(question["options"], [])


if __name__ == "__main__":
    unittest.main()
