"""Shared helpers for isolated development and release operations (stdlib only)."""
import hashlib
import json
import os
import subprocess
import tempfile
from pathlib import Path


def clean_env():
    """Never inherit production keys or paths into a build/test/dev process."""
    env = {k: v for k, v in os.environ.items() if not k.startswith('ILOVETJU_')}
    env['PYTHONDONTWRITEBYTECODE'] = '1'
    return env


def sha256(path):
    digest = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
    return digest.hexdigest()


def write_private_json(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + '.', dir=path.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write('\n')
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def atomic_link(link, target):
    link = Path(link)
    if os.path.lexists(link) and not link.is_symlink():
        raise ValueError('Refusing to replace a non-symlink: ' + str(link))
    fd, temporary = tempfile.mkstemp(prefix=link.name + '.', dir=link.parent)
    os.close(fd)
    os.unlink(temporary)
    try:
        os.symlink(str(target), temporary)
        os.replace(temporary, link)
    finally:
        if os.path.lexists(temporary):
            os.unlink(temporary)


def git(root, *args):
    return subprocess.check_output(['git', '-C', str(root), *args], text=True).strip()
