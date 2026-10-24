package com.tju.quizhub;

import android.content.ActivityNotFoundException;
import android.net.Uri;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebView;

class MyChrome extends WebChromeClient {
    private final MainActivity act;
    MyChrome(MainActivity act) { this.act = act; }

    @Override public boolean onShowFileChooser(WebView v, ValueCallback<Uri[]> cb, FileChooserParams params) {
        if (act.fileUploadCallback != null) act.fileUploadCallback.onReceiveValue(null);
        act.fileUploadCallback = cb;
        try {
            act.startActivityForResult(params.createIntent(), 100);
        } catch (ActivityNotFoundException e) {
            act.fileUploadCallback = null;
            return false;
        }
        return true;
    }
}
