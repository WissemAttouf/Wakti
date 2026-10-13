#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('js/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Ameliorer la fonction openHifz
OLD_OPEN = """async function openHifz(n, i) {
  n = n || P.n || 1;
  i = i || 0;

  hifzState.active = true;
  hifzState.n = n;
  hifzState.i = i;
  hifzState.level = store.get('hifzLevel', 'medium');
  hifzState.revealed = false;

  const overlay = document.getElementById('hifzOverlay');
  if (overlay) overlay.hidden = false;

  // Masquer le lecteur classique
  const qLec = document.getElementById('quranLecteur');
  if (qLec) qLec.style.visibility = 'hidden';

  // Mettre a jour les infos
  updateHifzUI();

  // Charger le verset
  await renderHifzVerse();

  // Setup les event listeners (une seule fois)
  setupHifzListeners();
}"""

NEW_OPEN = """async function openHifz(n, i) {
  n = n || P.n || 1;
  i = i || 0;

  console.log('[Hifz] Ouverture pour sourate', n, 'verset', i);

  hifzState.active = true;
  hifzState.n = n;
  hifzState.i = i;
  hifzState.level = store.get('hifzLevel', 'medium');
  hifzState.revealed = false;

  // 1. Mettre l'overlay au premier plan
  const overlay = document.getElementById('hifzOverlay');
  if (!overlay) {
    console.error('[Hifz] Overlay introuvable !');
    toast('Erreur : overlay Hifz introuvable', 3000);
    return;
  }
  overlay.hidden = false;
  overlay.style.zIndex = '9999';

  // 2. Masquer le lecteur classique completement (pas juste visibility)
  const qLec = document.getElementById('quranLecteur');
  if (qLec) {
    qLec.style.display = 'none';
  }

  // 3. Mettre a jour les infos
  updateHifzUI();

  // 4. Charger le verset
  try {
    await renderHifzVerse();
  } catch (e) {
    console.error('[Hifz] Erreur chargement verset:', e);
    const arEl = document.getElementById('hifzAr');
    if (arEl) arEl.textContent = 'Erreur de chargement';
  }

  // 5. Setup les event listeners
  setupHifzListeners();

  console.log('[Hifz] Pret');
}"""

if OLD_OPEN in js:
    js = js.replace(OLD_OPEN, NEW_OPEN)
    print("OK openHifz ameliore")
else:
    print("ATTENTION : bloc openHifz introuvable - recherche par regex")

# Ameliorer aussi closeHifz
OLD_CLOSE = """function closeHifz() {
  hifzState.active = false;
  const overlay = document.getElementById('hifzOverlay');
  if (overlay) overlay.hidden = true;
  const qLec = document.getElementById('quranLecteur');
  if (qLec) qLec.style.visibility = '';
}"""

NEW_CLOSE = """function closeHifz() {
  hifzState.active = false;
  const overlay = document.getElementById('hifzOverlay');
  if (overlay) {
    overlay.hidden = true;
    overlay.style.zIndex = '';
  }
  const qLec = document.getElementById('quranLecteur');
  if (qLec) {
    qLec.style.display = '';
  }
}"""

if OLD_CLOSE in js:
    js = js.replace(OLD_CLOSE, NEW_CLOSE)
    print("OK closeHifz ameliore")
else:
    print("ATTENTION : bloc closeHifz introuvable")

with open('js/app.js', 'w', encoding='utf-8', newline='\n') as f:
    f.write(js)
