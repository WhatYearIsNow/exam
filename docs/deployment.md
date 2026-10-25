# 运行与部署

## 现有 KVM19 部署

开发与部署均使用 KVM19 上的 `/opt/exam`。2026-10-25 已将原 `/opt/toy/i-love-tju` 整体迁入，包括 Git 历史、未提交的 ZCode 计划、私有配置、个人数据、Android 构建与签名档案；原目录仅保留兼容符号链接。后续开发请直接打开 `/opt/exam`，不用在旧路径另建副本。

| 路径 | 用途 |
| --- | --- |
| `/opt/exam/config.json` | 服务端访问口令和模型密钥，更新后按文件更新时间自动读取 |
| `/opt/exam/web/config.local.js` | 浏览器应用访问令牌，不存模型密钥 |
| `/opt/exam/data/` | 个人作答、备注与修正数据 |
| `/opt/exam/.local/android-signing/` | 私有 Android 签名资料 |
| `/opt/exam/.local/dev/` | 独立开发站点、配置和测试数据 |
| `/opt/exam/.local/releases/` | 按确定 Git 提交构建的只读运行版本 |
| `/opt/exam/.local/current`、`.local/previous` | 当前与上一个正式版本的链接 |
| `/opt/exam/.local/public/` | 现有 APK 和 `dl/` 下载资料，独立于源码发布 |
| `/opt/exam/.local/deploy/Caddyfile.exam` | 当前站点的 Caddy 配置，由系统 Caddy 配置导入 |
| `/opt/exam/.local/archive/` | 迁入的历史资料与原路径档案 |

后端通过 `i-love-tju-api.service` 开机启动并在异常退出时自动重启，工作目录为 `/opt/exam/.local/current`，监听 `127.0.0.1:8901`。关闭 Codex 或 ZCode 不影响服务。Caddy 从 `/opt/exam/.local/current/web` 提供静态页面；APK 和 `dl/` 单独从 `.local/public/` 提供。正式配置继续读取根目录 `config.json`，个人数据继续写入根目录 `data/`，代码发布与回滚不复制或还原个人数据。

```bash
cd /opt/exam
systemctl status i-love-tju-api.service
curl --fail http://127.0.0.1:8901/health
python3 tools/release.py status
```

`/etc/systemd/system/i-love-tju-api.service` 链接到项目内 `.local/deploy/i-love-tju-api.service`，该文件是部署时安装的配置副本。`/var/www/i-love-tju` 指向正式版本的 `web/`；`/tmp/tjuapp` 等旧入口只保留兼容链接，实际文件统一位于 `/opt/exam`。Python、Java、Android SDK 和系统 Caddy 等共享运行工具仍按系统安装位置使用。

## 发布与回滚

使用短期功能分支开发，通过 PR 和 CI 核对后合并到 `main`。首次将服务切到发布目录时保留原站点行为；之后每次部署都指定已批准的提交或标签。`build` 不读取未提交的源码，不改动正式版本：

```bash
cd /opt/exam
python3 tools/release.py build --ref <已批准的提交或标签>
python3 tools/release.py verify <输出的版本ID>
python3 tools/release.py activate <版本ID>
python3 tools/release.py status
# 回到上一个版本，也可提供某个保留的版本ID
python3 tools/release.py rollback
```

构建在临时目录导出指定提交，运行该提交的测试（要求 Node.js）、首页 payload 一致性检查、题库导出和 Android 工具入口检查。运行版本只包含后端、受版本控制的网页和许可证说明，记录提交 SHA 与文件哈希；不打包模型密钥、个人数据或签名凭证。发布文件设为只读，激活前重新核对清单。构建与切换有互斥锁，避免两个发布进程同时更改版本。

激活通过原子链接切换 `.local/current`，重启后端，检查健康状态及其首页版本哈希；失败时自动恢复原链接、重启旧服务并再次检查。成功后 `.local/previous` 保存上一个版本。Caddy 使用固定的 `.local/current/web` 路径，无需每次重载。首次发布尚无上一版时，`rollback` 会明确报错；旧版本保留直到人工清理。涉及数据格式变更时必须另外设计兼容或数据回退，本工具只回退代码。

`web/config.local.js` 作为共享浏览器配置链接进入运行版本，不属于代码文件哈希；模型 Key 仍只在服务端根配置中。修改这些配置会影响当前服务，无需重新发布。已有 APK 和 `dl/` 已迁到 `.local/public/`，源码 `web/` 中原下载入口为兼容链接；新增下载文件放到 `.local/public/`，由 Caddy 直接提供。

首次安装或升级服务模板时，先构建版本并准备 `.local/current`，再把已审阅模板复制到 `.local/deploy/`，将系统单元链接到该副本，执行 `systemctl daemon-reload` 后启动或重启对应服务。常规代码发布不修改系统单元。开发预览模板为 `deploy/i-love-tju-dev.service`，只在需要时启动，不与正式服务共享配置、数据或端口。

## 配置

从项目根目录复制 `config.example.json` 为 `config.json`，复制 `web/config.example.js` 为 `web/config.local.js`。前端 `appToken` 与服务端 `app_token` 应一致。前端口令会发给浏览器，适用于自己或受信任使用者；模型密钥仅保存在服务端。

| 服务端字段 | 环境变量 | 用途 |
| --- | --- | --- |
| `app_token` | `ILOVETJU_APP_TOKEN` | 同步、注解和 AI API 访问口令 |
| `tju_llm_base`、`tju_llm_key`、`tju_llm_model` | `ILOVETJU_TJU_LLM_BASE`、`ILOVETJU_TJU_LLM_KEY`、`ILOVETJU_TJU_LLM_MODEL` | 首轮 AI 核验（校园网环境） |
| `llm_base`、`llm_key`、`llm_model` | `ILOVETJU_LLM_BASE`、`ILOVETJU_LLM_KEY`、`ILOVETJU_LLM_MODEL` | 后续 AI 复核；校园模型不可达或未配置时自动跳过一审直接使用 |

环境变量优先于 JSON，包括空字符串；不提供 JSON 文件时也可完全用环境变量配置。未配置模型密钥时，AI 核验会返回配置错误，题库浏览仍可使用。

使用私有 JSON 时，在项目根目录 `config.json` 更新 `tju_llm_key`（天大一审）或 `llm_key`（DeepSeek）并保存，后端会在后续请求中按文件更新时间重新读取。保留其余配置字段。若对应字段由环境变量覆盖，则应更新服务环境并重启服务。

服务路径和监听设置：

| 环境变量 | 默认值 | 命令行覆盖 |
| --- | --- | --- |
| `ILOVETJU_HOST` | `127.0.0.1` | `--host` |
| `ILOVETJU_PORT` | `8901` | `--port` |
| `ILOVETJU_WEB_DIR` | `<项目>/web` | `--web-dir` |
| `ILOVETJU_CONFIG` | `<项目>/config.json` | — |
| `ILOVETJU_DATA_DIR` | `<项目>/data` | — |

```bash
python3 server.py --host 127.0.0.1 --port 8901
```

同一端口提供 `/`、`/exam/` 等静态页面和下列 API：

| 路径 | 方法 | 说明 |
| --- | --- | --- |
| `/health` | GET | 无需鉴权的健康检查 |
| `/api/manifest` | GET | 无需鉴权的静态页面版本清单（`/` 与 `/config.local.js` 的 sha256），供离线客户端检测题库更新 |
| `/sync?slot=default` | GET、PUT | 作答记录，按记录的 `at` 合并 |
| `/api/annotations?subject=probability` | GET、PUT | `flags`、`notes`、`ai`、`corr` 四类个人注解 |
| `/api/ai-check` | POST | AI 核验 |

除健康检查和版本清单外，上表 API 需要 `Authorization: Bearer <口令>`，也兼容 `X-Auth-Token`。数据写入 `ILOVETJU_DATA_DIR`；更新代码时应保留配置和该目录。

## Caddy 与 systemd

`deploy/Caddyfile.example` 是独立站点模板：替换示例域名和项目路径后，将静态根目录指向 `web/`，将 `/sync`、`/api/*`、`/health` 反代到后端监听端口。不要把项目根目录作为静态根目录。

`deploy/i-love-tju-api.service` 提供后端服务定义。新环境需调整 `WorkingDirectory`、`ExecStart` 和运行用户，并保证服务用户可写数据目录、可读配置。配置可使用私有 JSON，或通过 systemd 的私有 `EnvironmentFile` 提供上述环境变量。

本工作区现有部署将 systemd 服务文件链接到 `.local/deploy/` 中安装的副本；站点专用 Caddy 配置保存在忽略的 `.local/deploy/Caddyfile.exam`，由系统 Caddy 配置导入。更新现有部署时只处理该站点配置，仓库内通用模板不包含其他站点设置。

调整服务定义后执行 `systemctl daemon-reload`，再重启对应服务；修改 Caddy 时先使用 `caddy validate` 校验完整配置，再重载。部署后检查 `/health`、首页加载与一次同步。
