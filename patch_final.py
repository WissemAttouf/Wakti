#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("=== CORRECTION DES 2 PROBLEMES ===\n")

# ============================================================
# PROBLEME 1 : AUTHENTIFICATION
# ============================================================
print("[1/4] Correction auth.js (flowType + attente)")

with open('js/auth.js', 'r', encoding='utf-8') as f:
    auth = f.read()

# 1a. Supprimer flowType: 'implicit' (laisser par defaut = pkce)
OLD_FLOW = """    sb = window.supabase.createClient(config.url, config.anonKey, {
      auth: {
        detectSessionInUrl: true,
        persistSession: true,
        autoRefreshToken: true,
        flowType: 'implicit'
      }
    });"""

NEW_FLOW = """    sb = window.supabase.createClient(config.url, config.anonKey, {
      auth: {
        detectSessionInUrl: true,
        persistSession: true,
        autoRefreshToken: true,
        flowType: 'pkce'
      }
    });"""

if OLD_FLOW in auth:
    auth = auth.replace(OLD_FLOW, NEW_FLOW)
    print("    OK flowType: implicit -> pkce")
elif "flowType: 'pkce'" in auth:
    print("    flowType deja pkce")
else:
    print("    ATTENTION : bloc createClient introuvable")

# 1b. Ajouter attente + traitement manuel du hash apres creation du client
OLD_GETSESSION = """    // Verifier la session actuelle
    const { data: { session } } = await sb.auth.getSession();"""

NEW_GETSESSION = """    // Attendre un tick pour que Supabase traite le hash de l'URL
    await new Promise(r => setTimeout(r, 150));

    // Traiter manuellement le hash si present (fallback)
    if (window.location.hash && window.location.hash.includes('access_token')) {
      try {
        const hashParams = new URLSearchParams(window.location.hash.substring(1));
        const access_token = hashParams.get('access_token');
        const refresh_token = hashParams.get('refresh_token');
        if (access_token && refresh_token) {
          console.log('[Auth] Traitement manuel du hash OAuth');
          await sb.auth.setSession({ access_token, refresh_token });
          // Nettoyer l'URL
          history.replaceState(null, '', window.location.pathname + window.location.search);
        }
      } catch (err) {
        console.warn('[Auth] Erreur traitement hash:', err.message);
      }
    }

    // Verifier la session actuelle
    const { data: { session } } = await sb.auth.getSession();"""

if OLD_GETSESSION in auth:
    auth = auth.replace(OLD_GETSESSION, NEW_GETSESSION)
    print("    OK attente + traitement hash ajoute")
elif 'Traitement manuel du hash OAuth' in auth:
    print("    Traitement hash deja present")
else:
    print("    ATTENTION : bloc getSession introuvable")

with open('js/auth.js', 'w', encoding='utf-8', newline='\n') as f:
    f.write(auth)


# ============================================================
# PROBLEME 2 : SON DE PRIERE
# ============================================================
print("\n[2/4] Correction send-prayers.js (audio par priere)")

with open('api/send-prayers.js', 'r', encoding='utf-8') as f:
    sp = f.read()

# 2a. Ajouter fonction adhanFor
if 'function adhanFor(' not in sp:
    ADHAN_FN = """
// Choix de l'adhan selon la priere
function adhanFor(prayerKey) {
  if (prayerKey === 'Fajr') return '/audio/adhan-fajr.mp3';
  if (prayerKey === 'Maghrib') return '/audio/adhan-maghrib.mp3';
  return '/audio/adhan-standard.mp3';
}

"""
    marker = 'function isPrayerDue('
    idx = sp.find(marker)
    if idx > 0:
        sp = sp[:idx] + ADHAN_FN + sp[idx:]
        print("    OK fonction adhanFor ajoutee")
    else:
        print("    ATTENTION : marqueur isPrayerDue introuvable")
else:
    print("    adhanFor deja present")

# 2b. Remplacer audio: '/audio/adhan-1.mp3' par audio: adhanFor(p.key)
if "audio: '/audio/adhan-1.mp3'" in sp:
    sp = sp.replace("audio: '/audio/adhan-1.mp3'", "audio: adhanFor(p.key)")
    print("    OK payload utilise adhanFor(p.key)")
elif 'audio: adhanFor(p.key)' in sp:
    print("    payload deja patche")
else:
    print("    ATTENTION : payload audio introuvable")

# 2c. Ajouter ?key= support (cron-job.org)
OLD_AUTH = """    const auth = req.headers.authorization || '';
    if (!CRON_SECRET || auth !== 'Bearer ' + CRON_SECRET) {
      return res.status(401).json({ error: 'Unauthorized' });
    }"""

NEW_AUTH = """    const auth = req.headers.authorization || '';
    const queryKey = (req.query && req.query.key) || '';
    const validHeader = CRON_SECRET && auth === 'Bearer ' + CRON_SECRET;
    const validQuery = CRON_SECRET && queryKey === CRON_SECRET;

    if (!validHeader && !validQuery) {
      return res.status(401).json({ error: 'Unauthorized' });
    }"""

if OLD_AUTH in sp:
    sp = sp.replace(OLD_AUTH, NEW_AUTH)
    print("    OK support ?key= ajoute")
elif 'queryKey' in sp:
    print("    support ?key= deja present")

with open('api/send-prayers.js', 'w', encoding='utf-8', newline='\n') as f:
    f.write(sp)


print("\n[3/4] Correction app.js (fallback audio)")

with open('js/app.js', 'r', encoding='utf-8') as f:
    app = f.read()

# 3a. Remplacer adhan-1 par adhan-standard dans fallback
if "data.audio || '/audio/adhan-1.mp3'" in app:
    app = app.replace("data.audio || '/audio/adhan-1.mp3'", "data.audio || '/audio/adhan-standard.mp3'")
    print("    OK fallback adhan-standard")
elif "data.audio || '/audio/adhan-standard.mp3'" in app:
    print("    fallback deja correct")

# 3b. Test adhan-1 -> adhan-standard
if "new Audio('/audio/adhan-1.mp3')" in app:
    app = app.replace("new Audio('/audio/adhan-1.mp3')", "new Audio('/audio/adhan-standard.mp3')")
    print("    OK test() adhan-standard")

with open('js/app.js', 'w', encoding='utf-8', newline='\n') as f:
    f.write(app)


print("\n[4/4] Correction sw.js (fallback)")

with open('sw.js', 'r', encoding='utf-8') as f:
    sw = f.read()

if "data.audio || '/audio/adhan-1.mp3'" in sw:
    sw = sw.replace("data.audio || '/audio/adhan-1.mp3'", "data.audio || '/audio/adhan-standard.mp3'")
    print("    OK sw.js fallback")
else:
    print("    sw.js fallback deja correct (utilise data.audio)")

with open('sw.js', 'w', encoding='utf-8', newline='\n') as f:
    f.write(sw)


print("\n=== CORRECTIONS TERMINEES ===")
print("\nProchaines etapes :")
print("1. Verifier les fichiers audio : dir audio")
print("2. Redeployer : npx vercel --prod")
print("3. Tester en incognito")
