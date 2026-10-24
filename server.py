#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""I Love TJU —— 三合一刷题中心后端服务

能力：
1. /sync        多端作答记录同步（兼容前端页面内置的 Cloudflare Worker 协议：
                 GET/PUT ?slot=xxx，Bearer Token，按记录 at 时间戳合并）
2. /api/annotations  题目存疑标记 / 备注 / AI 结论的持久化（按 at 时间戳合并）
3. /api/ai-check      AI 答案核验（复用服务器现有 DeepSeek 配置，密钥仅存服务端）
4. /health       健康检查

默认监听 127.0.0.1:8901，同时提供 web/ 静态页面和 API。
生产环境可由 Caddy 提供静态文件并反代 /sync、/api 前缀。
"""
import argparse
import json
import os
import re
import threading
import time
import urllib.request
import urllib.error

from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from functools import partial
from urllib.parse import urlsplit

ROOT = os.path.dirname(os.path.abspath(__file__))
HOST = os.environ.get("ILOVETJU_HOST", "127.0.0.1")
PORT = int(os.environ.get("ILOVETJU_PORT", "8901"))
CFG_PATH = os.environ.get("ILOVETJU_CONFIG", os.path.join(ROOT, "config.json"))
DATA_DIR = os.environ.get("ILOVETJU_DATA_DIR", os.path.join(ROOT, "data"))
WEB_DIR = os.environ.get("ILOVETJU_WEB_DIR", os.path.join(ROOT, "web"))
CONFIG_ENV = {
    name: "ILOVETJU_" + name.upper()
    for name in ("app_token", "llm_base", "llm_key", "llm_model",
                 "tju_llm_base", "tju_llm_key", "tju_llm_model")
}

MAX_SYNC_BODY = 25 * 1024 * 1024      # 作答记录全量同步上限
MAX_ANNOT_BODY = 4 * 1024 * 1024      # 注解（备注/存疑/AI）上限
MAX_CHECK_BODY = 1200 * 1024          # AI 校验请求上限（含缩图 base64）
LLM_TIMEOUT = 90

_lock = threading.Lock()
_cfg_cache = None
_cfg_mtime = 0


def load_config(force=False):
    global _cfg_cache, _cfg_mtime
    try:
        mt = os.path.getmtime(CFG_PATH)
    except OSError:
        mt = None
    if force or _cfg_cache is None or mt != _cfg_mtime:
        try:
            with open(CFG_PATH, "r", encoding="utf-8") as f:
                value = json.load(f)
            _cfg_cache = value if isinstance(value, dict) else {}
        except (OSError, json.JSONDecodeError, ValueError):
            _cfg_cache = {}
        _cfg_mtime = mt
    cfg = dict(_cfg_cache)
    for name, env_name in CONFIG_ENV.items():
        if env_name in os.environ:
            cfg[name] = os.environ[env_name]
    return cfg


def safe_name(s):
    return re.sub(r"[^A-Za-z0-9_.-]", "_", s or "default")


def sync_file(slot):
    return os.path.join(DATA_DIR, "sync-" + safe_name(slot) + ".json")


def annot_file(subject):
    return os.path.join(DATA_DIR, "annot-" + safe_name(subject) + ".json")


def read_json(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError, ValueError, UnicodeDecodeError):
        return default


def write_json(path, obj):
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False)
    os.replace(tmp, path)


def _ts(v):
    """提取时间戳：None/缺失/0/非数字 都视为 0（未设置）。"""
    if not isinstance(v, dict):
        return 0
    t = v.get("at")
    if t is None or not isinstance(t, (int, float)) or t <= 0:
        return 0
    return t


def merge_by_at(stored, incoming):
    """逐条按 at 时间戳合并（与前端 mergeRemote 逻辑一致）。

    墓碑（removed: true）保护规则：
    - 如果云端已有 removed: true，无论 incoming 时间戳多大都不覆盖（墓碑永久生效）。
    - 如果 incoming 有 removed: true 且 at 更大，则写入墓碑。
    """
    if not isinstance(stored, dict):
        stored = {}
    if not isinstance(incoming, dict):
        return dict(stored)
    out = dict(stored)
    now_ms = int(time.time() * 1000)
    skew_cap = now_ms + 120_000   # 容许 2 分钟时钟偏移；超过视为异常时钟，钳制
    for k, v in incoming.items():
        if not isinstance(v, dict):
            continue
        v = dict(v)
        at = v.get("at")
        if isinstance(at, (int, float)) and at > skew_cap:
            v["at"] = int(skew_cap)   # 防时钟偏快设备的旧数据反超新清除
        old = out.get(k)
        # 墓碑保护：云端已有墓碑，不覆盖
        if old and old.get("removed"):
            continue
        # 新记录是墓碑，写入
        if v.get("removed"):
            out[k] = v
            continue
        # 正常记录：按 at 时间戳合并
        if not old or _ts(v) > _ts(old):
            out[k] = v
    return out


def authed(handler, cfg):
    a = handler.headers.get("Authorization", "") or ""
    if a.startswith("Bearer "):
        t = a[len("Bearer "):].strip()
    else:
        t = (handler.headers.get("X-Auth-Token", "") or "").strip()
    tok = cfg.get("app_token") or ""
    if not tok or not t:
        return False
    import hmac
    return hmac.compare_digest(t, tok)


# ─────────────────────────── AI 核验 ───────────────────────────
# 两段式核验：一审 tju-llm（天大校内服务，校园网可直连）→ 二审 DeepSeek（用户不认可一审时才调用）
_ai_last = [0.0]          # 简单限频：全局最小间隔（在 _lock 保护下读写，避免竞态）


def _chat(base, key, model, prompt, timeout=LLM_TIMEOUT, images=None):
    content = prompt
    if images:
        # 多模态：文本在前，图片随后（data URI）
        content = [{"type": "text", "text": prompt}]
        for u in images:
            content.append({"type": "image_url", "image_url": {"url": u}})
    body = json.dumps({
        "model": model,
        "messages": [{"role": "user", "content": content}],
        "temperature": 0.2,
        "max_tokens": 2000,
        "stream": False,
    }).encode("utf-8")
    req = urllib.request.Request(
        base.rstrip("/") + "/chat/completions", data=body, method="POST",
        headers={"Content-Type": "application/json",
                 "Authorization": "Bearer " + key})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        obj = json.loads(r.read().decode("utf-8", "replace"))
    choices = obj.get("choices")
    if not choices or not isinstance(choices, list) or len(choices) == 0:
        raise ValueError("LLM API returned empty choices")
    content = choices[0].get("message", {}).get("content")
    if content is None:
        raise ValueError("LLM API returned no message content")
    return parse_llm_json(content)


def ai_check(cfg, payload):
    q = payload.get("question") or payload
    if not isinstance(q, dict) or not q.get("desc"):
        return {"error": "缺少题目内容"}
    doubt = (payload.get("doubt") or "").strip()
    first = payload.get("firstResult") or None   # 非空 = 用户不认可一审，触发二审
    subject = payload.get("subject") or ""
    # 题目附图（data URI 列表，前端已缩图）：最多 3 张、单张 ≤ 400KB
    images = [u for u in (payload.get("images") or [])
              if isinstance(u, str) and u.startswith("data:image/") and len(u) <= 400 * 1024][:3]

    if not first:
        # ── 一审：tju-llm（天大校内 LLM 服务）──
        tkey = cfg.get("tju_llm_key") or ""
        if not tkey:
            return {"error": "服务端未配置 tju-llm Key（config.json tju_llm_key）"}
        tbase = cfg.get("tju_llm_base") or "https://ai.tju.edu.cn/api/v3"
        tmodel = cfg.get("tju_llm_model") or "tju-llm"
        try:
            parsed = _chat(tbase, tkey, tmodel,
                           build_prompt(subject, q, doubt, None, images_count=len(images)),
                           images=images)
            if parsed is None:
                return {"error": "AI 一审输出无法解析"}
            parsed["reason"] = format_reason(parsed.get("reason"))
            parsed["stage"] = 1
            parsed["model"] = "tju-llm"
            return parsed
        except urllib.error.HTTPError as e:
            return {"error": "tju-llm HTTP %s：%s" % (e.code, e.read().decode("utf-8", "replace")[:120])}
        except Exception as e:
            return {"error": "tju-llm 调用失败：" + str(e)[:200]}

    # ── 二审：DeepSeek，基于上一轮结论 + 用户质疑 复核 ──
    # 实测 deepseek-v4-flash / reasoner / flash 均支持 image_url 读图；
    # deepseek-v4-pro 与 deepseek-chat 不支持，故带图题回退链不含 deepseek-chat
    key = cfg.get("llm_key") or ""
    if not key:
        return {"error": "服务端未配置 DeepSeek Key（config.json llm_key）"}
    base = (cfg.get("llm_base") or "https://api.deepseek.com").rstrip("/")
    prompt = build_prompt(subject, q, doubt, first, images_count=len(images))
    configured_model = cfg.get("llm_model") or "deepseek-chat"
    models = [configured_model]
    if images:
        for v in ("deepseek-reasoner", "deepseek-flash"):
            if v not in models:
                models.append(v)
    elif configured_model != "deepseek-chat":
        models.append("deepseek-chat")
    last_err = None
    for model in models:
        try:
            parsed = _chat(base, key, model, prompt, LLM_TIMEOUT, images=images)
            if parsed is None:
                last_err = "AI 二审输出无法解析"
                continue
            parsed["reason"] = format_reason(parsed.get("reason"))
            parsed["stage"] = int(first.get("stage") or 1) + 1
            parsed["model"] = "deepseek"
            parsed["firstResult"] = {k: first.get(k) for k in
                                     ("correct", "confidence", "correctAnswer", "reason")}
            return parsed
        except urllib.error.HTTPError as e:
            last_err = "LLM HTTP %s" % e.code
            if e.code in (401, 403):
                break          # 鉴权失败，换模型也没用
        except Exception as e:
            last_err = str(e)[:200]
    return {"error": "AI 二审失败：" + str(last_err)}


def build_prompt(subject, q, doubt, first=None, images_count=0):
    tname = {"choice": "单选题", "multi": "多选题", "open": "开放题/填空题"}.get(
        q.get("type"), q.get("type") or "题")
    opts = ""
    for o in q.get("options") or []:
        if isinstance(o, dict):
            opts += "\n%s. %s" % (o.get("letter", "?"), o.get("text", ""))
    img_note = ""
    if images_count:
        img_note = "【附图】本题随消息附有 %d 张图片，独立解题必须以读图为准；图中信息与文字描述冲突时，以图为准。" % images_count

    common_head = [
        "你是一位《%s》课程的资深教师，正在独立解答一道%s。你的唯一标准是数学与物理事实：既不迎合用户质疑，也不维护页面标注答案——三方（你的独立结论、用户质疑、页面答案）谁符合事实就支持谁，并明确声明你站在哪一方。" % (subject or "未知课程", tname),
        "",
        "【核验流程（务必按此顺序执行）】",
        "1. 盲解：只依据题面与附图独立解题，得出你自己的答案。此刻下方「待核验的页面材料」不存在——禁止参考、禁止回头对照；",
        "2. 质疑核验：若有用户质疑，把质疑的推理逐步拆开，逐条检验每一步（公式、符号约定、方向/正负、数量级、单位），明确指出哪几步成立、哪一步不成立及具体原因。质疑是对的就要干脆承认；",
        "3. 三方对照：现在才允许查看「待核验的页面材料」。将你的独立结论、用户质疑、页面标注答案三方对照：一致则增强置信；不一致则明确声明你支持谁、分歧出在哪一步。页面答案完全可能是错的，不要因为它是「标注答案」而倾向它；",
        "4. 若题目信息不足、图文歧义或答案不唯一，如实给 correct=null 并说明分歧点，不要强行选边。",
    ]

    info = [
        "",
        img_note or "（本题无附图）",
        "【题目信息】",
        "题目类型：" + tname,
        "题目来源：" + (q.get("source") or "未知"),
        "题干：" + (q.get("desc") or ""),
        ("选项：\n" + opts) if opts else "选项：无（填空/解答题）",
        "",
        "【用户质疑/补充观点】",
        (doubt if doubt else "（无）"),
        "",
        "【待核验的页面材料】（读到这一节之前，你必须已完成第 1 步盲解）",
        "页面标注答案：" + (q.get("answer") or ""),
        "页面自带解析（仅一方观点，未必正确）：" + (q.get("analysis") or "无"),
    ]

    if first:
        # 继续审核（二审、三审……）：模型始终为 DeepSeek
        fc = {True: "答案正确", False: "答案疑似有误", None: "无法确定"}.get(first.get("correct"), "未知")
        prev_stage = int(first.get("stage") or 1)
        prev_model = "tju-llm" if prev_stage <= 1 else "DeepSeek"
        prev = [
            "",
            "【上一轮审核结论】（第 %d 轮，由 %s 给出）" % (prev_stage, prev_model),
            "上一轮判定：" + fc + ("（置信度 %s）" % first.get("confidence") if first.get("confidence") is not None else ""),
            "上一轮给出的正确答案：" + (first.get("correctAnswer") or ""),
            "上一轮推理：" + (first.get("reason") or ""),
            "",
            "上一轮结论同样只是参考意见：它先于你完成，不因其已存在而更正确。请独立重做第 1 步盲解，再检验上一轮推理的每一步——发现它有错就直接推翻，不要为保持结论一致而迁就。",
        ]
        lines = common_head + prev + info
        out_spec = "\"reason\": \"第1条【盲解】你的独立推导与结论（禁止引用页面材料与上一轮结论）；第2条【质疑核验】逐条回应用户质疑（无质疑则直接进入第3条）；第3条【上一轮复核】指出上一轮推理每一步的对错；第4条【最终裁定】声明你支持的答案及理由。300字以内\""
    else:
        lines = common_head + info
        out_spec = "\"reason\": \"第1条【盲解】你的独立推导与结论（禁止引用页面材料）；第2条【质疑核验】逐条回应用户质疑（无质疑则直接进入第3条）；第3条【最终裁定】声明你支持的答案及理由。300字以内\""

    lines += [
        "",
        "【输出要求】",
        "只输出一个 JSON 对象，不要输出任何其他文字、解释或 Markdown 代码块：",
        "{\"correct\": 页面标注答案是否成立（true=页面答案正确 / false=页面答案有误 / null=无法确定，须与你的最终裁定一致）, \"confidence\": 0到1的小数, \"correctAnswer\": \"你认为正确的答案（无法确定时可为空字符串）\", " + out_spec + "}",
        "【格式要求】reason 用阿拉伯数字编号分步，每条独立一行；第 1 条必须是盲解（若与页面答案一致，第 3 条须注明「独立推导亦得此答案」）；公式一律用 $...$ 包裹 LaTeX（例如 $\\varphi_0=\\pi/3$、$A=10\\,\\mathrm{cm}$）；在 JSON 的 reason 字符串内换行写成 \\n 转义序列，禁止直接回车或写成一整段。",
    ]
    return "\n".join(lines)

def format_reason(text):
    """保底分行：模型若没按提示词分行，则按分句符拆行，保证页面解析不挤在一行。"""
    t = (text or "").strip()
    if not t:
        return t
    # 字面 \n（模型转义两次）还原为真实换行
    t = t.replace("\\n", "\n")
    # 没有真实换行时，按中英文分号/句号+空格拆行
    if "\n" not in t:
        t = re.sub(r"[；;]\s*", "；\n", t)
        t = re.sub(r"[。．.]\s+", "。\n", t)
    # 折叠多余空行
    t = re.sub(r"\n{3,}", "\n\n", t)
    return t.strip()


# 合法 JSON 转义字符
_JSON_ESCAPES = set('"\\/bfnrtu')


def _fix_json_newlines(s):
    """状态机：修复小模型输出的脏 JSON。
    1) 字符串内裸换行 -> \\n；
    2) 字符串内非法反斜杠转义（含单反斜杠 LaTeX，如 \\cos、\\pi）-> 双反斜杠；
    3) \\r 丢弃。
    """
    out = []
    in_str = False
    i = 0
    n = len(s)
    while i < n:
        ch = s[i]
        if not in_str:
            out.append(ch)
            if ch == '"':
                in_str = True
            i += 1
            continue
        # 字符串内
        if ch == '\\':
            nxt = s[i + 1] if i + 1 < n else ''
            # 合法 JSON 转义：\" \\ \/ \b \f \n \r \t \uXXXX
            # 仅 \\uXXXX（后 4 位十六进制）视为合法 unicode 转义；
            # b/f/n/r/t 不保留——它们与 \\frac/\\nabla/\\times/\\right/\\bar 冲突，
            # 一律双写（模型字面 \\n 双写后由 format_reason 还原为真换行）
            if nxt == 'u':
                hex4 = s[i + 2:i + 6]
                if len(hex4) == 4 and all(c in '0123456789abcdefABCDEF' for c in hex4):
                    out.append(ch)
                    out.append(nxt)
                    i += 2
                    continue
                out.append('\\\\')
                i += 1
                continue
            # 其余（LaTeX 命令、模型字面 \\n）一律双写：
            # json.loads 才能通过，解析出的字符串值还原为单反斜杠原样
            if nxt:
                out.append('\\\\')
                out.append(nxt)
                i += 2
                continue
            # 其他非法转义：补成双反斜杠
            out.append('\\\\')
            out.append(nxt)
            i += 2
            continue
        if ch == '"':
            out.append(ch)
            in_str = False
            i += 1
            continue
        if ch == '\n':
            out.append('\\n')
            i += 1
            continue
        if ch == '\r':
            i += 1
            continue
        if ch == '\t':
            out.append('\\t')
            i += 1
            continue
        out.append(ch)
        i += 1
    return ''.join(out)


def _repair_truncated(raw):
    """输出被 max_tokens 掐断时的兜底：从尾部找能闭合的截点，
    补齐未闭合的引号与括号后尝试解析。返回 dict 或 None。"""
    if not raw or not raw.lstrip().startswith('{'):
        return None
    # 从尾往头找候选截点：值字符串结束处（"," 或 换行+键名前）
    cuts = []
    for m in re.finditer(r'",(?=\s*\n?\s*")|",(?=\s*})|"(?=\s*\n?\s*})', raw):
        cuts.append(m.end())
    def closes(cand, keep_partial):
        # 数未转义引号，必要时补 "，再补闭括号
        in_str = False
        j = 0
        while j < len(cand):
            if cand[j] == '\\':
                j += 2
                continue
            if cand[j] == '"':
                in_str = not in_str
            j += 1
        if in_str:
            cand += '"'
            truncated_mid = True
        cand = cand.rstrip().rstrip(',')
        try:
            obj = json.loads(cand + '}')
        except Exception:
            return None
        if isinstance(obj, dict) and 'correct' in obj:
            return obj
        return None

    # 1) 优先：就地闭引号闭括号，保住（可能半截的）reason
    obj = closes(raw, keep_partial=True)
    if obj and obj.get('reason'):
        return obj
    # 2) 干净截点（丢不完整的 reason 值）
    best = obj
    for cut in reversed(cuts):
        o = closes(raw[:cut], keep_partial=False)
        if o:
            if o.get('reason'):
                return o
            if best is None:
                best = o
    return best


def parse_llm_json(content):
    if not content:
        return None
    text = content.strip()
    # 去代码围栏
    text = re.sub(r"^```[^\n]*\n", "", text)
    text = re.sub(r"\n```\s*$", "", text)
    # 找第一个 { 到配对的 }
    start = text.find("{")
    if start < 0:
        return None
    depth = 0
    for i in range(start, len(text)):
        ch = text[i]
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                break
    end = i
    raw = text[start:end + 1]
    try:
        obj = json.loads(raw)
    except Exception:
        # 容错链：脏转义修复 → 截断修复（max_tokens 掐断）
        try:
            obj = json.loads(_fix_json_newlines(raw))
        except Exception:
            # 两个候选都算（转义修复后/原文），优先带 reason 的
            cand_fixed = _repair_truncated(_fix_json_newlines(raw))
            cand_raw = _repair_truncated(raw)
            obj = None
            for c in (cand_fixed, cand_raw):
                if c and c.get('reason'):
                    obj = c
                    break
            if obj is None:
                obj = cand_fixed or cand_raw
            if obj is None:
                print("PARSE_FAIL:", repr(raw[:500]), flush=True)
                return None
    if not isinstance(obj, dict):
        return None
    out = {
        "correct": obj.get("correct"),
        "confidence": obj.get("confidence"),
        "correctAnswer": obj.get("correctAnswer") or "",
        "reason": obj.get("reason") or "",
    }
    if out["correct"] is not None and not isinstance(out["correct"], bool):
        # 兼容模型返回 1/0 而非 true/false
        if out["correct"] in (0, 1):
            out["correct"] = bool(out["correct"])
        elif isinstance(out["correct"], str):
            low = out["correct"].strip().lower()
            if low in ("true", "yes", "是"):
                out["correct"] = True
            elif low in ("false", "no", "否"):
                out["correct"] = False
            else:
                return None
        else:
            return None
    return out


# ─────────────────────────── HTTP ───────────────────────────
class Handler(SimpleHTTPRequestHandler):
    server_version = "ILoveTJU/1.0"

    def log_message(self, fmt, *args):
        print("%s %s" % (time.strftime("%H:%M:%S"), fmt % args), flush=True)

    def _read_body(self, cap):
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0:
            return b""
        if length > cap:
            self._json(413, {"error": "请求体过大"})
            return None
        return self.rfile.read(length)

    def _json(self, code, obj):
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _route(self):
        cfg = load_config()
        parsed = None
        try:
            import urllib.parse
            parsed = urllib.parse.urlparse(self.path)
        except Exception:
            parsed = None
        path = (parsed.path if parsed else self.path) or "/"
        query = urllib.parse.parse_qs(parsed.query) if parsed else {}

        if path == "/health":
            self._json(200, {"ok": True, "t": int(time.time())})
            return

        if path.startswith("/sync"):
            if not authed(self, cfg):
                self._json(401, {"error": "unauthorized"})
                return
            slot = (query.get("slot") or ["default"])[0]
            f = sync_file(slot)
            if self.command == "GET":
                obj = read_json(f, {"records": {}})
                self._json(200, {"records": obj.get("records", {})})
                return
            if self.command == "PUT":
                raw = self._read_body(MAX_SYNC_BODY)
                if raw is None:
                    return
                try:
                    inc = json.loads(raw.decode("utf-8"))
                except Exception:
                    self._json(400, {"error": "bad json"})
                    return
                with _lock:
                    cur = read_json(f, {"records": {}})
                    merged = merge_by_at(cur.get("records", {}),
                                         inc.get("records", {}) if isinstance(inc, dict) else {})
                    write_json(f, {"v": 1,
                                   "pushedAt": time.strftime("%Y-%m-%dT%H:%M:%S+08:00"),
                                   "records": merged})
                self._json(200, {"ok": True, "merged": len(merged)})
                return
            self._json(405, {"error": "method not allowed"})
            return

        if path.startswith("/api/annotations"):
            if not authed(self, cfg):
                self._json(401, {"error": "unauthorized"})
                return
            subject = (query.get("subject") or [""])[0]
            if not subject:
                self._json(400, {"error": "missing subject"})
                return
            f = annot_file(subject)
            if self.command == "GET":
                self._json(200, read_json(f, {"flags": {}, "notes": {}, "ai": {}, "corr": {}}))
                return
            if self.command == "PUT":
                raw = self._read_body(MAX_ANNOT_BODY)
                if raw is None:
                    return
                try:
                    inc = json.loads(raw.decode("utf-8"))
                except Exception:
                    self._json(400, {"error": "bad json"})
                    return
                with _lock:
                    cur = read_json(f, {"flags": {}, "notes": {}, "ai": {}, "corr": {}})
                    for sec in ("flags", "notes", "ai", "corr"):
                        cur[sec] = merge_by_at(cur.get(sec, {}),
                                               inc.get(sec, {}) if isinstance(inc, dict) else {})
                    write_json(f, cur)
                self._json(200, {"ok": True})
                return
            self._json(405, {"error": "method not allowed"})
            return

        if path == "/api/ai-check":
            if not authed(self, cfg):
                self._json(401, {"error": "unauthorized"})
                return
            raw = self._read_body(MAX_CHECK_BODY)
            if raw is None:
                return
            try:
                payload = json.loads(raw.decode("utf-8"))
            except Exception:
                self._json(400, {"error": "bad json"})
                return
            now = time.time()
            with _lock:
                if now - _ai_last[0] < 1.0:
                    self._json(429, {"error": "请求太频繁，请稍后再试"})
                    return
                _ai_last[0] = now
            result = ai_check(cfg, payload)
            self._json(200, result)
            return

        if self.command == "GET" and not path.startswith(("/api", "/sync")):
            super().do_GET()
            return
        self._json(404, {"error": "not found"})

    def list_directory(self, path):
        self.send_error(404, "Not found")
        return None

    def do_HEAD(self):
        if urlsplit(self.path).path.startswith(("/api", "/sync")):
            self.send_error(405, "Method not allowed")
            return
        super().do_HEAD()

    do_GET = do_PUT = do_POST = _route


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default=HOST, help="监听地址（默认 127.0.0.1）")
    parser.add_argument("--port", default=PORT, type=int, help="监听端口（默认 8901）")
    parser.add_argument("--web-dir", default=WEB_DIR, help="静态页面目录（默认 <root>/web）")
    args = parser.parse_args()
    os.makedirs(DATA_DIR, exist_ok=True)
    print("I Love TJU listening on %s:%d" % (args.host, args.port), flush=True)
    handler = partial(Handler, directory=os.path.abspath(args.web_dir))
    ThreadingHTTPServer((args.host, args.port), handler).serve_forever()


if __name__ == "__main__":
    main()
