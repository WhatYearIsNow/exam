# PROJECT STATUS · 归档快照

> ⚠️ **本项目已于 2026-09-30 暂停更新，2026-10-01 归档整理**。暂停 ≠ 废弃：代码、题库数据、部署配置全部保留，可随时恢复。
> **归档位置**：`D:\Documents\AI-System\Projects\Archive\TJU-Quiz-Hub`
> **去向**：功能已被部署在 **KVM 虚拟机上的 I love TJU** 站点取代（2026-10-01 补记）。本仓库降级为历史参考实现与题库数据源。
> 接手顺序：先读完本文档 → 再看 README.md → 细节按下文「恢复开发指南」查阅。

## 去向与继任（2026-10-01 补记）

- 继任者：**I love TJU**，部署在用户自有的 KVM 虚拟机上；访问地址与源码位置未记录在本地，**待补**（问到后回填此处）。
- 名称血缘：I love TJU 最早是 2026-04 的单文件 Python 题库（本仓库 `archive/I love TJU.html`，知识库条目「[[北洋答题系统]]」）；KVM 上的现役站点沿用此名，与本仓库代码的具体承继关系待确认。
- 对接手者的含义：默认不要在本仓库上继续开发，刷题功能看 KVM 上的 I love TJU。本仓库的留存价值：① physics/probability 题库 JSON 与 source 源文件可直接复用；② 构建脚本与 Playwright 验证流程；③ 云同步 Worker 方案。

## 一句话定位

天津大学多科目客观题刷题站：章节练习 / 整卷训练 / 模拟考试 / 错题回顾 / 成绩追踪。纯前端（HTML + 原生 JS + localStorage），本地 KaTeX 公式排版，零外网依赖；可选 Cloudflare Worker 做多设备作答记录云同步。与天津大学官方无隶属关系。

## 现状速览

| 模块 | 位置 | 状态 |
| --- | --- | --- |
| 托管站（Vinext/React 首页 + quiz 页） | `app/` `worker/` `public/` `banks/` | ✅ 已提交（82c1489），历史主线 |
| 独立刷题页（旧单页） | 根 `index.html` | ❌ 已删除（被两个自包含子站取代） |
| **大学物理刷题站** | `physics-quiz/` | ⚠️ 数据完备（264 题），**入口 index.html 缺失（P0）** |
| **概率论刷题站** | `probability-quiz/` | ✅ 完整可用（406 题） |
| 构建 / 验证脚本 | `scripts/` | ✅ 归档时入库 |
| 云同步 Worker | `physics-quiz/sync/` | ✅ 代码齐备，是否已部署待确认 |
| CI | `.github/workflows/ci.yml` | ✅ `npm run check` + Flask 语法检查 |
| 可选 Flask 局域网统计示例 | `examples/flask-server/` | ✅ 历史功能 |
| 测试截图（物理站全流程） | `docs/screenshots/`（12 张，归档时移入） | ✅ |

## 两条产品线

1. **主线（历史，已提交）**：Vinext/React + Cloudflare Worker 托管站，题库在 `banks/`（史纲 264/178 题 + 计算机软件基础 Python 100 题），构建产物同步到 `public/`。根目录 `index.html` 曾是「独立刷题页唯一来源」，2026-08 起被下面两个子站取代并删除。
2. **新子站（2026-08 开发，归档时入库）**：每个子站完全自包含（入口 HTML + 题库 JSON + vendor/katex + images/），整个目录拷走即可离线使用，任意静态服务器可跑。

### physics-quiz/（大学物理下册，第 9–15 章）

- 264 题，`physics-data.json`（version 3，构建于 2026-08-24）；题目配图 55 张（`images/`，sha256 文件名）
- 源：`source/` 11 份历年卷 MD（15161–25261 学年学期）+ `chapter-notes.md`（必备知识）
- 数据管线：`node scripts/build-physics.mjs` 把 `source/*.md` 解析为 `physics-data.json`（支持 `--only 25261`；源格式规范见脚本头部注释）
- 回归验证：`python scripts/verify-physics.py [url]`（Playwright 无头截图 + 公式残留扫描，默认 `http://localhost:8766/index.html`，输出到 `physics-quiz/verify/`）
- ⚠️ **P0 遗留：`physics-quiz/index.html` 入口页在工作区、git 历史、stash、构建产物中均不存在**。verify 脚本与 `docs/screenshots/` 截图证明它曾于 2026-08-25 前后存在并测过。恢复途径：① 查本机回收站 / 本地备份；② 以 `probability-quiz/index.html` 为模板改造（两站同源）。
- 云同步：`sync/`（Cloudflare Workers + KV，name=`physics-quiz-sync`）。部署步骤见 `sync/README.md`；密钥走 `wrangler secret put SYNC_TOKEN`，仓库内无硬编码密钥（已扫描确认）。probability 站的 `index.html` 内含同样 sync 逻辑，可复用同一 Worker。

### probability-quiz/（概率论与数理统计）

- 406 题，`probability-data.json`（version 1，构建于 2026-08-29）；入口 `index.html`（561KB 单文件，含全部 UI 与逻辑，自带云同步设置入口）
- 源：`source/` 23 份 MD（13 份学期卷 18191–24252 + 10 份模拟卷）+ `chapter-notes.md`
- ⚠️ 待确认：概率题库 MD→JSON 的构建脚本未随库保存（`scripts/` 只有 physics 的），重建需仿照 `build-physics.mjs` 补写或手工维护 JSON

## 本地运行 / 构建 / 验证

```bash
# 主线托管站（Node >= 22.13，见 .nvmrc）
npm ci && npm run dev          # 本地开发
npm run check                  # sync:check + lint + typecheck + test + build

# physics-quiz / probability-quiz（零依赖，任意静态服务器）
python -m http.server 8766 -d physics-quiz       # verify 脚本默认地址
python -m http.server 8767 -d probability-quiz
node scripts/build-physics.mjs                   # 改题后重建 physics-data.json
python scripts/verify-physics.py                 # Playwright 回归验证
```

## 部署

- 主线：CI 只做检查不部署；托管走 `.openai/hosting.json` + `worker/`（Cloudflare 兼容构建），细节见 `docs/deploy.md`
- 云同步 Worker：`cd physics-quiz/sync && npx wrangler deploy`（一次性部署，详见其 README）
- 未发现 GitHub Pages 配置

## Git 现状（归档时点）

- 远端：<https://github.com/WhatYearIsNow/TJU-Quiz-Hub.git>
- 归档前：分支 `agent/publish-2026-08-13` 领先 master 1 个提交（82c1489「统一题库站点构建与部署流程」），工作区有大量未跟踪内容
- 归档整理提交：① 子站 / 脚本 / 截图入库 + 删除根 `index.html`；② 本文档 + README 状态横幅
- **master 已快进到最新**，工作区干净；`agent/publish-2026-08-13` 分支保留
- ⚠️ 本地领先 origin/master 数个提交，**未 push**（push 可能触发线上动作，留待恢复时决策）

## 遗留问题清单（恢复时从这里开始）

1. **P0**：physics-quiz/index.html 入口页丢失 → 恢复途径见上文
2. 概率题库构建脚本缺失：改 `source/*.md` 后无法自动重建 `probability-data.json`
3. README 的「项目结构 / 可用题库」章节未覆盖两个新子站（已加横幅指路本文档）
4. 双轨整合未做：新子站与主线（`banks/`、`public/quiz.html`、`worker/`）各自独立，未统一
5. `outputs/tju-quiz-hub-site.tgz`（2026-07-26）为旧打包产物，已 gitignore，可删

## 恢复开发指南（按阅读顺序）

1. 本文档 → 2. README.md → 3. `docs/deploy.md`（主线部署）→ 4. `physics-quiz/sync/README.md`（云同步）→ 5. `scripts/build-physics.mjs` 头部注释（题库源格式规范）

常见任务入口：

| 任务 | 做法 |
| --- | --- |
| 物理加题 | 编辑 `physics-quiz/source/<卷>.md` → `node scripts/build-physics.mjs` → `python scripts/verify-physics.py` |
| 概率加题 | 直接维护 `probability-quiz/probability-data.json`（或补写构建脚本后改 `source/*.md`） |
| 改概率站样式/逻辑 | 直接改 `probability-quiz/index.html`（单文件应用） |
| 云同步 | `physics-quiz/sync/`：wrangler login → deploy → secret put SYNC_TOKEN |
| 主线站改版 | `app/` `worker/`，提交前 `npm run check` |
