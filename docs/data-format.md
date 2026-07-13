# 题库数据格式说明

每个题库文件（`banks/*.js`）需要定义以下变量。

## QUIZ_META — 题库元信息

```javascript
const QUIZ_META = {
    subject: "中国近现代史纲要",   // 科目名称
    version: "25262版",           // 版本号
    totalQuestions: 264,          // 题目总数
    campusName: "北洋校歌"         // 校歌/文化标语
};
```

## questionData — 题目数组

```javascript
const questionData = [
    {
        title: "【单项选择题001】",  // 题目标题（需包含数字编号）
        desc: "题目描述文本",         // 题目内容，填空处用（　　）表示
        code: "",                   // 代码块（可选），无代码时设为 ""
        options: [                  // 选项数组，4个字符串
            "A. 选项A文本",
            "B. 选项B文本",
            "C. 选项C文本",
            "D. 选项D文本"
        ],
        answer: "A",                // 正确答案：单选为单个字母，多选为多个字母如 "ABC"
        analysis: "解析文本"          // 答案解析
    },
    // ... 更多题目
];
```

### 字段说明

| 字段 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `title` | string | 是 | 题目标题，必须包含数字编号，系统通过正则提取编号作为题目 ID |
| `desc` | string | 是 | 题目内容文本，填空处建议用（　　）表示 |
| `code` | string | 是 | 代码块内容，无代码时设为空字符串 `""` |
| `options` | string[] | 是 | 4 个选项，格式为 `"字母. 文本"` |
| `answer` | string | 是 | 正确答案，单选如 `"A"`，多选如 `"ABC"` |
| `analysis` | string | 是 | 答案解析，显示在作答后 |

## QUESTION_CHAPS — 章节分配

数组长度必须与 `questionData` 一致，每个元素为该题所属章节名称。

```javascript
const QUESTION_CHAPS = [
    "导言",
    "导言",
    "01 进入近代后中华民族的磨难与抗争",
    // ... 与 questionData 一一对应
];
```

## CAT_MAP — 章节名称映射

用于显示时的章节名称格式化。

```javascript
const CAT_MAP = {
    "导言": "导言",
    "01 进入近代后中华民族的磨难与抗争": "01 进入近代后中华民族的磨难与抗争",
    // ...
};
```

## SONG_LINES — 校园文化标语

在准备页面底部随机显示。

```javascript
const SONG_LINES = [
    "花堤蔼蔼，北运滔滔",
    "巍巍学府北洋高",
    // ...
];
```

## 自动检测

系统会自动检测题库是否包含多选题（`answer.length > 1`），并据此调整界面：
- 有多选题：显示三种模式（章节检测、综合训练、模拟考试）
- 无多选题：仅显示章节检测和综合训练两种模式
