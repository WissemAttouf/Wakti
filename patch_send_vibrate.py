#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('api/send-prayers.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Ajouter vibrate + renotify dans le payload
OLD = """          const payload = JSON.stringify({
            title: "C'est l'heure de " + p.fr,
            body: 'Wakti - ' + p.ar,
            icon: '/img/icons/icon-192.png',
            badge: '/img/icons/icon-192.png',
            tag: 'prayer-' + p.key,
            url: '/#/prieres',
            prayer: p.key,
            audio: adhanFor(p.key),
            requireInteraction: true
          });"""

NEW = """          const payload = JSON.stringify({
            title: "🕌 C'est l'heure de " + p.fr,
            body: 'Wakti - ' + p.ar + ' · Cliquez pour écouter l\\'adhan',
            icon: '/img/icons/icon-192.png',
            badge: '/img/icons/icon-192.png',
            tag: 'prayer-' + p.key + '-' + Date.now(),
            renotify: true,
            url: '/#/prieres',
            prayer: p.key,
            audio: adhanFor(p.key),
            requireInteraction: true,
            vibrate: [500, 200, 500, 200, 500, 200, 500]
          });"""

if OLD in js:
    js = js.replace(OLD, NEW)
    with open('api/send-prayers.js', 'w', encoding='utf-8', newline='\n') as f:
        f.write(js)
    print('OK send-prayers.js : vibrate + renotify + tag unique')
elif 'renotify: true' in js:
    print('Deja patche')
else:
    print('ATTENTION : payload introuvable')
