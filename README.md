# TJU Quiz Hub

[![CI](https://github.com/WhatYearIsNow/TJU-Quiz-Hub/actions/workflows/ci.yml/badge.svg)](https://github.com/WhatYearIsNow/TJU-Quiz-Hub/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

天津大学多科目客观题刷题站，支持章节练习、综合训练、模拟考试、错题回顾和成绩追踪。

项目包含两个互补入口：

- 托管站点：Vinext、React 和 Cloudflare Worker 构建的课程选择首页。
- 独立刷题页：纯 HTML/CSS/JavaScript，直接打开根目录 `index.html` 即可使用。

默认情况下，答题记录仅保存在当前浏览器的 `localStorage` 中。项目与天津大学官方无隶属关系。

## 功能

- 章节检测、综合训练和模拟考试
- 单选题与多选题
- 错题自动收录和集中重练
- 历史成绩与进度保存
- 手机、平板和桌面端响应式布局
- 无需注册，独立版无需安装依赖
- 可选的 Flask 局域网统计示例

## 快速使用

### 直接刷题

1. 下载或克隆仓库。
2. 双击根目录的 `index.html`。
3. 输入姓名并选择练习模式。

也可以通过查询参数直接切换题库：

```text
index.html?bank=history-264
index.html?bank=history-178
index.html?bank=cs-python-100
```

### 本地开发

需要 Node.js 22.13 或更高版本。

```bash
npm ci
npm run dev
```

常用命令：

| 命令 | 用途 |
| --- | --- |
| `npm run dev` | 启动本地开发服务器 |
| `npm run build` | 生成生产构建 |
| `npm run lint` | 检查代码规范 |
| `npm run typecheck` | 检查 TypeScript 类型 |
| `npm test` | 运行题库与静态资源测试 |
| `npm run check` | 运行提交前的完整检查 |

## 可用题库

| 题库文件 | 科目 | 题数 | 题型 |
| --- | --- | ---: | --- |
| `banks/history-264.js` | 中国近现代史纲要 | 264 | 单选、多选 |
| `banks/history-178.js` | 中国近现代史纲要 | 178 | 单选、多选 |
| `banks/cs-python-100.js` | 计算机软件技术基础（Python） | 100 | 单选 |

创建新题库时，请参考[题库数据格式](docs/data-format.md)和[自定义题库指南](docs/custom-quiz-guide.md)。提交前可运行 `npm test` 检查题目结构和答案。

## 项目结构

```text
TJU-Quiz-Hub/
├── .github/                 # CI、Issue 与 PR 模板
├── .openai/                 # Sites 托管配置
├── app/                     # Vinext/React 托管首页
├── archive/                 # 历史原始资料
├── banks/                   # 题库唯一来源
├── docs/                    # 数据格式和部署文档
├── examples/flask-server/   # 可选的局域网统计示例
├── public/                  # 托管静态资源
├── tests/                   # Node.js 测试
├── tooling/                 # 构建与资源同步工具
├── worker/                  # Cloudflare Worker 入口
├── index.html               # 独立刷题页的唯一来源
├── package.json
└── vite.config.ts
```

`public/quiz.html`、`public/banks/` 和 `public/LICENSE.txt` 由根目录对应文件同步生成，请勿直接编辑。`npm run dev` 和 `npm run build` 会自动同步；`npm run sync:check` 可检查是否一致。

## 部署

生产构建输出到 `dist/`：

```bash
npm ci
npm run build
```

当前托管站点使用 `.openai/hosting.json` 与 Cloudflare Worker 兼容构建。其他部署方式及可选 Flask 示例见[部署说明](docs/deploy.md)。

## 贡献

欢迎修正题目、补充题库或改进功能。提交前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)，并确保 `npm run check` 通过。

报告漏洞或隐私问题时，请遵循 [SECURITY.md](SECURITY.md)，不要在公开 Issue 中披露敏感信息。

## 许可与题库内容

项目代码采用 [MIT License](LICENSE)。题库内容可能整理自课程资料，其著作权归原权利人所有，仅供学习交流；如需更正来源、授权信息或申请移除，请通过仓库维护者联系方式反馈。
