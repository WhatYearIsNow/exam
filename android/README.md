# Android 原生壳

使用 Java、系统 WebView 和 Android SDK 构建，不依赖 Gradle。保留 2.3 版的站点加载、离线重试、音量键切题和文件导出行为；2.5 起内置站点离线缓存与自动更新（详见下方"离线模式"）。

## 目录

- `java/com/tju/quizhub/`：Activity、WebView 回调和 JavaScript 导出接口。
- `java/com/tju/quizhub/CacheStore.java`：站点离线缓存（应用私有 `files/site-cache/`，存壳页面与 `/config.local.js`）。
- `java/com/tju/quizhub/SiteUpdater.java`：比对 `/api/manifest` 哈希并增量下载更新缓存。
- `res/`：图标与主题。
- `assets/offline.html`：离线页模板；构建时替换站点地址。仅在本地从未成功缓存过站点内容时出现。
- `AndroidManifest.xml`：包名 `com.tju.quizhub`，版本 `2.5`（versionCode 25），最低 Android 7.0 / API 24。
- `build.py`：命令行构建入口。
- `sign.py`：签名、校验，以及与旧 APK 的升级身份比对。

## 构建

需要 Python 3.8+、JDK 17+、Android SDK Platform 34 和 Build Tools 34.0.0。将 JDK 的 `java`、`javac`、`jar` 加入 `PATH`，并通过 `ANDROID_HOME`、`ANDROID_SDK_ROOT` 或 `--sdk` 指定 SDK。

工具链注意：本环境的 d8（Build Tools 34.0.0）遇到非静态内部类（含匿名类）会在写 dex 时内部崩溃（NPE）。嵌套类一律写成 `static` 并通过构造参数传入外部实例，参考 `CacheStore`、`SiteUpdater.RevalidateTask` 与 `CrashGuard.Guard` 的写法。

在项目根目录运行，替换为自己的部署地址：

```bash
python3 android/build.py --sdk /path/to/android-sdk --url https://example.com/
# 或：EXAM_URL=https://example.com/ python3 android/build.py
```

站点地址必须显式指定，主页面、站内链接判断和离线重试均使用同一份配置。`BuildConfig.java` 在临时构建目录生成，无需修改 Java 源文件。运行 `python3 android/build.py --help` 查看 SDK 版本和输出目录参数。

产物默认写入 `android/build/local/ILoveTJU-2.4-local-unsigned.apk`，已经过 zipalign，尚未签名。脚本不会读取签名密钥，也不会覆盖历史 APK 和原有 `build/` 文件。

安装前，用现有密钥签名。更新已有安装时，使用原证书和递增的 versionCode；传入旧 APK 后，脚本会校验证书、包名和版本号，不匹配时不会写入发布文件。

```bash
python3 android/sign.py android/build/local/ILoveTJU-2.4-local-unsigned.apk \
  --sdk /path/to/android-sdk \
  --keystore /path/to/your-release.jks \
  --ks-pass env:EXAM_ANDROID_STORE_PASSWORD \
  --previous-apk /path/to/ILoveTJU-2.3.apk \
  --out android/build/local/ILoveTJU-2.4.apk
```

`EXAM_ANDROID_STORE_PASSWORD` 通过本地安全方式注入；也支持 `--ks-pass file:/path/to/private-password-file`。不要把密码、私钥或包含密码的命令提交到 Git。`--alias` 可选择密钥；私钥密码不同时另用 `--key-pass env:变量名` 或 `file:路径` 指定。

签名密钥与构建产物均不提交 Git。迁移保留的历史 APK 仍对应原来的站点地址，改地址后需要重新构建、签名并安装。

## 独立安装的测试版

当前测试包见 [Android 2.4 预览版 2](https://github.com/WhatYearIsNow/exam/releases/tag/android-v2.4-preview.2)。真机验收由测试者在设备上进行。

正式签名库尚未解锁时，可以用独立预览身份提供手机测试，不替换正式版的签名或包名：

```bash
python3 android/build.py --sdk /path/to/android-sdk \
  --url http://your-exam-site/ --preview --preview-build 1
```

源版本 2.5 构建的预览包为 `2.5-preview.N`、versionCode `25000+N`，包名为 `com.tju.quizhub.preview`，桌面名称为“Exam 测试版”。正式版仍为 `com.tju.quizhub`。预览版使用单独的本地签名库，之后更新预览版时复用该库并递增 `--preview-build`；仍通过 `sign.py` 校验签名输出。已发布的 `2.4-preview.2`（versionCode 24002）可直接被同签名、更高 versionCode 的新预览包覆盖安装。

两种应用可同时安装，本地 WebView 数据分开保存。预览版连接的站点和云端服务仍由构建 URL 决定；连接现有站点时，云端同步仍会影响该服务中的对应同步记录。预览版不能作为原正式版的覆盖升级包。

测试时请检查三科加载、公式和附图、作答及重启留存、同步与备注、音量键切题、文件导出和断网后的重试。完整正式版升级检查仍需使用原正式签名。

## 离线模式

2.5 起 App 在本地缓存一份可用的站点内容，校园网之外也能刷题：

- **缓存内容**：站点根页面 `/`（内嵌三科题库的单文档壳）与 `/config.local.js`，保存在应用私有目录 `files/site-cache/`，与站点同源回放，作答和同步配置仍走原有 localStorage。
- **播种**：首次联网成功加载站点后，后台拉取 `/api/manifest` 校验哈希并缓存一份；此后启动优先加载本地缓存（秒开），同时后台比对清单。
- **自动更新**：启动时和网络恢复（`ConnectivityManager` 回调）都会比对 `/api/manifest`；哈希变化才重新下载，下载完成后校验哈希再原子替换，并 toast「题库已更新，重启应用后生效」。更新在下次启动生效。
- **离线作答**：站点不可达时页面照常可用；作答与注解由网页层排队保存在 localStorage，服务器恢复可达后自动补推（按时间戳合并）。
- **兜底**：仅当本地从未成功缓存过站点内容且联网失败时，才显示 `offline.html` 重试页；网络恢复且缓存就绪后会自动回到站点。

## 发布与设备验收

站点本身仍限校园网或可访问该内网的网络访问；2.5 起离线缓存让 App 在校外也能用最近一次缓存的题库刷题，云端同步与 AI 核验仍需站点可达。发布包应使用实际可访问的站点地址；使用内部 CA 的 HTTPS 还需要设备信任该证书，不能直接当作公开受信任 HTTPS。

同签名升级能保留应用安装数据，但 WebView 的本地存储按站点 origin 区分。更换域名或端口前，先同步或导出未同步的作答记录；不要把安装数据保留等同于新域名自动读到旧记录。

真机验收应覆盖三科加载、作答和重启留存、云端同步、AI 核验、音量键切题、文件导出、离线重试，以及从上一版本直接安装升级。2.5 离线模式另需覆盖：首次联网后断网重进 App（应加载缓存秒开）、离线作答与备注后杀掉 App、恢复校园网后确认记录自动补推、服务端更新题库后确认收到「题库已更新」提示且重启后生效。编译和签名通过不等同于这些流程已经在设备上通过。

## 与网页的接口

网页通过 `AndroidBridge.setPractice(boolean)` 通知练习状态，并通过 `AndroidBridge.saveFile(name, content)` 导出文本。Android 10+ 使用系统 MediaStore，较旧版本写入应用专属下载目录。网页内容由指定站点提供，APK 不包含完整题库。
