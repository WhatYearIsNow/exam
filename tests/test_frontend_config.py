"""Exercise the real iframe enhancer with mocked DOM and network using Node.js."""
import json
from pathlib import Path
import re
import shutil
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which("node")
HARNESS = r"""
const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');
const input = JSON.parse(fs.readFileSync(0, 'utf8'));
const requests = [], intervals = [], timeouts = [], cloud = [];
const storage = new Map();
function node() {
  return {
    style: {}, dataset: {}, textContent: '', innerHTML: '',
    classList: {contains() {return false;}, add() {}, remove() {}},
    appendChild() {}, addEventListener() {}, remove() {},
    querySelector() {return null;}, querySelectorAll() {return [];}
  };
}
const box = node();
const document = {
  head: node(), body: node(), referrer: 'https://example.test/',
  createElement: node,
  getElementById() {return null;},
  querySelector(selector) {return selector === '.tju-ai-box' ? box : null;},
  querySelectorAll() {return [];},
  addEventListener() {}
};
const context = {
  assert, requests, intervals, timeouts, storage, cloud, box,
  window: {parent: {ILOVETJU_CONFIG: input.config}, addEventListener() {}},
  location: {protocol: 'https:', origin: 'https://example.test'},
  document,
  localStorage: {
    getItem(key) {return storage.get(key) || null;},
    setItem(key, value) {storage.set(key, value);}
  },
  LS_KEY: 'physics-quiz-records-v1', LS_SYNC: 'physics-quiz-sync-v1',
  syncCfg: input.sync || null,
  pullCloud() {cloud.push(context.syncCfg);},
  qs(id) {return {id, desc: 'question', type: 'choice', answer: 'A'};},
  fetch(url, options) {
    requests.push({url, ...options});
    return Promise.resolve({
      ok: true,
      json() {return Promise.resolve({flags: {}, notes: {}, ai: {}, corr: {}, correct: true});}
    });
  },
  setTimeout(fn, delay) {timeouts.push({fn, delay}); return timeouts.length;},
  setInterval(fn, delay) {intervals.push({fn, delay}); return intervals.length;},
  clearTimeout() {}, clearInterval() {}
};
const end = input.enhancer.lastIndexOf('})();');
assert.ok(end > 0);
const enhancer = input.enhancer.slice(0, end) + `
globalThis.enhancer = {tjuToken, pushAnnot, pullAnnot, annotChanged, tjuAiSend, annot};
` + input.enhancer.slice(end);
vm.createContext(context);
vm.runInContext(enhancer, context);
Promise.resolve(vm.runInContext('(async () => {' + input.scenario + '\n})()', context))
  .then(() => process.stdout.write('ok\n'))
  .catch(error => {console.error(error); process.exitCode = 1;});
"""


class ConfigMarkupTests(unittest.TestCase):
    def test_runtime_config_loads_before_iframe_and_from_site_root(self):
        html = (ROOT / "web/index.html").read_text(encoding="utf-8")
        script = '<script src="/config.local.js"></script>'
        self.assertIn(script, html)
        self.assertLess(html.index(script), html.index('id="tju-enhancer"'))
        self.assertNotRegex(html, r"\bvar TOKEN\s*=")
        example = (ROOT / "web/config.example.js").read_text(encoding="utf-8")
        self.assertRegex(example, r"appToken:\s*''")


@unittest.skipUnless(NODE, "Node.js is needed for iframe JavaScript behavior checks")
class EnhancerConfigTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        html = (ROOT / "web/index.html").read_text(encoding="utf-8")
        cls.enhancer = re.search(
            r'<script id="tju-enhancer" type="text/plain">(.*?)</script>', html, re.S
        ).group(1)

    def run_scenario(self, scenario, config=None, sync=None):
        result = subprocess.run(
            [NODE, "-e", HARNESS],
            input=json.dumps({"enhancer": self.enhancer, "scenario": scenario,
                              "config": config, "sync": sync}),
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_no_token_keeps_annotations_local_and_sends_no_requests(self):
        self.run_scenario(r"""
assert.equal(syncCfg, null);
enhancer.annot.notes.q1 = {v: 'offline note', at: 1};
enhancer.annotChanged();
enhancer.pullAnnot();
enhancer.tjuAiSend('q1', '', null, {});
for (const timer of intervals.filter(timer => timer.delay === 30000)) timer.fn();
assert.equal(requests.length, 0);
assert.equal(cloud.length, 0);
assert.equal(JSON.parse(storage.get('physics-quiz-annot-v1')).notes.q1.v, 'offline note');
assert.ok(box.innerHTML.includes('配置云端同步密钥'));
""")

    def test_parent_deployment_config_authenticates_all_enhancement_requests(self):
        self.run_scenario(r"""
assert.equal(syncCfg.token, 'deployment-test-token');
assert.equal(syncCfg.url, 'https://example.test/sync');
assert.equal(cloud.length, 1);
enhancer.pullAnnot();
enhancer.annotChanged();
enhancer.tjuAiSend('q1', '', null, {});
assert.equal(requests.length, 3);
assert.equal(requests.map(request => request.method || 'GET').join(','), 'GET,PUT,POST');
assert.ok(requests.every(request => request.headers.authorization === 'Bearer deployment-test-token'));
""", config={"appToken": "deployment-test-token"})

    def test_sync_setting_changes_apply_to_annotations_and_ai_without_reload(self):
        self.run_scenario(r"""
enhancer.pullAnnot();
assert.equal(requests[0].headers.authorization, 'Bearer first-test-token');
syncCfg = {url: 'https://example.test/sync', token: 'second-test-token', slot: 'default'};
enhancer.annotChanged();
enhancer.tjuAiSend('q1', '', null, {});
assert.equal(requests[1].headers.authorization, 'Bearer second-test-token');
assert.equal(requests[2].headers.authorization, 'Bearer second-test-token');
syncCfg = null;
enhancer.pullAnnot();
assert.equal(requests.length, 3);
""", config={"appToken": ""},
            sync={"url": "https://example.test/sync", "token": "first-test-token", "slot": "default"})

    def test_pending_offline_notes_sync_after_configuration(self):
        self.run_scenario(r"""
enhancer.annot.notes.q1 = {v: 'queued note', at: 1};
enhancer.annotChanged();
assert.equal(requests.length, 0);
syncCfg = {url: 'https://example.test/sync', token: 'new-test-token', slot: 'default'};
intervals.find(timer => timer.delay === 30000).fn();
const put = requests.find(request => request.method === 'PUT');
assert.ok(put);
assert.equal(put.headers.authorization, 'Bearer new-test-token');
assert.equal(JSON.parse(put.body).notes.q1.v, 'queued note');
""")


if __name__ == "__main__":
    unittest.main()
