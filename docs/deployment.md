# 运行与部署

## 配置

从项目根目录复制 `config.example.json` 为 `config.json`，复制 `web/config.example.js` 为 `web/config.local.js`。前端 `appToken` 与服务端 `app_token` 应一致。前端口令会发给浏览器，适用于自己或受信任使用者；模型密钥仅保存在服务端。

| 服务端字段 | 环境变量 | 用途 |
| --- | --- | --- |
| `app_token` | `ILOVETJU_APP_TOKEN` | 同步、注解和 AI API 访问口令 |
| `tju_llm_base`、`tju_llm_key`、`tju_llm_model` | `ILOVETJU_TJU_LLM_BASE`、`ILOVETJU_TJU_LLM_KEY`、`ILOVETJU_TJU_LLM_MODEL` | 首轮 AI 核验 |
| `llm_base`、`llm_key`、`llm_model` | `ILOVETJU_LLM_BASE`、`ILOVETJU_LLM_KEY`、`ILOVETJU_LLM_MODEL` | 后续 AI 复核 |

环境变量优先于 JSON，包括空字符串；不提供 JSON 文件时也可完全用环境变量配置。未配置模型密钥时，AI 核验会返回配置错误，题库浏览仍可使用。

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
| `/sync?slot=default` | GET、PUT | 作答记录，按记录的 `at` 合并 |
| `/api/annotations?subject=probability` | GET、PUT | `flags`、`notes`、`ai`、`corr` 四类个人注解 |
| `/api/ai-check` | POST | AI 核验 |

除健康检查外，上表 API 需要 `Authorization: Bearer <口令>`，也兼容 `X-Auth-Token`。数据写入 `ILOVETJU_DATA_DIR`；更新代码时应保留配置和该目录。

## Caddy 与 systemd

`deploy/Caddyfile.example` 是独立站点模板：替换示例域名和项目路径后，将静态根目录指向 `web/`，将 `/sync`、`/api/*`、`/health` 反代到后端监听端口。不要把项目根目录作为静态根目录。

`deploy/i-love-tju-api.service` 提供后端服务定义。新环境需调整 `WorkingDirectory`、`ExecStart` 和运行用户，并保证服务用户可写数据目录、可读配置。配置可使用私有 JSON，或通过 systemd 的私有 `EnvironmentFile` 提供上述环境变量。

本工作区现有部署将 systemd 服务文件链接到项目内文件；站点专用 Caddy 配置保存在忽略的 `.local/deploy/Caddyfile.exam`，由系统 Caddy 配置导入。更新现有部署时只处理该站点配置，仓库内通用模板不包含其他站点设置。

调整服务定义后执行 `systemctl daemon-reload`，再重启对应服务；修改 Caddy 时先使用 `caddy validate` 校验完整配置，再重载。部署后检查 `/health`、首页加载与一次同步。
