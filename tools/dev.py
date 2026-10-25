#!/usr/bin/env python3
"""Prepare and serve a private development site without production data or keys."""
import argparse
import json
import os
import secrets
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import runtime_support as rt

ROOT = Path(__file__).resolve().parents[1]


def prepare(root):
    root = Path(root).resolve()
    base = root / '.local/dev'
    base.mkdir(parents=True, exist_ok=True)
    base.chmod(0o700)
    (base / 'data').mkdir(exist_ok=True)
    config_path = base / 'config.json'
    if not config_path.exists():
        cfg = json.loads((root / 'config.example.json').read_text())
        cfg.update(app_token=secrets.token_urlsafe(32), tju_llm_key='', llm_key='')
        rt.write_private_json(config_path, cfg)
    cfg = json.loads(config_path.read_text())
    if not cfg.get('app_token'):
        raise ValueError('Development config needs its own app_token')
    # Reject reused production credentials even if someone manually edited dev config.
    prod_path = root / 'config.json'
    if prod_path.exists():
        prod = json.loads(prod_path.read_text())
        if any(cfg.get(k) and cfg.get(k) == prod.get(k)
               for k in ('app_token', 'llm_key', 'tju_llm_key')):
            raise ValueError('Development must not reuse production tokens/model keys')
    site = Path(tempfile.mkdtemp(prefix='site-', dir=base))
    try:
        names = rt.git(root, 'ls-files', '--cached', '--others', '--exclude-standard',
                       '--', 'web').splitlines()
        for name in names:
            source = root / name
            relative = Path(name).relative_to('web')
            if relative == Path('config.local.js'):
                continue
            if source.is_symlink():
                raise ValueError('Development source must not be a symlink: ' + name)
            if source.is_file():
                dest = site / relative
                dest.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, dest)
        (site / 'config.local.js').write_text(
            'window.ILOVETJU_CONFIG = ' + json.dumps({'appToken': cfg['app_token']}) + ';\n')
        subprocess.run([sys.executable, str(root / 'tools/build_frontend.py'),
                        '--web-dir', str(site)], check=True, env=rt.clean_env(),
                       stdout=subprocess.DEVNULL)
        rt.atomic_link(base / 'web', site.name)
        # Keep one previous site for in-flight reads; discard only our generated sites.
        previous = sorted((p for p in base.glob('site-*') if p.is_dir() and p != site),
                          key=lambda p: p.stat().st_mtime, reverse=True)
        for stale in previous[1:]:
            shutil.rmtree(stale)
    except Exception:
        shutil.rmtree(site)
        raise
    return base


def environment(base):
    env = rt.clean_env()
    env.update(ILOVETJU_CONFIG=str(base / 'config.json'),
               ILOVETJU_DATA_DIR=str(base / 'data'),
               ILOVETJU_WEB_DIR=str(base / 'web'))
    return env


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action', choices=['prepare', 'serve'])
    parser.add_argument('--port', type=int, default=8902)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535 or args.port == 8901:
        parser.error('Use a development port other than production port 8901')
    try:
        base = prepare(ROOT)
        if args.action == 'prepare':
            print('Development site prepared at ' + str(base) + ' (no keys printed)')
        else:
            print('Development: http://127.0.0.1:%d/ (separate config/data)' % args.port,
                  flush=True)
            os.execve(sys.executable, [sys.executable, str(ROOT / 'server.py'),
                      '--host', '127.0.0.1', '--port', str(args.port)], environment(base))
    except (OSError, ValueError, subprocess.CalledProcessError) as exc:
        parser.exit(1, 'Development preparation failed: %s\n' % exc)


if __name__ == '__main__':
    main()
