#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

with open('js/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Trouver le bloc ADHAN SYSTEM et le remplacer
pattern = re.compile(
    r'/\* ===== WAKTI ADHAN SYSTEM ===== \*/.*?/\* ===== WAKTI ADHAN TOGGLE ===== \*/',
    re.DOTALL
)

NEW_ADHAN_SYSTEM = """/* ===== WAKTI ADHAN SYSTEM v2 ===== */
(function() {
  if (!('serviceWorker' in navigator)) return;

  const adhanState = { enabled: true, lastPlayed: 0, currentAudio: null };

  try {
    const stored = localStorage.getItem('wakti:adhanEnabled');
    if (stored !== null) adhanState.enabled = JSON.parse(stored);
  } catch (e) {}

  // Fonction pour jouer l'adhan avec fallback
  function playAdhan(audioPath) {
    const now = Date.now();
    if (now - adhanState.lastPlayed < 30000) {
      console.log('[Adhan] Ignore (30s anti-spam)');
      return;
    }
    adhanState.lastPlayed = now;

    if (!adhanState.enabled) {
      console.log('[Adhan] Desactive par l\\'utilisateur');
      return;
    }

    // Arreter l'audio en cours
    if (adhanState.currentAudio) {
      try { adhanState.currentAudio.pause(); } catch (e) {}
    }

    const audio = new Audio(audioPath);
    audio.volume = 1.0;
    adhanState.currentAudio = audio;

    audio.play()
      .then(() => {
        console.log('[Adhan] Lecture demarree :', audioPath);
        // Toast
        if (typeof toast === 'function') {
          toast('🕌 Adhan en cours...', 3000);
        }
      })
      .catch(err => {
        console.warn('[Adhan] Lecture bloquee :', err.message);
        // Vibration de fallback
        if (navigator.vibrate) navigator.vibrate([500, 200, 500, 200, 500]);
        // Notifier l'utilisateur
        if (typeof toast === 'function') {
          toast('Cliquez sur la page pour activer l\\'audio', 5000);
        }
      });
  }

  // Ecouter les messages du Service Worker
  navigator.serviceWorker.addEventListener('message', event => {
    const data = event.data || {};
    if (data.type !== 'PLAY_ADHAN') return;
    console.log('[Adhan] Message recu :', data);
    playAdhan(data.audio || '/audio/adhan-standard.mp3');
  });

  // Detecter quand l'app revient au premier plan
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden && adhanState.currentAudio && adhanState.currentAudio.paused) {
      // L'utilisateur revient : on peut essayer de rejouer
      adhanState.currentAudio.play().catch(() => {});
    }
  });

  window.WaktiAdhan = {
    isEnabled: () => adhanState.enabled,
    setEnabled: (v) => {
      adhanState.enabled = !!v;
      try { localStorage.setItem('wakti:adhanEnabled', JSON.stringify(adhanState.enabled)); } catch (e) {}
    },
    test: () => {
      playAdhan('/audio/adhan-standard.mp3');
    },
    testFajr: () => {
      playAdhan('/audio/adhan-fajr.mp3');
    }
  };

  console.log('[Adhan] Listener pret (v2)');
})();

"""

js_new = pattern.sub(NEW_ADHAN_SYSTEM, js)

with open('js/app.js', 'w', encoding='utf-8', newline='\n') as f:
    f.write(js_new)

print('OK app.js : ADHAN SYSTEM ameliore')
