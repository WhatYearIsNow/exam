/**
 * physics-quiz-sync — 物理刷题作答记录云同步 Worker（最小实现）
 *
 * 接口：
 *   GET  /?token=xxx&slot=default   读取记录
 *   PUT  /?token=xxx&slot=default   覆盖写入（body 为完整 records JSON）
 * 鉴权：Authorization: Bearer <SYNC_TOKEN> 或 ?token= 查询参数
 * 存储：KV 命名空间 QUIZ_SYNC，key = records:<slot>
 */
const CORS = {
  'access-control-allow-origin': '*',
  'access-control-allow-headers': 'authorization,content-type',
  'access-control-allow-methods': 'GET,PUT,POST,OPTIONS',
};
const json = (o, s = 200) => new Response(JSON.stringify(o), {
  status: s, headers: { 'content-type': 'application/json', ...CORS },
});

export default {
  async fetch(request, env) {
    if (request.method === 'OPTIONS') return new Response(null, { headers: CORS });
    const url = new URL(request.url);

    const token = (request.headers.get('authorization') || '')
      .replace(/^Bearer\s+/i, '') || url.searchParams.get('token') || '';
    if (!env.SYNC_TOKEN || token !== env.SYNC_TOKEN) return json({ error: 'unauthorized' }, 401);

    const slot = (url.searchParams.get('slot') || 'default').replace(/[^a-zA-Z0-9_-]/g, '').slice(0, 32) || 'default';
    const key = 'records:' + slot;

    if (request.method === 'GET') {
      const v = await env.QUIZ_SYNC.get(key);
      return json(v ? JSON.parse(v) : { v: 1, records: {} });
    }
    if (request.method === 'PUT' || request.method === 'POST') {
      const body = await request.text();
      try { JSON.parse(body); } catch (e) { return json({ error: 'bad json' }, 400); }
      await env.QUIZ_SYNC.put(key, body);
      return json({ ok: true, key });
    }
    return json({ error: 'method not allowed' }, 405);
  },
};
