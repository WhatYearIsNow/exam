package com.tju.quizhub;

import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.net.Uri;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebResourceResponse;
import android.os.Build;
import android.webkit.WebView;
import android.webkit.WebViewClient;

class MyClient extends WebViewClient {
    private final MainActivity act;
    MyClient(MainActivity act) { this.act = act; }

    @Override public boolean shouldOverrideUrlLoading(WebView v, WebResourceRequest req) {
        Uri u = req.getUrl();
        String scheme = u.getScheme() == null ? "" : u.getScheme();
        if (scheme.equals("http") || scheme.equals("https")) {
            if (MainActivity.HOST.equalsIgnoreCase(u.getHost())) return false;   // 站内继续用本 WebView
            try {                                                        // 外部链接交给系统浏览器
                act.startActivity(new Intent(Intent.ACTION_VIEW, u));
            } catch (ActivityNotFoundException ignored) {}
            return true;
        }
        return scheme.equals("file");
    }

    /* 离线优先入口：同源主页/配置命中本地缓存时直接回包 */
    @Override public WebResourceResponse shouldInterceptRequest(WebView v, WebResourceRequest req) {
        return act.interceptRequest(req);
    }

    @Override public void onPageFinished(WebView v, String url) {
        Uri u = Uri.parse(url);
        String scheme = u.getScheme() == null ? "" : u.getScheme();
        if ((scheme.equals("http") || scheme.equals("https"))
                && MainActivity.HOST.equalsIgnoreCase(u.getHost())) {
            act.onSitePageLoaded();
        }
    }

    @Override public boolean onRenderProcessGone(WebView v, android.webkit.RenderProcessGoneDetail detail) {
        if (Build.VERSION.SDK_INT >= 26 && detail.didCrash()) {
            act.onRenderGone();
            return true;   // 已处理：重建 WebView，避免整 APP 闪退
        }
        return false;
    }

    @Override public void onReceivedError(WebView v, WebResourceRequest req, WebResourceError err) {
        if (req.isForMainFrame()) {
            act.onMainFrameError();
        }
    }
}
