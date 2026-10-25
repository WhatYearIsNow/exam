/* I Love TJU 壳页面离线缓存（Service Worker）。
 *
 * 只缓存两个同源资源：/（内嵌三科题库的单文档壳）与 /config.local.js。
 * 更新检测不在本文件：页面拉取 /api/manifest 比对哈希后直接写入本缓存，
 * 因此这里保持"纯缓存层"——cache-first 命中即返回，不主动联网校验。
 * 手工维护，不参与 tools/build_frontend.py 的 payload 构建。
 */
'use strict';
var CACHE = 'tju-shell-v1';

function precache(cache, path) {
  var req;
  try { req = new Request(path, { cache: 'reload' }); } catch (e) { req = path; }
  return cache.add(req).catch(function () {});   // /config.local.js 可能不存在，失败不阻塞安装
}

self.addEventListener('install', function (ev) {
  ev.waitUntil(caches.open(CACHE).then(function (cache) {
    // 页面的更新检查可能已写入更新的 '/'，已有缓存则不回填旧版
    return Promise.all([
      cache.match('/').then(function (hit) { return hit ? null : precache(cache, '/'); }),
      precache(cache, '/config.local.js'),
    ]);
  }).then(function () { return self.skipWaiting(); }));
});

self.addEventListener('activate', function (ev) {
  ev.waitUntil(caches.keys().then(function (keys) {
    return Promise.all(keys.filter(function (k) { return k !== CACHE; })
      .map(function (k) { return caches.delete(k); }));
  }).then(function () { return self.clients.claim(); }));
});

self.addEventListener('fetch', function (ev) {
  var req = ev.request;
  if (req.method !== 'GET') return;
  var url = new URL(req.url);
  if (url.origin !== self.location.origin) return;
  // API 与清单永远走网络；页面带 cache:'reload' 的请求表示强制取新版，同样放行
  if (url.pathname === '/api/manifest') return;
  if (url.pathname.indexOf('/api/') === 0 || url.pathname.indexOf('/sync') === 0) return;
  if (req.cache === 'reload' || req.cache === 'no-store') return;
  var isNav = req.mode === 'navigate';
  var key = isNav ? '/' : url.pathname;
  if (!isNav && url.pathname !== '/config.local.js') return;
  ev.respondWith(caches.match(key).then(function (hit) {
    if (hit) return hit;
    return fetch(req).then(function (resp) {
      if (resp && resp.ok) {
        var copy = resp.clone();
        caches.open(CACHE).then(function (c) { c.put(key, copy); });
      }
      return resp;
    });
  }));
});
