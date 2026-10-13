#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re
import json

# ============================================================
# 1. MODIFIER sw.js — Handler push qui joue l'adhan
# ============================================================
print('=== 1/5 : Modification de sw.js ===')
with open('sw.js', 'r', encoding='utf-8') as f:
    sw = f.read()

NEW_PUSH_HANDLER = """
// ===== WAKTI ADHAN PUSH HANDLER =====
self.addEventListener('push', event => {
  const data = event.data ? event.data.json() : {};
  const options = {
    body: data.body || '',
    icon: data.icon || '/img/icons/icon-192.png',
    badge: data.badge || '/img/icons/icon-192.png',
    tag: data.tag || 'wakti',
    data: { url: data.url || '/', prayer: data.prayer || null },
    requireInteraction: data.requireInteraction === true,
    vibrate: [200, 100, 200, 100, 200]
  };

  event.waitUntil(
    (async () => {
      await self.registration.showNotification(data.title || 'Wakti', options);
      const clients = await self.clients.matchAll({
        type: 'window',
        includeUncontrolled: true
      });
      for (const client of clients) {
        client.postMessage({
          type: 'PLAY_ADHAN',
          prayer: data.prayer,
          audio: data.audio || '/audio/adhan-1.mp3'
        });
      }
    })()
  );
});

self.addEventListener('notificationclick', event => {
  event.notification.close();
  const url = event.notification.data && event.notification.data.url
    ? event.notification.data.url
    : '/';
  event.waitUntil(
    self.clients.matchAll({ type: 'window' }).then(clients => {
      for (const client of clients) {
        if (client.url.includes(self.location.origin) && 'focus' in client) {
          client.navigate(url);
          return client.focus();
        }
      }
      if (self.clients.openWindow) return self.clients.openWindow(url);
    })
  );
});
// ===== FIN WAKTI ADHAN PUSH HANDLER =====
"""

if 'WAKTI ADHAN PUSH HANDLER' in sw:
    print('  sw.js : deja patche')
else:
    sw += NEW_PUSH_HANDLER
    # Bump version pour forcer la mise a jour du cache
    sw = re.sub(r"const VERSION = 'wakti-v\d+';", "const VERSION = 'wakti-v23';", sw)
    with open('sw.js', 'w', encoding='utf-8', newline='\n') as f:
        f.write(sw)
    print('  OK sw.js patche')

# ============================================================
# 2. MODIFIER js/app.js — Ecouteur PLAY_ADHAN + toggle
# ============================================================
print('=== 2/5 : Modification de js/app.js ===')
with open('js/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

ADHAN_CODE = """

/* ===== WAKTI ADHAN SYSTEM ===== */
(function() {
  if (!('serviceWorker' in navigator)) return;

  const adhanState = { enabled: true, lastPlayed: 0 };

  try {
    const stored = localStorage.getItem('wakti:adhanEnabled');
    if (stored !== null) adhanState.enabled = JSON.parse(stored);
  } catch (e) {}

  navigator.serviceWorker.addEventListener('message', event => {
    const data = event.data || {};
    if (data.type !== 'PLAY_ADHAN') return;

    const now = Date.now();
    if (now - adhanState.lastPlayed < 30000) return;
    adhanState.lastPlayed = now;

    if (!adhanState.enabled) return;

    const audioPath = data.audio || '/audio/adhan-1.mp3';
    try {
      const audio = new Audio(audioPath);
      audio.volume = 1.0;
      audio.play().catch(err => {
        console.warn('[Adhan] Lecture bloquee :', err.message);
        if (navigator.vibrate) navigator.vibrate([500, 200, 500]);
      });
    } catch (e) {
      console.warn('[Adhan] Erreur :', e.message);
    }
  });

  window.WaktiAdhan = {
    isEnabled: () => adhanState.enabled,
    setEnabled: (v) => {
      adhanState.enabled = !!v;
      try { localStorage.setItem('wakti:adhanEnabled', JSON.stringify(adhanState.enabled)); } catch (e) {}
    },
    test: () => {
      const audio = new Audio('/audio/adhan-1.mp3');
      audio.play().catch(e => console.warn('Test adhan bloque :', e.message));
    }
  };

  console.log('[Adhan] Listener pret');
})();

/* ===== WAKTI ADHAN TOGGLE ===== */
(function() {
  const toggle = document.getElementById('adhanSw');
  if (!toggle) return;

  try {
    const stored = localStorage.getItem('wakti:adhanEnabled');
    if (stored !== null) toggle.checked = JSON.parse(stored);
  } catch (e) {}

  toggle.addEventListener('change', () => {
    const enabled = toggle.checked;
    try {
      localStorage.setItem('wakti:adhanEnabled', JSON.stringify(enabled));
    } catch (e) {}
    if (window.WaktiAdhan) window.WaktiAdhan.setEnabled(enabled);
    if (typeof toast === 'function') {
      toast(enabled ? 'Adhan active' : 'Adhan desactive', 2000);
    }
  });
})();
"""

if 'WAKTI ADHAN SYSTEM' in js:
    print('  app.js : deja patche')
else:
    js += ADHAN_CODE
    with open('js/app.js', 'w', encoding='utf-8', newline='\n') as f:
        f.write(js)
    print('  OK app.js patche')

# ============================================================
# 3. MODIFIER api/send-prayers.js — Ajouter audio dans payload
# ============================================================
print('=== 3/5 : Modification de api/send-prayers.js ===')
with open('api/send-prayers.js', 'r', encoding='utf-8') as f:
    sp = f.read()

OLD = """            tag: 'prayer-' + p.key,
            url: '/#/prieres',
            prayer: p.key
          });"""

NEW = """            tag: 'prayer-' + p.key,
            url: '/#/prieres',
            prayer: p.key,
            audio: '/audio/adhan-1.mp3',
            requireInteraction: true
          });"""

if OLD in sp:
    sp = sp.replace(OLD, NEW)
    with open('api/send-prayers.js', 'w', encoding='utf-8', newline='\n') as f:
        f.write(sp)
    print('  OK send-prayers.js patche')
elif 'audio:' in sp and 'adhan' in sp:
    print('  send-prayers.js : deja patche')
else:
    print('  ATTENTION : payload introuvable - verifier manuellement')

# ============================================================
# 4. MODIFIER index.html — Toggle Adhan
# ============================================================
print('=== 4/5 : Modification de index.html ===')
with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

if 'adhanSw' in html:
    print('  index.html : deja patche')
else:
    OLD_ROW = """<div class="sw-row"><div>Rappel à l'heure de la prière<small>Son et notification tant que Wakti reste ouvert.</small></div>"""
    NEW_ROW = """<div class="sw-row">
      <div>Adhan à l'heure de la prière<small>Jouer l'adhan quand une prière commence.</small></div>
      <label class="switch"><input type="checkbox" id="adhanSw" checked><span class="tr"></span><span class="sr">Activer</span></label>
    </div>
    <div class="sw-row"><div>Rappel à l'heure de la prière<small>Notification push quand une prière commence.</small></div>"""
    
    if OLD_ROW in html:
        html = html.replace(OLD_ROW, NEW_ROW)
        with open('index.html', 'w', encoding='utf-8', newline='\n') as f:
            f.write(html)
        print('  OK index.html patche')
    else:
        print('  ATTENTION : ligne Rappel introuvable')

# ============================================================
# 5. MODIFIER vercel.json — Cron
# ============================================================
print('=== 5/5 : Modification de vercel.json ===')
with open('vercel.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

if 'crons' in config and any(c.get('path') == '/api/send-prayers' for c in config['crons']):
    print('  vercel.json : cron deja present')
else:
    config['crons'] = [
        { "path": "/api/send-prayers", "schedule": "*/5 * * * *" }
    ]
    with open('vercel.json', 'w', encoding='utf-8', newline='\n') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)
    print('  OK vercel.json patche')

print('')
print('=== RESUME ===')
print('sw.js, app.js, send-prayers.js, index.html, vercel.json')
print('Tous patches avec succes.')
