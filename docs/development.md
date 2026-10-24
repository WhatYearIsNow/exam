# 原生开发

前端直接编辑 HTML、CSS 和 JavaScript，无 npm 构建步骤。后端和工具脚本使用 Python 标准库。

## 页面与题库

`web/exam/marx.html`、`physics.html`、`probability.html` 分别包含各科页面逻辑和 `<subject>-data` JSON 题库。`web/exam/index.html` 是 iframe 切换入口；`web/index.html` 是站点首页，内嵌了三科页面的 base64 副本。

修改科目页面后，在项目根目录重建首页：

```bash
python3 tools/build_frontend.py
python3 server.py
```

直接访问 `/exam/` 可调试科目裸页，访问 `/` 检查首页中的实际效果。首页自身的顶栏和增强功能直接在 `web/index.html` 中维护，重建脚本只更新其中的 `payload-*` 内容。

可选样式版本由 `python3 tools/build_premium.py` 生成到 `web/premium/`。这是生成目录，修改应落在科目源页面或构建脚本中。

两个构建脚本都支持 `--web-dir`、`--exam-dir`，也可设置 `ILOVETJU_WEB_DIR`、`ILOVETJU_EXAM_DIR`；默认路径分别为项目内 `web/` 和 `web/exam/`。`--help` 可查看参数。

## 数据来源

题库的事实来源是 `web/exam/*.html` 内嵌 JSON。需要更新离线快照时执行：

```bash
python3 tools/extract_bank.py
python3 tools/make_book.py --subject probability --inspect
```

PDF 工具优先读取 HTML；相应 HTML 不存在时才读取 `bank-data/`。HTML 格式错误会报错，不会悄悄改用旧快照。

`data/` 保存同步记录和个人注解，包含手动改题及 AI 采纳结果；它们与题库源文件分开保存。`bank-data-export/` 是历史修正导出，尚未作为本次整理的一部分合并。更新题库前应逐题核对修正来源。

## 配置与检查

本地启动与访问口令设置见根目录 README；服务端配置细节见 [部署说明](deployment.md)。`config.json`、`web/config.local.js` 和个人数据均已忽略，提交时使用不含密钥的示例文件。

```bash
python3 server.py --help
python3 -m unittest discover -s tests -v
```

集成测试在临时目录启动服务，检查静态页面、鉴权、同步合并、注解和环境配置，不调用真实 AI。前端配置行为测试通过 Node.js 执行真实增强层，需要在 PATH 中提供 Node.js；它不替代浏览器视觉和交互检查。页面修改还需在浏览器检查桌面和手机布局、公式、切题及作答流程。

GitHub Actions 在推送和 PR 时运行上述测试、三科 `--inspect` 和离线包生成。无需为运行网站安装 npm 依赖。

## 本次目录整理

站点文件已归入 `web/`，Android 源码归入 `android/`，离线包所需组件归入 `vendor/`。旧离线包、备份和迁移档案保存在忽略的 `.local/` 下。原站点路径和 Android 临时路径保留了兼容符号链接，后续开发使用项目内路径。
