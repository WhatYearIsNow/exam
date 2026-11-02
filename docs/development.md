# 原生开发

前端直接编辑 HTML、CSS 和 JavaScript，无 npm 构建步骤。后端和工具脚本使用 Python 标准库。

本项目维护网页题库、答题功能和经过确认的题目修正，并按需提供题库数据。PDF 题册及其生成流程属于 `zhenti-pipeline-v2`，相关文件的迁入检查不构成 `exam` 的开发待办。

## 页面与题库

`web/exam/marx.html`、`physics.html`、`probability.html` 分别包含各科页面逻辑和 `<subject>-data` JSON 题库。`web/exam/index.html` 是 iframe 切换入口；`web/index.html` 是站点首页，内嵌了三科页面的 base64 副本。

修改科目页面后，在项目根目录重建首页：

```bash
python3 tools/build_frontend.py
python3 tools/dev.py serve
```

重建脚本同时从各科题库 JSON 计算首页的题量标签，避免页面文案与实际题数不一致。

开发预览监听 `127.0.0.1:8902`。`tools/dev.py` 将工作区页面复制到 `.local/dev/site-*`，在那里重建 payload，再通过 `.local/dev/web` 提供页面，不改动正式页面。启动时清除继承的 `ILOVETJU_*` 环境变量，使用 `.local/dev/config.json`、`.local/dev/data/` 和单独生成的应用访问令牌；默认模型密钥为空。脚本拒绝复用当前正式配置中的口令或模型密钥。刷新预览副本时保留已有测试记录；源码修改后重新启动 `serve`，或在服务运行期间执行 `python3 tools/dev.py prepare`。

可在 Windows 编辑器中通过 SSH 打开 `/opt/exam`，把服务器的 8902 端口转发到本机；用独立浏览器配置或该端口查看预览。端口属于浏览器 origin 的一部分，开发站点的本地作答与正式域名独立。默认开发服务器只监听回环地址。

服务器也提供可手动启动的 `i-love-tju-dev.service`；它与正式服务分开，未启用开机启动。使用 `systemctl restart i-love-tju-dev.service` 重建并启动预览，用 `systemctl stop i-love-tju-dev.service` 停止。不要同时在终端和服务中占用 8902。

正式站点读取 `.local/current/web`，编辑工作区不直接上线。发布版本固定到 Git 提交并保存文件哈希；正式数据、服务端配置和下载文件单独持久化，详见 [部署说明](deployment.md#发布与回滚)。

直接访问 `/exam/` 可调试科目裸页，访问 `/` 检查首页中的实际效果。首页自身的顶栏和增强功能直接在 `web/index.html` 中维护，重建脚本只更新其中的 `payload-*` 内容。

## 离线缓存与题库更新

浏览器端离线能力由三个手工维护的部分组成：`web/sw.js`（Service Worker，cache-first 提供 `/` 与 `/config.local.js` 的离线回放）、`web/index.html` 末尾的注册与更新检查脚本（拉取 `/api/manifest` 比对哈希后写入 SW 缓存）。它们都不参与 `tools/build_frontend.py` 的构建，修改后无需重建 payload。服务端清单接口见 [部署说明](deployment.md)；Android 壳的同款机制（本地缓存 + 拦截回放 + 自动更新）见 `android/README.md` 的"离线模式"。

三科页面的作答同步有持久化脏队列：离线期间的记录保存在 localStorage，恢复拉取成功后自动补推；注解脏标记同样持久化。改动同步逻辑需同步修改三个科目页面（复制粘贴的代码块）。

可选样式版本由 `python3 tools/build_premium.py` 生成到 `web/premium/`。这是生成目录，修改应落在科目源页面或构建脚本中。

两个构建脚本都支持 `--web-dir`、`--exam-dir`，也可设置 `ILOVETJU_WEB_DIR`、`ILOVETJU_EXAM_DIR`；默认路径分别为项目内 `web/` 和 `web/exam/`。`--help` 可查看参数。

## 数据来源

题库的事实来源是 `web/exam/*.html` 内嵌 JSON。需要更新离线快照时执行：

```bash
python3 tools/extract_bank.py
```

向其他项目提供数据时，使用 `--out` 导出到独立目录，避免无意刷新本地快照。文件格式和交接规则见 [题库数据交接](data-handoff.md)。

`data/` 保存同步记录和个人注解，包含手动改题及 AI 采纳结果；它们与题库源文件分开保存。`bank-data-export/` 是历史修正导出，尚未作为本次整理的一部分合并。更新题库前应逐题核对修正来源。

## 配置与检查

本地启动与访问口令设置见根目录 README；服务端配置细节见 [部署说明](deployment.md)。`config.json`、`web/config.local.js` 和个人数据均已忽略，提交时使用不含密钥的示例文件。

```bash
python3 server.py --help
python3 -m unittest discover -s tests -v
```

集成测试在临时目录启动服务，检查静态页面、鉴权、同步合并、注解和环境配置，不调用真实 AI。前端配置行为测试通过 Node.js 执行真实增强层，需要在 PATH 中提供 Node.js；它不替代浏览器视觉和交互检查。页面修改还需在浏览器检查桌面和手机布局、公式、切题及作答流程。

GitHub Actions 在推送和 PR 时运行上述测试、首页重建一致性检查、Android 工具入口检查和题库提取校验。无需为运行网站安装 npm 依赖。

## 本次目录整理

站点文件已归入 `web/`，Android 源码归入 `android/`。迁入的 PDF 脚本和 `vendor/` 组件作为历史交接资料保留，生产开发归 `zhenti-pipeline-v2`。旧离线包、备份和迁移档案保存在忽略的 `.local/` 下。原站点路径和 Android 临时路径保留了兼容符号链接，后续开发使用项目内路径。
