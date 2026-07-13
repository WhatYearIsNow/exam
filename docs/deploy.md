# 服务器部署指南（参考方案）

> ⚠️ **免责声明**：此方案为社区参考，作者未在生产环境中实测验证。使用前请自行评估和测试。欢迎提交改进 PR。

部署后，学生通过浏览器访问即可刷题，答题数据自动汇总到全服统计看板。

---

## 方式一：本地/局域网部署（最简单）

适合教室、机房、宿舍局域网。

```bash
# 1. 安装 Python（需 3.8+）
# 2. 安装依赖
pip install flask

# 3. 启动服务器
cd TJU-Quiz-Hub
python server.py
```

启动后：
- 刷题页面：`http://你的IP:5000`
- 统计看板：`http://你的IP:5000/stats`

学生只需在浏览器输入你的 IP 即可访问，无需安装任何软件。

---

## 方式二：Render 免费部署（推荐，公网访问）

[Render](https://render.com) 提供免费 Python 托管，适合长期使用。

### 步骤

1. Fork 本仓库到你的 GitHub
2. 登录 [Render Dashboard](https://dashboard.render.com)
3. 点击 **New** → **Web Service**
4. 连接你的 GitHub 仓库
5. 配置：
   - **Name**: `tju-quiz-hub`
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python server.py`
   - **Free Instance**: 勾选
6. 点击 **Create Web Service**

几分钟后即可通过 `https://tju-quiz-hub.onrender.com` 访问。

> 注意：免费实例 15 分钟无访问会休眠，首次唤醒需几秒。数据保存在 SQLite 中（免费实例重启会丢失，建议定期备份或升级付费计划）。

---

## 方式三：Railway 部署

[Railway](https://railway.app) 提供更稳定的免费额度。

1. Fork 本仓库
2. 登录 Railway，点击 **New Project** → **Deploy from GitHub repo**
3. 选择仓库，Railway 自动检测 Python 项目
4. 添加 Start Command：`python server.py`
5. 部署

---

## 方式四：自有服务器（Nginx + Flask）

适用于已有服务器的情况。

### 1. 上传项目

```bash
scp -r TJU-Quiz-Hub user@server:/opt/
```

### 2. 安装依赖并运行

```bash
ssh user@server
cd /opt/TJU-Quiz-Hub
pip install flask
python server.py &   # 或使用 systemd/supervisor
```

### 3. 配置 Nginx 反向代理（可选）

```nginx
server {
    listen 80;
    server_name quiz.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 数据说明

- 数据存储在 `quiz_data.db`（SQLite）
- 包含：提交记录、错题详情
- 备份：直接复制 `quiz_data.db` 文件即可
- 迁移：复制 `quiz_data.db` 到新服务器即可

---

## 验证部署

部署后访问以下地址确认服务正常：

| URL | 预期结果 |
|-----|---------|
| `/` | 刷题页面 |
| `/stats` | 统计看板（初始为空） |
| `/api/ping` | `{"ok": true, "time": "..."}` |
| `/api/stats` | `{"overview": {}, ...}` |
