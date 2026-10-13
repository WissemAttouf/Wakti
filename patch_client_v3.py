#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('js/auth.js', 'r', encoding='utf-8') as f:
    js = f.read()

OLD = "sb = window.supabase.createClient(config.url, config.anonKey);"

NEW = """sb = window.supabase.createClient(config.url, config.anonKey, {
      auth: {
        detectSessionInUrl: true,
        persistSession: true,
        autoRefreshToken: true,
        flowType: 'implicit'
      }
    });"""

if OLD in js:
    js = js.replace(OLD, NEW)
    with open('js/auth.js', 'w', encoding='utf-8', newline='\n') as f:
        f.write(js)
    print('OK createClient patche')
elif 'detectSessionInUrl' in js:
    print('Deja patche')
else:
    print('ERREUR : ligne introuvable')
