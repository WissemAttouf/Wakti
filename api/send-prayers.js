import { Redis } from '@upstash/redis';
import webpush from 'web-push';

export const config = {
  runtime: 'nodejs',
  maxDuration: 30
};

const kv = Redis.fromEnv();

const VAPID_PUBLIC = process.env.VAPID_PUBLIC_KEY;
const VAPID_PRIVATE = process.env.VAPID_PRIVATE_KEY;
const CRON_SECRET = process.env.CRON_SECRET;

if (VAPID_PUBLIC && VAPID_PRIVATE) {
  try {
    webpush.setVapidDetails('mailto:contact@wakti.app', VAPID_PUBLIC, VAPID_PRIVATE);
  } catch (e) {
    console.error('VAPID init failed:', e.message);
  }
}

async function fetchTimings(city, country, method, school) {
  const now = new Date();
  const dateStr = String(now.getUTCDate()).padStart(2, '0') + '-' +
    String(now.getUTCMonth() + 1).padStart(2, '0') + '-' +
    now.getUTCFullYear();

  const q = [];
  if (method && method !== 'auto') q.push('method=' + method);
  if (school === '1') q.push('school=1');
  const extra = q.length ? '&' + q.join('&') : '';

  const url = 'https://api.aladhan.com/v1/timingsByCity/' + dateStr +
    '?city=' + encodeURIComponent(city) +
    '&country=' + encodeURIComponent(country) + extra;

  try {
    const res = await fetch(url);
    if (!res.ok) return null;
    const json = await res.json();
    return json.data.timings;
  } catch (e) {
    return null;
  }
}

function getTimezoneOffsetMinutes(timezone) {
  try {
    const now = new Date();
    const utcStr = now.toLocaleString('en-US', { timeZone: 'UTC' });
    const tzStr = now.toLocaleString('en-US', { timeZone: timezone || 'UTC' });
    return (new Date(tzStr) - new Date(utcStr)) / 60000;
  } catch (e) {
    return 0;
  }
}


// Choix de l'adhan selon la priere
function adhanFor(prayerKey) {
  if (prayerKey === 'Fajr') return '/audio/adhan-fajr.mp3';
  if (prayerKey === 'Maghrib') return '/audio/adhan-maghrib.mp3';
  return '/audio/adhan-standard.mp3';
}

function isPrayerDue(timingStr, timezone, windowMinutes) {
  if (!timingStr) return false;
  windowMinutes = windowMinutes || 6;
  const parts = String(timingStr).split(':').map(Number);
  const hh = parts[0];
  const mm = parts[1];
  if (isNaN(hh) || isNaN(mm)) return false;
  const now = new Date();
  const offsetMin = getTimezoneOffsetMinutes(timezone);
  const utcMinutes = now.getUTCHours() * 60 + now.getUTCMinutes();
  const localMinutes = (utcMinutes + offsetMin + 1440) % 1440;
  const prayerMinutes = hh * 60 + mm;
  const diff = (prayerMinutes - localMinutes + 1440) % 1440;
  return diff >= 0 && diff <= windowMinutes;
}

const PRAYERS = [
  { key: 'Fajr', ar: 'الفجر', fr: 'Fajr' },
  { key: 'Dhuhr', ar: 'الظهر', fr: 'Dhouhr' },
  { key: 'Asr', ar: 'العصر', fr: 'Asr' },
  { key: 'Maghrib', ar: 'المغرب', fr: 'Maghrib' },
  { key: 'Isha', ar: 'العشاء', fr: 'Icha' }
];

export default async function handler(req, res) {
  try {
    const auth = req.headers.authorization || '';
    const queryKey = (req.query && req.query.key) || '';
    const validHeader = CRON_SECRET && auth === 'Bearer ' + CRON_SECRET;
    const validQuery = CRON_SECRET && queryKey === CRON_SECRET;

    if (!validHeader && !validQuery) {
      return res.status(401).json({ error: 'Unauthorized' });
    }

    if (!VAPID_PUBLIC || !VAPID_PRIVATE) {
      return res.status(500).json({ error: 'VAPID keys not configured' });
    }

    let subs = [];
    try {
      subs = await kv.smembers('subs:all');
    } catch (e) {
      console.error('Redis smembers failed:', e.message);
      return res.status(503).json({ error: 'Storage unavailable' });
    }

    if (!subs || subs.length === 0) {
      return res.status(200).json({ sent: 0, checked: 0 });
    }

    let sent = 0;
    let checked = 0;
    const timingsCache = new Map();

    for (const id of subs) {
      let entry;
      try {
        entry = await kv.get('sub:' + id);
      } catch (e) {
        continue;
      }
      if (!entry) continue;
      if (typeof entry === 'string') {
        try { entry = JSON.parse(entry); } catch (e) { continue; }
      }
      if (!entry.subscription || !entry.meta) continue;
      checked++;

      const meta = entry.meta;
      const city = meta.city;
      const country = meta.country;
      const method = meta.method || '18';
      const school = meta.school || '0';
      const timezone = meta.timezone || 'UTC';

      if (!city || !country) continue;

      const cacheKey = city + '|' + country + '|' + method + '|' + school;
      let timings = timingsCache.get(cacheKey);
      if (!timings) {
        timings = await fetchTimings(city, country, method, school);
        if (timings) timingsCache.set(cacheKey, timings);
      }
      if (!timings) continue;

      for (const p of PRAYERS) {
        if (isPrayerDue(timings[p.key], timezone)) {
          const payload = JSON.stringify({
            title: "🕌 C'est l'heure de " + p.fr,
            body: 'Wakti - ' + p.ar + ' · Cliquez pour écouter l\'adhan',
            icon: '/img/icons/icon-192.png',
            badge: '/img/icons/icon-192.png',
            tag: 'prayer-' + p.key + '-' + Date.now(),
            renotify: true,
            url: '/#/prieres',
            prayer: p.key,
            audio: adhanFor(p.key),
            requireInteraction: true,
            vibrate: [500, 200, 500, 200, 500, 200, 500]
          });

          try {
            await webpush.sendNotification(entry.subscription, payload, {
              TTL: 900,
              urgency: 'high'
            });
            sent++;
          } catch (err) {
            if (err.statusCode === 410 || err.statusCode === 404) {
              try {
                await kv.del('sub:' + id);
                await kv.srem('subs:all', id);
              } catch (e) {}
            }
          }
        }
      }
    }

    return res.status(200).json({ sent: sent, checked: checked });
  } catch (err) {
    console.error('send-prayers error:', err);
    return res.status(500).json({
      error: 'Internal error',
      message: err.message
    });
  }
}
