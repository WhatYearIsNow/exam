"""ai_check unit checks: two-stage review routing without real AI services.

Run with: python3 -m unittest discover -s tests -v
_chat is monkeypatched per test; no network, no real keys.
"""
import importlib.util
import sys
import unittest
from pathlib import Path

SERVER = Path(__file__).resolve().parents[1] / "server.py"

CFG = {"app_token": "t", "tju_llm_key": "campus-key", "llm_key": "ds-key"}
PAYLOAD = {"subject": "probability", "question": {"desc": "题目", "answer": "A"}}


def load_server():
    spec = importlib.util.spec_from_file_location("exam_server_under_test", SERVER)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class AiCheckTests(unittest.TestCase):
    def setUp(self):
        self.server = load_server()
        self.calls = []
        self.responses = {}

        def fake_chat(base, key, model, prompt, timeout=None, images=None):
            self.calls.append((base, key, model))
            result = self.responses[(base, model)]
            if isinstance(result, Exception):
                raise result
            return dict(result)

        self.server._chat = fake_chat

    def answer(self, correct=True):
        return {"correct": correct, "confidence": 0.9,
                "correctAnswer": "", "reason": "依据"}

    def test_campus_available_uses_tju_first_stage(self):
        self.responses[("https://ai.tju.edu.cn/api/v3", "tju-llm")] = self.answer()
        result = self.server.ai_check(CFG, PAYLOAD)
        self.assertEqual(result["model"], "tju-llm")
        self.assertEqual(result["stage"], 1)
        self.assertEqual(len(self.calls), 1)

    def test_campus_unreachable_falls_back_to_deepseek_stage_one(self):
        self.responses[("https://ai.tju.edu.cn/api/v3", "tju-llm")] = \
            OSError("timed out")
        self.responses[("https://api.deepseek.com", "deepseek-chat")] = self.answer()
        result = self.server.ai_check(CFG, PAYLOAD)
        self.assertEqual(result["model"], "deepseek")
        self.assertEqual(result["stage"], 1)
        self.assertIn("已跳过一审", result["reason"])
        self.assertNotIn("firstResult", result)

    def test_missing_campus_key_skips_first_stage(self):
        self.responses[("https://api.deepseek.com", "deepseek-chat")] = self.answer()
        result = self.server.ai_check(
            {"app_token": "t", "tju_llm_key": "", "llm_key": "ds-key"}, PAYLOAD)
        self.assertEqual(result["model"], "deepseek")
        self.assertEqual(result["stage"], 1)
        self.assertIn("已跳过一审", result["reason"])

    def test_disagreement_still_routes_to_second_stage(self):
        first = self.answer(correct=False)
        first.update({"stage": 1, "model": "tju-llm"})
        self.responses[("https://api.deepseek.com", "deepseek-chat")] = self.answer()
        payload = dict(PAYLOAD, firstResult={
            "correct": False, "confidence": 0.5, "correctAnswer": "B",
            "reason": "一审理由", "stage": 1})
        result = self.server.ai_check(CFG, payload)
        self.assertEqual(result["stage"], 2)
        self.assertEqual(result["firstResult"]["correct"], False)
        self.assertEqual(len(self.calls), 1)   # 未再尝试 tju-llm


if __name__ == "__main__":
    unittest.main()
