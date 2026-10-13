#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

print("=== MISE A JOUR DU SYSTEME DE TEMOIGNAGES ===\n")

with open('js/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Nouveau systeme complet
NEW_SYSTEM = """/* ===== WAKTI TESTIMONIALS SYSTEM v2 ===== */
(function() {
  // Attendre que Supabase soit prêt
  function waitForSupabase(cb) {
    if (window.WaktiAuth && window.WaktiAuth.sb) {
      cb(window.WaktiAuth.sb);
    } else {
      setTimeout(() => waitForSupabase(cb), 200);
    }
  }

  // Échapper le HTML
  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, c => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[c]));
  }

  // Formatage de la date
  function formatDate(isoStr) {
    try {
      const d = new Date(isoStr);
      const now = new Date();
      const diffMs = now - d;
      const diffMin = Math.floor(diffMs / 60000);
      const diffH = Math.floor(diffMin / 60);
      const diffD = Math.floor(diffH / 24);

      if (diffMin < 1) return "à l'instant";
      if (diffMin < 60) return `il y a ${diffMin} min`;
      if (diffH < 24) return `il y a ${diffH}h`;
      if (diffD < 7) return `il y a ${diffD}j`;
      return d.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' });
    } catch (e) {
      return '';
    }
  }

  // Affiche un témoignage (avec état approuvé ou non)
  function testimonialHTML(t, isOwn) {
    const stars = '★'.repeat(t.rating) + '☆'.repeat(5 - t.rating);
    const location = t.author_city ? ', ' + escapeHtml(t.author_city) : '';
    const isApproved = t.approved === true;
    
    let badge = '';
    if (isApproved) {
      badge = '<span class="verified">Vérifié</span>';
    } else if (isOwn) {
      badge = '<span class="pending">En attente</span>';
    }

    // Ajouter la classe "own" pour vos propres témoignages
    const className = 'testimonial-card' + (isOwn ? ' own' : '');

    return '<div class="' + className + '" data-id="' + (t.id || '') + '">' +
      '<div class="stars">' + stars + '</div>' +
      '<p>"' + escapeHtml(t.message) + '"</p>' +
      '<cite>— ' + escapeHtml(t.author_name) + location + ' ' + badge + '</cite>' +
      '<div class="testimonial-date">' + formatDate(t.created_at) + '</div>' +
      '</div>';
  }

  // Charge les témoignages (approuvés + propres)
  async function loadTestimonials(sb) {
    const user = window.WaktiAuth?.state?.user;
    
    try {
      // 1. Charger les témoignages approuvés (publics)
      const { data: approved, error: err1 } = await sb
        .from('wakti_testimonials')
        .select('id, author_name, author_city, rating, message, approved, created_at')
        .eq('approved', true)
        .order('created_at', { ascending: false })
        .limit(10);
      
      if (err1) console.warn('[Testimonials] Approved load error:', err1.message);
      
      // 2. Charger les témoignages de l'utilisateur (même non approuvés)
      let own = [];
      if (user) {
        const { data: ownData, error: err2 } = await sb
          .from('wakti_testimonials')
          .select('id, author_name, author_city, rating, message, approved, created_at')
          .eq('user_id', user.id)
          .order('created_at', { ascending: false })
          .limit(10);
        
        if (err2) console.warn('[Testimonials] Own load error:', err2.message);
        own = ownData || [];
      }
      
      // 3. Fusionner : les propres témoignages en premier (avec marqueur)
      const ownIds = new Set(own.map(t => t.id));
      const approvedFiltered = (approved || []).filter(t => !ownIds.has(t.id));
      
      // Marquer les témoignages propres
      const ownMarked = own.map(t => ({ ...t, _isOwn: true }));
      const approvedMarked = approvedFiltered.map(t => ({ ...t, _isOwn: false }));
      
      // Trier par date
      const all = [...ownMarked, ...approvedMarked].sort((a, b) => 
        new Date(b.created_at) - new Date(a.created_at)
      );
      
      return all;
    } catch (e) {
      console.warn('[Testimonials] Load error:', e.message);
      return [];
    }
  }

  // Affiche les témoignages
  function renderTestimonials(list) {
    const container = document.getElementById('testimonials-container');
    const section = document.getElementById('testimonials-live');
    const countEl = document.getElementById('testimonialsCount');
    if (!container || !section) return;

    if (!list || list.length === 0) {
      section.hidden = true;
      return;
    }

    section.hidden = false;
    container.innerHTML = list.map(t => testimonialHTML(t, t._isOwn)).join('');
    
    // Mettre à jour le compteur
    if (countEl) {
      const publicCount = list.filter(t => t.approved).length;
      countEl.textContent = publicCount + (publicCount > 1 ? ' témoignages' : ' témoignage');
    }
    
    // Mettre à jour le titre selon le contexte
    const titleEl = section.querySelector('h3');
    if (titleEl) {
      const hasOwn = list.some(t => t._isOwn && !t.approved);
      if (hasOwn) {
        titleEl.innerHTML = '💬 Tes témoignages & ceux des utilisateurs';
      } else {
        titleEl.innerHTML = '💬 Ce que disent nos utilisateurs';
      }
    }
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
      const user = window.WaktiAuth?.state?.user;
      if (!user) {
        if (typeof toast === 'function') {
          toast('Connecte-toi d\\'abord pour laisser un témoignage', 4000);
        }
        if (window.WaktiAuth?.openLogin) {
          setTimeout(() => window.WaktiAuth.openLogin(), 500);
        }
        return;
      }
      const meta = user.user_metadata || {};
      const prefName = meta.full_name || meta.name || meta.user_name || '';
      if (prefName && !document.getElementById('tName').value) {
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
        const { data, error } = await sb.from('wakti_testimonials').insert({
          user_id: user.id,
          author_name: name,
          author_city: city || null,
          rating: rating,
          message: message,
          approved: false
        }).select();

        if (error) throw error;

        hint.textContent = '✅ Merci ! Ton témoignage est publié ci-dessous.';
        hint.className = 'testimonial-hint success';
        if (typeof toast === 'function') {
          toast('Merci pour ton témoignage ! 🌙', 4000);
        }
        if (typeof vibrate === 'function') vibrate([10, 30, 10]);

        // Fermer le dialogue
        setTimeout(() => {
          form.reset();
          document.getElementById('tRating').value = 5;
          ratingInput.querySelectorAll('.star-btn').forEach(s => {
            s.classList.toggle('active', parseInt(s.dataset.rating, 10) <= 5);
          });
          charCount.textContent = '0';
          closeFn();
        }, 1500);

        // Recharger les témoignages immédiatement
        setTimeout(() => {
          loadTestimonials(sb).then(renderTestimonials);
          
          // Faire défiler jusqu'à la section des témoignages
          const section = document.getElementById('testimonials-live');
          if (section) {
            section.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }
        }, 500);
      } catch (e) {
        console.error('[Testimonials] Insert error:', e);
        hint.textContent = 'Erreur : ' + (e.message || 'impossible d\\'envoyer');
        hint.className = 'testimonial-hint error';
      } finally {
        submitBtn.disabled = false;
      }
    });

    // Charger les témoignages initiaux
    loadTestimonials(sb).then(renderTestimonials);
  }

  // Écouter les changements d'auth pour recharger
  function watchAuth(sb) {
    if (window.WaktiAuth?.sb?.auth?.onAuthStateChange) {
      sb.auth.onAuthStateChange(() => {
        setTimeout(() => {
          loadTestimonials(sb).then(renderTestimonials);
        }, 500);
      });
    }
  }

  // Démarrer
  waitForSupabase(sb => {
    setupForm(sb);
    watchAuth(sb);
  });

  // Exposer pour debug
  window.WaktiTestimonials = {
    reload: () => waitForSupabase(sb => loadTestimonials(sb).then(renderTestimonials))
  };
})();
/* ===== FIN WAKTI TESTIMONIALS SYSTEM v2 ===== */
"""

# Supprimer l'ancien système
pattern = re.compile(
    r'/\* ===== WAKTI TESTIMONIALS SYSTEM(?: v2)? ===== \*/.*?/\* ===== FIN WAKTI TESTIMONIALS SYSTEM(?: v2)? ===== \*/',
    re.DOTALL
)
js = pattern.sub('', js)

# Ajouter le nouveau système
js = js.rstrip() + '\n\n' + NEW_SYSTEM

with open('js/app.js', 'w', encoding='utf-8', newline='\n') as f:
    f.write(js)

print("OK Systeme de temoignages mis a jour (v2)")
print("  - Affiche tes propres temoignages immediatement")
print("  - Badge 'En attente' pour non approuves")
print("  - Badge 'Verifie' pour approuves")
print("  - Scroll automatique vers la section")
