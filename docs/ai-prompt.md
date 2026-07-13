# AI 制题提示词

把下面的提示词发给任意 AI 助手，再附上你的题库文件（docx/pdf/图片/文本均可），AI 会自动生成题库 JS 文件。

---

## 方式一：在 Claude Code 中制题（推荐，支持 docx/pdf 直接读取）

把题库文件（.docx / .pdf / .txt）放到项目目录下，然后对 Claude Code 说：

```
请读取 题库.docx（或 题库.pdf），按照 banks/_template.js 的格式，
生成 banks/新题库名.js。

科目名称：XXX
版本：XXX
```

AI 会直接读取 Word/PDF 文件，理解题目结构，自动生成符合规范的题库文件。

### 支持的原始格式

| 格式 | 能否直接读取 | 说明 |
|------|------------|------|
| .docx | 能 | Claude Code 原生支持 |
| .pdf | 能 | Claude Code 原生支持 |
| .txt | 能 | 直接读取 |
| 图片（截图/扫描） | 能 | Claude Code 可 OCR 识别 |
| 网页内容 | 能 | 直接抓取 |

---

## 方式二：使用 AI 聊天助手（ChatGPT / DeepSeek / 千问等）

把下面这段提示词 + 你的题目内容发给 AI 聊天助手。题目内容可以直接粘贴文本，也可以上传文件（ChatGPT 和千问均支持文件上传）。

### 提示词

```
你是一个题库生成助手。请根据我提供的题目，生成一个符合 TJU-Quiz-Hub 格式的题库 JS 文件。

项目仓库（含模板和格式说明）：https://github.com/WhatYearIsNow/TJU-Quiz-Hub

## 输出格式

生成完整的 .js 文件，包含以下变量：

// 1. 元信息
const QUIZ_META = {
    subject: "科目名称",
    version: "版本号",
    totalQuestions: 题目总数,
    campusName: "北洋校歌"
};

// 2. 题目数据
const questionData = [
    {
        title: "【单项选择题001】",
        desc: "题目标题（　　）",
        code: "",
        options: ["A. ...", "B. ...", "C. ...", "D. ..."],
        answer: "A",          // 单选一个字母，多选多个字母如"ABC"
        analysis: "解析"
    },
    // ...更多题目
];

// 3. 章节分配（与questionData等长）
const QUESTION_CHAPS = ["第一章", "第一章", ...];

// 4. 章节名称映射
const CAT_MAP = { "第一章": "第一章", ... };

// 5. 校园标语
const SONG_LINES = ["标语1", "标语2", ...];

## 关键规则
- title 中的数字用于生成题目 ID，确保递增唯一
- desc 中如有填空，用（　　）表示
- options 始终为 4 个，带 A-D 字母前缀
- 题目是纯文本时 code 设为 ""
- 如果原题没有解析，analysis 至少写一句话简要说明

## 我的题目

[在这里粘贴题目文字，或上传文件]

## 参数
- 科目名称：
- 版本：
- 文件名建议：banks/xxx.js
```

---

## 方式三：用 Python 批量转换结构化数据

如果你已经有结构化的题库数据（Excel 导出的 CSV、JSON 等），可以用以下脚本批量转换：

```python
import json

# 你的原始数据（替换为实际数据）
raw = [
    {"q": "题目1", "opts": ["A. a", "B. b", "C. c", "D. d"], "ans": "A", "exp": "解析1"},
    # ...
]

# 生成 JS 文件
lines = []
lines.append('const QUIZ_META = { subject: "科目名", version: "v1", totalQuestions: %d, campusName: "北洋校歌" };' % len(raw))
lines.append('')
lines.append('const questionData = [')

for i, r in enumerate(raw, 1):
    lines.append('    {')
    lines.append('        title: "【单项选择题%03d】",' % i)
    lines.append('        desc: "%s",' % r["q"].replace('"', '\\"'))
    lines.append('        code: "",')
    lines.append('        options: %s,' % json.dumps(r["opts"], ensure_ascii=False))
    lines.append('        answer: "%s",' % r["ans"])
    lines.append('        analysis: "%s"' % r["exp"].replace('"', '\\"'))
    lines.append('    },')

lines.append('];')
lines.append('')
lines.append('const QUESTION_CHAPS = %s;' % json.dumps(["第一章"] * len(raw), ensure_ascii=False))
lines.append('const CAT_MAP = { "第一章": "第一章" };')
lines.append('const SONG_LINES = ["花堤蔼蔼，北运滔滔"];')

with open('banks/output.js', 'w', encoding='utf-8') as f:
    f.write('\n'.join(lines))

print("生成完成！")
```

---

## 验证

生成题库后，在浏览器中打开：

```
index.html?bank=你的题库名
```

检查题目显示、选项、答案、解析是否正确。
