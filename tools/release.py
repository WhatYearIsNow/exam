#!/usr/bin/env python3
"""Build verified releases from Git commits, activate them, and roll back safely."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import io
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
import urllib.request

import runtime_support as rt

ROOT = Path(__file__).resolve().parents[1]
SERVICE = 'i-love-tju-api.service'
RELEASE_ID = re.compile(r'^[0-9]{8}T[0-9]{12}Z-[0-9a-f]{12}$')


@contextmanager
def deployment_lock(root):
    import fcntl
    base = Path(root) / '.local'
    base.mkdir(exist_ok=True)
    with (base / 'release.lock').open('a') as lock:
        try:
            fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise ValueError('Another release operation is in progress')
        yield


def release_path(root, release_id):
    if not RELEASE_ID.fullmatch(release_id):
        raise ValueError('Invalid release ID')
    base = Path(root).resolve() / '.local/releases'
    path = base / release_id
    if path.is_symlink() or path.resolve().parent != base.resolve():
        raise ValueError('Release must be a real directory under .local/releases')
    return path


def export_commit(root, ref, destination):
    commit = rt.git(root, 'rev-parse', '--verify', ref + '^{commit}')
    if not re.fullmatch(r'[0-9a-f]{40,64}', commit):
        raise ValueError('Invalid commit')
    archive = subprocess.check_output(['git', '-C', str(root), 'archive', commit])
    with tarfile.open(fileobj=io.BytesIO(archive)) as stream:
        for member in stream:
            relative = Path(member.name)
            if relative.is_absolute() or '..' in relative.parts:
                raise ValueError('Unsafe archive path')
            if member.isdir():
                continue
            if not member.isfile():
                raise ValueError('Release sources must be regular files: ' + member.name)
            if (member.name in ('config.json', 'web/config.local.js')
                    or relative.parts[0] in ('.local', '.git')
                    or (relative.parts[0] == 'data' and member.name != 'data/.gitkeep')
                    or relative.suffix in ('.keystore', '.jks')
                    or relative.name == '.env'
                    or (relative.name.startswith('.env.') and relative.name != '.env.example')):
                raise ValueError('Private file is tracked; refusing release: ' + member.name)
            target = Path(destination) / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            with stream.extractfile(member) as source, target.open('wb') as output:
                shutil.copyfileobj(source, output)
    return commit


def validate_source(source):
    """Validate the exported commit, never the developer's private configuration."""
    if not shutil.which('node'):
        raise ValueError('Node.js is required; frontend checks must not be skipped')
    env = rt.clean_env()
    # Isolate even imports that have module-level path defaults.
    env.update(ILOVETJU_CONFIG=str(source / 'unused-config.json'),
               ILOVETJU_DATA_DIR=str(source / 'unused-data'),
               ILOVETJU_WEB_DIR=str(source / 'web'))
    subprocess.run([sys.executable, '-m', 'unittest', 'discover', '-s', 'tests', '-v'],
                   cwd=source, env=env, check=True)
    before = {name: rt.sha256(source / name) for name in
              ('web/index.html', 'web/exam/index.html')}
    subprocess.run([sys.executable, 'tools/build_frontend.py'], cwd=source,
                   env=env, check=True, stdout=subprocess.DEVNULL)
    if any(rt.sha256(source / name) != sha for name, sha in before.items()):
        raise ValueError('Committed frontend payloads are stale; rebuild and commit first')
    subprocess.run([sys.executable, 'tools/extract_bank.py', '--out',
                    str(source / 'export-check')], cwd=source, env=env, check=True,
                   stdout=subprocess.DEVNULL)
    for script in ('android/build.py', 'android/sign.py'):
        subprocess.run([sys.executable, script, '--help'], cwd=source, env=env,
                       check=True, stdout=subprocess.DEVNULL)


def attach_shared_files(root, release):
    links = {}
    config = Path(root) / 'web/config.local.js'
    if config.exists():
        links['web/config.local.js'] = str(config.resolve())
    public = Path(root) / '.local/public'
    if public.exists():
        for item in sorted(public.iterdir()):
            if item.name == 'dl' or item.suffix in ('.apk', '.idsig'):
                links['web/' + item.name] = str(item.resolve())
    for name, target in links.items():
        dest = release / name
        if os.path.lexists(dest):
            raise ValueError('Shared file collides with release code: ' + name)
        dest.symlink_to(target)
    return links


def build_release(root, ref):
    root = Path(root).resolve()
    releases = root / '.local/releases'
    releases.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='release-build-', dir=root / '.local') as t:
        source = Path(t) / 'source'
        source.mkdir()
        commit = export_commit(root, ref, source)
        validate_source(source)
        release_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '-' + commit[:12]
        staging = Path(t) / 'runtime'
        staging.mkdir()
        for name in ('server.py', 'LICENSE', 'THIRD_PARTY_NOTICES.md'):
            shutil.copy2(source / name, staging / name)
        shutil.copytree(source / 'web', staging / 'web')
        files = {str(p.relative_to(staging)): rt.sha256(p)
                 for p in staging.rglob('*') if p.is_file()}
        links = attach_shared_files(root, staging)
        metadata = {'id': release_id, 'commit': commit,
                    'built_at': datetime.now(timezone.utc).isoformat(),
                    'files': files, 'shared_links': links}
        (staging / 'release.json').write_text(json.dumps(metadata, indent=2) + '\n')
        staging.rename(releases / release_id)
    verify_release(root, release_id)
    # Published code is immutable by convention and read-only on disk. Config and
    # downloads remain explicit links to shared runtime files, outside this inventory.
    target = releases / release_id
    for p in target.rglob('*'):
        if not p.is_symlink():
            p.chmod(0o555 if p.is_dir() else 0o444)
    target.chmod(0o555)
    return release_id


def verify_release(root, release_id):
    path = release_path(root, release_id)
    meta = json.loads((path / 'release.json').read_text())
    if meta.get('id') != release_id:
        raise ValueError('Release metadata ID mismatch')
    expected = meta.get('files', {})
    if not all(name in expected for name in ('server.py', 'web/index.html')):
        raise ValueError('Incomplete release inventory')
    actual = set()
    allowed_links = meta.get('shared_links', {})
    for p in path.rglob('*'):
        name = str(p.relative_to(path))
        if p.is_symlink():
            allowed = (name == 'web/config.local.js' and
                       p.resolve() == (Path(root) / 'web/config.local.js').resolve())
            allowed = allowed or (name.startswith('web/') and
                (Path(name).name == 'dl' or Path(name).suffix in ('.apk', '.idsig')) and
                p.resolve() == (Path(root) / '.local/public' / Path(name).name).resolve())
            if not allowed or allowed_links.get(name) != str(p.resolve()) or not p.exists():
                raise ValueError('Invalid shared link: ' + name)
        elif p.is_file() and name != 'release.json':
            actual.add(name)
            if expected.get(name) != rt.sha256(p):
                raise ValueError('Release file changed: ' + name)
    if actual != set(expected):
        raise ValueError('Release inventory differs from disk')
    if set(allowed_links) != {str(p.relative_to(path)) for p in path.rglob('*') if p.is_symlink()}:
        raise ValueError('Shared link inventory differs from disk')
    return meta


def selected_release(root, name):
    link = Path(root) / '.local' / name
    if not os.path.lexists(link):
        return None
    if not link.is_symlink():
        raise ValueError('Expected deployment symlink: ' + str(link))
    path = link.resolve()
    expected = release_path(root, path.name)
    if path != expected or not path.is_dir():
        raise ValueError('Deployment link points outside release storage')
    return path.name


def restart_service():
    subprocess.run(['systemctl', 'restart', SERVICE], check=True)


def wait_healthy(metadata, timeout=15):
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    expected = metadata['files']['web/index.html']
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            with opener.open('http://127.0.0.1:8901/health', timeout=2) as response:
                healthy = json.load(response).get('ok')
            with opener.open('http://127.0.0.1:8901/api/manifest', timeout=2) as response:
                actual = json.load(response)['files']['/']['sha256']
            if healthy and actual == expected:
                return
        except (OSError, ValueError, KeyError):
            pass
        time.sleep(.2)
    raise RuntimeError('Backend did not become healthy with the selected release')


def activate(root, release_id, restart=restart_service, check=wait_healthy):
    root = Path(root).resolve()
    meta = verify_release(root, release_id)
    current = root / '.local/current'
    old_id = selected_release(root, 'current')
    old_meta = verify_release(root, old_id) if old_id else None
    rt.atomic_link(current, 'releases/' + release_id)
    try:
        restart()
        check(meta)
    except (Exception, KeyboardInterrupt) as original:
        if old_id:
            rt.atomic_link(current, 'releases/' + old_id)
            try:
                restart()
                check(old_meta)
            except Exception as rollback_error:
                raise RuntimeError('Activation and recovery both failed; inspect service logs') from rollback_error
        else:
            current.unlink()
        raise RuntimeError('Activation failed; restored previous deployment') from original
    if old_id and old_id != release_id:
        rt.atomic_link(root / '.local/previous', 'releases/' + old_id)
    rt.write_private_json(root / '.local/deployment.json', {
        'current': release_id, 'commit': meta['commit'],
        'previous': selected_release(root, 'previous'),
        'activated_at': datetime.now(timezone.utc).isoformat()})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='action', required=True)
    build = commands.add_parser('build', help='Validate an exact Git commit and build a release')
    build.add_argument('--ref', required=True, help='Approved commit or tag (working edits excluded)')
    for command in ('verify', 'activate'):
        commands.add_parser(command).add_argument('release_id')
    commands.add_parser('rollback').add_argument('release_id', nargs='?')
    commands.add_parser('status')
    args = parser.parse_args()
    try:
        with deployment_lock(ROOT):
            if args.action == 'build':
                print('Built release: ' + build_release(ROOT, args.ref))
            elif args.action == 'verify':
                print(json.dumps(verify_release(ROOT, args.release_id), indent=2))
            elif args.action == 'status':
                print(json.dumps({key: selected_release(ROOT, key)
                                  for key in ('current', 'previous')}, indent=2))
            else:
                release_id = args.release_id
                if args.action == 'rollback' and not release_id:
                    release_id = selected_release(ROOT, 'previous')
                if not release_id:
                    raise ValueError('No previous release; supply an existing release ID')
                activate(ROOT, release_id)
                print('Active release: ' + release_id)
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as exc:
        parser.exit(1, 'Release operation failed: %s\n' % exc)


if __name__ == '__main__':
    main()
