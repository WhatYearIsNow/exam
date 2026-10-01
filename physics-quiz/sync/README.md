# physics-quiz-sync 部署说明

作答记录云同步（Cloudflare Workers + KV，免费额度内）。部署一次，手机/电脑任何网络都能同步。

## 一次性部署（在电脑上，需有 Cloudflare 账号）

```powershell
cd Projects\TJU-Quiz-Hub\physics-quiz\sync

# 1. 登录（浏览器授权，仅首次）
npx wrangler login

# 2. 生成同步密钥并记下（一串随机字符，相当于密码）
node -e "console.log(require('crypto').randomBytes(24).toString('hex'))"

# 3. 部署 Worker（首次会自动创建 KV 命名空间）
npx wrangler deploy

# 4. 把第 2 步的密钥存为 Worker secret（替换 <你的密钥>）
npx wrangler secret put SYNC_TOKEN
```

部署完成后 wrangler 会输出 Worker URL，形如：
`https://physics-quiz-sync.<你的子域>.workers.dev`

## 在刷题页启用

1. 打开刷题页，点右上角 `⋯` → 「☁️ 云端同步设置」
2. 依次填入：
   - **服务器地址**：上面的 Worker URL
   - **同步密钥**：第 2 步生成的密钥
   - **同步槽位**：保持 `default`（你自己的所有设备用同一个）
3. 保存后：打开页面自动拉取云端记录合并；每次作答后自动推送

## 换手机 / 重装浏览器

同样在 `⋯` 菜单里配置一次地址 + 密钥即可，记录自动拉回。

## 说明

- 云端只存作答状态（题号、对错、错题标记、时间戳），不含任何个人信息
- 密钥泄露的后果 = 别人能读写你的刷题记录；不放心就重新 `wrangler secret put SYNC_TOKEN` 换一个
- 冲突规则：同一题以时间戳较新的记录为准
