"""Verify that each embedded subject migrates to an isolated cloud slot."""
import json
from pathlib import Path
import shutil
import subprocess
import unittest


ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which("node")


@unittest.skipUnless(NODE, "Node.js is needed for subject sync behavior checks")
class SubjectSyncIsolationTests(unittest.TestCase):
    def run_subject(self, subject):
        html = (ROOT / "web/exam" / f"{subject}.html").read_text(encoding="utf-8")
        start = html.index("function syncSubjectSlot()")
        end = html.index("function syncConfig()", start)
        helpers = html[start:end]
        sync_url_start = html.index("function syncUrl()", end)
        sync_url_end = html.index("\n", sync_url_start)
        helpers += "\n" + html[sync_url_start:sync_url_end]
        merge_start = html.index("function mergeRemote(", sync_url_end)
        merge_end = html.index("\nasync function pullCloud", merge_start)
        helpers += "\n" + html[merge_start:merge_end]
        script = r"""
const assert = require('node:assert/strict');
const input = JSON.parse(require('node:fs').readFileSync(0, 'utf8'));
const LS_KEY = input.subject + '-quiz-records-v1';
const LS_SNAP = LS_KEY + ':pushsnap';
const LS_SYNC_SCOPE = LS_KEY + ':subject-sync-v2';
const storage = new Map([[LS_SNAP, '{"old":true}']]);
const localStorage = {
  getItem(key) { return storage.has(key) ? storage.get(key) : null; },
  setItem(key, value) { storage.set(key, value); },
  removeItem(key) { storage.delete(key); }
};
let syncCfg = {url: 'https://sync.test/sync/', slot: 'default'};
let DATA = {questions: [{id: 'keep'}]};
let records = {keep: {my: 'A', at: 10}, foreign: {my: 'B', at: 20}};
let dirtyKeys = {stale: 1};
let pendingPush = false;
function saveDirty() { storage.set(LS_KEY + ':dirty', JSON.stringify(dirtyKeys)); }
eval(input.helpers);

assert.equal(syncSubjectSlot(), 'default--' + input.subject);
assert.equal(syncUrl(), 'https://sync.test/sync/?slot=' +
  encodeURIComponent('default--' + input.subject));
assert.equal(prepareSubjectSync(), true);
assert.deepEqual(Object.keys(records), ['keep']);
assert.deepEqual(dirtyKeys, {keep: 1});
assert.equal(pendingPush, true);
assert.equal(storage.has(LS_SNAP), false);
assert.equal(JSON.parse(storage.get(LS_KEY)).foreign, undefined);
assert.equal(storage.get(LS_SYNC_SCOPE),
  'https://sync.test/sync|default--' + input.subject);

dirtyKeys = {};
pendingPush = false;
assert.equal(prepareSubjectSync(), false);
assert.deepEqual(dirtyKeys, {});
assert.equal(pendingPush, false);

syncCfg = {url: 'https://sync.test/sync', slot: 'another'};
assert.equal(prepareSubjectSync(), true);
assert.deepEqual(dirtyKeys, {keep: 1});
assert.equal(storage.get(LS_SYNC_SCOPE),
  'https://sync.test/sync|another--' + input.subject);

records = {keep: {my: 'A', at: 10}};
assert.equal(mergeRemote({
  keep: {my: 'new', at: 30},
  foreign: {my: 'wrong subject', at: 40}
}), 1);
assert.equal(records.keep.my, 'new');
assert.equal(records.foreign, undefined);
"""
        result = subprocess.run(
            [NODE, "-e", script],
            input=json.dumps({"subject": subject, "helpers": helpers}),
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_all_subjects_use_distinct_slots_and_filter_foreign_records(self):
        for subject in ("marx", "physics", "probability"):
            with self.subTest(subject=subject):
                self.run_subject(subject)

    def test_migration_runs_before_initial_cloud_pull(self):
        for subject in ("marx", "physics", "probability"):
            html = (ROOT / "web/exam" / f"{subject}.html").read_text(encoding="utf-8")
            data_ready = html.index("dataReady.then(async d=>")
            prepare = html.index("prepareSubjectSync();", data_ready)
            pull = html.index("if(syncCfg)await pullCloud(true);", data_ready)
            self.assertLess(prepare, pull, subject)


if __name__ == "__main__":
    unittest.main()
