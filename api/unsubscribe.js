import { Redis } from '@upstash/redis';

export const config = {
  runtime: 'nodejs',
  maxDuration: 10
};

const kv = Redis.fromEnv();

function withTimeout(promise, ms, label) {
  return Promise.race([
    promise,
    new Promise(function(_, reject) {
      setTimeout(function() { reject(new Error(label + ' timeout')); }, ms);
    })
  ]);
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

    let body = req.body;
    if (typeof body === 'string') {
      try { body = JSON.parse(body); } catch (e) { body = null; }
    }
    if (!body || typeof body !== 'object') {
      return res.status(400).json({ error: 'Invalid JSON body' });
    }

    const endpoint = body.endpoint;
    if (!endpoint || typeof endpoint !== 'string') {
      return res.status(400).json({ error: 'Missing endpoint' });
    }

    const id = await hashEndpoint(endpoint);

    try {
      await withTimeout(kv.del('sub:' + id), 5000, 'del');
      await withTimeout(kv.srem('subs:all', id), 5000, 'srem');
    } catch (e) {
      console.error('Redis delete failed:', e.message);
      return res.status(503).json({ error: 'Storage temporarily unavailable' });
    }

    return res.status(200).json({ ok: true });

  } catch (err) {
    console.error('unsubscribe error:', err);
    return res.status(500).json({
      error: 'Internal error',
      message: err.message
    });
  }
}
