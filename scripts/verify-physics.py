# -*- coding: utf-8 -*-
"""physics-quiz 渲染回归验证：无头截图 + 残留命令扫描
用法: python scripts/verify-physics.py [url]（默认 http://localhost:8766/index.html）
"""
import sys, re
from pathlib import Path
from playwright.sync_api import sync_playwright

sys.stdout.reconfigure(encoding='utf-8')

URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8766/index.html"
OUT = Path(__file__).resolve().parent.parent / "physics-quiz" / "verify"
OUT.mkdir(exist_ok=True)

errors = []
raw_hits = []

with sync_playwright() as p:
    b = p.chromium.launch(headless=True)
    ctx = b.new_context(viewport={"width": 430, "height": 900}, device_scale_factor=2)
    page = ctx.new_page()
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)

    page.goto(URL, wait_until="networkidle")
    page.evaluate("localStorage.clear()")
    page.reload(wait_until="networkidle")
    page.wait_for_selector(".grp, .qrow", timeout=8000)

    # 1. 初始页（章节训练）
    page.screenshot(path=str(OUT / "1-chapter-list.png"), full_page=True)
    sub = page.text_content("#app-sub")
    groups = page.eval_on_selector_all(".grp-h", "els=>els.map(e=>e.innerText.trim())")
    # 章节排序检查：提取章号应递增（9→15）
    chap_nums = page.evaluate("""
        () => [...document.querySelectorAll('.grp-h')]
            .map(e => parseInt((e.innerText.match(/第\\s*(\\d+)\\s*章/) || [])[1] || '999'))
    """)
    chap_sorted = chap_nums == sorted(chap_nums)

    # 2. 进入填空题（第11题，德布罗意波长）查看答案 → 检查 \frac 渲染与空位样式
    page.evaluate("""
        const q = DATA.questions.find(q=>q.id==='25261-T11');
        startPractice(['25261-T11'],'验证','25261-T11');
    """)
    page.wait_for_selector(".qcard", timeout=5000)
    blank_cnt = page.eval_on_selector_all(".qcard .qblank", "els=>els.length")
    page.click("text=查看答案")
    page.wait_for_selector(".ansbox", timeout=5000)
    # KaTeX 真实排版检查：应产生 .katex 容器，而非备用渲染器或裸命令
    page.wait_for_timeout(300)
    katex_cnt = page.eval_on_selector_all(".qcard .katex", "els=>els.length")
    katex_loaded = page.evaluate("typeof renderMathInElement === 'function'")
    page.screenshot(path=str(OUT / "2-fill-answer.png"), full_page=True)

    # 3. 选择题判错（T4）：进入整卷练习，验证进度条存在且题号导航已移除
    page.evaluate("""
        startPractice(DATA.questions.map(q=>q.id),'验证整卷','25261-T4');
    """)
    page.wait_for_selector(".pv-progress", timeout=5000)
    qnum_cnt = page.eval_on_selector_all(".qnum-grid .qnum", "els=>els.length")
    qnum_title = '(已移除)'
    page.evaluate("pickOpt('25261-T4','A')")  # 正确答案 D，选 A 判错
    page.wait_for_selector(".ansbox", timeout=5000)
    page.screenshot(path=str(OUT / "3-choice-wrong.png"), full_page=True)

    # 3.5 刷新恢复：页面应停留在练习视图同一题，而非跳回主界面
    before_reload_cnt = page.text_content(".pv-cnt").strip()
    page.reload(wait_until="networkidle")
    page.wait_for_selector(".pv-top", timeout=8000)
    restored_cnt = page.text_content(".pv-cnt").strip()
    restored_ok = before_reload_cnt == restored_cnt and "/" in restored_cnt

    # 3.6 题号选择弹层：点计数器弹出，点题号跳转，点背景关闭
    page.click(".pv-cnt")
    page.wait_for_selector(".qnav-mask", timeout=5000)
    qnav_cnt = page.eval_on_selector_all(".qnav-mask .qnum", "els=>els.length")
    page.evaluate("document.querySelectorAll('.qnav-mask .qnum')[0].click()")
    page.wait_for_timeout(300)
    qnav_jump_ok = page.text_content(".pv-cnt").strip().startswith("1")

    # 3.7 ⋯ 菜单：点开后应出现导出/导入项，点外部关闭
    page.click("text=⋯")
    page.wait_for_timeout(200)
    menu_visible = page.evaluate("!document.getElementById('menu-pop').classList.contains('hidden')")
    page.click(".pv-title")
    page.wait_for_timeout(200)
    menu_closed = page.evaluate("document.getElementById('menu-pop').classList.contains('hidden')")

    # 4. 错题回顾：行内应含日期时间（格式 08-24 15:30）
    page.evaluate("switchMode('wrong')")
    page.wait_for_selector(".qrow", timeout=5000)
    page.screenshot(path=str(OUT / "4-wrong-list.png"), full_page=True)
    wrong_rows = page.eval_on_selector_all(".qrow .t1", "els=>els.map(e=>e.innerText)")
    wrong_meta = page.eval_on_selector_all(".qrow .t2", "els=>els.map(e=>e.innerText)")
    import re as _re
    wrong_has_date = all(_re.search(r"\d{2}-\d{2} \d{2}:\d{2}", m) for m in wrong_meta)

    # 5. 图片题（T1 含图）
    page.evaluate("switchMode('chapter')")
    page.evaluate("startPractice(['25261-T1'],'验证','25261-T1')")
    page.wait_for_selector(".qbody img", timeout=5000)
    page.evaluate("document.querySelector('.qbody img').loading='eager'")
    page.wait_for_timeout(800)
    img_ok = page.eval_on_selector(".qbody img", "el=>el.complete&&el.naturalWidth>0")
    page.screenshot(path=str(OUT / "5-image-question.png"), full_page=True)

    # 6. 全量残留扫描：遍历全部题渲染结果，查找裸反斜杠命令与源码外泄
    page.set_default_timeout(180000)  # 264 题全量渲染，放宽超时
    scan = page.evaluate("""
        () => {
            const hits = [];
            for (const q of DATA.questions) {
                const ctx = document.createElement('div');
                document.body.appendChild(ctx);
                for (const t of [q.desc, q.answer, q.analysis, ...q.options.map(o=>o.text)]) {
                    ctx.innerHTML = renderMd(t);
                    if (typeof renderMathInElement === 'function') {
                        renderMathInElement(ctx, {delimiters:[{left:'$$',right:'$$',display:true},{left:'$',right:'$',display:false}], throwOnError:false});
                    }
                    const txt = ctx.innerText;
                    const raw = txt.match(/\\\\[a-zA-Z]+/g);
                    if (raw) hits.push(q.id + ': ' + [...new Set(raw)].join(','));
                    if (/<span class=/.test(ctx.innerText)) hits.push(q.id + ': HTML源码外泄');
                }
                ctx.remove();
            }
            return hits;
        }
    """)
    raw_hits = scan

    print("副标题:", sub)
    print("章分组:", " | ".join(groups))
    print("章节排序(9→15):", "正确" if chap_sorted else "错误: " + str(chap_nums))
    print("题号导航:", "已移除" if qnum_cnt == 0 else "异常：仍有 " + str(qnum_cnt) + " 个格子")
    print("刷新恢复进度:", "正确（" + restored_cnt + "）" if restored_ok else "失败（前后: " + before_reload_cnt + " → " + restored_cnt + "）")
    print("题号弹层:", qnav_cnt, "格，跳转第1题", "成功" if qnav_jump_ok else "失败")
    print("⋯ 菜单:", "开关正常" if (menu_visible and menu_closed) else "异常")
    print("错题行日期:", "有" if wrong_has_date else "缺失")
    print("填空空位渲染:", blank_cnt, "个")
    print("KaTeX 本地渲染:", "已加载" if katex_loaded else "未加载（走备用渲染器）", "·", katex_cnt, "个公式容器")
    print("错题列表:", wrong_rows)
    print("图片加载:", "成功" if img_ok else "失败")
    print("JS 错误:", errors if errors else "无")
    print("残留命令:", raw_hits if raw_hits else "无")
    print("截图目录:", OUT)
    b.close()

sys.exit(1 if (errors or raw_hits or not chap_sorted or qnum_cnt != 0 or katex_cnt == 0
               or not restored_ok or qnav_cnt == 0 or not qnav_jump_ok
               or not menu_visible or not menu_closed or not wrong_has_date) else 0)
