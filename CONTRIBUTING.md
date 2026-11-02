# 参与开发

保持原生 HTML/CSS/JavaScript、Python 标准库后端和 Java Android 壳。项目职责、题库来源和数据交接规则见 `AGENTS.md` 与 `docs/data-handoff.md`。

## 开发流程

一个功能或修复使用一个短期分支，例如 `fix/offline-note-sync`。提交应围绕完整且可核对的改动。推送分支并创建 PR，说明问题、改动后的行为与验证结果；通过 CI 后再合并。`main` 保存可发布代码，实际线上版本以发布记录为准。

KVM19 上直接打开 `/opt/exam` 开发，使用独立预览：

```bash
python3 tools/dev.py serve
```

开发环境使用自己的端口、口令和测试数据，默认不配置真实模型。请勿复制正式个人数据或密钥来测试，也不要在 `.local/releases/` 中修改代码。预览和源码重建流程见 [开发说明](docs/development.md)。

## 验证与提交

修改学科页面后，运行 `python3 tools/build_frontend.py` 更新首页 payload；运行 `python3 -m unittest discover -s tests -v`，并按改动检查浏览器或 Android 行为。Node.js 用于前端行为测试，不是网站运行依赖。

PR 不包含真实配置、个人作答、未经确认的私人修正、签名凭证或生成物。不要用 AI 结果覆盖已确认的人工修正。题库快照与导出按需显式更新，不顺带导出个人注解。

合并不自动上线。部署者选定批准的提交，通过 `tools/release.py` 构建、激活与校验；步骤和回滚方法见 [部署说明](docs/deployment.md#发布与回滚)。
