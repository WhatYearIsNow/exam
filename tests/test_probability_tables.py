"""Behavior checks for OCR-flattened probability distribution tables."""
import json
from pathlib import Path
import re
import shutil
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which("node")


@unittest.skipUnless(NODE, "Node.js is needed for distribution-table checks")
class ProbabilityDistributionTableTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = (ROOT / "web" / "exam" / "probability.html").read_text(
            encoding="utf-8"
        )
        start = cls.html.index("function distributionTableTex(")
        end = cls.html.index("// OCR 早期题目", start)
        cls.helpers = cls.html[start:end]

    def run_node(self, script, payload):
        result = subprocess.run(
            [NODE, "-e", script],
            input=json.dumps(payload),
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_flattened_distribution_rows_become_katex_arrays(self):
        script = r"""
const assert = require('node:assert/strict');
const input = JSON.parse(require('node:fs').readFileSync(0, 'utf8'));
eval(input.helpers);

const normalized = input.cases.map(normalizeDistributionTables);
assert.match(normalized[0], /\\begin\{array\}\{c\|ccc\}X&-1&0&1\\\\\\hline P_X&0\.2&0\.5&0\.3/);
assert.match(normalized[1], /\\begin\{array\}\{c\|ccc\}X&1&2&3\\\\\\hline P_X&0\.2&0\.3&0\.5/);
assert.match(normalized[2], /\\begin\{array\}\{c\|cccc\}X&1&2&3&4\\\\\\hline P&0\.2&0\.1\+a&0\.4-b&c/);
for (const value of normalized) {
  assert.doesNotMatch(value, /\\frac\{X\}\{P(?:_\{?X\}?)?\}\$\s*\|/);
}
assert.equal(
  normalizeDistributionTables(String.raw`条件概率 $P\{Y\leq|X|\}=0.5$ 不应改变`),
  String.raw`条件概率 $P\{Y\leq|X|\}=0.5$ 不应改变`
);
assert.equal(distributionTableTex('P', '1 2', '0.5'), '');
"""
        cases = [
            r"设 $\frac{X}{P_{X}}$ | -1 0 1 | 0.2 0.5 0.3, 随机变量 X 与 Y 同分布",
            r"已知随机变量 X 的概率分布律为 $\frac{X}{P_{X}}$ | 1 2 3 0.2 0.3 0.5, 求 X 的分布函数",
            r"设随机变量 X 的分布律为 $\frac{X}{P}$ | 1 2 3 4 | 0.2 0.1+a 0.4-b c, 则常数满足",
        ]
        self.run_node(script, {"helpers": self.helpers, "cases": cases})

    def test_all_embedded_flattened_x_over_p_tables_are_covered(self):
        match = re.search(
            r'<script id="probability-data" type="application/json">(.*?)</script>',
            self.html,
            flags=re.DOTALL,
        )
        self.assertIsNotNone(match)
        questions = json.loads(match.group(1))["questions"]
        flattened = {
            question["id"]: question["desc"]
            for question in questions
            if re.search(
                r"\$\\frac\{X\}\{P(?:_\{?X\}?)?\}\$\s*\|",
                question.get("desc", ""),
            )
        }
        self.assertEqual(
            set(flattened), {"18192-T9", "模拟卷5-T13", "模拟卷8-T4"}
        )


if __name__ == "__main__":
    unittest.main()
