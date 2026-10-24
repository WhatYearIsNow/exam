#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把裸页内嵌的题库 JSON 抽取为 bank-data/{subject}.json 本地快照。

用途：make_book.py 优先读取 web/exam 裸页内嵌题库，缺失时回退读取
bank-data 快照。题库更新后重跑本脚本刷新快照。
环境变量 ILOVETJU_EXAM_DIR 或 --exam-dir 可覆盖裸页目录。
"""
import argparse
import json
import os
import re
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAM_DIR = os.environ.get("ILOVETJU_EXAM_DIR", os.path.join(PROJECT_ROOT, "web", "exam"))
OUT = os.path.join(PROJECT_ROOT, "bank-data")
SUBJECTS = ("marx", "physics", "probability")


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--exam-dir", default=EXAM_DIR,
                    help="裸页目录（默认 ILOVETJU_EXAM_DIR 或 <root>/web/exam）")
    ap.add_argument("--out", default=OUT,
                    help="快照输出目录（默认 <root>/bank-data）")
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    for s in SUBJECTS:
        path = os.path.join(args.exam_dir, s + ".html")
        html = open(path, encoding="utf-8").read()
        m = re.search(r'<script id="' + s + r'-data" type="application/json">(.*?)</script>',
                      html, re.S)
        if not m:
            sys.exit(f"未在 {path} 中找到 {s}-data JSON 块")
        data = json.loads(m.group(1))
        out = os.path.join(args.out, s + ".json")
        with open(out, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        print("written:", out, len(data["questions"]), "题")


if __name__ == "__main__":
    main()
