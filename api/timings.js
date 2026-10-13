import { Redis } from '@upstash/redis';

export const config = { runtime: 'nodejs' };

const redis = Redis.fromEnv();
const CACHE_TTL = 6 * 60 * 60; // 6 heures en secondes

// Méthode Tunisie + tune (Fajr +2, Asr +1)
const TN_METHOD = '18';
const TN_TUNE = '0,2,0,0,1,0,0,0,0';

function buildAladhanUrl(city, country, method, school, dateStr) {
  const q = [];
  if (method && method !== 'auto') q.push('method=' + method);
  if (school === '1') q.push('school=1');
  const extra = q.length ? '&' + q.join('&') : '';
  return 'https://api.aladhan.com/v1/timingsByCity/' + dateStr +
    '?city=' + encodeURIComponent(city) +
    '&country=' + encodeURIComponent(country) + extra;
}

function buildAladhanCoordsUrl(lat, lng, method, school, dateStr) {
  const q = [];
  if (method && method !== 'auto') q.push('method=' + method);
  if (school === '1') q.push('school=1');
  const extra = q.length ? '&' + q.join('&') : '';
  return 'https://api.aladhan.com/v1/timings/' + dateStr +
    '?latitude=' + lat + '&longitude=' + lng + extra;
}

function isTunisia(country, city) {
  if (!country && !city) return false;
  const c = (country || '').toUpperCase();
  const ci = (city || '').toLowerCase();
  return c === 'TN' || c === 'TUNISIE' || c === 'TUNISIA' ||
         ci.includes('tunis') || ci.includes('sfax') || ci.includes('sousse') ||
         ci.includes('bizerte') || ci.includes('kairouan') || ci.includes('gabes') ||
         ci.includes('ariana') || ci.includes('ben arous') || ci.includes('monastir');
}

async function fetchFromAladhan(url) {
  const res = await fetch(url, { signal: AbortSignal.timeout(8000) });
  if (!res.ok) throw new Error('Aladhan HTTP ' + res.status);
  const json = await res.json();
  if (!json.data || !json.data.timings) throw new Error('Aladhan invalid response');
  return json;
}

function parseTimings(t) {
  const keys = ['Fajr', 'Sunrise', 'Dhuhr', 'Asr', 'Maghrib', 'Isha'];
  const out = {};
  for (const k of keys) {
    const raw = String(t[k] || '');
    const mm = raw.match(/(\d{1,2}):(\d{2})/);
    if (!mm) continue;
    const hh = String(+mm[1]).padStart(2, '0');
    out[k] = hh + ':' + mm[2];
  }
  return out;
}

export default async function handler(req, res) {
  try {
    const {
      city,
      country,
      lat,
      lng,
      method = 'auto',
      school = '0',
      date
    } = req.query;

    // Valider les paramètres
    if (!date) {
      return res.status(400).json({ error: 'Missing date parameter' });
    }

    if (!lat && !lng && (!city || !country)) {
      return res.status(400).json({ error: 'Missing location: provide city+country or lat+lng' });
    }

    // Détecter la Tunisie
    const tunisia = isTunisia(country, city);

    // Appliquer method=18 + tune si Tunisie
    let finalMethod = method;
    let finalTune = null;

    if (tunisia && (method === 'auto' || method === '18')) {
      finalMethod = TN_METHOD;
      finalTune = TN_TUNE;
    }

    // Construire la clé de cache
    const cacheKey = 'timings:' + [
      lat ? 'coords' : 'city',
      city || lat,
      country || lng,
      finalMethod,
      school,
      date
    ].join(':');

    // 1. Chercher en cache
    try {
      const cached = await redis.get(cacheKey);
      if (cached) {
        const data = typeof cached === 'string' ? JSON.parse(cached) : cached;
        return res.status(200).json({
          ...data,
          cached: true
        });
      }
    } catch (e) {
      console.warn('Cache read error:', e.message);
    }

    // 2. Fetch depuis Aladhan
    let url;
    if (lat && lng) {
      url = buildAladhanCoordsUrl(lat, lng, finalMethod, school, date);
    } else {
      url = buildAladhanUrl(city, country, finalMethod, school, date);
    }

    // Ajouter le tune si Tunisie
    if (finalTune) {
      url += '&tune=' + finalTune;
    }

    let json;
    try {
      json = await fetchFromAladhan(url);
    } catch (e) {
      // Fallback : essayer sans le tune si l'API refuse
      if (finalTune) {
        try {
          const fallbackUrl = url.replace('&tune=' + finalTune, '');
          json = await fetchFromAladhan(fallbackUrl);
        } catch (e2) {
          return res.status(503).json({
            error: 'Aladhan unavailable',
            message: e2.message
          });
        }
      } else {
        return res.status(503).json({
          error: 'Aladhan unavailable',
          message: e.message
        });
      }
    }

    // 3. Normaliser la réponse
    const result = {
      date,
      location: lat && lng ? { lat, lng } : { city, country },
      method: finalMethod,
      school,
      tune: finalTune,
      timings: parseTimings(json.data.timings),
      timezone: (json.data.meta && json.data.meta.timezone) || 'UTC',
      hijri: (json.data.date && json.data.date.hijri) || null,
      gregorian: (json.data.date && json.data.date.gregorian) || null,
      fetchedAt: Date.now(),
      cached: false
    };

    // 4. Mettre en cache
    try {
      await redis.setex(cacheKey, CACHE_TTL, JSON.stringify(result));
    } catch (e) {
      console.warn('Cache write error:', e.message);
    }

    return res.status(200).json(result);

  } catch (err) {
    console.error('timings error:', err);
    return res.status(500).json({
      error: 'Internal error',
      message: err.message
    });
  }
}