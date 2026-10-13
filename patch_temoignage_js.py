#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('js/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

MARKER = '/* ===== WAKTI TESTIMONIALS SYSTEM ===== */'

if MARKER in js:
    print("Système de témoignages déjà présent")
else:
    NEW_CODE = """

/* ===== WAKTI TESTIMONIALS SYSTEM ===== */
(function() {
  // Attendre que Supabase soit prêt
  function waitForSupabase(cb) {
    if (window.WaktiAuth && window.WaktiAuth.sb) {
      cb(window.WaktiAuth.sb);
    } else {
      setTimeout(() => waitForSupabase(cb), 200);
    }
  }

  // Charge les témoignages approuvés
  async function loadTestimonials(sb) {
    try {
      const { data, error } = await sb
        .from('wakti_testimonials')
        .select('author_name, author_city, rating, message, created_at')
        .eq('approved', true)
        .order('created_at', { ascending: false })
        .limit(6);

      if (error) throw error;
      return data || [];
    } catch (e) {
      console.warn('[Testimonials] Load error:', e.message);
      return null;
    }
  }

  // Affiche les témoignages
  function renderTestimonials(list) {
    const container = document.getElementById('testimonials-container');
    const section = document.getElementById('testimonials-live');
    if (!container || !section) return;

    if (!list || list.length === 0) {
      // Aucun témoignage : garder la section cachée
      section.hidden = true;
      return;
    }

    section.hidden = false;
    container.innerHTML = list.map(t => {
      const stars = '★'.repeat(t.rating) + '☆'.repeat(5 - t.rating);
      const location = t.author_city ? ', ' + escapeHtml(t.author_city) : '';
      return '<div class="testimonial-card">' +
        '<div class="stars">' + stars + '</div>' +
        '<p>"' + escapeHtml(t.message) + '"</p>' +
        '<cite>— ' + escapeHtml(t.author_name) + location +
        ' <span class="verified">Vérifié</span></cite>' +
        '</div>';
    }).join('');
  }

  // Échapper le HTML
  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, c => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[c]));
  }

  // Initialise le formulaire
  function setupForm(sb) {
    const dialog = document.getElementById('testimonialDialog');
    const openBtn = document.getElementById('openTestimonialForm');
    const closeBtn = document.getElementById('testimonialClose');
    const cancelBtn = document.getElementById('testimonialCancel');
    const form = document.getElementById('testimonialForm');
    const messageInput = document.getElementById('tMessage');
    const charCount = document.getElementById('tCharCount');
    const ratingInput = document.getElementById('ratingInput');
    const ratingHidden = document.getElementById('tRating');
    const hint = document.getElementById('testimonialHint');
    const submitBtn = document.getElementById('testimonialSubmit');

    if (!dialog || !openBtn) return;

    // Ouvrir
    openBtn.addEventListener('click', () => {
      // Vérifier si l'utilisateur est connecté
      const user = window.WaktiAuth?.state?.user;
      if (!user) {
        if (typeof toast === 'function') {
          toast('Connecte-toi d\\'abord pour laisser un témoignage', 4000);
        }
        // Ouvrir le dialogue de connexion
        if (window.WaktiAuth?.openLogin) {
          setTimeout(() => window.WaktiAuth.openLogin(), 500);
        }
        return;
      }
      // Pré-remplir le nom
      const meta = user.user_metadata || {};
      const prefName = meta.full_name || meta.name || meta.user_name || '';
      if (prefName) {
        document.getElementById('tName').value = prefName.split(' ')[0];
      }
      dialog.showModal();
    });

    // Fermer
    const closeFn = () => {
      if (dialog.close) dialog.close();
      hint.textContent = '';
      hint.className = 'testimonial-hint';
    };
    closeBtn?.addEventListener('click', closeFn);
    cancelBtn?.addEventListener('click', closeFn);

    // Compteur de caractères
    messageInput?.addEventListener('input', () => {
      const len = messageInput.value.length;
      charCount.textContent = len;
      charCount.parentElement.style.color = len > 500 ? '#e88' : '';
    });

    // Étoiles
    ratingInput?.addEventListener('click', e => {
      const btn = e.target.closest('.star-btn');
      if (!btn) return;
      const rating = parseInt(btn.dataset.rating, 10);
      ratingHidden.value = rating;
      // Mettre à jour les étoiles actives
      ratingInput.querySelectorAll('.star-btn').forEach(s => {
        const r = parseInt(s.dataset.rating, 10);
        s.classList.toggle('active', r <= rating);
      });
      if (typeof vibrate === 'function') vibrate([10]);
    });

    // Soumettre
    form?.addEventListener('submit', async e => {
      e.preventDefault();
      const name = document.getElementById('tName').value.trim();
      const city = document.getElementById('tCity').value.trim();
      const rating = parseInt(ratingHidden.value, 10) || 5;
      const message = messageInput.value.trim();

      // Validation
      if (name.length < 2) {
        hint.textContent = 'Ton prénom doit faire au moins 2 caractères.';
        hint.className = 'testimonial-hint error';
        return;
      }
      if (message.length < 10) {
        hint.textContent = 'Ton témoignage doit faire au moins 10 caractères.';
        hint.className = 'testimonial-hint error';
        return;
      }
      if (message.length > 500) {
        hint.textContent = 'Ton témoignage ne doit pas dépasser 500 caractères.';
        hint.className = 'testimonial-hint error';
        return;
      }

      submitBtn.disabled = true;
      hint.textContent = 'Envoi en cours...';
      hint.className = 'testimonial-hint';

      try {
        const user = window.WaktiAuth?.state?.user;
        const { error } = await sb.from('wakti_testimonials').insert({
          user_id: user.id,
          author_name: name,
          author_city: city || null,
          rating: rating,
          message: message,
          approved: false
        });

        if (error) throw error;

        hint.textContent = '✅ Merci ! Ton témoignage sera publié après vérification.';
        hint.className = 'testimonial-hint success';
        if (typeof toast === 'function') {
          toast('Merci pour ton témoignage ! 🌙', 4000);
        }
        if (typeof vibrate === 'function') vibrate([10, 30, 10]);

        // Vider et fermer après 2s
        setTimeout(() => {
          form.reset();
          document.getElementById('tRating').value = 5;
          ratingInput.querySelectorAll('.star-btn').forEach(s => {
            s.classList.toggle('active', parseInt(s.dataset.rating, 10) <= 5);
          });
          charCount.textContent = '0';
          closeFn();
        }, 2000);
      } catch (e) {
        console.error('[Testimonials] Insert error:', e);
        hint.textContent = 'Erreur : ' + (e.message || 'impossible d\\'envoyer');
        hint.className = 'testimonial-hint error';
      } finally {
        submitBtn.disabled = false;
      }
    });

    // Charger les témoignages
    loadTestimonials(sb).then(renderTestimonials);
  }

  // Démarrer
  waitForSupabase(sb => {
    setupForm(sb);
  });

  // Exposer pour debug
  window.WaktiTestimonials = {
    reload: () => waitForSupabase(sb => loadTestimonials(sb).then(renderTestimonials))
  };
})();
/* ===== FIN WAKTI TESTIMONIALS SYSTEM ===== */
"""

    # Insérer avant la fin du fichier (juste avant le dernier `})();` du système Adhan)
    js = js.rstrip() + '\n' + NEW_CODE

    with open('js/app.js', 'w', encoding='utf-8', newline='\n') as f:
        f.write(js)
    print("OK Systeme de temoignages ajoute a app.js")
