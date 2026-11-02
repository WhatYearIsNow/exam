package com.tju.quizhub;

import android.app.AlertDialog;
import android.content.ActivityNotFoundException;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.pm.PackageInfo;
import android.net.Uri;
import android.os.Build;

import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.Locale;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.RejectedExecutionException;
import java.util.concurrent.atomic.AtomicBoolean;

/* APK 更新检查器：启动和网络恢复时读取同源 /app-update.json。仅在远端
 * versionCode 更大且包名、下载地址均匹配时显示应用内提示；下载与安装交给
 * 系统处理，避免申请存储权限，也不会绕过 Android 的安装确认。 */
class AppUpdater {
    private static final int MAX_MANIFEST_BYTES = 256 * 1024;

    private final MainActivity activity;
    private final ExecutorService pool = Executors.newSingleThreadExecutor();
    private final AtomicBoolean busy = new AtomicBoolean(false);
    private long promptedCode = -1;
    private boolean foreground = false;
    private UpdateInfo pending;

    AppUpdater(MainActivity act) { activity = act; }

    void check() {
        if (pool.isShutdown()) return;
        if (!busy.compareAndSet(false, true)) return;
        try {
            pool.execute(new CheckTask(this));
        } catch (RejectedExecutionException ignored) {
            busy.set(false);
        }
    }

    void close() { pool.shutdownNow(); }

    void onForeground() {
        foreground = true;
        if (pending != null) show(pending);
    }

    void onBackground() { foreground = false; }

    private static final class CheckTask implements Runnable {
        private final AppUpdater updater;
        CheckTask(AppUpdater updater) { this.updater = updater; }

        public void run() {
            UpdateInfo update = null;
            try {
                update = updater.findUpdate();
            } catch (Exception ignored) {
            } finally {
                updater.busy.set(false);
            }
            if (update != null) updater.activity.runOnUiThread(new ShowUpdate(updater, update));
        }
    }

    private static final class ShowUpdate implements Runnable {
        private final AppUpdater updater;
        private final UpdateInfo update;
        ShowUpdate(AppUpdater updater, UpdateInfo update) {
            this.updater = updater;
            this.update = update;
        }

        public void run() { updater.show(update); }
    }

    private static final class OpenDownload implements DialogInterface.OnClickListener {
        private final MainActivity activity;
        private final String url;
        OpenDownload(MainActivity activity, String url) {
            this.activity = activity;
            this.url = url;
        }

        public void onClick(DialogInterface dialog, int which) {
            try {
                activity.startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(url)));
            } catch (ActivityNotFoundException ignored) {
                UiToast.show(activity, "没有可用的下载应用");
            }
        }
    }

    private static final class UpdateInfo {
        final long versionCode;
        final String versionName;
        final String apkUrl;
        final String notes;

        UpdateInfo(long code, String name, String url, String releaseNotes) {
            versionCode = code;
            versionName = name;
            apkUrl = url;
            notes = releaseNotes;
        }
    }

    private UpdateInfo findUpdate() throws Exception {
        String packageName = activity.getPackageName();
        String channel = packageName.endsWith(".preview") ? "preview" : "stable";
        URL site = new URL(BuildConfig.EXAM_URL);
        URL manifestUrl = new URL(site, "/app-update.json");
        byte[] data = fetchBytes(manifestUrl);
        if (data == null) return null;

        JSONObject channels = new JSONObject(new String(data, "UTF-8")).optJSONObject("channels");
        JSONObject item = channels == null ? null : channels.optJSONObject(channel);
        if (item == null || !packageName.equals(item.optString("packageName"))) return null;

        long remoteCode = item.optLong("versionCode", -1);
        if (remoteCode <= currentVersionCode()) return null;
        String versionName = item.optString("versionName", "").trim();
        String apkPath = item.optString("apkUrl", "").trim();
        if (versionName.length() == 0 || apkPath.length() == 0) return null;

        URL apk = new URL(manifestUrl, apkPath);
        String scheme = apk.getProtocol();
        if (!("http".equalsIgnoreCase(scheme) || "https".equalsIgnoreCase(scheme))) return null;
        if (apk.getUserInfo() != null || !site.getHost().equalsIgnoreCase(apk.getHost())
                || effectivePort(site) != effectivePort(apk)) {
            return null;
        }
        String path = apk.getPath();
        if (path == null || !path.toLowerCase(Locale.ROOT).endsWith(".apk")) return null;

        String notes = item.optString("releaseNotes", "").trim();
        if (notes.length() > 600) notes = notes.substring(0, 600);
        return new UpdateInfo(remoteCode, versionName, apk.toExternalForm(), notes);
    }

    private long currentVersionCode() throws Exception {
        PackageInfo info = activity.getPackageManager().getPackageInfo(activity.getPackageName(), 0);
        if (Build.VERSION.SDK_INT >= 28) return info.getLongVersionCode();
        return info.versionCode;
    }

    private void show(UpdateInfo update) {
        if (promptedCode >= update.versionCode) {
            pending = null;
            return;
        }
        pending = update;
        if (!foreground || activity.isFinishing() || activity.isDestroyed()) return;
        pending = null;
        promptedCode = update.versionCode;
        String message = "新版本 " + update.versionName + " 已发布。\n更新会覆盖安装并保留应用数据，下载后请按系统提示确认安装。";
        if (update.notes.length() > 0) message += "\n\n" + update.notes;
        new AlertDialog.Builder(activity)
            .setTitle("发现新版本")
            .setMessage(message)
            .setPositiveButton("立即更新", new OpenDownload(activity, update.apkUrl))
            .setNegativeButton("稍后", null)
            .show();
    }

    private static int effectivePort(URL url) {
        int port = url.getPort();
        return port >= 0 ? port : url.getDefaultPort();
    }

    private static byte[] fetchBytes(URL url) throws Exception {
        HttpURLConnection connection = (HttpURLConnection) url.openConnection();
        connection.setConnectTimeout(8000);
        connection.setReadTimeout(12000);
        connection.setUseCaches(false);
        connection.setInstanceFollowRedirects(false);
        try {
            if (connection.getResponseCode() != 200) return null;
            int declared = connection.getContentLength();
            if (declared > MAX_MANIFEST_BYTES) return null;
            InputStream in = connection.getInputStream();
            ByteArrayOutputStream out = new ByteArrayOutputStream();
            try {
                byte[] buffer = new byte[4096];
                int total = 0;
                int count;
                while ((count = in.read(buffer)) > 0) {
                    total += count;
                    if (total > MAX_MANIFEST_BYTES) return null;
                    out.write(buffer, 0, count);
                }
            } finally {
                in.close();
            }
            return out.toByteArray();
        } finally {
            connection.disconnect();
        }
    }
}
