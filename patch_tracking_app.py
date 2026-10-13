#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('js/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Helper : wrapper pour appeler logActivity
HELPER = """

/* ===== WAKTI ACTION LOGGING HELPERS ===== */
function waktiLog(action, target, metadata) {
  if (window.WaktiAuth && typeof window.WaktiAuth.logActivity === 'function') {
    window.WaktiAuth.logActivity(action, target, metadata);
  }
}
// FIN WAKTI ACTION LOGGING HELPERS
"""

MARKER = '// WAKTI ACTION LOGGING HELPERS'

if MARKER in js:
    print('Helpers deja presents')
else:
    js = HELPER + js
    print('OK helpers ajoutes')

    # 1. Logger apres toggleDone (priere marquee)
    OLD_TD = """  store.set('done', done);
  vibrate([10, 30, 10]);
  refreshDone();
  renderStreak();
}"""
    NEW_TD = """  store.set('done', done);
  vibrate([10, 30, 10]);
  waktiLog('check_prayer', 'prayer:' + k, { date: tk });
  refreshDone();
  renderStreak();
}"""
    if OLD_TD in js:
        js = js.replace(OLD_TD, NEW_TD)
        print('  OK tracking priere')

    # 2. Logger apres lecture sourate (openMushafForSurah)
    OLD_READ = """    await openMushafPage(p);
    store.set('last', { mode: 'lire', n });
    renderResume();"""
    NEW_READ = """    await openMushafPage(p);
    store.set('last', { mode: 'lire', n });
    waktiLog('read_surah', 'surah:' + n);
    renderResume();"""
    if OLD_READ in js:
        js = js.replace(OLD_READ, NEW_READ)
        print('  OK tracking lecture sourate')

    # 3. Logger apres playAt (ecoute verset)
    OLD_PLAY = """  store.set('last', { mode: 'ecouter', reciter: rid, n, i });
  renderResume();
  
}"""
    NEW_PLAY = """  store.set('last', { mode: 'ecouter', reciter: rid, n, i });
  waktiLog('listen_verse', 'surah:' + n + ':' + (i + 1), { reciter: rid });
  renderResume();
  
}"""
    if OLD_PLAY in js:
        js = js.replace(OLD_PLAY, NEW_PLAY)
        print('  OK tracking ecoute')

    # 4. Logger Hifz (markVerseLearned)
    OLD_HIFZ = """  setLearned(all);
}"""
    NEW_HIFZ = """  setLearned(all);
  if (learned) waktiLog('mark_hifz', 'verse:' + n + ':' + (i + 1));
}"""
    if OLD_HIFZ in js:
        js = js.replace(OLD_HIFZ, NEW_HIFZ)
        print('  OK tracking Hifz')

    # 5. Logger Wird
    OLD_WIRD = """    data.total = (data.total || 0) + 1;
    setWirdData(data);
    vibrate([10, 30, 10]);"""
    NEW_WIRD = """    data.total = (data.total || 0) + 1;
    setWirdData(data);
    waktiLog('check_wird', 'wird:' + data.goal, { total: data.total });
    vibrate([10, 30, 10]);"""
    if OLD_WIRD in js:
        js = js.replace(OLD_WIRD, NEW_WIRD)
        print('  OK tracking Wird')

    with open('js/app.js', 'w', encoding='utf-8', newline='\n') as f:
        f.write(js)
    print('OK app.js patche')
