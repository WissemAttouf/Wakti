#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('js/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Modifier le bouton "Passer" de l'onboarding
OLD_SKIP = """const skip = document.getElementById('obSkip');
  if (skip) skip.addEventListener('click', () => {
    markOnboardingDone();
    closeOnboarding();
  });"""

NEW_SKIP = """const skip = document.getElementById('obSkip');
  if (skip) skip.addEventListener('click', () => {
    markOnboardingDone();
    closeOnboarding();
    // Ouvrir le dialogue de connexion
    setTimeout(() => {
      if (window.WaktiAuth && window.WaktiAuth.openLogin) {
        window.WaktiAuth.openLogin();
      } else {
        const dlg = document.getElementById('loginDialog');
        if (dlg && dlg.showModal) dlg.showModal();
      }
    }, 400);
  });"""

if OLD_SKIP in js:
    js = js.replace(OLD_SKIP, NEW_SKIP)
    print('OK bouton Passer : ouvre maintenant le dialogue de connexion')
else:
    print('ATTENTION : bloc obSkip introuvable')

# 2. Modifier "Continuer sans compte" pour aller a la page Priere
OLD_SKIP_NOC = """// WAKTI SKIP LOGIN HANDLER
    document.addEventListener('click', e => {
      if (!e.target.closest('#loginSkip')) return;
      // Fermer le dialogue de connexion
      const dlg = document.getElementById('loginDialog');
      if (dlg && dlg.close) dlg.close();
      // Fermer l'onboarding si ouvert
      const ob = document.getElementById('onboarding');
      if (ob && ob.close) ob.close();
      // Marquer l'onboarding comme termine
      try {
        localStorage.setItem('wakti:onboardingDone', 'true');
      } catch (e) {}
      // Petit message de bienvenue
      if (typeof toast === 'function') {
        toast('Mode local : tes donnees restent sur cet appareil', 3500);
      }
    });
    // FIN WAKTI SKIP LOGIN HANDLER"""

NEW_SKIP_NOC = """// WAKTI SKIP LOGIN HANDLER
    document.addEventListener('click', e => {
      if (!e.target.closest('#loginSkip')) return;
      const dlg = document.getElementById('loginDialog');
      if (dlg && dlg.close) dlg.close();
      const ob = document.getElementById('onboarding');
      if (ob && ob.close) ob.close();
      try { localStorage.setItem('wakti:onboardingDone', 'true'); } catch (e) {}
      if (typeof toast === 'function') {
        toast('Mode local : tes donnees restent sur cet appareil', 3500);
      }
    });
    // FIN WAKTI SKIP LOGIN HANDLER"""

if OLD_SKIP_NOC in js:
    js = js.replace(OLD_SKIP_NOC, NEW_SKIP_NOC)
    print('OK handler Continuer sans compte')

with open('js/app.js', 'w', encoding='utf-8', newline='\n') as f:
    f.write(js)
