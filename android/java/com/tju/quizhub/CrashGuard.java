package com.tju.quizhub;

import android.content.Context;

import java.io.File;
import android.os.Environment;
import java.io.FileOutputStream;
import java.io.OutputStream;
import java.io.PrintWriter;
import java.io.StringWriter;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

class CrashGuard {
    private static Thread.UncaughtExceptionHandler mDefault;

    static void install(final Context ctx) {
        mDefault = Thread.getDefaultUncaughtExceptionHandler();
        Thread.setDefaultUncaughtExceptionHandler(new Guard(ctx.getApplicationContext(), mDefault));
    }

    /* 启动时若存在上次闪退日志：Toast 提示文件位置（用户可分享排障） */
    static void notifyIfCrashed(final Context ctx) {
        try {
            final File f = new File(ctx.getFilesDir(), "crash-latest.txt");
            if (f.exists() && f.length() > 0) {
                UiToast.show(ctx, "检测到上次闪退日志：文件保存在 Android/data/com.tju.quizhub/files/crash-latest.txt");
            }
        } catch (Exception ignored) {}
    }

    private static class Guard implements Thread.UncaughtExceptionHandler {
        private final Context ctx;
        private final Thread.UncaughtExceptionHandler def;

        Guard(Context c, Thread.UncaughtExceptionHandler d) { ctx = c; def = d; }

        public void uncaughtException(Thread t, Throwable e) {
            try {
                StringWriter sw = new StringWriter();
                sw.write("时间: " + new SimpleDateFormat("yyyy-MM-dd HH:mm:ss", Locale.CHINA).format(new Date()) + "\n");
                sw.write("线程: " + t.getName() + "\n");
                PrintWriter pw = new PrintWriter(sw);
                e.printStackTrace(pw);
                pw.flush();
                FileOutputStream fos = ctx.openFileOutput("crash-latest.txt", Context.MODE_PRIVATE);
                try { fos.write(sw.toString().getBytes("UTF-8")); } finally { fos.close(); }
                /* 尽力复制一份到公共下载目录，方便用户分享 */
                try {
                    File pub = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS);
                    if (!pub.exists()) pub.mkdirs();
                    File out = new File(pub, "ilovetju-crash.txt");
                    OutputStream os = new FileOutputStream(out);
                    try { os.write(sw.toString().getBytes("UTF-8")); } finally { os.close(); }
                } catch (Exception ignored) {}
            } catch (Exception ignored) {}
            if (def != null) def.uncaughtException(t, e);
        }
    }
}
