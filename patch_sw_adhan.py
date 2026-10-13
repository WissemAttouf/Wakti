#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

with open('sw.js', 'r', encoding='utf-8') as f:
    sw = f.read()

# Nouveau handler push qui joue l'adhan via showNotification
NEW_PUSH = """// ===== WAKTI ADHAN PUSH HANDLER v2 =====
self.addEventListener('push', event => {
  let data = {};
  try {
    data = event.data ? event.data.json() : {};
  } catch (e) {
    data = { title: 'Wakti', body: event.data ? event.data.text() : 'Pri\\u00e8re' };
  }

  const title = data.title || 'Wakti';
  const prayer = data.prayer || 'Fajr';
  const audioPath = data.audio || '/audio/adhan-standard.mp3';

  // IMPORTANT : utiliser le son integre au lieu de postMessage
  // Sur Android, "sound" fonctionne avec un fichier dans /res/raw
  // Sur le web, on utilise le son du navigateur + fallback postMessage
  const options = {
    body: data.body || 'C\\'est l\\'heure de la pri\\u00e8re',
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
"""

# Supprimer l'ancien handler
pattern = re.compile(
    r'// ===== WAKTI ADHAN PUSH HANDLER =====.*?// ===== FIN WAKTI ADHAN PUSH HANDLER =====',
    re.DOTALL
)
sw = pattern.sub('', sw)

# Ajouter le nouveau handler
if 'WAKTI ADHAN PUSH HANDLER v2' not in sw:
    sw += '\n' + NEW_PUSH

# Bump version
sw = re.sub(r"const VERSION = 'wakti-v\d+';", "const VERSION = 'wakti-v25';", sw)

with open('sw.js', 'w', encoding='utf-8', newline='\n') as f:
    f.write(sw)

print('OK sw.js mis a jour (v25)')
print('  - Handler push v2 (adhan + vibration + requireInteraction)')
print('  - Version cache bumpee')
