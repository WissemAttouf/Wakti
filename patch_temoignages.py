#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("=== MISE A JOUR DE LA SECTION TEMOIGNAGES ===\n")

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Remplacer l'ancien bloc social-proof
OLD_BLOCK = """  <!-- SECTION SOCIAL PROOF (avant le footer) -->
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
  </section>"""

NEW_BLOCK = """  <!-- SECTION CARACTÉRISTIQUES OBJECTIVES -->
  <section class="features-highlight" aria-label="Pourquoi choisir Wakti">
    <h2>✨ Pourquoi choisir Wakti ?</h2>
    <p class="section-sub">Des engagements concrets, vérifiables et sans compromis.</p>
    
    <div class="features-grid">
      <div class="feature-card">
        <div class="feature-icon">💰</div>
        <h3>100% gratuit</h3>
        <p>Aucun abonnement, aucune carte bancaire, aucune publicité. Pour toujours.</p>
      </div>
      
      <div class="feature-card">
        <div class="feature-icon">🔒</div>
        <h3>Données privées</h3>
        <p>Tes données restent sur ton appareil ou sur ton compte privé. Aucun partage avec des tiers.</p>
      </div>
      
      <div class="feature-card">
        <div class="feature-icon">📴</div>
        <h3>Fonctionne hors ligne</h3>
        <p>Pas de connexion Internet ? Pas de problème. Wakti marche quand même.</p>
      </div>
      
      <div class="feature-card">
        <div class="feature-icon">📱</div>
        <h3>Tous tes appareils</h3>
        <p>Ordinateur, tablette, smartphone. Installe Wakti sur ton écran d'accueil.</p>
      </div>
      
      <div class="feature-card">
        <div class="feature-icon">🕌</div>
        <h3>Adhan automatique</h3>
        <p>Notification et adhan à chaque prière, sans que tu aies besoin d'ouvrir l'app.</p>
      </div>
      
      <div class="feature-card">
        <div class="feature-icon">📖</div>
        <h3>Coran complet</h3>
        <p>114 sourates · 12 récitateurs · Mode Hifz pour la mémorisation · Traductions.</p>
      </div>
      
      <div class="feature-card">
        <div class="feature-icon">🌍</div>
        <h3>Partout dans le monde</h3>
        <p>Horaires de prière calculés avec précision pour n'importe quelle ville.</p>
      </div>
      
      <div class="feature-card">
        <div class="feature-icon">❤️</div>
        <h3>Fait avec soin</h3>
        <p>Développé bénévolement pour la communauté musulmane. Sans but lucratif.</p>
      </div>
    </div>

    <!-- Zone de témoignages réels (à remplir progressivement) -->
    <div class="testimonials-live" id="testimonials-live" hidden>
      <h3>💬 Ce que disent nos utilisateurs</h3>
      <div class="testimonials" id="testimonials-container">
        <!--
        Exemple de témoignage réel (à décommenter quand vous en avez) :
        
        <blockquote>
          <div class="stars">★★★★★</div>
          <p>"Enfin une app gratuite qui respecte notre religion et nos données."</p>
          <cite>— Ahmed, Tunis <span class="verified">✓ Vérifié</span></cite>
        </blockquote>
        -->
      </div>
    </div>

    <!-- Appel à témoignage -->
    <div class="testimonials-cta">
      <p>💡 <b>Tu utilises Wakti ?</b> Partage ton expérience et aide-nous à améliorer l'app.</p>
      <a href="mailto:contact@wakti.app?subject=T%C3%A9moignage%20Wakti&body=Bonjour%2C%0A%0AJe%20souhaite%20partager%20mon%20t%C3%A9moignage%20sur%20Wakti.%0A%0AMon%20pr%C3%A9nom%20%3A%20%0AMa%20ville%20%3A%20%0AMon%20exp%C3%A9rience%20%3A%20%0A%0AMerci%20!" class="btn primary">
        ✍️ Envoyer mon témoignage
      </a>
    </div>
  </section>"""

if OLD_BLOCK in html:
    html = html.replace(OLD_BLOCK, NEW_BLOCK)
    print("OK Section temoignages remplacee par caracteristiques objectives")
elif 'features-highlight' in html:
    print("Section deja mise a jour")
else:
    print("ATTENTION : bloc social-proof introuvable")

# Mettre a jour le footer (mention Wakti + contact)
OLD_FOOTER_MADE = """        <p class="footer-made">Fait avec ❤️ pour la communauté musulmane</p>"""
NEW_FOOTER_MADE = """        <p class="footer-made">Fait avec ❤️ pour la communauté musulmane</p>
        <p class="footer-made"><a href="mailto:contact@wakti.app?subject=T%C3%A9moignage" style="color:var(--gold)">✍️ Partage ton témoignage</a></p>"""

if OLD_FOOTER_MADE in html:
    html = html.replace(OLD_FOOTER_MADE, NEW_FOOTER_MADE)
    print("OK lien temoignage ajoute au footer")

with open('index.html', 'w', encoding='utf-8', newline='\n') as f:
    f.write(html)

print("\n=== TERMINE ===")
