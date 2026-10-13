#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("=== AJOUT DU SYSTEME DE TEMOIGNAGES ===\n")

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Remplacer le bloc testimonials-live vide par un bloc dynamique + formulaire
OLD_BLOCK = """    <!-- Zone de témoignages réels (à remplir progressivement) -->
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

NEW_BLOCK = """    <!-- Zone de témoignages réels (dynamique, chargé depuis Supabase) -->
    <div class="testimonials-live" id="testimonials-live" hidden>
      <h3>💬 Ce que disent nos utilisateurs</h3>
      <div class="testimonials" id="testimonials-container"></div>
    </div>

    <!-- Appel à témoignage (formulaire) -->
    <div class="testimonials-cta">
      <p>💡 <b>Tu utilises Wakti ?</b> Partage ton expérience et aide-nous à améliorer l'app.</p>
      <button class="btn primary" id="openTestimonialForm" type="button">
        ✍️ Écrire mon témoignage
      </button>
    </div>
  </section>

  <!-- DIALOGUE : Formulaire de témoignage -->
  <dialog id="testimonialDialog" class="testimonial-dlg">
    <div class="testimonial-form-wrap">
      <button class="testimonial-close" id="testimonialClose" aria-label="Fermer">
        <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>
      </button>

      <div class="testimonial-header">
        <div class="testimonial-emoji">💬</div>
        <h2>Partage ton expérience</h2>
        <p>Ton témoignage aidera d'autres musulmans à découvrir Wakti, in sha Allah.</p>
      </div>

      <form id="testimonialForm" class="testimonial-form">
        <div class="testimonial-field">
          <label for="tName">Ton prénom *</label>
          <input type="text" id="tName" placeholder="Ex. Ahmed" required minlength="2" maxlength="50" autocomplete="given-name">
        </div>

        <div class="testimonial-field">
          <label for="tCity">Ta ville (optionnel)</label>
          <input type="text" id="tCity" placeholder="Ex. Tunis" maxlength="50" autocomplete="address-level2">
        </div>

        <div class="testimonial-field">
          <label for="tRating">Ta note</label>
          <div class="rating-input" id="ratingInput">
            <button type="button" class="star-btn" data-rating="1" aria-label="1 étoile">★</button>
            <button type="button" class="star-btn" data-rating="2" aria-label="2 étoiles">★</button>
            <button type="button" class="star-btn" data-rating="3" aria-label="3 étoiles">★</button>
            <button type="button" class="star-btn" data-rating="4" aria-label="4 étoiles">★</button>
            <button type="button" class="star-btn active" data-rating="5" aria-label="5 étoiles">★</button>
          </div>
          <input type="hidden" id="tRating" value="5">
        </div>

        <div class="testimonial-field">
          <label for="tMessage">Ton témoignage *</label>
          <textarea id="tMessage" placeholder="Comment Wakti t'aide dans ta pratique quotidienne ? (10 à 500 caractères)" required minlength="10" maxlength="500" rows="4"></textarea>
          <div class="char-counter"><span id="tCharCount">0</span> / 500 caractères</div>
        </div>

        <p class="testimonial-hint" id="testimonialHint"></p>

        <div class="testimonial-actions">
          <button type="button" class="btn" id="testimonialCancel">Annuler</button>
          <button type="submit" class="btn primary" id="testimonialSubmit">
            <svg class="ic"><use href="#i-check"/></svg>
            Envoyer
          </button>
        </div>

        <p class="testimonial-legal">
          <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 018 0v4"/></svg>
          Ton témoignage sera <strong>modéré</strong> avant publication. Il sera visible publiquement avec ton prénom et ta ville (si fournie).
        </p>
      </form>
    </div>
  </dialog>"""

if OLD_BLOCK in html:
    html = html.replace(OLD_BLOCK, NEW_BLOCK)
    print("OK Formulaire temoignage ajoute")
elif 'testimonialDialog' in html:
    print("Formulaire deja present")
else:
    print("ATTENTION : bloc testimonials-cta introuvable")

with open('index.html', 'w', encoding='utf-8', newline='\n') as f:
    f.write(html)

print("\n=== TERMINE ===")
