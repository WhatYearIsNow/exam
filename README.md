# exam · I Love TJU

天津大学课程刷题工具。前端使用原生 HTML、CSS 和 JavaScript，后端使用 Python 标准库；包含马原、大学物理、概率论题库，以及作答同步、题目备注、修正和 AI 核验功能。

本仓库是 [TJU-Quiz-Hub](https://github.com/WhatYearIsNow/TJU-Quiz-Hub) 的后续开发版本，保留其原始提交历史。旧版源码可通过 [legacy-tju-quiz-hub 标签](https://github.com/WhatYearIsNow/exam/tree/legacy-tju-quiz-hub) 查看；原有分支与版本关系见 [项目沿革](docs/history.md)。

## 本地运行

在项目根目录执行：

```bash
cp -n config.example.json config.json
cp -n web/config.example.js web/config.local.js
python3 server.py
```

打开 `http://127.0.0.1:8901/`。只看题库可以直接运行服务；需要同步、备注或 AI 核验时，在 `config.json` 的 `app_token` 与 `web/config.local.js` 的 `appToken` 填入相同访问口令。模型密钥只填服务端 `config.json` 或环境变量。

上述复制命令保留已有配置；已有部署直接使用原配置即可。

需要 Python 3.8+，无需安装第三方 Python 库。题库、图片和公式渲染资源已内嵌于页面；同步与 AI 核验需要相应服务可用。PDF 编译另需 TeX Live。

## 目录

| 路径 | 用途 |
| --- | --- |
| `web/` | 首页与各科原生 HTML；`web/exam/` 是题库和页面功能的开发入口 |
| `server.py` | 同端口提供静态页面、同步、注解和 AI 核验 API |
| `tools/` | 首页重建、样式版本构建、题库快照、PDF 和离线打包工具 |
| `bank-data/` | 从 HTML 提取的题库快照，供缺少裸页时使用 |
| `vendor/` | PDF 使用的第三方 LaTeX 组件和字体 |
| `android/` | Android 原生 WebView 壳与构建说明 |
| `deploy/` | Caddy 示例和 systemd 服务文件 |
| `tests/` | 使用临时目录启动实际后端的集成测试 |
| `data/`、`book/`、`.local/` | 个人运行数据、生成物和本地档案，均不纳入版本控制 |

修改科目页面后运行 `python3 tools/build_frontend.py`，把更新写入首页内嵌页面。题库以 `web/exam/*.html` 为准；`bank-data-export/` 中的旧修正导出不自动合并。

## 开发与部署

- [项目沿革](docs/history.md)：TJU-Quiz-Hub 与 exam 的延续关系、旧版标签及历史分支。
- [开发说明](docs/development.md)：原生页面、重建流程与测试。
- [部署说明](docs/deployment.md)：配置、API、Caddy 和 systemd。
- [PDF 与离线包](docs/offline-book.md)：章节汇编、TeX 依赖和已知限制。
- [Android 说明](android/README.md)：原生壳的构建与配置。

运行后端与前端配置检查（前端行为测试需要 Node.js，运行网站本身不需要）：

```bash
python3 -m unittest discover -s tests -v
```

GitHub Actions 配置会在推送和 PR 时运行测试、题库检查及离线打包。

## 许可

原创代码采用 [MIT](LICENSE)。题库、试卷内容及第三方组件另见 [第三方与内容说明](THIRD_PARTY_NOTICES.md) 和 `licenses/`；MIT 不替代这些内容自身的授权条件。
