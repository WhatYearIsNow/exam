"""Exercise development isolation and release rollback with temporary repositories."""
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]


def load_tool(name):
    # Scripts use sibling imports when invoked as `python3 tools/name.py`.
    sys.path.insert(0, str(ROOT / 'tools'))
    try:
        spec = importlib.util.spec_from_file_location('exam_' + name, ROOT / 'tools' / (name + '.py'))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    finally:
        sys.path.pop(0)


dev = load_tool('dev')
release = load_tool('release')


class RuntimeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='exam-runtime-test-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'web/exam').mkdir(parents=True)
        (self.root / 'tools').mkdir()
        (self.root / 'data').mkdir()
        (self.root / '.gitignore').write_text('config.json\ndata/\n.local/\nweb/config.local.js\n')
        for name in ('LICENSE', 'THIRD_PARTY_NOTICES.md', 'config.example.json',
                     'tools/build_frontend.py'):
            shutil.copy2(ROOT / name, self.root / name)
        (self.root / 'server.py').write_text("VERSION = 'committed'\n")
        shell = []
        for subject in ('marx', 'physics', 'probability'):
            (self.root / 'web/exam' / (subject + '.html')).write_text(
                '<script id="' + subject + '-data" type="application/json">'
                + json.dumps({'questions': [{'id': 'q1', 'desc': subject}]}) + '</script>')
            shell.append('<button data-page="' + subject + '"><span class="tab-meta">1 道题</span></button>'
                         + '<script id="payload-' + subject + '"></script>')
        (self.root / 'web/index.html').write_text(''.join(shell))
        self.prod = {'app_token': 'production-sentinel', 'llm_key': 'production-model-sentinel'}
        (self.root / 'config.json').write_text(json.dumps(self.prod))
        (self.root / 'web/config.local.js').write_text('PRODUCTION_CONFIG_SENTINEL')
        (self.root / 'data/private.json').write_text('PRIVATE_RECORD_SENTINEL')
        self.git('init', '-q')
        self.git('add', '.')
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'fixture')
        self.commit = self.git('rev-parse', 'HEAD')

    def git(self, *args):
        return subprocess.check_output(['git', '-C', str(self.root), *args], text=True).strip()

    def build(self):
        with mock.patch.object(release, 'validate_source'):
            return release.build_release(self.root, self.commit)

    def test_dev_uses_separate_token_data_and_clean_environment(self):
        with mock.patch.dict(os.environ, {'ILOVETJU_LLM_KEY': 'inherited-production-key',
                                         'ILOVETJU_DATA_DIR': '/production-data'}):
            base = dev.prepare(self.root)
            env = dev.environment(base)
        config = json.loads((base / 'config.json').read_text())
        self.assertNotEqual(config['app_token'], self.prod['app_token'])
        self.assertEqual(config['llm_key'], '')
        self.assertEqual(config['tju_llm_key'], '')
        self.assertNotIn('ILOVETJU_LLM_KEY', env)
        self.assertEqual(env['ILOVETJU_DATA_DIR'], str(base / 'data'))
        self.assertEqual(list((base / 'data').iterdir()), [])
        self.assertNotIn('PRODUCTION_CONFIG_SENTINEL', (base / 'web/config.local.js').read_text())
        self.assertEqual((self.root / 'data/private.json').read_text(), 'PRIVATE_RECORD_SENTINEL')
        (base / 'data/dev-note.json').write_text('test note')
        dev.prepare(self.root)
        self.assertEqual((base / 'data/dev-note.json').read_text(), 'test note')

    def test_dev_refuses_reused_production_credentials(self):
        base = self.root / '.local/dev'
        base.mkdir(parents=True)
        (base / 'config.json').write_text(json.dumps(self.prod))
        with self.assertRaisesRegex(ValueError, 'reuse production'):
            dev.prepare(self.root)

    def test_release_build_uses_commit_and_excludes_working_edits_and_private_data(self):
        (self.root / 'server.py').write_text("VERSION = 'uncommitted'\n")
        (self.root / '.local/public').mkdir(parents=True)
        (self.root / '.local/public/preview.apk').write_bytes(b'APK')
        name = self.build()
        path = release.release_path(self.root, name)
        self.assertIn('committed', (path / 'server.py').read_text())
        self.assertNotIn('uncommitted', (path / 'server.py').read_text())
        self.assertFalse((path / 'config.json').exists())
        self.assertFalse((path / 'data').exists())
        self.assertTrue((path / 'web/config.local.js').is_symlink())
        self.assertEqual((path / 'web/preview.apk').read_bytes(), b'APK')
        self.assertEqual(release.verify_release(self.root, name)['commit'], self.commit)
        self.assertFalse((path / 'server.py').stat().st_mode & 0o222)

    def test_tampered_release_is_rejected_before_switch(self):
        name = self.build()
        target = release.release_path(self.root, name) / 'server.py'
        target.chmod(0o644)
        target.write_text('tampered')
        restart = mock.Mock()
        with self.assertRaisesRegex(ValueError, 'changed'):
            release.activate(self.root, name, restart=restart)
        restart.assert_not_called()
        self.assertFalse((self.root / '.local/current').exists())

    def test_successful_activation_and_rollback_preserve_shared_data(self):
        first, second = self.build(), self.build()
        restart, check = mock.Mock(), mock.Mock()
        before = (self.root / 'data/private.json').read_bytes()
        release.activate(self.root, first, restart=restart, check=check)
        release.activate(self.root, second, restart=restart, check=check)
        self.assertEqual(release.selected_release(self.root, 'current'), second)
        self.assertEqual(release.selected_release(self.root, 'previous'), first)
        release.activate(self.root, first, restart=restart, check=check)
        self.assertEqual(release.selected_release(self.root, 'current'), first)
        self.assertEqual(release.selected_release(self.root, 'previous'), second)
        self.assertEqual((self.root / 'data/private.json').read_bytes(), before)

    def test_failed_activation_automatically_restores_previous_release(self):
        first, second = self.build(), self.build()
        release.activate(self.root, first, restart=lambda: None, check=lambda meta: None)
        restart = mock.Mock()
        def check(meta):
            if meta['id'] == second:
                raise RuntimeError('simulated bad health')
        with self.assertRaisesRegex(RuntimeError, 'restored previous'):
            release.activate(self.root, second, restart=restart, check=check)
        self.assertEqual(release.selected_release(self.root, 'current'), first)
        self.assertEqual(restart.call_count, 2)

    def test_paths_cannot_escape_release_directory(self):
        for value in ('../config.json', '/tmp/release', 'not-a-release'):
            with self.assertRaises(ValueError):
                release.release_path(self.root, value)

    def test_release_rejects_tracked_secret_files(self):
        self.git('add', '-f', 'config.json')
        self.git('-c', 'user.name=Test', '-c', 'user.email=test@example.invalid', 'commit', '-qm', 'bad fixture')
        with tempfile.TemporaryDirectory() as output:
            with self.assertRaisesRegex(ValueError, 'Private file'):
                release.export_commit(self.root, 'HEAD', Path(output))


if __name__ == '__main__':
    unittest.main()
