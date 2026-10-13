#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('js/auth.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Ajouter queryParams a signInWithOAuth
OLD = """      const { error } = await sb.auth.signInWithOAuth({
        provider: provider,
        options: { redirectTo: window.location.origin + window.location.pathname }
      });"""

NEW = """      const { error } = await sb.auth.signInWithOAuth({
        provider: provider,
        options: {
          redirectTo: window.location.origin + window.location.pathname,
          queryParams: {
            prompt: 'consent',
            access_type: 'offline'
          }
        }
      });"""

if OLD in js:
    js = js.replace(OLD, NEW)
    with open('js/auth.js', 'w', encoding='utf-8', newline='\n') as f:
        f.write(js)
    print('OK signInWithOAuth : prompt=consent ajoute')
elif 'prompt:' in js and 'consent' in js:
    print('Deja patche')
else:
    print('ATTENTION : bloc signInWithOAuth introuvable')
