#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

print("=== REMPLACEMENT DE WIRD PAR DOUAS ===\n")

# ============================================================
# 1. MODIFIER index.html
# ============================================================
print("[1/4] Modification de index.html")

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1a. Remplacer le lien "Wird" par "Douas" dans le menu principal
OLD_NAV = """      <a href="#/wird" data-nav="wird"><svg class="ic"><use href="#i-book-open"/></svg>Wird</a>
      <a href="#/aide" data-nav="aide"><svg class="ic"><use href="#i-book"/></svg>Aide</a>"""
NEW_NAV = """      <a href="#/douas" data-nav="douas"><svg class="ic"><use href="#i-book-open"/></svg>Douas</a>
      <a href="#/aide" data-nav="aide"><svg class="ic"><use href="#i-book"/></svg>Aide</a>"""
if OLD_NAV in html:
    html = html.replace(OLD_NAV, NEW_NAV)
    print("  OK lien Douas ajoute au menu")

# 1b. Remplacer le lien "Wird" par "Douas" dans le menu mobile
OLD_BNAV = """  <a href="#/wird" data-nav="wird"><svg class="ic"><use href="#i-book-open"/></svg>Wird</a>
  <a href="#/aide" data-nav="aide"><svg class="ic"><use href="#i-book"/></svg>Aide</a>"""
NEW_BNAV = """  <a href="#/douas" data-nav="douas"><svg class="ic"><use href="#i-book-open"/></svg>Douas</a>
  <a href="#/aide" data-nav="aide"><svg class="ic"><use href="#i-book"/></svg>Aide</a>"""
if OLD_BNAV in html:
    html = html.replace(OLD_BNAV, NEW_BNAV)
    print("  OK lien Douas ajoute au menu mobile")

# 1c. Remplacer la section WIRD par DOUAS
OLD_WIRD_SECTION = """  <!-- WIRD -->
  <section id="view-wird" class="view" aria-label="Wird quotidien">
    <div class="section-head">
      <div>
        <h1 class="page-title">Mon Wird quotidien</h1>
        <p class="page-sub">Fixe un objectif et suis ta progression</p>
      </div>
    </div>
    <div class="wird-stage">
      <div class="wird-card">
        <h2>Objectif du jour</h2>
        <div class="wird-goal"><input type="number" id="wirdGoal" min="1" max="100" value="5"><span>versets / jour</span></div>
        <p class="wird-hint">Objectif suggéré : 5 versets (débutant), 20 (régulier), 100 (avancé)</p>
      </div>
      <div class="wird-progress-card">
        <h2>Progression aujourd'hui</h2>
        <div class="wird-ring-wrap">
          <svg viewBox="0 0 200 200"><circle class="wird-ring-track" cx="100" cy="100" r="80"/><circle class="wird-ring-prog" id="wirdRing" cx="100" cy="100" r="80"/></svg>
          <div class="wird-ring-in"><b id="wirdDone">0</b><small id="wirdOf">sur 5</small></div>
        </div>
        <button class="btn primary" id="wirdIncrement"><svg class="ic"><use href="#i-check"/></svg>J'ai lu un verset</button>
        <button class="btn" id="wirdReset">Réinitialiser</button>
      </div>
      <div class="wird-stats">
        <h2>Régularité</h2>
        <div class="wird-week" id="wirdWeek"></div>
        <div class="wird-total"><b id="wirdTotal">0</b><span>versets lus depuis le début</span></div>
      </div>
    </div>
  </section>"""

NEW_DOUAS_SECTION = """  <!-- DOUAS -->
  <section id="view-douas" class="view" aria-label="Douas et invocations">
    <div class="section-head">
      <div>
        <h1 class="page-title">Douas & Invocations</h1>
        <p class="page-sub">Invocations authentiques de la Sunnah pour chaque moment de la journée</p>
      </div>
    </div>

    <!-- Filtres par catégorie -->
    <div class="douas-filters" id="douasFilters">
      <button class="doua-filter active" data-category="all">Toutes</button>
    </div>

    <!-- Barre de recherche -->
    <div class="search douas-search">
      <svg class="ic"><use href="#i-search"/></svg>
      <label class="sr" for="douasSearch">Chercher une doua</label>
      <input id="douasSearch" type="search" placeholder="Chercher une doua par titre ou contenu..." autocomplete="off">
    </div>

    <!-- Liste des douas -->
    <div class="douas-list" id="douasList">
      <div class="loading"><div class="skel"></div><div class="skel"></div><div class="skel"></div></div>
    </div>
    <p class="empty" id="noDouas" hidden>Aucune doua ne correspond à ta recherche.</p>

    <!-- Bouton aléatoire -->
    <div class="douas-random">
      <button class="btn primary" id="douasRandomBtn">
        🎲 Doua aléatoire
      </button>
    </div>
  </section>"""

if OLD_WIRD_SECTION in html:
    html = html.replace(OLD_WIRD_SECTION, NEW_DOUAS_SECTION)
    print("  OK section Wird remplacee par Douas")
else:
    print("  ATTENTION : section Wird introuvable")

with open('index.html', 'w', encoding='utf-8', newline='\n') as f:
    f.write(html)


# ============================================================
# 2. MODIFIER app.js
# ============================================================
print("\n[2/4] Modification de app.js")

with open('js/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 2a. Remplacer 'wird' par 'douas' dans VIEWS
OLD_VIEWS = "const VIEWS = ['prieres', 'coran', 'calendrier', 'qibla', 'wird', 'aide'];"
NEW_VIEWS = "const VIEWS = ['prieres', 'coran', 'calendrier', 'qibla', 'douas', 'aide'];"
if OLD_VIEWS in js:
    js = js.replace(OLD_VIEWS, NEW_VIEWS)
    print("  OK route 'douas' ajoutee")

# 2b. Supprimer les fonctions Wird et les remplacer par Douas
# Trouver et supprimer la section Phase 5.6 - Wird
pattern_wird = re.compile(
    r'/\* =====================================================================\s*Phase 5\.6 — Wird quotidien\s*===================================================================== \*/.*?(?=/\* =====================================================================\s*Phase 5\.7)',
    re.DOTALL
)

NEW_DOUAS_JS = """/* =====================================================================
   Phase 5.6 — Douas quotidiennes (API fitrahive/dua-dhikr)
===================================================================== */

// Cache des douas
let douasCache = null;
let douasCategories = null;
let douasCurrentCategory = 'all';
let douasAll = [];

// API endpoints
const DOUAS_API = 'https://dua-dhikr.vercel.app';

// Charger les catégories
async function loadDouasCategories() {
  if (douasCategories) return douasCategories;
  try {
    const res = await fetch(DOUAS_API + '/categories', {
      headers: { 'Accept-Language': 'fr' }
    });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const data = await res.json();
    douasCategories = Array.isArray(data) ? data : (data.data || []);
    return douasCategories;
  } catch (e) {
    console.warn('[Douas] Categories error:', e.message);
    return [];
  }
}

// Charger toutes les douas d'une catégorie
async function loadDouasByCategory(slug) {
  try {
    const url = DOUAS_API + '/categories/' + encodeURIComponent(slug);
    const res = await fetch(url, {
      headers: { 'Accept-Language': 'fr' }
    });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const data = await res.json();
    const list = Array.isArray(data) ? data : (data.data || data.duas || []);
    // Normaliser les champs
    return list.map(d => ({
      id: d.id || Math.random().toString(36).slice(2),
      title: d.title || d.name || '',
      arabic: d.arabic || d.arab || '',
      latin: d.latin || d.transliteration || '',
      translation: d.translation || d.fr || d.meaning || '',
      notes: d.notes || d.note || '',
      fawaid: d.fawaid || d.benefits || d.virtues || '',
      source: d.source || d.reference || d.hadith || '',
      category: d.category || slug
    }));
  } catch (e) {
    console.warn('[Douas] Load category error:', e.message);
    return [];
  }
}

// Charger TOUTES les douas (toutes catégories)
async function loadAllDouas() {
  if (douasAll.length > 0) return douasAll;
  
  const cats = await loadDouasCategories();
  const promises = cats.slice(0, 20).map(c => loadDouasByCategory(c.slug || c.id));
  const results = await Promise.allSettled(promises);
  
  const all = [];
  results.forEach(r => {
    if (r.status === 'fulfilled') all.push(...r.value);
  });
  
  // Dédupliquer par id
  const seen = new Set();
  douasAll = all.filter(d => {
    if (seen.has(d.id)) return false;
    seen.add(d.id);
    return true;
  });
  
  console.log('[Douas] Chargé', douasAll.length, 'douas');
  return douasAll;
}

// Afficher une doua
function douaHTML(d) {
  return '<article class="doua-card">' +
    '<h3 class="doua-title">' + esc(d.title) + '</h3>' +
    (d.arabic ? '<p class="doua-ar" lang="ar" dir="rtl">' + esc(d.arabic) + '</p>' : '') +
    (d.latin ? '<p class="doua-latin">' + esc(d.latin) + '</p>' : '') +
    (d.translation ? '<p class="doua-translation">' + esc(d.translation) + '</p>' : '') +
    (d.notes ? '<p class="doua-notes">' + esc(d.notes) + '</p>' : '') +
    (d.fawaid ? '<p class="doua-fawaid"><b>Bienfaits :</b> ' + esc(d.fawaid) + '</p>' : '') +
    (d.source ? '<p class="doua-source"><b>Source :</b> ' + esc(d.source) + '</p>' : '') +
    '<button class="doua-copy" data-copy="' + esc((d.arabic || '') + '\\n\\n' + (d.translation || '')) + '" aria-label="Copier">' +
    '<svg class="ic"><use href="#i-copy"/></svg>' +
    '</button>' +
    '</article>';
}

// Filtrer et afficher
function renderDouas() {
  const container = document.getElementById('douasList');
  const noEl = document.getElementById('noDouas');
  if (!container) return;

  let list = douasAll;
  
  // Filtre par catégorie
  if (douasCurrentCategory !== 'all') {
    list = list.filter(d => d.category === douasCurrentCategory);
  }
  
  // Filtre par recherche
  const searchInput = document.getElementById('douasSearch');
  const q = searchInput ? searchInput.value.trim().toLowerCase() : '';
  if (q) {
    list = list.filter(d =>
      d.title.toLowerCase().includes(q) ||
      d.translation.toLowerCase().includes(q) ||
      d.arabic.includes(q)
    );
  }
  
  if (list.length === 0) {
    container.innerHTML = '';
    if (noEl) noEl.hidden = false;
    return;
  }
  
  if (noEl) noEl.hidden = true;
  container.innerHTML = list.map(douaHTML).join('');
}

// Ajouter les filtres de catégorie
async function renderDouasFilters() {
  const el = document.getElementById('douasFilters');
  if (!el) return;
  
  const cats = await loadDouasCategories();
  
  // Calculer le nombre par catégorie
  const counts = {};
  douasAll.forEach(d => {
    counts[d.category] = (counts[d.category] || 0) + 1;
  });
  
  let html = '<button class="doua-filter' + (douasCurrentCategory === 'all' ? ' active' : '') + '" data-category="all">Toutes <span class="count">' + douasAll.length + '</span></button>';
  
  cats.forEach(c => {
    const slug = c.slug || c.id;
    const name = c.name || c.title || slug;
    const count = counts[slug] || 0;
    const on = douasCurrentCategory === slug;
    html += '<button class="doua-filter' + (on ? ' active' : '') + '" data-category="' + esc(slug) + '">' + esc(name) + ' <span class="count">' + count + '</span></button>';
  });
  
  el.innerHTML = html;
}

// Initialiser
async function initDouas() {
  const container = document.getElementById('douasList');
  if (!container) return;
  
  // Charger toutes les douas
  await loadAllDouas();
  
  // Afficher les filtres
  await renderDouasFilters();
  
  // Afficher les douas
  renderDouas();
  
  // Hook recherche
  const searchInput = document.getElementById('douasSearch');
  if (searchInput && !searchInput.dataset.hooked) {
    searchInput.dataset.hooked = '1';
    searchInput.addEventListener('input', renderDouas);
  }
  
  // Hook filtres
  const filters = document.getElementById('douasFilters');
  if (filters && !filters.dataset.hooked) {
    filters.dataset.hooked = '1';
    filters.addEventListener('click', e => {
      const btn = e.target.closest('[data-category]');
      if (!btn) return;
      douasCurrentCategory = btn.dataset.category;
      filters.querySelectorAll('.doua-filter').forEach(b => {
        b.classList.toggle('active', b.dataset.category === douasCurrentCategory);
      });
      renderDouas();
      vibrate([10]);
    });
  }
  
  // Hook bouton aléatoire
  const randBtn = document.getElementById('douasRandomBtn');
  if (randBtn && !randBtn.dataset.hooked) {
    randBtn.dataset.hooked = '1';
    randBtn.addEventListener('click', () => {
      if (douasAll.length === 0) return;
      const random = douasAll[Math.floor(Math.random() * douasAll.length)];
      // Faire défiler vers la doua
      const cards = container.querySelectorAll('.doua-card');
      // Afficher un toast avec la doua
      toast(random.title + ' : ' + random.translation.slice(0, 60) + '...', 5000);
      vibrate([10, 30, 10]);
    });
  }
  
  // Hook copie
  if (!container.dataset.hooked) {
    container.dataset.hooked = '1';
    container.addEventListener('click', async e => {
      const btn = e.target.closest('[data-copy]');
      if (!btn) return;
      try {
        await navigator.clipboard.writeText(btn.dataset.copy);
        toast('Doua copiée !');
        vibrate([10]);
      } catch (err) {
        toast('Impossible de copier');
      }
    });
  }
}

// Recharger les douas quand on ouvre la vue
document.addEventListener('DOMContentLoaded', () => {
  setTimeout(() => {
    const observer = new MutationObserver(() => {
      const view = document.getElementById('view-douas');
      if (view && view.classList.contains('active') && !view.dataset.loaded) {
        view.dataset.loaded = '1';
        initDouas();
      }
    });
    document.querySelectorAll('.view').forEach(v => observer.observe(v, { attributes: true, attributeFilter: ['class'] }));
  }, 1000);
});

"""

js = pattern_wird.sub(NEW_DOUAS_JS, js)
print("  OK section Wird remplacee par Douas dans app.js")

# 2c. Remplacer 'wird' par 'douas' dans init()
js = js.replace("initWird();", "// initDouas(); // chargé automatiquement")

with open('js/app.js', 'w', encoding='utf-8', newline='\n') as f:
    f.write(js)


# ============================================================
# 3. MODIFIER style.css
# ============================================================
print("\n[3/4] Modification de style.css")

with open('css/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

NEW_CSS = """

/* =====================================================================
   Douas & Invocations
===================================================================== */

.douas-filters {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding-bottom: 10px;
  margin-bottom: 20px;
  scrollbar-width: none;
}
.douas-filters::-webkit-scrollbar { display: none; }

.doua-filter {
  flex: none;
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 999px;
  border: 1px solid var(--line);
  background: var(--card);
  color: var(--muted);
  font-size: 0.88rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 200ms;
  white-space: nowrap;
  font-family: inherit;
}

.doua-filter:hover {
  border-color: var(--gold);
  color: var(--ink);
}

.doua-filter.active {
  background: var(--gold);
  border-color: var(--gold);
  color: var(--accent-ink);
}

.doua-filter .count {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 20px;
  height: 20px;
  padding: 0 6px;
  border-radius: 10px;
  background: rgba(0, 0, 0, 0.12);
  font-size: 0.72rem;
}

.doua-filter.active .count {
  background: rgba(0, 0, 0, 0.2);
}

.douas-search {
  margin-bottom: 20px;
}

.douas-list {
  display: grid;
  gap: 16px;
  margin-bottom: 30px;
}

.doua-card {
  position: relative;
  padding: 22px 24px;
  border-radius: var(--r);
  border: 1px solid var(--line);
  background: var(--card);
  transition: border-color 200ms;
}

.doua-card:hover {
  border-color: var(--gold);
}

.doua-title {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--gold);
  margin-bottom: 14px;
  letter-spacing: -0.01em;
  padding-right: 40px;
}

.doua-ar {
  font-family: var(--font-ar);
  font-size: clamp(1.3rem, 3.5vw, 1.6rem);
  line-height: 2.1;
  color: var(--ink);
  text-align: right;
  direction: rtl;
  margin-bottom: 12px;
  padding: 12px 0;
  border-bottom: 1px dashed var(--line);
}

.doua-latin {
  font-style: italic;
  color: var(--muted);
  font-size: 0.92rem;
  line-height: 1.6;
  margin-bottom: 10px;
}

.doua-translation {
  color: var(--ink);
  font-size: 0.95rem;
  line-height: 1.65;
  margin-bottom: 12px;
}

.doua-notes {
  font-size: 0.82rem;
  color: var(--gold);
  font-weight: 600;
  margin-bottom: 8px;
}

.doua-fawaid {
  font-size: 0.85rem;
  color: var(--muted);
  line-height: 1.55;
  margin-bottom: 8px;
  padding: 10px 12px;
  border-radius: 10px;
  background: var(--hl);
}

.doua-fawaid b {
  color: var(--gold);
}

.doua-source {
  font-size: 0.78rem;
  color: var(--muted);
  font-style: italic;
  margin-top: 8px;
  padding-top: 8px;
  border-top: 1px solid var(--line);
}

.doua-source b {
  color: var(--gold);
  font-style: normal;
}

.doua-copy {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 34px;
  height: 34px;
  border-radius: 50%;
  border: 1px solid var(--line);
  background: var(--card2);
  color: var(--muted);
  display: grid;
  place-items: center;
  cursor: pointer;
  transition: all 200ms;
}

.doua-copy:hover {
  color: var(--gold);
  border-color: var(--gold);
}

.doua-copy:active {
  transform: scale(0.9);
}

.douas-random {
  text-align: center;
  padding: 20px 0;
}
"""

if '.doua-card' not in css:
    css = css.rstrip() + NEW_CSS
    with open('css/style.css', 'w', encoding='utf-8', newline='\n') as f:
        f.write(css)
    print("  OK CSS Douas ajoute")
else:
    print("  CSS deja present")


# ============================================================
# 4. VERIFICATION
# ============================================================
print("\n[4/4] Verification")

with open('index.html', 'r', encoding='utf-8') as f:
    h = f.read()
with open('js/app.js', 'r', encoding='utf-8') as f:
    j = f.read()
with open('css/style.css', 'r', encoding='utf-8') as f:
    c = f.read()

checks = {
    'view-douas dans HTML': 'view-douas' in h,
    'douasList dans HTML': 'douasList' in h,
    'douasFilters dans HTML': 'douasFilters' in h,
    'route douas dans JS': "'douas'" in j,
    'loadAllDouas dans JS': 'loadAllDouas' in j,
    '.doua-card dans CSS': '.doua-card' in c,
}

for name, ok in checks.items():
    status = "OK" if ok else "MANQUANT"
    print(f"  [{status}] {name}")

print("\n=== TERMINE ===")
print("Prochaine etape : npx vercel --prod --force")
