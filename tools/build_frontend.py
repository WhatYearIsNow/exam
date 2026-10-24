# -*- coding: utf-8 -*-
"""I Love TJU 原生前端重建脚本。

用法: python3 tools/build_frontend.py [--web-dir WEB] [--exam-dir EXAM]
1. 把 web/exam/{marx,physics,probability}.html 以 base64 重新打进
   壳 web/index.html 的 payload-* 模板块（顶栏与增强层不动）。
2. 重新生成调试页 web/exam/index.html（三个裸页的 iframe 切换器，
   不再内嵌内容副本，永远与裸页同步）。
"""
import argparse
import base64
import json
import os
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SUBJECTS = {'marx': '马原', 'physics': '大物', 'probability': '概率论'}

TAB_HTML = '''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>I Love TJU - 裸页面</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:100%;height:100%;overflow:hidden}
body{font-family:"Microsoft YaHei","PingFang SC","Segoe UI",sans-serif;background:#f0f4f8}
.tabbar{display:flex;align-items:center;padding:6px 12px;gap:6px;background:#fff;border-bottom:1px solid #dde3ea}
.tabbar .brand{font-size:13px;color:#8b98aa;margin-right:8px;white-space:nowrap}
.tabbar .tab{padding:6px 18px;border-radius:8px;border:1px solid #c8d3e0;background:#f8fafc;color:#4a5568;font-size:13px;font-weight:600;cursor:pointer}
.tabbar .tab:hover{background:#edf2f7}
.tabbar .tab.active{background:#2b6cb0;color:#fff;border-color:#2b6cb0}
#frame{width:100%;height:calc(100vh - 37px);border:none;display:block}
</style>
</head>
<body>
<div class="tabbar">
  <span class="brand">I Love TJU</span>
  <button class="tab active" data-page="marx">马原</button>
  <button class="tab" data-page="physics">大物</button>
  <button class="tab" data-page="probability">概率论</button>
</div>
<iframe id="frame" src="marx.html"></iframe>
<script>
var frame=document.getElementById('frame');
document.querySelectorAll('.tab').forEach(function(b){
  b.addEventListener('click',function(){
    document.querySelectorAll('.tab').forEach(function(x){x.classList.remove('active')});
    b.classList.add('active');
    frame.src=b.dataset.page+'.html';
  });
});
</script>
</body>
</html>
'''


def build_frontend(web_dir, exam_dir):
    web_dir, exam_dir = Path(web_dir), Path(exam_dir)
    shell_path = web_dir / 'index.html'
    shell = shell_path.read_text(encoding='utf-8')
    for subj in SUBJECTS:
        raw = (exam_dir / (subj + '.html')).read_bytes()
        data_match = re.search(r'<script\b[^>]*\bid=["\']' + subj
                               + r'-data["\'][^>]*>(.*?)</script>', raw.decode('utf-8'), re.S)
        if not data_match:
            raise ValueError(f'{subj}.html 缺少题库 JSON')
        questions = json.loads(data_match.group(1)).get('questions')
        if not isinstance(questions, list):
            raise ValueError(f'{subj}.html 题库 questions 必须是列表')
        count = len(questions)
        button_pattern = re.compile(r'(<button\b[^>]*\bdata-page=["\']' + subj
                                    + r'["\'][^>]*>)(.*?)(</button>)', re.S)
        count_pattern = re.compile(r'(<span\b[^>]*\bclass=["\'][^"\']*\btab-meta\b[^"\']*["\'][^>]*>)(.*?)(</span>)', re.S)
        def update_count(match):
            body, changed = count_pattern.subn(lambda label: label.group(1) + str(count)
                                               + ' 道题' + label.group(3), match.group(2), count=1)
            if not changed:
                raise ValueError(f'首页 {subj} 按钮缺少 tab-meta 题量标签')
            return match.group(1) + body + match.group(3)
        shell, changed = button_pattern.subn(update_count, shell, count=1)
        if not changed:
            raise ValueError(f'首页缺少 {subj} 学科按钮')
        b64 = base64.b64encode(raw).decode()
        pat = re.compile(r'(<script[^>]*id=["\']payload-' + subj + r'["\'][^>]*>)(.*?)(</script>)', re.S)
        if not pat.search(shell):
            raise ValueError(f'payload-{subj} block not found in {shell_path}')
        shell = pat.sub(lambda m: m.group(1) + b64 + m.group(3), shell, count=1)
        print(f'[OK] payload-{subj} -> {len(b64)} chars (src {len(raw)} bytes, {count} questions)')
    with shell_path.open('w', encoding='utf-8', newline='') as f:
        f.write(shell)
    print(f'[OK] shell rebuilt: {shell_path}')

    index_path = exam_dir / 'index.html'
    with index_path.open('w', encoding='utf-8', newline='') as f:
        f.write(TAB_HTML)
    print(f'[OK] debug tab page rebuilt: {index_path} ({len(TAB_HTML)} chars)')
    print('DONE')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--web-dir', type=Path,
                    default=Path(os.environ.get('ILOVETJU_WEB_DIR', PROJECT_ROOT / 'web')),
                    help='站点目录（默认 ILOVETJU_WEB_DIR 或 <root>/web）')
    ap.add_argument('--exam-dir', type=Path, default=None,
                    help='裸页目录（默认 ILOVETJU_EXAM_DIR 或 <web-dir>/exam）')
    args = ap.parse_args()
    exam_dir = args.exam_dir or Path(os.environ.get('ILOVETJU_EXAM_DIR', args.web_dir / 'exam'))
    try:
        build_frontend(args.web_dir, exam_dir)
    except (OSError, ValueError) as exc:
        ap.exit(1, f'[FAIL] {exc}\n')


if __name__ == '__main__':
    main()
