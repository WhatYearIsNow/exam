"""Behavior checks for wrong-answer redo grading and previous-answer feedback."""
import json
from pathlib import Path
import shutil
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which("node")
SUBJECTS = ("marx", "physics", "probability")


@unittest.skipUnless(NODE, "Node.js is needed for redo behavior checks")
class WrongRedoTests(unittest.TestCase):
    def subject_html(self, subject):
        return (ROOT / "web/exam" / f"{subject}.html").read_text(encoding="utf-8")

    def run_node(self, script, payload):
        result = subprocess.run(
            [NODE, "-e", script],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_previous_answer_feedback_separates_wrong_and_missing_choices(self):
        script = r"""
const assert = require('node:assert/strict');
const input = JSON.parse(require('node:fs').readFileSync(0, 'utf8'));
eval(input.helpers);
assert.equal(choiceLetters('D、A、C'), 'ACD');
assert.equal(
  previousAnswerFeedback({type: 'multi', answer: 'A、C、D'}, 'ABCD'),
  '上次作答：ABCD · 错选：B'
);
assert.equal(
  previousAnswerFeedback({type: 'multi', answer: 'ACD'}, 'AC'),
  '上次作答：AC · 漏选：D'
);
assert.equal(
  previousAnswerFeedback({type: 'choice', answer: 'A'}, 'B'),
  '上次作答：B · 错选：B · 漏选：A'
);
assert.equal(
  previousAnswerFeedback({type: 'choice', answer: 'A'}, 'A'),
  '上次作答：A'
);
"""
        for subject in SUBJECTS:
            with self.subTest(subject=subject):
                html = self.subject_html(subject)
                start = html.index("function choiceLetters(")
                end = html.index("function toggleAna(", start)
                self.run_node(script, {"helpers": html[start:end]})

    def test_multi_redo_grades_normalized_choice_sets(self):
        html = self.subject_html("marx")
        helper_start = html.index("function choiceLetters(")
        helper_end = html.index("function previousAnswerFeedback(", helper_start)
        submit_start = html.index("function submitMulti(")
        submit_end = html.index("function reveal(", submit_start)
        script = r"""
const assert = require('node:assert/strict');
const input = JSON.parse(require('node:fs').readFileSync(0, 'utf8'));
const qid = 'q';
const question = {answer: 'A、C、D'};
let records = {q: {my: 'ABCD', ok: false, wrong: true, n: 1}};
let multiSel = {q: 'DAC'};
const redoDone = new Set(), redoPeeked = new Set();
let mode = 'wrong', saved = 0, rendered = 0, message = '';
function qs() { return question; }
function rec() { return records[qid]; }
function recIn() { return records[qid]; }
function isWrong() { return !!records[qid].wrong; }
function redoActive() { return mode === 'wrong' && isWrong(); }
function saveRecords() { saved++; }
function renderPractice() { rendered++; }
function toast(value) { message = value; }
eval(input.helpers + '\n' + input.submit);

submitMulti(qid);
assert.equal(records.q.my, 'ACD');
assert.equal(records.q.ok, true);
assert.equal(records.q.wrong, false);
assert.equal(records.q.prevMy, 'ABCD');
assert.equal(redoDone.has(qid), true);
assert.match(message, /答对了/);

records.q = {my: 'ABCD', ok: false, wrong: true, n: 2};
multiSel.q = 'ABCD';
redoDone.clear();
submitMulti(qid);
assert.equal(records.q.ok, false);
assert.equal(records.q.wrong, true);
assert.match(message, /又答错了/);
assert.equal(saved, 2);
assert.equal(rendered, 2);
"""
        self.run_node(
            script,
            {
                "helpers": html[helper_start:helper_end],
                "submit": html[submit_start:submit_end],
            },
        )

    def test_feedback_box_is_raised_and_inset_consistently(self):
        expected = ".prev-ans{margin:-4px 20px 12px;"
        for subject in SUBJECTS:
            with self.subTest(subject=subject):
                html = self.subject_html(subject)
                self.assertIn(expected, html)
                self.assertNotIn("上次错选：'+escHtml(String(prevSel))", html)


if __name__ == "__main__":
    unittest.main()
