package com.tju.quizhub;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.graphics.Color;
import android.net.ConnectivityManager;
import android.net.Network;
import android.net.NetworkCapabilities;
import android.net.NetworkRequest;
import android.net.Uri;
import android.os.Bundle;
import android.view.KeyEvent;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.widget.FrameLayout;

import java.io.File;

public class MainActivity extends Activity {
    static final String MAIN_URL = BuildConfig.EXAM_URL;
    static final String HOST = BuildConfig.EXAM_HOST;
    private static final String OFFLINE_URL = "file:///android_asset/offline.html";
    private static final String MAIN_PATH = pathOf(MAIN_URL);
    private boolean offlineShown = false;
    ValueCallback<Uri[]> fileUploadCallback;
    private Bridge bridge;
    private WebView web;
    private FrameLayout root;
    private SiteUpdater updater;
    private ConnectivityManager.NetworkCallback netCallback;

    private static String pathOf(String url) {
        String p = Uri.parse(url).getPath();
        return p == null ? "/" : p;
    }

    @SuppressLint("SetJavaScriptEnabled")
    @Override protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        CrashGuard.install(this);
        CrashGuard.notifyIfCrashed(this);
        bridge = new Bridge(this);
        updater = new SiteUpdater(this);
        root = new FrameLayout(this);
        root.setBackgroundColor(Color.parseColor("#002a55"));
        buildWebView();
        setContentView(root);
        registerNetworkCallback();

        if (savedInstanceState != null) {
            web.restoreState(savedInstanceState);
        } else {
            web.loadUrl(MAIN_URL);
        }
        updater.revalidate();   // 启动即后台比对清单，有新版自动下载，重启后生效
    }

    private void buildWebView() {
        web = new WebView(this);
        web.setBackgroundColor(Color.parseColor("#002a55"));
        root.addView(web, 0, new FrameLayout.LayoutParams(
            FrameLayout.LayoutParams.MATCH_PARENT, FrameLayout.LayoutParams.MATCH_PARENT));
        web.addJavascriptInterface(bridge, "AndroidBridge");
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setAllowFileAccess(true);
        s.setUseWideViewPort(true);
        s.setLoadWithOverviewMode(true);
        s.setMediaPlaybackRequiresUserGesture(false);
        web.setWebViewClient(new MyClient(this));
        web.setWebChromeClient(new MyChrome(this));
    }

    /* 渲染进程被系统杀掉时重建 WebView，而不是整 APP 闪退 */
    void onRenderGone() {
        try {
            root.removeAllViews();
            buildWebView();
            web.loadUrl(MAIN_URL);
        } catch (Exception ignored) {}
    }

    /* 离线优先：同源主页面命中本地缓存就直接回包（同源保住 localStorage 里的
     * 作答与同步配置），同时后台比对清单检查新版；未命中走网络，加载完成后
     * 播种缓存。config.local.js 仅在离线兜底时使用缓存。 */
    WebResourceResponse interceptRequest(WebResourceRequest req) {
        if (updater == null) return null;
        Uri u = req.getUrl();
        if (!"GET".equalsIgnoreCase(req.getMethod())) return null;
        if (u.getHost() == null || !HOST.equalsIgnoreCase(u.getHost())) return null;
        String path = u.getPath() == null ? "/" : u.getPath();
        if (path.equals("/") || path.equals("/index.html") || path.equals(MAIN_PATH)) {
            File root = updater.cache().rootFile();
            if (root.isFile()) {
                updater.revalidate();
                return updater.cache().response(root, "text/html");
            }
            return null;
        }
        if (path.equals("/config.local.js")) {
            File cfg = updater.cache().configFile();
            if (cfg.isFile()) return updater.cache().response(cfg, "application/javascript");
        }
        return null;
    }

    /* 站点页面加载成功（含离线恢复）：清掉离线标记；从未播种过时补一份缓存 */
    void onSitePageLoaded() {
        offlineShown = false;
        if (updater != null && updater.cache().rootSha() == null) updater.revalidate();
    }

    /* 非静态内部类会让本工具链的 d8 内部崩溃，嵌套类一律 static（与 CrashGuard.Guard 同理） */
    private static final class NetCb extends ConnectivityManager.NetworkCallback {
        private final MainActivity act;
        NetCb(MainActivity act) { this.act = act; }

        @Override public void onAvailable(Network network) {
            act.runOnUiThread(new Pump(act));
        }
    }

    private static final class Pump implements Runnable {
        private final MainActivity act;
        Pump(MainActivity act) { this.act = act; }

        public void run() { act.onNetworkAvailable(); }
    }

    private static final class Recover implements SiteUpdater.Done {
        private final MainActivity act;
        Recover(MainActivity act) { this.act = act; }

        public void onDone(boolean reachable) {
            if (!reachable) return;
            act.runOnUiThread(new RecoverReload(act));
        }
    }

    private static final class RecoverReload implements Runnable {
        private final MainActivity act;
        RecoverReload(MainActivity act) { this.act = act; }

        public void run() { act.recoverFromOffline(); }
    }

    void onNetworkAvailable() {
        if (updater == null) return;
        if (!offlineShown) {
            updater.revalidate();
            return;
        }
        /* 离线页卡住时：确认清单可达（顺带完成播种/更新）再自动回到站点 */
        updater.revalidate(new Recover(this));
    }

    void recoverFromOffline() {
        if (!offlineShown) return;
        offlineShown = false;
        web.loadUrl(MAIN_URL);
    }

    private void registerNetworkCallback() {
        try {
            ConnectivityManager cm = (ConnectivityManager) getSystemService(CONNECTIVITY_SERVICE);
            if (cm == null) return;
            netCallback = new NetCb(this);
            cm.registerNetworkCallback(new NetworkRequest.Builder()
                .addCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET).build(), netCallback);
        } catch (Exception ignored) {}
    }

    @Override protected void onDestroy() {
        if (netCallback != null) {
            try {
                ConnectivityManager cm = (ConnectivityManager) getSystemService(CONNECTIVITY_SERVICE);
                if (cm != null) cm.unregisterNetworkCallback(netCallback);
            } catch (Exception ignored) {}
            netCallback = null;
        }
        super.onDestroy();
    }

    /* 音量键切题：仅题目页拦截（上=上一题，下=下一题）；其余视图恢复系统音量 */
    private static final String NAV_JS =
        "(function(dir){var f=document.querySelector('.subject-frame.is-active');" +
        "if(f&&f.contentWindow&&typeof f.contentWindow.pNav==='function'){f.contentWindow.pNav(dir);}})(";

    private void volumeNav(int dir) {
        web.evaluateJavascript(NAV_JS + dir + ");", null);
    }

    @Override public boolean dispatchKeyEvent(KeyEvent event) {
        if (event.getAction() == KeyEvent.ACTION_DOWN && event.getRepeatCount() == 0
                && bridge != null && bridge.isInPractice()) {
            int kc = event.getKeyCode();
            if (kc == KeyEvent.KEYCODE_VOLUME_UP)   { volumeNav(-1); return true; }
            if (kc == KeyEvent.KEYCODE_VOLUME_DOWN) { volumeNav(1);  return true; }
        }
        return super.dispatchKeyEvent(event);
    }

    void onMainFrameError() {
        offlineShown = true;
        web.loadUrl(OFFLINE_URL);
    }

    private int dp(int v) { return Math.round(v * getResources().getDisplayMetrics().density); }

    @Override protected void onSaveInstanceState(Bundle outState) {
        super.onSaveInstanceState(outState);
        web.saveState(outState);
    }

    @Override public void onBackPressed() {
        if (web != null && web.canGoBack() && !offlineShown) web.goBack();
        else finish();
    }
}
