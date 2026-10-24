package com.tju.quizhub;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.view.KeyEvent;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.widget.FrameLayout;

public class MainActivity extends Activity {
    static final String MAIN_URL = BuildConfig.EXAM_URL;
    static final String HOST = BuildConfig.EXAM_HOST;
    private static final String OFFLINE_URL = "file:///android_asset/offline.html";
    private boolean offlineShown = false;
    ValueCallback<Uri[]> fileUploadCallback;
    private Bridge bridge;
    private WebView web;
    private FrameLayout root;

    @SuppressLint("SetJavaScriptEnabled")
    @Override protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        CrashGuard.install(this);
        CrashGuard.notifyIfCrashed(this);
        bridge = new Bridge(this);
        root = new FrameLayout(this);
        root.setBackgroundColor(Color.parseColor("#002a55"));
        buildWebView();
        setContentView(root);

        if (savedInstanceState != null) {
            web.restoreState(savedInstanceState);
        } else {
            web.loadUrl(MAIN_URL);
        }
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
