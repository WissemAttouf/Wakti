#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('js/auth.js', 'r', encoding='utf-8') as f:
    js = f.read()

MARKER = "// WAKTI SKIP LOGIN HANDLER"

if MARKER in js:
    print('Handler skip deja present')
else:
    SKIP_HANDLER = """
    // WAKTI SKIP LOGIN HANDLER
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
    // FIN WAKTI SKIP LOGIN HANDLER
"""

    # Inserer dans hookUI() juste avant la fermeture de la fonction
    OLD_HOOK_END = """    document.addEventListener('click', async e => {
      if (!e.target.closest('#loginSignup')) return;"""
    if OLD_HOOK_END in js:
        js = js.replace(OLD_HOOK_END, SKIP_HANDLER + "\n    " + OLD_HOOK_END)
        with open('js/auth.js', 'w', encoding='utf-8', newline='\n') as f:
            f.write(js)
        print('OK handler skip ajoute')
    else:
        print('ATTENTION : bloc hookUI introuvable')
