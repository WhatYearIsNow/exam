package com.tju.quizhub;

import android.content.Context;
import android.os.Environment;
import android.webkit.JavascriptInterface;

import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStream;

class Bridge {
    private volatile boolean inPractice = false;
    private Context appContext;

    Bridge(Context ctx) { appContext = ctx.getApplicationContext(); }

    @JavascriptInterface public void setPractice(boolean v) {
        inPractice = v;
    }

    boolean isInPractice() { return inPractice; }

    /* 学情报告等导出：保存到系统下载目录，Toast 提示路径 */
    @JavascriptInterface public void saveFile(final String name, final String content) {
        if (appContext == null || name == null || content == null) return;
        final String msg;
        try {
            if (android.os.Build.VERSION.SDK_INT >= 29) {
                android.content.ContentValues cv = new android.content.ContentValues();
                cv.put(android.provider.MediaStore.Downloads.DISPLAY_NAME, name);
                cv.put(android.provider.MediaStore.Downloads.MIME_TYPE, "text/markdown");
                android.net.Uri uri = appContext.getContentResolver()
                    .insert(android.provider.MediaStore.Downloads.EXTERNAL_CONTENT_URI, cv);
                if (uri == null) throw new IllegalStateException("MediaStore insert failed");
                OutputStream os = appContext.getContentResolver().openOutputStream(uri);
                try { os.write(content.getBytes("UTF-8")); } finally { os.close(); }
                msg = "已保存到 Android/data/com.tju.quizhub/files/Download/" + name;
            } else {
                /* API<29：写应用专属下载目录（免运行时权限，避免 SecurityException） */
                File dir = appContext.getExternalFilesDir("Download");
                if (dir == null) dir = appContext.getFilesDir();
                if (!dir.exists()) dir.mkdirs();
                File f = new File(dir, name);
                FileOutputStream fos = new FileOutputStream(f);
                try { fos.write(content.getBytes("UTF-8")); } finally { fos.close(); }
                android.media.MediaScannerConnection.scanFile(appContext, new String[]{f.getAbsolutePath()}, null, null);
                msg = "已保存到 下载/" + name;
            }
        } catch (final Exception e) {
            UiToast.show(appContext, "保存失败：" + e.getMessage());
            return;
        }
        UiToast.show(appContext, msg);
    }
}
