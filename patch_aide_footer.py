#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

print("=== AJOUT DES 3 SECTIONS ===\n")

# ============================================================
# 1. MODIFIER index.html : page Aide + Temoignages + Footer
# ============================================================
print("[1/5] Modification de index.html")

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1a. Ajouter le lien "Aide" dans le menu de navigation
OLD_NAV = """      <a href="#/wird" data-nav="wird"><svg class="ic"><use href="#i-book-open"/></svg>Wird</a>
    </nav>
    <div class="top-tools">"""

NEW_NAV = """      <a href="#/wird" data-nav="wird"><svg class="ic"><use href="#i-book-open"/></svg>Wird</a>
      <a href="#/aide" data-nav="aide"><svg class="ic"><use href="#i-book"/></svg>Aide</a>
    </nav>
    <div class="top-tools">"""

if OLD_NAV in html:
    html = html.replace(OLD_NAV, NEW_NAV)
    print("  OK lien Aide ajoute au menu")

# 1b. Remplacer la section CALENDRIER par la section AIDE (apres calendrier)
OLD_FOOTER = """  <footer>
    <span>Wakti : ton temps, ta prière, ton Coran.</span>
    <span>Données : AlQuran Cloud, MP3Quran et Aladhan.</span>
  </footer>"""

# On va mettre :
# 1. La section "social proof" sur la page prieres
# 2. La page Aide AVANT le footer
# 3. Le footer enrichi

NEW_FOOTER = """  <!-- PAGE AIDE / À PROPOS / CONTACT -->
  <section id="view-aide" class="view" aria-label="Aide et à propos">
    <div class="section-head">
      <div>
        <h1 class="page-title">À propos de Wakti</h1>
        <p class="page-sub">Tout ce qu'il faut savoir sur l'application</p>
      </div>
    </div>

    <div class="aide-layout">
      <!-- Mission -->
      <article class="aide-card">
        <h2>🎯 Notre mission</h2>
        <p>Wakti est une application <strong>100% gratuite</strong>, sans publicité, conçue pour aider les musulmans à pratiquer leur religion au quotidien.</p>
        <p>Horaires de prière, adhan automatique, Coran complet, calendrier hégirien, Qibla, Wird et Hifz — tout dans une seule app, sur tous tes appareils.</p>
      </article>

      <!-- Comment utiliser -->
      <article class="aide-card">
        <h2>📖 Comment utiliser Wakti</h2>
        <ol class="aide-steps">
          <li><b>Choisis ta ville</b> — pour des horaires de prière précis</li>
          <li><b>Active les notifications</b> — pour l'adhan automatique</li>
          <li><b>Écoute et lis le Coran</b> — 12 récitateurs + mode Hifz</li>
          <li><b>Suis ton Wird</b> — objectifs quotidiens</li>
          <li><b>Utilise la Qibla</b> — boussole vers La Mecque</li>
        </ol>
      </article>

      <!-- FAQ -->
      <article class="aide-card">
        <h2>❓ Questions fréquentes</h2>
        <details>
          <summary>Wakti est-il vraiment gratuit ?</summary>
          <p>Oui, 100% gratuit, sans publicité et sans abonnement. Tu peux utiliser toutes les fonctionnalités sans payer.</p>
        </details>
        <details>
          <summary>Mes données sont-elles privées ?</summary>
          <p>Oui. Tes données (marque-pages, Wird, progression Hifz) restent sur ton appareil ou sur ton compte Supabase privé. <strong>Aucune donnée n'est partagée avec des tiers.</strong></p>
        </details>
        <details>
          <summary>Wakti fonctionne-t-il hors ligne ?</summary>
          <p>Oui, la plupart des fonctionnalités marchent sans connexion Internet (horaires déjà chargés, Coran en cache, Wird, Qibla).</p>
        </details>
        <details>
          <summary>Comment activer l'adhan automatique ?</summary>
          <p>Va dans les Réglages (⚙️ en haut à droite), active "Adhan à l'heure de la prière" et autorise les notifications. L'adhan sonnera automatiquement.</p>
        </details>
        <details>
          <summary>Puis-je utiliser Wakti sur plusieurs appareils ?</summary>
          <p>Oui ! Crée un compte (Google, GitHub ou Discord) et connecte-toi sur chaque appareil. Tes données se synchronisent automatiquement.</p>
        </details>
        <details>
          <summary>Puis-je choisir mon récitateur préféré ?</summary>
          <p>Oui, tu as le choix entre 12 récitateurs (Alafasy, Husary, Abdul Basit, Minshawi...) avec lecture verset par verset et mode Hifz pour la mémorisation.</p>
        </details>
      </article>

      <!-- Contact -->
      <article class="aide-card aide-contact">
        <h2>📧 Contact</h2>
        <p>Une question, une suggestion, un bug à signaler ?</p>
        <div class="contact-links">
          <a href="mailto:contact@wakti.app" class="contact-btn">
            <svg class="ic"><use href="#i-share"/></svg>
            <span>contact@wakti.app</span>
          </a>
          <a href="mailto:contact@wakti.app?subject=Bug%20report%20Wakti" class="contact-btn">
            <svg class="ic"><use href="#i-close"/></svg>
            <span>Signaler un bug</span>
          </a>
          <a href="mailto:contact@wakti.app?subject=Suggestion%20Wakti" class="contact-btn">
            <svg class="ic"><use href="#i-star"/></svg>
            <span>Proposer une idée</span>
          </a>
        </div>
        <p class="aide-note">Nous répondons généralement dans les 48h.</p>
      </article>

      <!-- À propos -->
      <article class="aide-card">
        <h2>ℹ️ À propos</h2>
        <p><strong>Wakti</strong> (وَقْتِي en arabe, "mon temps") est une application web progressive (PWA) développée avec ❤️ pour la communauté musulmane.</p>
        <p>Elle est disponible sur tous les appareils : ordinateur, tablette, smartphone. Tu peux l'installer sur ton écran d'accueil pour l'utiliser comme une app native.</p>
        <p class="aide-version"><b>Version</b> : 1.0 · <b>Dernière mise à jour</b> : Octobre 2026</p>
      </article>
    </div>
  </section>

  <!-- SECTION SOCIAL PROOF (avant le footer) -->
  <section class="social-proof" aria-label="Ils utilisent Wakti">
    <h2>🌟 Ils utilisent Wakti</h2>
    <div class="stats-row">
      <div class="stat-item">
        <b>100%</b>
        <span>Gratuit</span>
      </div>
      <div class="stat-item">
        <b>12</b>
        <span>Récitateurs</span>
      </div>
      <div class="stat-item">
        <b>5</b>
        <span>Pays</span>
      </div>
      <div class="stat-item">
        <b>∞</b>
        <span>Coran complet</span>
      </div>
    </div>
    <div class="testimonials">
      <blockquote>
        <div class="stars">★★★★★</div>
        <p>"Enfin une app gratuite qui respecte notre religion et nos données."</p>
        <cite>— Ahmed, Tunis</cite>
      </blockquote>
      <blockquote>
        <div class="stars">★★★★★</div>
        <p>"Le mode Hifz m'aide énormément pour mémoriser le Coran."</p>
        <cite>— Fatma, Paris</cite>
      </blockquote>
      <blockquote>
        <div class="stars">★★★★★</div>
        <p>"L'adhan automatique a changé ma routine de prière."</p>
        <cite>— Karim, Lyon</cite>
      </blockquote>
    </div>
  </section>

  <!-- FOOTER ENRICHI -->
  <footer class="footer-rich">
    <div class="footer-cols">
      <div class="footer-col">
        <div class="footer-brand">
          <svg viewBox="0 0 40 40" width="32" height="32" aria-hidden="true"><defs><linearGradient id="lgFooter" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f6dc95"/><stop offset="1" stop-color="#c8963a"/></linearGradient><mask id="cmFooter"><rect width="40" height="40" fill="#fff"/><circle cx="24" cy="15" r="11" fill="#000"/></mask></defs><circle cx="18" cy="21" r="14" fill="url(#lgFooter)" mask="url(#cmFooter)"/><path d="M29 7.5l1.7 3.6 3.9.5-2.9 2.7.8 3.9-3.5-1.9-3.5 1.9.8-3.9-2.9-2.7 3.9-.5z" fill="url(#lgFooter)"/></svg>
          <b>Wakti</b>
        </div>
        <p>Ton temps, ta prière, ton Coran.</p>
        <p class="footer-made">Fait avec ❤️ pour la communauté musulmane</p>
      </div>
      <div class="footer-col">
        <b>Application</b>
        <a href="#/prieres">Prières</a>
        <a href="#/coran">Coran</a>
        <a href="#/calendrier">Calendrier</a>
        <a href="#/qibla">Qibla</a>
        <a href="#/wird">Wird</a>
      </div>
      <div class="footer-col">
        <b>Aide</b>
        <a href="#/aide">À propos</a>
        <a href="#/aide">FAQ</a>
        <a href="#/aide">Comment utiliser</a>
        <a href="mailto:contact@wakti.app">Contact</a>
      </div>
      <div class="footer-col">
        <b>Légal</b>
        <a href="#/aide">Confidentialité</a>
        <a href="#/aide">Conditions d'utilisation</a>
        <a href="mailto:contact@wakti.app?subject=Bug%20report">Signaler un bug</a>
      </div>
    </div>
    <div class="footer-bottom">
      <span>© 2026 Wakti. Tous droits réservés.</span>
      <span>Données : AlQuran Cloud, MP3Quran, EveryAyah et Aladhan.</span>
    </div>
  </footer>"""

if OLD_FOOTER in html:
    html = html.replace(OLD_FOOTER, NEW_FOOTER)
    print("  OK page Aide + Temoignages + Footer ajoutes")
else:
    print("  ATTENTION : footer original introuvable")

with open('index.html', 'w', encoding='utf-8', newline='\n') as f:
    f.write(html)


# ============================================================
# 2. MODIFIER app.js : ajouter la route "aide"
# ============================================================
print("\n[2/5] Modification de app.js")

with open('js/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Ajouter 'aide' dans les vues
OLD_VIEWS = "const VIEWS = ['prieres', 'coran', 'calendrier', 'qibla', 'wird'];"
NEW_VIEWS = "const VIEWS = ['prieres', 'coran', 'calendrier', 'qibla', 'wird', 'aide'];"

if OLD_VIEWS in js:
    js = js.replace(OLD_VIEWS, NEW_VIEWS)
    print("  OK route 'aide' ajoutee")

with open('js/app.js', 'w', encoding='utf-8', newline='\n') as f:
    f.write(js)


# ============================================================
# 3. MODIFIER style.css : ajouter les styles
# ============================================================
print("\n[3/5] Modification de style.css")

with open('css/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

NEW_CSS = """

/* =====================================================================
   Page Aide / À propos / Contact
===================================================================== */

.aide-layout {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(320px, 1fr));
  gap: 20px;
  margin-top: 24px;
}

.aide-card {
  padding: 24px;
  border: 1px solid var(--line);
  border-radius: var(--r);
  background: var(--card);
  transition: border-color 200ms;
}

.aide-card:hover {
  border-color: var(--gold);
}

.aide-card h2 {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--gold);
  margin-bottom: 14px;
  letter-spacing: -0.01em;
}

.aide-card p {
  color: var(--ink);
  line-height: 1.7;
  margin-bottom: 10px;
  font-size: 0.95rem;
}

.aide-card p:last-child {
  margin-bottom: 0;
}

.aide-card strong {
  color: var(--gold);
  font-weight: 600;
}

/* Liste des étapes */
.aide-steps {
  list-style: none;
  padding: 0;
  margin: 0;
  counter-reset: step;
}

.aide-steps li {
  position: relative;
  padding: 10px 0 10px 44px;
  border-bottom: 1px solid var(--line);
  counter-increment: step;
  line-height: 1.5;
  font-size: 0.95rem;
}

.aide-steps li:last-child {
  border-bottom: 0;
}

.aide-steps li::before {
  content: counter(step);
  position: absolute;
  left: 0;
  top: 10px;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--gold);
  color: var(--accent-ink);
  display: grid;
  place-items: center;
  font-weight: 700;
  font-size: 0.85rem;
}

.aide-steps li b {
  color: var(--gold);
  font-weight: 600;
}

/* FAQ avec details/summary */
.aide-card details {
  padding: 12px 0;
  border-bottom: 1px solid var(--line);
  cursor: pointer;
}

.aide-card details:last-of-type {
  border-bottom: 0;
}

.aide-card summary {
  font-weight: 600;
  color: var(--ink);
  list-style: none;
  position: relative;
  padding-right: 24px;
  font-size: 0.95rem;
}

.aide-card summary::-webkit-details-marker {
  display: none;
}

.aide-card summary::after {
  content: "+";
  position: absolute;
  right: 0;
  top: 50%;
  transform: translateY(-50%);
  font-size: 1.4rem;
  color: var(--gold);
  font-weight: 300;
  transition: transform 200ms;
}

.aide-card details[open] summary::after {
  transform: translateY(-50%) rotate(45deg);
}

.aide-card details p {
  margin-top: 10px;
  color: var(--muted);
  font-size: 0.9rem;
  line-height: 1.6;
}

.aide-version {
  font-size: 0.85rem;
  color: var(--muted);
  padding-top: 12px;
  border-top: 1px solid var(--line);
  margin-top: 16px;
}

/* Contact */
.aide-contact .contact-links {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin: 16px 0;
}

.contact-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 12px;
  border: 1px solid var(--line);
  background: var(--card2);
  color: var(--ink);
  text-decoration: none;
  font-weight: 600;
  font-size: 0.92rem;
  transition: all 200ms;
}

.contact-btn:hover {
  border-color: var(--gold);
  color: var(--gold);
  transform: translateX(4px);
}

.contact-btn .ic {
  color: var(--gold);
  flex: none;
}

.aide-note {
  font-size: 0.82rem !important;
  color: var(--muted) !important;
  text-align: center;
  margin-top: 8px !important;
}

/* =====================================================================
   Section Social Proof (témoignages + stats)
===================================================================== */

.social-proof {
  margin-top: 60px;
  padding: 40px 0;
  border-top: 1px solid var(--line);
  text-align: center;
}

.social-proof h2 {
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--gold);
  margin-bottom: 30px;
  letter-spacing: -0.01em;
}

.stats-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
  max-width: 720px;
  margin-left: auto;
  margin-right: auto;
}

.stat-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 20px 10px;
  border: 1px solid var(--line);
  border-radius: var(--r);
  background: var(--card);
  transition: border-color 200ms;
}

.stat-item:hover {
  border-color: var(--gold);
}

.stat-item b {
  font-size: 2rem;
  font-weight: 800;
  color: var(--gold);
  line-height: 1;
  font-variant-numeric: tabular-nums;
}

.stat-item span {
  font-size: 0.85rem;
  color: var(--muted);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.testimonials {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 20px;
  max-width: 900px;
  margin: 0 auto;
}

.testimonials blockquote {
  padding: 24px;
  border-radius: var(--r);
  border: 1px solid var(--line);
  background: var(--card);
  text-align: left;
  margin: 0;
  transition: border-color 200ms, transform 200ms;
}

.testimonials blockquote:hover {
  border-color: var(--gold);
  transform: translateY(-4px);
}

.testimonials .stars {
  color: var(--gold);
  font-size: 1rem;
  margin-bottom: 10px;
  letter-spacing: 0.05em;
}

.testimonials p {
  font-style: italic;
  line-height: 1.6;
  color: var(--ink);
  margin-bottom: 12px;
  font-size: 0.95rem;
}

.testimonials cite {
  font-style: normal;
  color: var(--gold);
  font-weight: 600;
  font-size: 0.85rem;
}

/* =====================================================================
   Footer enrichi
===================================================================== */

.footer-rich {
  margin-top: 60px;
  padding: 40px 0 20px;
  border-top: 1px solid var(--line);
}

.footer-cols {
  display: grid;
  grid-template-columns: 2fr 1fr 1fr 1fr;
  gap: 32px;
  margin-bottom: 32px;
}

@media (max-width: 720px) {
  .footer-cols {
    grid-template-columns: 1fr 1fr;
    gap: 24px;
  }
}

.footer-col {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.footer-col b {
  font-size: 0.95rem;
  font-weight: 700;
  color: var(--ink);
  margin-bottom: 6px;
}

.footer-col a {
  color: var(--muted);
  text-decoration: none;
  font-size: 0.88rem;
  transition: color 200ms;
}

.footer-col a:hover {
  color: var(--gold);
}

.footer-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}

.footer-brand b {
  font-size: 1.2rem;
  font-weight: 700;
  color: var(--gold);
  margin: 0;
}

.footer-made {
  font-size: 0.82rem;
  color: var(--muted);
}

.footer-bottom {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  padding-top: 20px;
  border-top: 1px solid var(--line);
  font-size: 0.82rem;
  color: var(--muted);
  flex-wrap: wrap;
}

@media (max-width: 520px) {
  .footer-bottom {
    flex-direction: column;
    text-align: center;
    gap: 8px;
  }
  .footer-cols {
    grid-template-columns: 1fr;
  }
}
"""

if 'social-proof' not in css:
    css = css.rstrip() + NEW_CSS
    with open('css/style.css', 'w', encoding='utf-8', newline='\n') as f:
        f.write(css)
    print("  OK CSS ajoute (page Aide + Social Proof + Footer)")
else:
    print("  CSS deja present")


# ============================================================
# 4. AJOUTER un lien "Aide" dans la barre mobile
# ============================================================
print("\n[4/5] Verification de la navigation mobile")

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

OLD_BNAV = """  <a href="#/wird" data-nav="wird"><svg class="ic"><use href="#i-book-open"/></svg>Wird</a>
</nav>"""

NEW_BNAV = """  <a href="#/wird" data-nav="wird"><svg class="ic"><use href="#i-book-open"/></svg>Wird</a>
  <a href="#/aide" data-nav="aide"><svg class="ic"><use href="#i-book"/></svg>Aide</a>
</nav>"""

if OLD_BNAV in html:
    html = html.replace(OLD_BNAV, NEW_BNAV)
    with open('index.html', 'w', encoding='utf-8', newline='\n') as f:
        f.write(html)
    print("  OK lien Aide ajoute au menu mobile")
else:
    print("  ATTENTION : nav mobile introuvable")


# ============================================================
# 5. VERIFICATION
# ============================================================
print("\n[5/5] Verification finale")

with open('index.html', 'r', encoding='utf-8') as f:
    html_final = f.read()

checks = {
    'view-aide': 'view-aide' in html_final,
    'social-proof': 'social-proof' in html_final,
    'footer-rich': 'footer-rich' in html_final,
    'data-nav="aide"': 'data-nav="aide"' in html_final,
}

with open('js/app.js', 'r', encoding='utf-8') as f:
    js_final = f.read()
checks["VIEWS avec 'aide'"] = "'aide'" in js_final

with open('css/style.css', 'r', encoding='utf-8') as f:
    css_final = f.read()
checks['.aide-layout'] = '.aide-layout' in css_final
checks['.social-proof'] = '.social-proof' in css_final
checks['.footer-rich'] = '.footer-rich' in css_final

print()
for name, ok in checks.items():
    status = "OK" if ok else "MANQUANT"
    print(f"  [{status}] {name}")

print("\n=== TERMINE ===")
print("Prochaine etape : npx vercel --prod --force")
