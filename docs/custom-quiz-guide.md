# 自定义题库指南

只需 4 步，即可将系统迁移到任意科目。

## 第一步：创建题库文件

在 `banks/` 目录下新建一个 `.js` 文件，如 `banks/math-linear-algebra.js`。

## 第二步：填写 QUIZ_META

```javascript
const QUIZ_META = {
    subject: "线性代数",       // 你的科目名
    version: "期末复习版",      // 版本标识
    totalQuestions: 50,        // 题目总数
    campusName: "北洋校歌"      // 可自定义文化标语
};
```

## 第三步：编写题目数据

参考 [data-format.md](./data-format.md) 的完整格式说明。

关键要点：
- `title` 中的数字会被提取为题目 ID，确保唯一性
- `answer` 单选用单个字母 `"A"`，多选用多个字母 `"AB"`
- `options` 始终包含 4 个选项
- `code` 没有代码时设为空字符串 `""`

### 快速生成题库

如果你有现成的题库（Word/Excel/CSV），可以用以下 Python 脚本快速转换：

```python
import json

# 假设你的题库是这样的列表
raw_questions = [
    {
        "id": 1,
        "question": "矩阵A可逆的充要条件是？",
        "options": ["A. |A|≠0", "B. |A|=0", "C. A=0", "D. A=I"],
        "answer": "A",
        "analysis": "矩阵可逆当且仅当行列式不为零。"
    },
    # ...
]

# 生成 questionData
questions = []
for q in raw_questions:
    questions.append({
        "title": f"【单项选择题{q['id']:03d}】",
        "desc": q["question"],
        "code": "",
        "options": q["options"],
        "answer": q["answer"],
        "analysis": q["analysis"]
    })

# 写入 JS 文件
with open("banks/my-subject.js", "w", encoding="utf-8") as f:
    f.write("const QUIZ_META = {\n")
    f.write('    subject: "我的科目",\n')
    f.write('    version: "v1.0",\n')
    f.write(f'    totalQuestions: {len(questions)},\n')
    f.write('    campusName: "北洋校歌"\n')
    f.write("};\n\n")
    f.write("const questionData = [\n")
    for q in questions:
        f.write("    {\n")
        f.write(f'        title: "{q["title"]}",\n')
        f.write(f'        desc: "{q["desc"]}",\n')
        f.write(f'        code: "{q["code"]}",\n')
        f.write(f'        options: {json.dumps(q["options"], ensure_ascii=False)},\n')
        f.write(f'        answer: "{q["answer"]}",\n')
        f.write(f'        analysis: "{q["analysis"]}"\n')
        f.write("    },\n")
    f.write("];\n\n")
    f.write("const QUESTION_CHAPS = [\n")
    for q in questions:
        f.write('    "第一章",\n')  # 根据实际章节填写
    f.write("];\n\n")
    f.write("const CAT_MAP = {\n")
    f.write('    "第一章": "第一章"\n')
    f.write("};\n\n")
    f.write('const SONG_LINES = ["自定义标语"];\n')

print("Done!")
```

## 第四步：使用题库

### 方式一：URL 参数

```
index.html?bank=math-linear-algebra
```

### 方式二：设为默认

修改 `index.html` 中 `banks/history-264.js` 为你的题库路径。

### 方式三：直接双击

复制 `index.html` 和新题库文件到同一目录，修改 `index.html` 中的默认题库路径即可。

## 章节分配

`QUESTION_CHAPS` 数组长度必须与 `questionData` 完全一致，每个元素是该题所属的章节名称。

系统会自动从数据中提取章节列表，用于：
- 章节检测模式的章节选择页
- 题目显示时的章节标签
- 模拟考试的按章节比例抽题

## 多科目整合

你可以将多个题库文件放在 `banks/` 目录下，通过 URL 参数切换：

| URL | 科目 |
|-----|------|
| `index.html?bank=history-264` | 中国近现代史纲要（264题） |
| `index.html?bank=history-178` | 中国近现代史纲要（178题） |
| `index.html?bank=cs-python-100` | 计算机软件技术基础（Python） |
| `index.html?bank=your-subject` | 你的自定义题库 |
