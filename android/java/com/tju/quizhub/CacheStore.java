package com.tju.quizhub;

import android.content.Context;
import android.webkit.WebResourceResponse;

import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.security.MessageDigest;

/* 站点离线缓存：应用私有目录 files/site-cache/ 下保存壳页面（/）与
 * /config.local.js 的最近一份可用内容。只缓存与构建站点同源的响应；
 * meta.json 记录内容哈希，供 SiteUpdater 增量比对。写入用 tmp+rename
 * 原子替换，WebView IO 线程随时可读，无需加锁。免运行时权限。 */
class CacheStore {
    private final File dir;
    private final File metaFile;

    CacheStore(Context ctx) {
        dir = new File(ctx.getFilesDir(), "site-cache");
        if (!dir.exists()) dir.mkdirs();
        metaFile = new File(dir, "meta.json");
    }

    File rootFile() { return new File(dir, "root.html"); }

    File configFile() { return new File(dir, "config.local.js"); }

    String rootSha() { return meta().optString("rootSha", null); }

    String configSha() { return meta().optString("configSha", null); }

    void storeRoot(byte[] data, String sha) { store(rootFile(), data, "rootSha", sha); }

    void storeConfig(byte[] data, String sha) { store(configFile(), data, "configSha", sha); }

    /* mime 形如 "text/html"；读失败返回 null 交回 WebView 走网络 */
    WebResourceResponse response(File f, String mime) {
        try {
            return new WebResourceResponse(mime, "utf-8", new FileInputStream(f));
        } catch (Exception e) {
            return null;
        }
    }

    private JSONObject meta() {
        try {
            return new JSONObject(readAll(metaFile));
        } catch (Exception e) {
            return new JSONObject();
        }
    }

    private void store(File target, byte[] data, String key, String sha) {
        try {
            writeFile(new File(dir, target.getName() + ".tmp"), target, data);
            JSONObject m = meta();
            m.put(key, sha);
            writeFile(new File(dir, "meta.json.tmp"), metaFile, m.toString().getBytes("UTF-8"));
        } catch (Exception ignored) {}
    }

    private static void writeFile(File tmp, File target, byte[] data) throws Exception {
        FileOutputStream fos = new FileOutputStream(tmp);
        try { fos.write(data); } finally { fos.close(); }
        if (!tmp.renameTo(target)) {
            target.delete();
            if (!tmp.renameTo(target)) throw new IllegalStateException("rename failed: " + target);
        }
    }

    private static String readAll(File f) throws Exception {
        FileInputStream in = new FileInputStream(f);
        ByteArrayOutputStream out = new ByteArrayOutputStream();
        try {
            byte[] buf = new byte[8192];
            int n;
            while ((n = in.read(buf)) > 0) out.write(buf, 0, n);
        } finally { in.close(); }
        return new String(out.toByteArray(), "UTF-8");
    }

    static String sha256(byte[] data) {
        try {
            byte[] d = MessageDigest.getInstance("SHA-256").digest(data);
            StringBuilder sb = new StringBuilder(d.length * 2);
            for (byte b : d) sb.append(String.format("%02x", b));
            return sb.toString();
        } catch (Exception e) {
            return null;
        }
    }
}
