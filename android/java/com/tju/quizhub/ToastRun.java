package com.tju.quizhub;

import android.content.Context;
import android.widget.Toast;

import java.lang.ref.WeakReference;

class ToastRun implements Runnable {
    private final WeakReference<Context> ctx;
    private final String msg;

    ToastRun(Context ctx, String msg) { this.ctx = new WeakReference<>(ctx); this.msg = msg; }

    public void run() {
        Context c = ctx.get();
        if (c != null) Toast.makeText(c, msg, Toast.LENGTH_LONG).show();
    }
}
