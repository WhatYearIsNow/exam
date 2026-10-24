# -*- coding: utf-8 -*-
"""I Love TJU 质感版前端构建（默认输出到 web/premium/）。
用法: python3 tools/build_premium.py [--web-dir WEB] [--exam-dir EXAM] [--out OUT]
1. 把正式裸页（含全部功能与 ui-polish）复制到 premium/，注入 ui-premium-v1 质感层；
2. 复制壳并重打 premium payload（顶栏/增强层/AI核验等一切功能不变）。
回退：直接删掉 premium/ 目录与 Caddy 路由即可，正式站零影响。
"""
import argparse
import base64
import os
import re
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SUBJECTS = ['marx', 'physics', 'probability']

PREMIUM = '''<style id="ui-premium-v1">
/* ═══ 质感层 v1：只动观感，不动布局与功能 ═══ */
:root{
  --p-bg1:#eef3fa; --p-bg2:#f6f9fd;
  --p-card:#ffffff; --p-bd:#dfe7f1;
  --p-blue:#2b6cb0; --p-blue-d:#1a4e85; --p-ink:#182436; --p-sub:#5a6b82;
  --p-sh-sm:0 1px 2px rgba(16,42,77,.05),0 2px 8px rgba(16,42,77,.05);
  --p-sh-md:0 2px 4px rgba(16,42,77,.06),0 10px 26px rgba(16,42,77,.09);
  --p-sh-lg:0 6px 16px rgba(16,42,77,.10),0 20px 48px rgba(16,42,77,.13);
  --p-ring:0 0 0 3px rgba(43,108,176,.16);
}
html{background:var(--p-bg2)}
body{
  background:
    radial-gradient(1100px 480px at 88% -160px, rgba(84,140,208,.14), transparent 60%),
    radial-gradient(900px 420px at -10% 30%, rgba(64,120,190,.08), transparent 55%),
    linear-gradient(180deg,var(--p-bg1),var(--p-bg2) 30rem);
  -webkit-font-smoothing:antialiased;text-rendering:optimizeLegibility;
}
::selection{background:rgba(43,108,176,.22)}
main{scrollbar-color:#b9c9dc transparent}

/* ── 列表卡片：双层阴影 + 顶部高光 + 渐变饰条 ── */
.grp{
  background:linear-gradient(180deg,#ffffff,#fcfdff);
  border:1px solid var(--p-bd);border-radius:16px;
  box-shadow:var(--p-sh-sm),inset 0 1px 0 rgba(255,255,255,.9);
  transition:box-shadow .22s,border-color .22s,transform .22s;
}
.grp:hover{transform:translateY(-2px);border-color:#c4d5e8;box-shadow:var(--p-sh-md),inset 0 1px 0 rgba(255,255,255,.9)}
.grp.open{border-color:#b6cbe2;box-shadow:var(--p-sh-md),inset 0 1px 0 #fff}
.grp-h{border-radius:16px 16px 0 0}
.grp-h>span:first-child::before{
  background:linear-gradient(180deg,#4b8fd6,#2b6cb0);
  box-shadow:0 0 0 3px rgba(84,140,208,.16),0 2px 6px rgba(43,108,176,.35);
}
.grp.open .grp-h{background:linear-gradient(90deg,rgba(233,242,251,.95),rgba(255,255,255,.6) 72%)}
.grp-h .arrow{
  background:linear-gradient(180deg,#f4f8fc,#e9f1f9);
  border:1px solid #d5e1ee;color:var(--p-blue);
  box-shadow:inset 0 1px 0 rgba(255,255,255,.85);
  transition:transform .2s,background .2s,box-shadow .2s;
}
.grp-h:hover .arrow{background:linear-gradient(180deg,#e8f2fb,#dcebfa);box-shadow:var(--p-ring)}
.grp.open .grp-h .arrow{transform:rotate(90deg);background:var(--p-blue);color:#fff;border-color:var(--p-blue)}
.grp-h .meta{font-variant-numeric:tabular-nums;letter-spacing:.01em}
.grp-progress{background:#e4edf6;border-radius:99px;overflow:hidden}
.grp-progress i{
  background:linear-gradient(90deg,#3d83c8,#66a7e3);
  box-shadow:0 0 6px rgba(80,144,210,.55);border-radius:99px;
}
.grp-body{background:linear-gradient(180deg,#f7fafd,#fbfdff)}
.qrow{
  background:#fff;border:1px solid #e2eaf3;border-radius:12px;
  box-shadow:0 1px 2px rgba(16,42,77,.04);
  transition:border-color .16s,box-shadow .16s,transform .16s;
}
.qrow:hover{border-color:#bcd0e5;box-shadow:0 3px 10px rgba(16,42,77,.08);transform:translateY(-1px)}
.qrow .cnt{font-variant-numeric:tabular-nums}

/* ── 顶栏：毛玻璃悬浮 ── */
.pv-top,.list-hd{
  position:sticky;top:0;z-index:20;
  background:rgba(250,252,254,.78);
  -webkit-backdrop-filter:saturate(1.4) blur(14px);backdrop-filter:saturate(1.4) blur(14px);
  border-bottom:1px solid rgba(210,222,236,.7);
}
.back-btn,.pv-cnt{
  background:rgba(255,255,255,.85);border:1px solid var(--p-bd);
  box-shadow:var(--p-sh-sm);backdrop-filter:blur(6px);-webkit-backdrop-filter:blur(6px);
  transition:box-shadow .18s,transform .12s,border-color .18s;
}
.back-btn:hover,.pv-cnt:hover{border-color:#bfd2e6;box-shadow:var(--p-sh-md)}
.back-btn:active,.pv-cnt:active{transform:scale(.96)}
.pv-progress{border-radius:99px;background:#e2ebf4;box-shadow:inset 0 1px 2px rgba(16,42,77,.08)}
.pv-progress i{
  background:linear-gradient(90deg,#f0b429,#ffd25e);
  box-shadow:0 0 8px rgba(255,196,0,.5);border-radius:99px;position:relative;
}
.mode-tabs .tab,button.tab{
  transition:background .18s,color .18s,box-shadow .18s;
}
.mode-tabs .tab[aria-selected="true"],.mode-tabs .tab.active{
  box-shadow:0 4px 14px rgba(43,108,176,.32),inset 0 1px 0 rgba(255,255,255,.25);
}

/* ── 题卡：纸感 + 精修标签 ── */
.qcard{
  background:linear-gradient(180deg,#ffffff,#fdfefe);
  border:1px solid var(--p-bd);border-radius:18px;
  box-shadow:var(--p-sh-md),inset 0 1px 0 rgba(255,255,255,.95);
}
.qhead .tag{
  border-radius:999px;font-weight:600;letter-spacing:.01em;
  box-shadow:inset 0 1px 0 rgba(255,255,255,.55);
}
.qbody{color:var(--p-ink)}

/* ── 选项：层次与状态质感 ── */
.opt{
  background:#fff;border:1px solid #e2eaf3;border-radius:13px;
  box-shadow:0 1px 2px rgba(16,42,77,.04),inset 0 1px 0 #fff;
  transition:border-color .16s,background .16s,box-shadow .16s,transform .12s;
}
.opt:hover:not(.correct):not(.incorrect){border-color:#b9cfe6;background:linear-gradient(180deg,#fbfdff,#f5faff);box-shadow:0 3px 10px rgba(16,42,77,.07)}
.opt:active{transform:scale(.988)}
.opt.correct{
  border-color:#4d9e72;background:linear-gradient(180deg,#f2faf5,#e9f5ee);
  box-shadow:0 0 0 3px rgba(46,138,85,.10),inset 0 1px 0 rgba(255,255,255,.8);
}
.opt.incorrect{
  border-color:#cf7b74;background:linear-gradient(180deg,#fdf4f3,#fbeeed);
  box-shadow:0 0 0 3px rgba(189,59,50,.09),inset 0 1px 0 rgba(255,255,255,.8);
}
.opt-l{
  border-radius:10px;font-weight:700;
  background:linear-gradient(180deg,#f5f8fb,#eaf0f7);
  border:1px solid #dde6f0;color:var(--p-sub);
  box-shadow:inset 0 1px 0 rgba(255,255,255,.8);
  transition:all .16s;
}
.opt.correct .opt-l{background:linear-gradient(180deg,#379a68,#2c7d54);border-color:#2c7d54;color:#fff;box-shadow:0 2px 6px rgba(44,125,84,.35)}
.opt.incorrect .opt-l{background:linear-gradient(180deg,#c05a52,#a94a42);border-color:#a94a42;color:#fff;box-shadow:0 2px 6px rgba(169,74,66,.3)}

/* ── 按钮：微渐变 + 环 ── */
.btn{border-radius:12px;transition:all .16s}
.btn.primary{background:linear-gradient(180deg,#3584cf,#2b6cb0);box-shadow:0 4px 12px rgba(43,108,176,.32),inset 0 1px 0 rgba(255,255,255,.25)}
.btn.primary:hover{filter:brightness(1.06);box-shadow:0 6px 18px rgba(43,108,176,.4)}
.btn.show{background:linear-gradient(180deg,#fff,#f4f8fc);border:1px solid var(--p-bd);box-shadow:var(--p-sh-sm)}
.btn.show:hover{border-color:#bfd2e6;box-shadow:var(--p-sh-md)}
.btn:active{transform:scale(.97)}
.open-act .btn{border-radius:12px}

/* ── 答案/解析盒 ── */
.ansbox{
  border-radius:14px;border:1px solid #e0e9f2;
  box-shadow:0 1px 3px rgba(16,42,77,.05),inset 0 1px 0 #fff;
  overflow:hidden;background:#fff;
}
.ansbox .hd{
  background:linear-gradient(90deg,#f2f7fc,#fafcfe);
  border-bottom:1px solid #e8eef6;color:var(--p-sub);font-weight:700;
}
.ansbox .hd.right{background:linear-gradient(90deg,#e9f7ef,#f4fbf7);color:#256b47;border-bottom-color:#d5ecdf}
.ansbox .hd.wrong{background:linear-gradient(90deg,#fdefee,#fdf5f4);color:#a03d35;border-bottom-color:#f0dcda}
.ansbox .ct{line-height:1.9}
.ana-line>span:first-child{
  background:linear-gradient(180deg,#eaf2fb,#dfeaf7);color:var(--p-blue-d);
  border-radius:8px;font-weight:700;box-shadow:inset 0 1px 0 rgba(255,255,255,.7);
}

/* ── 增强层（AI核验/备注/存疑）质感对齐 ── */
.tju-tools .tju-btn{
  background:linear-gradient(180deg,#ffffff,#f7fafd) !important;
  border:1px solid #dbe4ee !important;border-radius:10px !important;
  box-shadow:0 1px 3px rgba(16,42,77,.07),inset 0 1px 0 #fff !important;
}
.tju-tools .tju-btn:hover{transform:translateY(-1px);box-shadow:0 4px 12px rgba(16,42,77,.12) !important}
.tju-ai-panel{
  border-radius:14px;border-color:#dfe7f1;
  background:linear-gradient(180deg,#ffffff,#fbfcfe);
  box-shadow:var(--p-sh-sm),inset 0 1px 0 #fff;
}
.tju-ai-model{color:var(--p-blue-d)}
.tju-ai-reason{color:#2a3950}
.tju-ai-ans,.tju-ai-doubt{border-radius:0 10px 10px 0}
.tju-mini-btn{border-radius:10px !important}
.tju-note-ta,.tju-doubt-ta{
  border-radius:10px;border-color:#dfe7f1;
  box-shadow:inset 0 1px 3px rgba(16,42,77,.05);
  transition:border-color .15s,box-shadow .15s;
}
.tju-note-ta:focus,.tju-doubt-ta:focus{outline:none;border-color:#8fb4d9;box-shadow:var(--p-ring)}

/* ── 弹层 / 跳题面板 ── */
.qnav-mask,.tju-editq-mask{background:rgba(15,26,42,.42);-webkit-backdrop-filter:blur(3px);backdrop-filter:blur(3px)}
.qnav-box,.tju-editq-box{
  border-radius:16px;border:1px solid rgba(223,231,241,.9);
  box-shadow:var(--p-sh-lg);background:linear-gradient(180deg,#fff,#fbfcff);
}
.qnum{border-radius:9px;transition:all .14s}
.qnum.cur{box-shadow:0 3px 10px rgba(43,108,176,.35)}
.qnum.done{background:#e8f2fb;color:var(--p-blue-d);border-color:#c9dcee}

/* ── 空状态 / 提示 ── */
.empty .big{filter:drop-shadow(0 6px 14px rgba(16,42,77,.18))}
@media (prefers-reduced-motion:reduce){
  *{transition:none !important;animation:none !important}
}
</style>'''

def build_premium(web_dir, exam_dir, out_dir):
    web_dir, exam_dir, out_dir = Path(web_dir), Path(exam_dir), Path(out_dir)
    shell = (web_dir / 'index.html').read_text(encoding='utf-8')
    pages = {}
    for subj in SUBJECTS:
        html = (exam_dir / (subj + '.html')).read_text(encoding='utf-8')
        html = re.sub(r'<style id="ui-premium-v1">.*?</style>\n?', '', html, flags=re.S)
        if '</head>' not in html:
            raise ValueError(f'{subj}.html 缺少 </head>')
        pages[subj] = html.replace('</head>', PREMIUM + '\n</head>')
        b64 = base64.b64encode(pages[subj].encode('utf-8')).decode()
        pat = re.compile(r'(<script[^>]*id=["\']payload-' + subj + r'["\'][^>]*>)(.*?)(</script>)', re.S)
        if not pat.search(shell):
            raise ValueError(f'payload-{subj} block not found in {web_dir / "index.html"}')
        shell = pat.sub(lambda m: m.group(1) + b64 + m.group(3), shell, count=1)
        print(f'[OK] payload-{subj} -> {len(b64)} chars')

    out_dir.mkdir(parents=True, exist_ok=True)
    for subj, html in pages.items():
        (out_dir / (subj + '.html')).write_text(html, encoding='utf-8')
        print(f'[OK] {out_dir / (subj + ".html")} ({len(html)} chars)')
    with (out_dir / 'index.html').open('w', encoding='utf-8', newline='') as f:
        f.write(shell)
    print(f'[OK] {out_dir / "index.html"} ({len(shell)} chars)')
    print('DONE')


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--web-dir', type=Path,
                    default=Path(os.environ.get('ILOVETJU_WEB_DIR', PROJECT_ROOT / 'web')),
                    help='站点目录（默认 ILOVETJU_WEB_DIR 或 <root>/web）')
    ap.add_argument('--exam-dir', type=Path, default=None,
                    help='裸页目录（默认 ILOVETJU_EXAM_DIR 或 <web-dir>/exam）')
    ap.add_argument('--out', type=Path, default=None,
                    help='输出目录（默认 <web-dir>/premium）')
    args = ap.parse_args()
    exam_dir = args.exam_dir or Path(os.environ.get('ILOVETJU_EXAM_DIR', args.web_dir / 'exam'))
    try:
        build_premium(args.web_dir, exam_dir, args.out or args.web_dir / 'premium')
    except (OSError, ValueError) as exc:
        ap.exit(1, f'[FAIL] {exc}\n')


if __name__ == '__main__':
    main()
