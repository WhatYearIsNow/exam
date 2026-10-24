# Android 原生壳

使用 Java、系统 WebView 和 Android SDK 构建，不依赖 Gradle。保留 2.3 版的站点加载、离线重试、音量键切题和文件导出行为。

## 目录

- `java/com/tju/quizhub/`：Activity、WebView 回调和 JavaScript 导出接口。
- `res/`：图标与主题。
- `assets/offline.html`：离线页模板；构建时替换站点地址。
- `AndroidManifest.xml`：包名 `com.tju.quizhub`，版本 `2.3`，最低 Android 7.0 / API 24。
- `build.py`：命令行构建入口。

## 构建

需要 Python 3.8+、JDK 17+、Android SDK Platform 34 和 Build Tools 34.0.0。将 JDK 的 `java`、`javac`、`jar` 加入 `PATH`，并通过 `ANDROID_HOME`、`ANDROID_SDK_ROOT` 或 `--sdk` 指定 SDK。

在项目根目录运行，替换为自己的部署地址：

```bash
python3 android/build.py --sdk /path/to/android-sdk --url https://example.com/
# 或：EXAM_URL=https://example.com/ python3 android/build.py
```

站点地址必须显式指定，主页面、站内链接判断和离线重试均使用同一份配置。`BuildConfig.java` 在临时构建目录生成，无需修改 Java 源文件。运行 `python3 android/build.py --help` 查看 SDK 版本和输出目录参数。

产物默认写入 `android/build/local/ILoveTJU-2.3-local-unsigned.apk`，已经过 zipalign，尚未签名。脚本不会读取签名密钥，也不会覆盖历史 APK 和原有 `build/` 文件。

安装前，用自己的密钥通过 SDK 的 `apksigner` 签名，例如：

```bash
"$ANDROID_HOME/build-tools/34.0.0/apksigner" sign \
  --ks /path/to/your-release.jks \
  --out android/build/local/ILoveTJU-2.3.apk \
  android/build/local/ILoveTJU-2.3-local-unsigned.apk
```

签名密钥与构建产物均不提交 Git。迁移保留的历史 APK 仍对应原来的站点地址，改地址后需要重新构建、签名并安装。

## 与网页的接口

网页通过 `AndroidBridge.setPractice(boolean)` 通知练习状态，并通过 `AndroidBridge.saveFile(name, content)` 导出文本。Android 10+ 使用系统 MediaStore，较旧版本写入应用专属下载目录。网页内容由指定站点提供，APK 不包含完整题库。
