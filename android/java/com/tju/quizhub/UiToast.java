package com.tju.quizhub;

import android.content.Context;
import android.os.Handler;
import android.os.Looper;
import android.widget.Toast;

class UiToast {
    static void show(Context ctx, String msg) {
        Handler h = new Handler(Looper.getMainLooper());
        h.post(new ToastRun(ctx, msg));
    }
}
