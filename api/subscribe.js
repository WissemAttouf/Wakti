import { Redis } from '@upstash/redis';

export const config = {
  runtime: 'nodejs',
  maxDuration: 10
};

const kv = Redis.fromEnv();

const RATE_LIMIT = 5;
const WINDOW_SECONDS = 3600;

function withTimeout(promise, ms, label) {
  return Promise.race([
    promise,
    new Promise((_, reject) =>
      setTimeout(() => reject(new Error(label + ' timeout')), ms)
    )
  ]);
}

async function checkRateLimit(ip) {
  const key = 'ratelimit:' + ip;
  try {
    const count = await withTimeout(kv.incr(key), 3000, 'incr');
    if (count === 1) {
      await withTimeout(kv.expire(key, WINDOW_SECONDS), 3000, 'expire');
    }
    return { allowed: count <= RATE_LIMIT, count };
  } catch (e) {
    console.warn('Rate limit check failed (fail-open):', e.message);
    return { allowed: true, count: 0 };
  }
}

const ALLOWED_PUSH_HOSTS = [
  'fcm.googleapis.com',
  'updates.push.services.mozilla.com',
  'web.push.apple.com',
  'wns2-par02p.notify.windows.com',
  'wns2-by3p.notify.windows.com'
];

function isAllowedPushEndpoint(endpoint) {
  try {
    const url = new URL(endpoint);
    return ALLOWED_PUSH_HOSTS.some(function(h) {
      return url.hostname === h || url.hostname.endsWith('.' + h);
    });
  } catch (e) {
    return false;
  }
}

async function hashEndpoint(endpoint) {
  const encoder = new TextEncoder();
  const data = encoder.encode(endpoint);
  const hash = await crypto.subtle.digest('SHA-256', data);
  const bytes = Array.from(new Uint8Array(hash));
  return bytes.map(function(b) { return b.toString(16).padStart(2, '0'); }).join('').slice(0, 32);
}

export default async function handler(req, res) {
  try {
    if (req.method !== 'POST') {
      return res.status(405).json({ error: 'Method not allowed' });
    }

    const ip = (req.headers['x-forwarded-for'] || '').split(',')[0].trim()
            || req.headers['x-real-ip']
            || 'unknown';

    const rate = await checkRateLimit(ip);
    if (!rate.allowed) {
      return res.status(429).json({
        error: 'Too many requests',
        count: rate.count,
        limit: RATE_LIMIT
      });
    }

    let body = req.body;
    if (typeof body === 'string') {
      try { body = JSON.parse(body); } catch (e) { body = null; }
    }
    if (!body || typeof body !== 'object') {
      return res.status(400).json({ error: 'Invalid JSON body' });
    }

    const subscription = body.subscription;
    const meta = body.meta || {};

    if (!subscription || typeof subscription !== 'object') {
      return res.status(400).json({ error: 'Missing subscription' });
    }
    if (!subscription.endpoint || typeof subscription.endpoint !== 'string') {
      return res.status(400).json({ error: 'Missing subscription.endpoint' });
    }
    if (!isAllowedPushEndpoint(subscription.endpoint)) {
      return res.status(400).json({ error: 'Invalid push endpoint host' });
    }
    if (subscription.endpoint.length > 500) {
      return res.status(400).json({ error: 'Endpoint too long' });
    }
    if (!subscription.keys || !subscription.keys.p256dh || !subscription.keys.auth) {
      return res.status(400).json({ error: 'Missing subscription keys' });
    }

    const cleanMeta = {
      city: String(meta.city || '').slice(0, 100),
      country: String(meta.country || '').slice(0, 10),
      method: String(meta.method || 'auto').slice(0, 10),
      school: String(meta.school || '0').slice(0, 2),
      timezone: String(meta.timezone || 'UTC').slice(0, 50),
      lang: String(meta.lang || 'fr').slice(0, 5),
      app: String(meta.app || 'wakti').slice(0, 20)
    };

    const id = await hashEndpoint(subscription.endpoint);

    try {
      await withTimeout(kv.set('sub:' + id, JSON.stringify({
        subscription: subscription,
        meta: cleanMeta,
        createdAt: Date.now(),
        lastSeen: Date.now()
      })), 5000, 'set');

      await withTimeout(kv.sadd('subs:all', id), 5000, 'sadd');
    } catch (e) {
      console.error('Redis storage failed:', e.message);
      return res.status(503).json({ error: 'Storage temporarily unavailable' });
    }

    return res.status(200).json({ ok: true, id: id });

  } catch (err) {
    console.error('subscribe error:', err);
    return res.status(500).json({
      error: 'Internal error',
      message: err.message
    });
  }
}
