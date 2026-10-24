# 项目沿革

`exam` 是 [WhatYearIsNow/TJU-Quiz-Hub](https://github.com/WhatYearIsNow/TJU-Quiz-Hub) 的后续开发仓库。2026 年 10 月 24 日迁入新仓库时，保留原始提交对象，并在旧主线的基础上提交当前原生应用。旧仓库继续保留。

## 版本关系

| 阶段 | 原始提交 | 新仓库中的入口 |
| --- | --- | --- |
| TJU-Quiz-Hub 初始框架，2026-07-13 | `c1d0e5f956ad14308d7f3b6fa2eebc4faf66256f` | 原始主线历史的首个提交 |
| TJU-Quiz-Hub 原主线最后状态，2026-07-13 | `451d3a5e416adc4859ae3bb488116d4695afe64e` | 标签 [`legacy-tju-quiz-hub`](https://github.com/WhatYearIsNow/exam/tree/legacy-tju-quiz-hub)，分支 `legacy/master` |
| 原网站开发分支最后状态，2026-08-13 | `82c14894a14028cf8c0222b89436a25c32ac2de5` | 分支 [`legacy/agent/publish-2026-08-13`](https://github.com/WhatYearIsNow/exam/tree/legacy/agent/publish-2026-08-13) |
| 旧仓库 `master` 的后续提交，2026-07-26 至 2026-10-01 | `c27c9507f6ca143bb5bb19e6fa09f6fcea073bc6` | 经合并提交 [`1f16508`](https://github.com/WhatYearIsNow/exam/commit/1f16508) 并入 `main` |
| exam 首个延续版本，2026-10-24 | 接续旧主线的新提交 | `main` 分支与 [`exam-initial`](https://github.com/WhatYearIsNow/exam/tree/exam-initial) 标签 |

旧主线的 5 条提交保持原 SHA、作者和时间，并作为 `main` 的祖先。原网站开发分支包含额外 2 条提交，通过 `legacy/` 下的分支保留。2026-10-24 的合并提交 [`1f16508`](https://github.com/WhatYearIsNow/exam/commit/1f16508) 又把旧仓库 `master` 在 `451d3a5` 之后的 6 条提交（`4da6cf1` 至 `c27c950`，含站点构建流程与 2026-10-01 的子站归档快照、去向说明）并入 `main` 的提交图；合并以 exam 的内容为准，不改变任何文件。至此 TJU-Quiz-Hub 的全部原始提交都能从 `main` 追溯，`legacy/` 分支与 `legacy-tju-quiz-hub` 标签继续保留。历史没有压缩或重新生成，旧版文件、文档与许可可直接从对应引用中取得。

## 从旧版到当前版本

TJU-Quiz-Hub 的主线提供纯前端刷题框架、外置题库和 Flask 参考方案，网站开发分支另外保留了其站点构建探索。当前 `exam` 以原生 HTML/CSS/JavaScript、Python 标准库后端和原生 Java Android 壳继续开发。

当前工作区维护 `web/` 页面、`server.py`、`android/` 和部署说明，并提供题库数据导出。迁入的 PDF 工具作为历史交接资料保留，完整题册生产归 `zhenti-pipeline-v2`。旧版 Flask 参考方案及网站框架保留在历史版本中，当前运行方式以根目录 README 为准。

根目录 MIT 许可证同时保留 TJU-Quiz-Hub 的原版权声明。题库材料及其他第三方组件的说明见 [第三方与内容说明](../THIRD_PARTY_NOTICES.md)。

## 查看历史

```bash
# 查看所有保留的分支和提交关系
git log --graph --oneline --all

# 查看旧版 README，无需切换当前工作区
git show legacy-tju-quiz-hub:README.md

# 比较旧主线与当前版本
git diff --stat legacy-tju-quiz-hub..main
```

需要运行旧版时，使用独立克隆或 worktree，避免在当前部署目录切换历史版本。
