"""Server integration checks using isolated files and loopback HTTP only.

Run with: python3 -m unittest discover -s tests -v
No test sends an authenticated AI request or uses the deployment's config/data.
"""
import http.client
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import tempfile
import time
import unittest


SERVER = Path(__file__).resolve().parents[1] / "server.py"


class ServerProcess:
    """Prepare a fresh site, config, and data directory for an actual server."""

    def __init__(self, config_exists=True):
        self.temp = tempfile.TemporaryDirectory(prefix="ilovetju-server-test-")
        self.root = Path(self.temp.name)
        self.web = self.root / "web"
        self.data = self.root / "data"
        self.config = self.root / "config.json"
        self.web.mkdir()
        (self.web / "exam").mkdir()
        self.index = "<!doctype html><title>临时刷题站</title>".encode("utf-8")
        self.exam = "<!doctype html><title>概率论测试页面</title>".encode("utf-8")
        (self.web / "index.html").write_bytes(self.index)
        (self.web / "exam" / "probability.html").write_bytes(self.exam)
        if config_exists:
            self.config.write_text(json.dumps({"app_token": "json-test-token"}),
                                   encoding="utf-8")
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", 0))
            self.port = sock.getsockname()[1]
        # Do not inherit a developer's real keys or configured deployment paths.
        self.env = {k: v for k, v in os.environ.items()
                    if not k.startswith("ILOVETJU_")}
        self.env.update({
            "PYTHONDONTWRITEBYTECODE": "1",
            "ILOVETJU_HOST": "127.0.0.1",
            "ILOVETJU_PORT": str(self.port),
            "ILOVETJU_CONFIG": str(self.config),
            "ILOVETJU_DATA_DIR": str(self.data),
            "ILOVETJU_WEB_DIR": str(self.web),
            "ILOVETJU_APP_TOKEN": "env-test-token",
        })
        self.process = None
        self.log_path = self.root / "server.log"
        self.log = self.log_path.open("w", encoding="utf-8")

    def request(self, method, path, body=None, token=None):
        headers = {}
        if token is not None:
            headers["Authorization"] = "Bearer " + token
        if body is not None:
            body = json.dumps(body, ensure_ascii=False).encode("utf-8")
            headers["Content-Type"] = "application/json"
        connection = http.client.HTTPConnection("127.0.0.1", self.port, timeout=2)
        try:
            connection.request(method, path, body=body, headers=headers)
            response = connection.getresponse()
            raw = response.read()
            if response.getheader("Content-Type", "").startswith("application/json"):
                payload = json.loads(raw.decode("utf-8"))
            else:
                payload = raw
            return response.status, payload
        finally:
            connection.close()

    def start(self):
        self.process = subprocess.Popen(
            [sys.executable, str(SERVER)], cwd=self.root, env=self.env,
            stdout=self.log, stderr=subprocess.STDOUT,
        )
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if self.process.poll() is not None:
                break
            try:
                status, payload = self.request("GET", "/health")
                if status == 200 and payload.get("ok"):
                    return self
            except (OSError, http.client.HTTPException):
                pass
            time.sleep(0.05)
        raise RuntimeError("Server failed to start:\n" + self.log_path.read_text())

    def close(self):
        if self.process is not None and self.process.poll() is None:
            self.process.terminate()
            try:
                self.process.wait(timeout=3)
            except subprocess.TimeoutExpired:
                self.process.kill()
                self.process.wait(timeout=3)
        self.log.close()
        self.temp.cleanup()


class ServerIntegrationTests(unittest.TestCase):
    def start_server(self, config_exists=True):
        server = ServerProcess(config_exists=config_exists)
        self.addCleanup(server.close)
        return server.start()

    def test_static_pages_and_api_use_one_port(self):
        server = self.start_server()
        self.assertEqual(server.request("GET", "/"), (200, server.index))
        self.assertEqual(server.request("GET", "/exam/probability.html"),
                         (200, server.exam))
        status, payload = server.request("GET", "/health")
        self.assertEqual(status, 200)
        self.assertTrue(payload["ok"])

    def test_api_rejects_missing_and_incorrect_authentication(self):
        server = self.start_server()
        requests = (
            ("GET", "/sync?slot=test", None),
            ("PUT", "/sync?slot=test", {"records": {}}),
            ("GET", "/api/annotations?subject=probability", None),
            ("PUT", "/api/annotations?subject=probability", {"notes": {}}),
            ("POST", "/api/ai-check", {"question": {"desc": "Unused"}}),
        )
        for method, path, body in requests:
            for token in (None, "incorrect-test-token"):
                with self.subTest(method=method, path=path, token=token):
                    status, payload = server.request(method, path, body, token)
                    self.assertEqual(status, 401)
                    self.assertEqual(payload["error"], "unauthorized")

    def test_sync_merges_records_by_timestamp_and_keeps_tombstones(self):
        server = self.start_server()
        path = "/sync?slot=isolated-test"
        token = "env-test-token"
        first = {
            "older": {"at": 200, "answer": "A"},
            "newer": {"at": 100, "answer": "A"},
            "removed": {"at": 100, "removed": True},
        }
        status, payload = server.request("PUT", path, {"records": first}, token)
        self.assertEqual(status, 200)
        self.assertTrue(payload["ok"])
        incoming = {
            "older": {"at": 100, "answer": "B"},
            "newer": {"at": 200, "answer": "B"},
            "new": {"at": 150, "answer": "C"},
            "removed": {"at": 300, "answer": "D"},
        }
        self.assertEqual(server.request("PUT", path, {"records": incoming}, token)[0], 200)
        expected = {
            "older": first["older"], "newer": incoming["newer"],
            "new": incoming["new"], "removed": first["removed"],
        }
        self.assertEqual(server.request("GET", path, token=token),
                         (200, {"records": expected}))
        persisted = json.loads((server.data / "sync-isolated-test.json").read_text())
        self.assertEqual(persisted["records"], expected)
        self.assertEqual(server.request("GET", "/sync?slot=another", token=token),
                         (200, {"records": {}}))

    def test_annotations_put_get_and_merge_all_sections(self):
        server = self.start_server()
        path = "/api/annotations?subject=probability"
        token = "env-test-token"
        first = {
            "flags": {"q1": {"at": 200, "value": True}},
            "notes": {"q1": {"at": 100, "text": "初始备注"}},
            "ai": {"q1": {"at": 100, "correct": True}},
            "corr": {"q1": {"at": 100, "answer": "A"}},
        }
        self.assertEqual(server.request("PUT", path, first, token), (200, {"ok": True}))
        self.assertEqual(server.request("GET", path, token=token), (200, first))
        incoming = {
            "flags": {"q1": {"at": 100, "value": False}},
            "notes": {"q1": {"at": 200, "text": "更新备注"}},
            "ai": {"q2": {"at": 100, "correct": False}},
            "corr": {"q1": {"at": 200, "answer": "B"}},
        }
        self.assertEqual(server.request("PUT", path, incoming, token)[0], 200)
        expected = {
            "flags": first["flags"], "notes": incoming["notes"],
            "ai": {**first["ai"], **incoming["ai"]}, "corr": incoming["corr"],
        }
        self.assertEqual(server.request("GET", path, token=token), (200, expected))
        persisted = json.loads((server.data / "annot-probability.json").read_text())
        self.assertEqual(persisted, expected)

    def test_environment_token_takes_precedence_over_json(self):
        server = self.start_server()
        self.assertEqual(server.request("GET", "/sync", token="json-test-token")[0], 401)
        self.assertEqual(server.request("GET", "/sync", token="env-test-token"),
                         (200, {"records": {}}))

    def test_environment_token_works_without_config_file(self):
        server = self.start_server(config_exists=False)
        self.assertFalse(server.config.exists())
        self.assertEqual(server.request("GET", "/sync", token="env-test-token"),
                         (200, {"records": {}}))
        status, payload = server.request("PUT", "/api/annotations?subject=physics",
                                         {"notes": {"q1": {"at": 100, "text": "本地"}}},
                                         "env-test-token")
        self.assertEqual((status, payload), (200, {"ok": True}))

    def test_help_exits_without_starting_server(self):
        server = ServerProcess(config_exists=False)
        self.addCleanup(server.close)
        result = subprocess.run([sys.executable, str(SERVER), "--help"],
                                cwd=server.root, env=server.env,
                                capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("usage:", result.stdout.lower())
        self.assertNotIn("listening on", result.stdout.lower())
        with socket.socket() as sock:
            sock.bind(("127.0.0.1", server.port))


if __name__ == "__main__":
    unittest.main()
