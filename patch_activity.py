#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('js/auth.js', 'r', encoding='utf-8') as f:
    js = f.read()

MARKER = '// WAKTI ACTIVITY TRACKER'

if MARKER in js:
    print('Tracker deja present')
else:
    # Ajouter la fonction de tracking AVANT updateAccountUI
    NEW_CODE = """
  // WAKTI ACTIVITY TRACKER
  async function logActivity(action, target, metadata) {
    if (!sb || !state.user) return false;
    try {
      const deviceType = /Mobi|Android|iPhone|iPad/i.test(navigator.userAgent) ? 'mobile' : 'web';
      const { error } = await sb.from('wakti_user_activity').insert({
        user_id: state.user.id,
        action: action,
        target: target || null,
        metadata: metadata || {},
        device_info: deviceType
      });
      if (error) throw error;
      return true;
    } catch (e) {
      console.warn('[Activity] log error:', e.message);
      return false;
    }
  }
  // FIN WAKTI ACTIVITY TRACKER
"""
    # Inserer avant 'function closeLoginDialog'
    idx = js.find('function closeLoginDialog')
    if idx > 0:
        js = js[:idx] + NEW_CODE + '\n  ' + js[idx:]
        print('OK tracker ajoute')

        # Exposer logActivity dans WaktiAuth
        OLD_EXPORT = """      save: saveUserData,
      load: loadUserData
    };"""
        NEW_EXPORT = """      save: saveUserData,
      load: loadUserData,
      logActivity: logActivity
    };"""
        if OLD_EXPORT in js:
            js = js.replace(OLD_EXPORT, NEW_EXPORT)
            print('OK logActivity expose dans WaktiAuth')
        else:
            print('ATTENTION : export introuvable')

        with open('js/auth.js', 'w', encoding='utf-8', newline='\n') as f:
            f.write(js)
    else:
        print('ERREUR : closeLoginDialog introuvable')
