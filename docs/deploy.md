# 构建与运行

项目包含两条彼此独立的运行路径：

- 托管站是主项目，使用 vinext、Vite 和 Cloudflare Worker 构建。
- Flask 服务器仅用于可信本机或局域网内体验共享答题统计，不属于托管站构建。

## 托管站

### 组成

- `app/`：站点首页。
- `public/quiz.html` 和 `public/banks/`：刷题页及题库静态资源。
- `worker/index.ts`：托管运行时入口。
- `.openai/hosting.json`：Sites 托管配置。
- `tooling/sites-vite-plugin.ts`：构建结束后打包托管元数据。

### 环境要求

- Node.js 22.13.0 或更高版本。
- npm，并使用仓库中的 `package-lock.json` 安装依赖。

### 本地开发

```bash
npm ci
npm run dev
```

开发服务器会输出本地访问地址。

### 生产构建

```bash
npm run build
```

构建结果写入被 Git 忽略的 `dist/`。构建插件会把
`.openai/hosting.json` 复制到 `dist/.openai/`，供托管流程识别。

需要在本机检查生产构建时，可在成功构建后运行：

```bash
npm run start
```

托管平台应从干净检出执行 `npm ci` 和 `npm run build`。不要提交
`node_modules/`、`dist/` 或 `.wrangler/`。

当前托管站以浏览器本地存储保存个人进度。下面的 Flask 统计服务是独立参考实现，
不会自动进入托管站构建。

## Flask 参考服务器

Flask 示例位于 `examples/flask-server/`，详细说明见该目录的
`README.md`。它只明确提供：

- 项目根目录的 `index.html`；
- 项目根目录的 `banks/`；
- 示例目录内的 `stats.html`；
- 示例所需的 `/api/*` 接口。

### 本机运行

在项目根目录执行：

```bash
python -m pip install -r examples/flask-server/requirements.txt
python examples/flask-server/server.py
```

默认仅监听 `127.0.0.1:5000`：

- 刷题页：`http://127.0.0.1:5000/`
- 统计页：`http://127.0.0.1:5000/stats`
- 健康检查：`http://127.0.0.1:5000/api/ping`

### 可信局域网运行

只有确认同一网络内的参与者可信时，才在 PowerShell 中显式开放监听：

```powershell
$env:TJU_QUIZ_HOST = "0.0.0.0"
python examples/flask-server/server.py
```

其他设备通过运行服务器的电脑局域网 IP 访问。不要设置
`TJU_QUIZ_DEBUG`；共享运行时必须保持调试模式关闭。

该示例没有身份认证、访问控制、HTTPS、请求限流或生产级数据保护，且会保存参与者姓名
和答题结果，因此不得直接暴露到公网。公网服务需要先补齐这些能力并经过独立安全评审。

SQLite 数据文件保存在 `examples/flask-server/quiz_data.db`，可在服务停止后复制备份。
