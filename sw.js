/* Wakti Service Worker v6 */

const VERSION = 'wakti-v25';
const SHELL_CACHE = VERSION + '-shell';
const IMG_CACHE = VERSION + '-img';
const API_CACHE = VERSION + '-api';

const SHELL_FILES = [
  '/',
  '/index.html',
  '/css/style.css',
  '/js/app.js',
  '/manifest.webmanifest',
  '/img/icons/icon-192.png',
  '/img/icons/icon-512.png'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(SHELL_CACHE).then(async cache => {
      for (const url of SHELL_FILES) {
        try { await cache.add(url); }
        catch (e) { console.warn('[SW] Skip', url); }
      }
    }).then(() => self.skipWaiting())
  );
});

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys => Promise.all(
      keys.filter(k => !k.startsWith(VERSION)).map(k => caches.delete(k))
    )).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', event => {
  const req = event.request;
  const url = new URL(req.url);
  if (req.method !== 'GET' || !url.protocol.startsWith('http')) return;

  // Ne PAS toucher aux Google Fonts (le navigateur s'en occupe)
  if (url.hostname === 'fonts.googleapis.com' || url.hostname === 'fonts.gstatic.com') return;

  // Images locales
  if (url.pathname.startsWith('/img/')) {
    event.respondWith(cacheFirst(req, IMG_CACHE));
    return;
  }

  // APIs
  if (url.hostname === 'api.aladhan.com' || url.hostname === 'api.alquran.cloud' || url.hostname === 'cdn.islamic.network') {
    event.respondWith(cacheFirst(req, API_CACHE));
    return;
  }

  // Serveurs mp3quran : network only (pas de cache, CSP l'autorise maintenant)
  if (/^server\d+\.mp3quran\.net$/.test(url.hostname)) {
    event.respondWith(fetch(req).catch(() => new Response('', { status: 503 })));
    return;
  }

  // Shell app
  if (url.origin === self.location.origin && /\.(css|js|woff2?|ttf|otf)$/.test(url.pathname)) {
    event.respondWith(cacheFirst(req, SHELL_CACHE));
    return;
  }

  if (url.origin === self.location.origin && (url.pathname === '/' || url.pathname === '/index.html')) {
    event.respondWith(networkFirst(req, SHELL_CACHE));
    return;
  }
});

async function cacheFirst(req, cacheName) {
  const cache = await caches.open(cacheName);
  const cached = await cache.match(req);
  if (cached) return cached;
  try {
    const res = await fetch(req);
    if (res && res.ok) cache.put(req, res.clone());
    return res;
  } catch (e) {
    return new Response('', { status: 503 });
  }
}

async function networkFirst(req, cacheName) {
  const cache = await caches.open(cacheName);
  try {
    const res = await fetch(req);
    if (res && res.ok) cache.put(req, res.clone());
    return res;
  } catch (e) {
    const cached = await cache.match(req);
    if (cached) return cached;
    if (req.mode === 'navigate') {
      const fb = await cache.match('/index.html');
      if (fb) return fb;
    }
    return new Response('', { status: 503 });
  }
}

self.addEventListener('message', event => {
  if (event.data === 'SKIP_WAITING') self.skipWaiting();
});



// ===== WAKTI ADHAN PUSH HANDLER v2 =====
self.addEventListener('push', event => {
  let data = {};
  try {
    data = event.data ? event.data.json() : {};
  } catch (e) {
    data = { title: 'Wakti', body: event.data ? event.data.text() : 'Pri\u00e8re' };
  }

  const title = data.title || 'Wakti';
  const prayer = data.prayer || 'Fajr';
  const audioPath = data.audio || '/audio/adhan-standard.mp3';

  // IMPORTANT : utiliser le son integre au lieu de postMessage
  // Sur Android, "sound" fonctionne avec un fichier dans /res/raw
  // Sur le web, on utilise le son du navigateur + fallback postMessage
  const options = {
    body: data.body || 'C\'est l\'heure de la pri\u00e8re',
    icon: data.icon || '/img/icons/icon-192.png',
    badge: data.badge || '/img/icons/icon-192.png',
    tag: data.tag || 'prayer-' + prayer + '-' + Date.now(),
    renotify: true,
    requireInteraction: true,
    vibrate: [500, 200, 500, 200, 500, 200, 500],
    silent: false,
    data: { url: data.url || '/#/prieres', prayer: prayer, audio: audioPath }
  };

  event.waitUntil(
    (async () => {
      // 1. Afficher la notification
      await self.registration.showNotification(title, options);

      // 2. Essayer de jouer l'adhan via les clients ouverts
      const clientList = await self.clients.matchAll({
        type: 'window',
        includeUncontrolled: true
      });

      if (clientList.length > 0) {
        // Envoyer le message a tous les clients ouverts
        for (const client of clientList) {
          try {
            client.postMessage({
              type: 'PLAY_ADHAN',
              prayer: prayer,
              audio: audioPath,
              timestamp: Date.now()
            });
          } catch (e) {
            console.warn('[SW] postMessage error:', e);
          }
        }
      } else {
        // Pas de client ouvert : notifier via Badging si dispo
        if (self.navigator && self.navigator.setAppBadge) {
          try { await self.navigator.setAppBadge(1); } catch (e) {}
        }
      }
    })()
  );
});

self.addEventListener('notificationclick', event => {
  event.notification.close();
  const url = (event.notification.data && event.notification.data.url)
    ? event.notification.data.url
    : '/';

  event.waitUntil(
    (async () => {
      const clientList = await self.clients.matchAll({ type: 'window' });
      for (const client of clientList) {
        if (client.url.includes(self.location.origin) && 'focus' in client) {
          client.navigate(url);
          return client.focus();
        }
      }
      if (self.clients.openWindow) return self.clients.openWindow(url);
    })()
  );
});

self.addEventListener('notificationclose', event => {
  console.log('[SW] Notification fermee :', event.notification.tag);
});
// ===== FIN WAKTI ADHAN PUSH HANDLER v2 =====
