#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""真题分类汇编生成器（exam-zh / XeLaTeX）

从刷题中心裸页内嵌的题库 JSON（web/exam/<subject>.html 的
<script id="<subject>-data" type="application/json">）抽取题目，按教材章节分类，
生成 exam-zh 排版源文件。题目区不带来源；来源在解析末尾另起一行（楷体）。
个人标注（存疑/备注/AI核验）按用户要求暂不呈现，但加载与修复层保留，便于日后恢复。

用法：
    python3 make_book.py --subject probability --chapter 1 --build
    python3 make_book.py --subject marx --chapter 3 --all --out /tmp/ch3

--chapter n   只取第 n 章（"第n章" 前缀匹配）
--all         收录整章全部题目（默认按各节配额精选，用于打样）
"""
import argparse
import json
import os
import re
import subprocess
import sys
from collections import Counter

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXAM_DIR = os.environ.get("ILOVETJU_EXAM_DIR", os.path.join(PROJECT_ROOT, "web", "exam"))
DATA_DIR = os.path.join(PROJECT_ROOT, "data")

SUBJECTS = {
    "marx": "马克思主义基本原理",
    "physics": "大学物理",
    "probability": "概率论与数理统计",
}

# 模拟卷所属的解析文档全名（按科目配置）；真题卷来源由卷号自动换算
MOCK_SOURCE = {
    "probability": "天津大学概率论与数理统计1考试真题解析（2018-2022）",
}
CN_SEM = {1: "一", 2: "二"}

# 打样时每节最多收题数（--all 时忽略）
SECTION_QUOTA = 4


# ---------------------------------------------------------------- 数据加载

def load_bank(subject, exam_dir=None):
    """题库加载：优先站点裸页内嵌 JSON（题库事实来源）；
    裸页不存在时回退到 bank-data/{subject}.json 本地快照（离线打包环境）。"""
    html_path = os.path.join(exam_dir if exam_dir is not None else EXAM_DIR, subject + ".html")
    if os.path.exists(html_path):
        html = open(html_path, encoding="utf-8").read()
        m = re.search(
            r'<script id="' + subject + r'-data" type="application/json">(.*?)</script>',
            html, re.S)
        if not m:
            sys.exit(f"未在 {html_path} 中找到 {subject}-data JSON 块")
        return json.loads(m.group(1))
    snap = os.path.join(PROJECT_ROOT, "bank-data", subject + ".json")
    if os.path.exists(snap):
        return _sanitize(json.load(open(snap, encoding="utf-8")))
    sys.exit("找不到题库数据：裸页路径 %s 与本地快照 %s 均不存在" % (html_path, snap))


def _sanitize_str(s):
    # JSON 转义事故修复：\frac/\times/\bar/\varepsilon 等命令的 \f、\t、\b、\v
    # 被 JSON 解析成控制字符（命令首字母被吞），按映射还原为“反斜杠+字母”。
    s = re.sub(r"[\x0b\x0c\x08\t](?=[a-zA-Z])",
               lambda m: "\\" + {0x0C: "f", 0x09: "t", 0x08: "b", 0x0B: "v"}[ord(m.group(0))],
               s)
    return s.replace("\r\n", "\n").replace("\r", "\n")


def _sanitize(obj):
    if isinstance(obj, str):
        return _sanitize_str(obj)
    if isinstance(obj, dict):
        return {k: _sanitize(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize(v) for v in obj]
    return obj


def load_annot(subject):
    path = os.path.join(DATA_DIR, f"annot-{subject}.json")
    if not os.path.exists(path):
        return {}
    return _sanitize(json.load(open(path, encoding="utf-8")))


def paper_source(paper, subject):
    """来源全名：'18191 概率论…' -> '2018—2019学年第一学期期末考试试卷'；
    '23241 … B卷' -> '…期末考试试卷（B卷）'；'模拟卷N' -> 解析文档全名+模拟卷N。

    卷号规则（与马原页面中 "14151 = 2014-2015学年第1学期" 的官方命名一致）：
    前两位+次两位=起止学年，第五位=学期序号。
    """
    m = re.match(r"^(\d{2})(\d{2})(\d)", paper)
    if not m:
        mock = re.match(r"模拟卷(\d+)", paper)
        if mock:
            return "%s模拟卷%s" % (MOCK_SOURCE[subject], mock.group(1))
        return paper
    s = "20%s—20%s学年第%s学期期末考试试卷" % (
        m.group(1), m.group(2), CN_SEM[int(m.group(3))])
    if "B卷" in paper:
        s += "（B卷）"
    return s


# ---------------------------------------------------------------- LaTeX 转义

RE_FILLIN = re.compile(r"(?:\\_){3,}|_{3,}")
RE_PAREN = re.compile(r"（\s*）|\(\s*\)")
RE_QUOTE = re.compile(r'"([^"\n]{1,60}?)"')
RE_CJK = re.compile(r"[\u4e00-\u9fff]")


def esc_text(seg, fillin=True):
    """转义纯文本段（数学段不经过此函数）。"""
    if fillin:
        seg = RE_FILLIN.sub(r"\\fillin{}", seg)
        seg = re.sub(r"\\fillin\{\}\s+([，．,.;；、)])", r"\\fillin{}\1", seg)
    seg = RE_PAREN.sub(r"\\mbox{\\paren} ", seg)
    seg = re.sub(r"\\mbox\{\\paren\}\s+([。．，,;；])", r"\\mbox{\\paren}\1", seg)
    seg = RE_QUOTE.sub(
        lambda m: "“" + m.group(1) + "”" if RE_CJK.search(m.group(1)) else m.group(0),
        seg)
    for ch, rep in (("&", r"\&"), ("%", r"\%"), ("#", r"\#")):
        seg = re.sub(r"(?<!\\)" + re.escape(ch), rep, seg)
    seg = re.sub(r"(?<!\\)_", r"\_", seg)
    return seg


# 把文本按 $...$ / \(...\) / \[...\] 切成 [纯文本, 数学, 纯文本, ...]
RE_MATH = re.compile(r"(\$.*?[^\\]\$|\\\(.*?\\\)|\\\[.*?\\\])", re.S)


def latexify(s, fillin=True):
    parts = RE_MATH.split(s)
    out = []
    for i, p in enumerate(parts):
        if i % 2:                      # 数学段原样保留
            out.append(p)
        elif p:
            out.append(esc_text(p, fillin=fillin))
    return "".join(out)


def md_notes_to_tex(md):
    """把 textbook.notes 的章节 Markdown 提要转成 LaTeX（仅处理用到的子集）。"""
    out, in_list = [], False
    for line in md.splitlines():
        line = line.rstrip()
        if not line.strip():
            if in_list:
                out.append(r"\end{itemize}")
                in_list = False
            continue
        if line.startswith("## "):
            if in_list:
                out.append(r"\end{itemize}")
                in_list = False
            out.append(r"\subsection*{%s}" % latexify(line[3:].strip(), fillin=False))
        elif line.startswith("- "):
            if not in_list:
                out.append(r"\begin{itemize}[leftmargin=2em]")
                in_list = True
            out.append(r"\item %s" % latexify(line[2:].strip(), fillin=False))
        elif in_list:
            out.append(r"\item %s" % latexify(line.strip(), fillin=False))
        else:
            out.append(latexify(line.strip(), fillin=False) + r"\par")
    if in_list:
        out.append(r"\end{itemize}")
    return "\n".join(out)


# ---------------------------------------------------------------- 选题

# 每节优先覆盖的题型组（顺序即优先级）：选择 → 填空 → 解答
TYPE_GROUPS = ({"choice"}, {"open", "fill"}, {"open", "calc"})


def pick_questions(chapter_qs, take_all):
    """精选打样：每节配额内先保证题型覆盖，再按卷次轮转补足；全量模式保持原序。

    稳定可复现：无随机成分，输入相同则输出相同。
    """
    if take_all:
        return list(chapter_qs)
    by_sec = {}
    for q in chapter_qs:
        by_sec.setdefault(q["chapter"]["section"], []).append(q)
    picked = []
    for sec, qs in by_sec.items():
        rest = sorted(qs, key=lambda q: (q["paper"].startswith("模拟卷"), q["paper"], q["num"]))
        chosen, seen = [], set()

        def first_of(types):
            for q in rest:
                if q["type"] in types and q["id"] not in seen:
                    return q
            return None

        for types in TYPE_GROUPS:               # 1) 题型覆盖，各保底一道
            q = first_of(types)
            if q:
                chosen.append(q)
                seen.add(q["id"])
        papers = []
        for q in rest:                          # 2) 卷次轮转补足配额
            if q["paper"] not in papers:
                papers.append(q["paper"])
        for p in papers:
            for q in rest:
                if len(chosen) >= SECTION_QUOTA:
                    break
                if q["paper"] == p and q["id"] not in seen:
                    chosen.append(q)
                    seen.add(q["id"])
        if not any(q["type"] == "open" and q["subtype"] == "calc" for q in chosen):
            for q in rest:                      # 3) 保底一道解答大题（可超配额 1）
                if q["type"] == "open" and q["subtype"] == "calc":
                    chosen.append(q)
                    break
        picked.extend(chosen)
    picked.sort(key=lambda q: (q["chapter"]["section"], q["paper"], q["num"]))
    return picked


# ---------------------------------------------------------------- 数据预检

VALID_TYPES = {"choice", "open", "fill"}


def hard_fail(msg):
    print("数据预检失败（已停止，未生成任何文件）：", msg, file=sys.stderr)
    sys.exit(1)


def screen_questions(qs, subject, warnings):
    """逐题可用性检查。坏题剔除并警告，绝不静默跳过、也绝不因个别坏题中止全书。"""
    usable = []
    for q in qs:
        problems = []
        if not str(q.get("answer", "")).strip():
            problems.append("缺答案")
        if not str(q.get("analysis", "")).strip():
            problems.append("缺解析")
        if q.get("type") not in VALID_TYPES:
            problems.append("未知题型 %s" % q.get("type"))
        elif paper_source(q["paper"], subject) == q["paper"]:
            problems.append("来源无法映射(%s)" % q["paper"])
        if problems:
            warnings.append("剔除题 %s：%s" % (q["id"], "、".join(problems)))
        else:
            usable.append(q)
    return usable


def run_inspect(data, subject):
    """只读检查模式：报告章节/题量/题型/notes/MOCK_SOURCE/数据损坏，不写任何文件。"""
    print("科目: %s (%s)" % (subject, data["meta"]["subject"]))
    chapters = data["textbook"]["sections"]
    total = 0
    for name, secs in chapters.items():
        qs = [q for q in data["questions"] if q["chapter"]["label"] == name]
        total += len(qs)
        tc = Counter((q["type"], q["subtype"]) for q in qs)
        has_notes = "有" if data["textbook"].get("notes", {}).get(name) else "无"
        print("  %s: %d题 / %d节 / 提要:%s / %s" % (
            name, len(qs), len(secs), has_notes,
            " ".join("%s/%s:%d" % (t, s, n) for (t, s), n in sorted(tc.items()))))
    print("目录树覆盖题数: %d（题库实际 %d）" % (total, len(data["questions"])))
    if total != len(data["questions"]):
        print("警告: %d 题的 chapter.label 不在目录树中（生成时会被忽略）"
              % (len(data["questions"]) - total))
    if subject in MOCK_SOURCE:
        print("MOCK_SOURCE[%s]: %s" % (subject, MOCK_SOURCE[subject]))
    else:
        print("MOCK_SOURCE[%s]: 未配置 —— 生成该科目前必须补充（凡例需引用模拟卷文档全名）" % subject)
    ctrl = 0

    def scan(x):
        nonlocal ctrl
        if isinstance(x, str):
            ctrl += sum(ch in "\x0b\x0c\x08\t" for ch in x)
        elif isinstance(x, dict):
            for v in x.values():
                scan(v)
        elif isinstance(x, list):
            for v in x:
                scan(v)

    scan(data["questions"])
    print("题库 JSON 控制字符: %d 处（>0 说明存在转义损坏，_sanitize 会修复）" % ctrl)
    annot_path = os.path.join(DATA_DIR, "annot-%s.json" % subject)
    if os.path.exists(annot_path):
        d = load_annot(subject)
        print("标注文件: flags=%d notes=%d ai=%d（已加载并修复，呈现层当前禁用）"
              % (len(d.get("flags", {})), len(d.get("notes", {})), len(d.get("ai", {}))))
    else:
        print("标注文件: 无")


# ---------------------------------------------------------------- 题目排版

def render_question(q, num):
    stem = latexify(q["desc"], fillin=(q["type"] != "choice"))
    body = stem + "\n"
    if q["type"] == "choice":
        opts = "\n".join(r"\item %s" % latexify(o["text"]) for o in q["options"])
        body += "\n\\begin{choices}\n%s\n\\end{choices}\n" % opts
    return "\\begin{question}\n%s\\end{question}\n" % body


def render_solution(q, num, subject):
    lines = [r"\needspace{6\baselineskip}"]
    lines.append(r"\noindent\solnum{%d.}\quad\textbf{【答案】}%s\par\vspace{.2em}"
                 % (num, latexify(str(q["answer"]))))
    lines.append(r"\textbf{【解析】}%s\par" % latexify(q["analysis"]))
    lines.append(r"\begin{quote}\small\kaishu 来源：%s 第%d题\end{quote}"
                 % (latexify(paper_source(q["paper"], subject), fillin=False), q["num"]))
    return "\n".join(lines) + "\n\\vspace{.6em}\n"


# ---------------------------------------------------------------- 文档骨架

PREAMBLE = r"""\documentclass[zihao=-4,a4paper]{exam-zh}
\usepackage{booktabs}
\usepackage{needspace}
\usepackage{hyperref}

\examsetup{
  font = lm,
  math-font = lm,
  page = { size = a4paper, margin = 2.2cm, foot-content = {%s第;页（共;页）} },
  solution/show-solution = hide,
  fillin/no-answer-type = none,
}
\subject{%s}

\everymath{\displaystyle}
\emergencystretch=3em

\newcommand{\solnum}[1]{\textbf{#1}}

\hypersetup{
  pdftitle    = {%s 真题分类汇编（样章）},
  pdfauthor   = {i-love-tju 刷题中心},
  pdfsubject  = {%s},
}

\begin{document}
"""


def build_tex(data, chapter_qs, subject, chapter_name):
    meta = data["meta"]
    notes = data["textbook"]["notes"].get(chapter_name, "")
    total = sum(1 for q in data["questions"] if q["chapter"]["label"] == chapter_name)
    secs = [q["chapter"]["section"] for q in chapter_qs]

    parts = [PREAMBLE % (meta["subject"], meta["subject"], meta["subject"], meta["subject"])]
    parts.append(r"""\begin{center}
  {\zihao{2}\heiti %s 真题分类汇编}\\[.6em]
  {\zihao{3}\heiti %s}\\[.8em]
  {\zihao{-4}\kaishu 样章 · 收录期末真题与模拟卷 %d 题（全章共 %d 题）}
\end{center}
\vspace{.5em}
\noindent\textbf{凡例}\quad
{\small 每题解析末尾以楷体注明题目来源：真题卷格式如“来源：2018—2019学年第一学期
期末考试试卷 第8题”；模拟卷均出自《%s》。答案速查仅列选择题，
填空与大题答案见卷末解析。}
\par
""" % (meta["subject"], chapter_name, len(chapter_qs), total, MOCK_SOURCE[subject]))

    parts.append(r"\section*{%s}" % latexify(chapter_name, fillin=False))
    if notes:
        parts.append(r"\section*{知识提要}")
        parts.append(md_notes_to_tex(notes))

    parts.append(r"\section*{真题}")
    cur_sec, num = None, 0
    sols = []
    for q in chapter_qs:
        num += 1
        if q["chapter"]["section"] != cur_sec:
            cur_sec = q["chapter"]["section"]
            parts.append(r"\subsection*{%s}" % latexify(cur_sec, fillin=False))
        parts.append(render_question(q, num))
        sols.append(render_solution(q, num, subject))

    parts.append(r"\section*{答案速查（选择题）}")
    obj = [(i + 1, q) for i, q in enumerate(chapter_qs) if q["type"] == "choice"]
    if obj:
        rows, cells = [], []
        for n, q in obj:
            cells += [str(n), latexify(str(q["answer"]))]
            if len(cells) == 8:
                rows.append(" & ".join(cells))
                cells = []
        if cells:
            rows.append(" & ".join(cells + [""] * (8 - len(cells))))
        cells = " \\\\\n".join(rows)
        parts.append(r"""\begin{center}\small
\begin{tabular}{@{}*{4}{c@{\qquad}c}@{}}
\toprule
%s \\
\bottomrule
\end{tabular}
\end{center}""" % cells)

    parts.append(r"\section*{答案与解析}")
    parts.extend(sols)
    parts.append("\\end{document}\n")
    return "\n".join(parts)


# ---------------------------------------------------------------- 主流程

def main():
    ap = argparse.ArgumentParser(description="按章节生成真题分类汇编；优先读取裸页内嵌题库，裸页缺失时回退到 <root>/bank-data 快照。")
    ap.add_argument("--subject", required=True, choices=SUBJECTS)
    ap.add_argument("--exam-dir", default=EXAM_DIR,
                    help="裸页目录（默认 ILOVETJU_EXAM_DIR 或 <root>/web/exam；快照仅为缺失时的回退）")
    ap.add_argument("--chapter", type=int, default=None, help="章号（--inspect 时可省略）")
    ap.add_argument("--all", action="store_true", help="收录整章全部题目（默认精选打样）")
    ap.add_argument("--inspect", action="store_true",
                    help="只读检查：报告章节/题量/题型/配置/数据损坏，不写任何文件")
    ap.add_argument("--out", default=None, help="输出目录（默认 <root>/book）")
    ap.add_argument("--build", action="store_true", help="生成后调用 xelatex 编译两遍")
    args = ap.parse_args()

    data = load_bank(args.subject, args.exam_dir)
    if args.inspect:
        run_inspect(data, args.subject)
        return

    chapters = data["textbook"]["sections"]
    if args.chapter is None:
        hard_fail("未指定章节。请用 --chapter N，可选：%s" % "、".join(chapters))
    chapter_name = next((k for k in chapters if k.startswith("第%d章" % args.chapter)), None)
    if chapter_name is None:
        hard_fail("第%d章不存在。可用章节：%s" % (args.chapter, "、".join(chapters)))
    if args.subject not in MOCK_SOURCE:
        hard_fail("MOCK_SOURCE 中未配置科目 %s 的模拟卷文档全名（凡例必须引用），禁止编造" % args.subject)

    warnings = []
    chapter_qs = [q for q in data["questions"] if q["chapter"]["label"] == chapter_name]
    if not chapter_qs:
        hard_fail("%s 目录树存在但没有任何题目" % chapter_name)
    usable_qs = screen_questions(chapter_qs, args.subject, warnings)

    empty_secs = [s for s in chapters[chapter_name]
                  if not any(q["chapter"]["section"] == s for q in usable_qs)]
    if empty_secs:
        warnings.append("以下小节无可用题（将不出现在汇编中）：%s" % "、".join(empty_secs))
    if not data["textbook"].get("notes", {}).get(chapter_name):
        warnings.append("%s 缺少知识提要（textbook.notes），输出将省略该部分" % chapter_name)

    picked = pick_questions(usable_qs, args.all)
    if not picked:
        hard_fail("筛选后没有任何可用题目，中止")
    mode = "全量" if args.all else "精选打样（每节≤%d题+保底解答）" % SECTION_QUOTA
    print("数据预检: %s 共 %d 题，可用 %d，本次收录 %d（%s）"
          % (chapter_name, len(chapter_qs), len(usable_qs), len(picked), mode))

    tex = build_tex(data, picked, args.subject, chapter_name)

    # 题数一致性硬校验：收录 = question环境 = 解析条目 = 来源行
    n_q = tex.count(r"\begin{question}")
    n_sol = len(re.findall(r"\\solnum\{", tex))
    n_src = tex.count(r"\kaishu 来源：")     # 凡例里的“来源：”不带此前缀，不会误计
    if not (len(picked) == n_q == n_sol == n_src):
        hard_fail("一致性校验失败：收录%d / question%d / 解析%d / 来源%d —— "
                  "禁止交付，请检查生成器" % (len(picked), n_q, n_sol, n_src))
    print("一致性校验: 收录=%d question=%d 解析=%d 来源=%d" % (len(picked), n_q, n_sol, n_src))

    tc = Counter(q["type"] for q in picked)
    n_judge = sum(1 for q in picked if q["subtype"] == "judge")
    n_fill = sum(1 for q in picked if q["type"] == "fill"
                 or (q["type"] == "open" and q["subtype"] == "fill"))
    n_big = sum(1 for q in picked if q["type"] == "open" and q["subtype"] in ("calc", "solution"))
    secs = list(dict.fromkeys(q["chapter"]["section"] for q in picked))
    print("[STATS]")
    print(json.dumps({
        "chapter": chapter_name, "mode": "all" if args.all else "sample",
        "bank": len(chapter_qs), "usable": len(usable_qs), "picked": len(picked),
        "choice": tc.get("choice", 0), "judge": n_judge,
        "fill": n_fill, "solution": n_big,
        "sections": secs,
    }, ensure_ascii=False))

    if warnings:
        print("已知问题（%d）:" % len(warnings))
        for w in warnings[:10]:
            print("  -", w)
        if len(warnings) > 10:
            print("  ... 其余 %d 条略" % (len(warnings) - 10))

    outdir = args.out or os.path.join(PROJECT_ROOT, "book")
    os.makedirs(outdir, exist_ok=True)
    stem = f"{args.subject}-ch{args.chapter}" + ("" if args.all else "-sample")
    texpath = os.path.join(outdir, stem + ".tex")
    open(texpath, "w", encoding="utf-8").write(tex)
    print("written:", texpath)

    if args.build:
        for i in range(2):
            r = subprocess.run(["xelatex", "-interaction=nonstopmode", "-halt-on-error",
                                stem + ".tex"], cwd=outdir, capture_output=True, text=True)
            if r.returncode != 0:
                tail = "\n".join((r.stdout or "").splitlines()[-40:])
                sys.exit(f"xelatex 第{i+1}遍失败:\n{tail}")
        print("built:", os.path.join(outdir, stem + ".pdf"))


if __name__ == "__main__":
    main()
