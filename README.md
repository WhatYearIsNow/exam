# TJU-Quiz-Hub

天津大学（北洋大学）多科目客观题刷题系统 —— 一个纯前端、零依赖、开箱即用的刷题框架。

> 天大学子，一键迁移到任意科目。

## 特色

- **零依赖** — 纯 HTML/CSS/JS，无需 Node.js、无需构建工具，双击即用
- **单文件框架** — 核心框架 `index.html` 不到 50KB
- **题库外置** — 题库为独立 `.js` 文件，替换即可切换科目
- **三种刷题模式**
  - 章节检测 — 逐章突破
  - 综合训练 — 全部题目随机打乱
  - 模拟考试 — 按章节比例抽题组卷（单选+多选）
- **智能错题本** — 错题自动收录，支持重练和一键清空
- **成绩追踪** — 历史记录 + SVG 成绩曲线
- **断点续答** — 退出自动保存，回来继续作答
- **响应式设计** — 手机/平板/电脑均可使用
- **支持单选+多选** — 自动检测题库类型，适配 UI

## 快速开始

1. 下载或克隆本仓库
2. 双击打开 `index.html`
3. 输入姓名，开始刷题

### 切换科目

支持通过 URL 参数切换题库：

```
index.html?bank=history-264    # 中国近现代史纲要（264题，默认）
index.html?bank=history-178    # 中国近现代史纲要（178题）
index.html?bank=cs-python-100  # 计算机软件技术基础（Python）
```

## 可用题库

| 文件 | 科目 | 题数 | 题型 |
|------|------|------|------|
| `banks/history-264.js` | 中国近现代史纲要 | 264 | 单选 + 多选 |
| `banks/history-178.js` | 中国近现代史纲要 | 178 | 单选 + 多选 |
| `banks/cs-python-100.js` | 计算机软件技术基础 | 100 | 单选 |

## 自定义题库

只需创建 `banks/your-subject.js`，定义题目数据即可。详见：

- [题库数据格式说明](docs/data-format.md)
- [自定义题库指南](docs/custom-quiz-guide.md)

核心步骤：
1. 复制 `banks/history-264.js` 为你的题库文件
2. 修改 `QUIZ_META`（科目名、版本号）
3. 替换 `questionData`（题目数组）
4. 更新 `QUESTION_CHAPS`（章节分配）
5. 通过 `?bank=your-subject` 使用

## 项目结构

```
TJU-Quiz-Hub/
├── index.html                   # 核心刷题框架
├── banks/                       # 题库目录
│   ├── history-264.js           # 中国近现代史纲要（264题）
│   ├── history-178.js           # 中国近现代史纲要（178题）
│   └── cs-python-100.js         # 计算机软件技术基础（Python）
├── docs/
│   ├── data-format.md           # 题库数据格式说明
│   └── custom-quiz-guide.md     # 自定义题库指南
├── archive/                     # 原始完整版 HTML（含内嵌题库，可独立使用）
│   ├── 25262版中国近现代史纲要选择题刷题系统.html
│   ├── 史纲选择题(178题).html
│   └── I love TJU.html
├── .gitignore
└── LICENSE
```

## 浏览器兼容性

支持所有现代浏览器（Chrome、Firefox、Safari、Edge）。使用 `localStorage` 存储数据，清除浏览器数据会导致记录丢失。

## License

MIT — 自由使用、修改、分发。欢迎贡献新题库！

## 贡献指南

欢迎提交 Pull Request 添加新科目题库，或将本框架迁移到其他高校的课程。

提交题库时，请确保：
- 题库文件放在 `banks/` 目录
- 包含完整的 `QUIZ_META`、`questionData`、`QUESTION_CHAPS`、`CAT_MAP`、`SONG_LINES`
- 题目内容准确，答案正确
