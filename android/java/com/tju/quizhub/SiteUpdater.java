package com.tju.quizhub;

import android.content.Context;
import android.net.Uri;

import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.util.concurrent.ExecutorService;
import java.util.concurrent.Executors;
import java.util.concurrent.atomic.AtomicBoolean;

/* 站点更新器：比对 /api/manifest（免鉴权）里的内容哈希，发现变化时重新
 * 下载壳页面与 /config.local.js 到本地缓存。全程单线程后台执行；清单
 * 不可达时静默失败（离线场景），busy 标记避免并发重复下载 6MB 壳页面。 */
class SiteUpdater {
    interface Done { void onDone(boolean reachable); }

    private final Context app;
    private final CacheStore cache;
    private final ExecutorService pool = Executors.newSingleThreadExecutor();
    final AtomicBoolean busy = new AtomicBoolean(false);

    SiteUpdater(Context ctx) {
        app = ctx.getApplicationContext();
        cache = new CacheStore(app);
    }

    CacheStore cache() { return cache; }

    void revalidate() { revalidate(null); }

    /* reachable=true 表示清单可达（缓存未必变化），供离线恢复判断用 */
    void revalidate(final Done done) {
        if (!busy.compareAndSet(false, true)) {
            if (done != null) done.onDone(cache.rootSha() != null);
            return;
        }
        pool.execute(new RevalidateTask(this, done));
    }

    /* 非静态内部类会让本工具链的 d8 内部崩溃，嵌套类一律 static（与 CrashGuard.Guard 同理） */
    private static final class RevalidateTask implements Runnable {
        private final SiteUpdater up;
        private final Done done;
        RevalidateTask(SiteUpdater up, Done d) { this.up = up; done = d; }

        public void run() {
            boolean ok = false;
            try {
                ok = up.runOnce();
            } catch (Exception ignored) {
            } finally {
                up.busy.set(false);
            }
            if (done != null) done.onDone(ok);
        }
    }

    boolean runOnce() throws Exception {
        JSONObject files = fetchJson(origin() + "/api/manifest");
        if (files == null) return false;
        JSONObject root = files.optJSONObject("/");
        if (root == null) return false;
        String rootSha = root.optString("sha256", null);

        String oldSha = cache.rootSha();
        if (rootSha != null && !rootSha.equals(oldSha)) {
            byte[] data = fetchBytes(BuildConfig.EXAM_URL);
            if (data != null && rootSha.equals(CacheStore.sha256(data))) {
                cache.storeRoot(data, rootSha);
                if (oldSha != null) UiToast.show(app, "题库已更新，重启应用后生效");
            }
        }

        JSONObject cfg = files.optJSONObject("/config.local.js");
        if (cfg != null) {
            String cfgSha = cfg.optString("sha256", null);
            if (cfgSha != null && !cfgSha.equals(cache.configSha())) {
                byte[] data = fetchBytes(origin() + "/config.local.js");
                if (data != null && cfgSha.equals(CacheStore.sha256(data))) {
                    cache.storeConfig(data, cfgSha);
                }
            }
        }
        return true;
    }

    /* 清单与 config.local.js 挂在站点根路径（server.py 与 Caddy 模板均按根部署） */
    private static String origin() {
        Uri u = Uri.parse(BuildConfig.EXAM_URL);
        String s = u.getScheme() + "://" + u.getHost();
        if (u.getPort() > 0) s += ":" + u.getPort();
        return s;
    }

    private static JSONObject fetchJson(String url) throws Exception {
        byte[] d = fetchBytes(url);
        if (d == null) return null;
        return new JSONObject(new String(d, "UTF-8")).optJSONObject("files");
    }

    private static byte[] fetchBytes(String url) throws Exception {
        HttpURLConnection c = (HttpURLConnection) new URL(url).openConnection();
        c.setConnectTimeout(8000);
        c.setReadTimeout(30000);
        c.setUseCaches(false);
        c.setInstanceFollowRedirects(true);
        try {
            if (c.getResponseCode() != 200) return null;
            InputStream in = c.getInputStream();
            ByteArrayOutputStream out = new ByteArrayOutputStream();
            try {
                byte[] buf = new byte[16384];
                int n;
                while ((n = in.read(buf)) > 0) out.write(buf, 0, n);
            } finally { in.close(); }
            return out.toByteArray();
        } finally {
            c.disconnect();
        }
    }
}
