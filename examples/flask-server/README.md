# Flask 参考服务器

此目录提供一个轻量的共享统计示例，适合单人本机测试或可信教室、宿舍局域网。
它不是生产部署方案，也不会参与主站的 vinext/Vite 构建。

## 服务范围

服务器关闭 Flask 的通用静态目录，只提供以下明确资源：

- `/`：项目根目录的 `index.html`；
- `/banks/<文件名>`：项目根目录的题库；
- `/stats`：本目录的 `stats.html`；
- `/api/submit`、`/api/stats`、`/api/ping`：示例 API。

仓库中的配置、源码和其他文档不会作为通用静态文件提供。

## 安装与启动

在项目根目录执行：

```bash
python -m pip install -r examples/flask-server/requirements.txt
python examples/flask-server/server.py
```

默认访问地址为：

- `http://127.0.0.1:5000/`
- `http://127.0.0.1:5000/stats`

脚本使用自身路径定位项目文件，因此也可以从其他工作目录启动。

## 可选环境变量

| 变量 | 默认值 | 用途 |
| --- | --- | --- |
| `TJU_QUIZ_HOST` | `127.0.0.1` | 监听地址；可信局域网可显式设为 `0.0.0.0` |
| `TJU_QUIZ_PORT` | `5000` | 监听端口 |
| `TJU_QUIZ_DEBUG` | 未设置 | 设为 `1`、`true`、`yes` 或 `on` 时开启调试 |

PowerShell 局域网示例：

```powershell
$env:TJU_QUIZ_HOST = "0.0.0.0"
python examples/flask-server/server.py
```

调试模式只能用于本机开发，不要与 `0.0.0.0` 同时启用。

## 数据

SQLite 数据保存在本目录的 `quiz_data.db`。停止服务后可直接复制该文件备份。

此实现没有身份认证、访问控制、HTTPS 或请求限流，不得直接暴露到公网。
