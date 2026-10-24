#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从固定文件清单生成 PDF 离线运行包，不刷新快照或收集个人数据。"""
import argparse
import os
from pathlib import Path
import tempfile
import zipfile


PROJECT_ROOT = Path(__file__).resolve().parent.parent
PACKAGE_NAME = "exam-compilation"
SUBJECTS = ("marx", "physics", "probability")


def package_files(root):
    """Only include distribution sources and their license information."""
    files = [
        (root / "docs/offline-book.md", "README.md"),
        (root / "tools/make_book.py", "tools/make_book.py"),
        (root / "tools/extract_bank.py", "tools/extract_bank.py"),
        (root / "tools/setup_tex.sh", "tools/setup_tex.sh"),
        (root / "LICENSE", "LICENSE"),
        (root / "THIRD_PARTY_NOTICES.md", "THIRD_PARTY_NOTICES.md"),
    ]
    files.extend((root / "bank-data" / (s + ".json"), "bank-data/" + s + ".json")
                 for s in SUBJECTS)
    for directory in ("vendor", "licenses"):
        source_dir = root / directory
        if not source_dir.is_dir() or source_dir.is_symlink():
            raise ValueError(f"缺少发行目录或目录是符号链接：{source_dir}")
        for path in sorted(source_dir.rglob("*")):
            if path.is_symlink():
                raise ValueError(f"发行目录不能包含符号链接：{path}")
            if path.is_file():
                files.append((path, path.relative_to(root).as_posix()))
    for path, _ in files:
        if not path.is_file() or path.is_symlink():
            raise ValueError(f"缺少发行文件或文件是符号链接：{path}")
    return files


def package_offline(out_path):
    files = package_files(PROJECT_ROOT)
    out_path = Path(out_path).resolve()
    source_paths = {path.resolve() for path, _ in files}
    if out_path in source_paths:
        raise ValueError("输出 ZIP 不能覆盖发行源文件")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(dir=out_path.parent, suffix=".zip", delete=False) as f:
            temporary = Path(f.name)
        with zipfile.ZipFile(temporary, "w", compression=zipfile.ZIP_DEFLATED,
                             compresslevel=9) as archive:
            for path, relative in files:
                archive.write(path, PACKAGE_NAME + "/" + relative)
        os.replace(temporary, out_path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()
    print(f"written: {out_path} ({len(files)} files)")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path,
                        default=PROJECT_ROOT / "book" / "exam-compilation.zip",
                        help="输出 ZIP 文件（默认 <root>/book/exam-compilation.zip）")
    args = parser.parse_args()
    try:
        package_offline(args.out)
    except (OSError, ValueError) as exc:
        parser.exit(1, f"打包失败：{exc}\n")


if __name__ == "__main__":
    main()
