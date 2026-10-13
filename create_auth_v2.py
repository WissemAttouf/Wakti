#!/usr/bin/env python3
# -*- coding: utf-8 -*-

AUTH_JS = r"""/* =====================================================================
   Wakti — Authentification Supabase + Sync multi-appareils
   Supporte les 2 formats de cles : JWT (eyJ...) et publishable (sb_...)
===================================================================== */

(function() {
  'use strict';

  if (!window.supabase || !window.supabase.createClient) {
    console.warn('[Auth] Supabase client non charge');
    window.WaktiAuth = { ready: false };
    return;
  }

  let sb = null;
  const state = {
    user: null,
    session: null,
    ready: false,
    syncing: false,
    lastSync: 0
  };

  /* ------------------ Charger la config depuis /api/config ------------------ */
  async function loadConfig() {
    try {
      const res = await fetch('/api/config');
      if (!res.ok) throw new Error('HTTP ' + res.status);
      const config = await res.json();
      if (!config.configured) {
        console.warn('[Auth] Supabase non configure sur le serveur');
        return null;
      }
      return config;
    } catch (e) {
      console.warn('[Auth] Impossible de charger la config:', e);
      return null;
    }
  }

  /* ------------------ UI : Dialog de connexion ------------------ */
  function createLoginDialog() {
    if (document.getElementById('loginDialog')) return;

    const html = `
      <dialog id="loginDialog" class="login-dlg" aria-labelledby="loginTitle">
        <div class="login-content">
          <button class="login-close" id="loginClose" aria-label="Fermer">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>
          </button>
          <div class="login-header">
            <div class="login-logo">
              <svg viewBox="0 0 40 40" width="60" height="60"><defs><linearGradient id="lgLogin" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#f6dc95"/><stop offset="1" stop-color="#c8963a"/></linearGradient><mask id="cmLogin"><rect width="40" height="40" fill="#fff"/><circle cx="24" cy="15" r="11" fill="#000"/></mask></defs><circle cx="18" cy="21" r="14" fill="url(#lgLogin)" mask="url(#cmLogin)"/><path d="M29 7.5l1.7 3.6 3.9.5-2.9 2.7.8 3.9-3.5-1.9-3.5 1.9.8-3.9-2.9-2.7 3.9-.5z" fill="url(#lgLogin)"/></svg>
            </div>
            <h2 id="loginTitle">Bienvenue sur Wakti</h2>
            <p class="login-sub">Connecte-toi pour retrouver tes donnees sur tous tes appareils : marque-pages, Wird, progression Hifz.</p>
          </div>
          <div class="login-providers">
            <button class="login-provider" data-provider="google">
              <svg width="20" height="20" viewBox="0 0 24 24"><path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/><path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/><path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/><path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/></svg>
              <span>Continuer avec Google</span>
            </button>
            <button class="login-provider" data-provider="facebook">
              <svg width="20" height="20" viewBox="0 0 24 24"><path fill="#1877F2" d="M23.998 12c0-6.627-5.373-12-12-12-6.628 0-12 5.373-12 12 0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 22.954 24 17.99 24 12z"/></svg>
              <span>Continuer avec Facebook</span>
            </button>
            <button class="login-provider" data-provider="email">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/></svg>
              <span>Continuer avec Email</span>
            </button>
          </div>
          <form class="login-form" id="loginEmailForm" hidden>
            <label for="loginEmail">Adresse email</label>
            <input type="email" id="loginEmail" placeholder="ton@email.com" required autocomplete="email">
            <label for="loginPassword">Mot de passe</label>
            <input type="password" id="loginPassword" placeholder="••••••••" required autocomplete="current-password" minlength="6">
            <div class="login-form-actions">
              <button type="submit" class="login-btn primary" id="loginSubmit">Se connecter</button>
              <button type="button" class="login-btn" id="loginSignup">Creer un compte</button>
            </div>
            <p class="login-hint" id="loginHint"></p>
          </form>
          <p class="login-legal">
            En te connectant, tu acceptes que Wakti synchronise tes marque-pages, Wird et progression Hifz sur ton compte.
            <strong>Aucune donnee n'est partagee avec des tiers.</strong>
          </p>
        </div>
      </dialog>
    `;

    const div = document.createElement('div');
    div.innerHTML = html;
    document.body.appendChild(div.firstElementChild);

    const dlgSet = document.getElementById('dlgSet');
    if (dlgSet) {
      const accountBlock = document.createElement('div');
      accountBlock.className = 'field';
      accountBlock.id = 'accountField';
      accountBlock.style.cssText = 'border-top:1px solid var(--line);padding-top:16px;margin-top:12px';
      accountBlock.innerHTML = `
        <span class="lab">Mon compte</span>
        <p id="accountStatus" style="color:var(--muted);font-size:.9rem;margin-bottom:10px">Non connecte</p>
        <button class="btn primary" id="accountBtn" type="button" style="width:100%">
          <svg class="ic"><use href="#i-users"/></svg>
          <span id="accountBtnText">Se connecter</span>
        </button>
      `;
      const dlgContent = dlgSet.querySelector('.dlg');
      if (dlgContent) dlgContent.appendChild(accountBlock);
    }
  }

  /* ------------------ Fonctions Auth ------------------ */
  async function signInWithOAuth(provider) {
    if (!sb) { alert('Supabase non configure'); return; }
    try {
      const { error } = await sb.auth.signInWithOAuth({
        provider: provider,
        options: { redirectTo: window.location.origin + window.location.pathname }
      });
      if (error) throw error;
    } catch (e) {
      console.error('OAuth error:', e);
      alert('Connexion impossible : ' + e.message);
    }
  }

  async function signInWithEmail(email, password) {
    if (!sb) throw new Error('Supabase non configure');
    const { data, error } = await sb.auth.signInWithPassword({ email, password });
    if (error) throw error;
    return data;
  }

  async function signUpWithEmail(email, password) {
    if (!sb) throw new Error('Supabase non configure');
    const { data, error } = await sb.auth.signUp({
      email, password,
      options: { emailRedirectTo: window.location.origin + window.location.pathname }
    });
    if (error) throw error;
    return data;
  }

  async function signOut() {
    if (!sb) return;
    try {
      await sb.auth.signOut();
      state.user = null;
      state.session = null;
      updateAccountUI();
    } catch (e) { console.error('Signout error:', e); }
  }

  /* ------------------ Sync donnees ------------------ */
  async function saveUserData() {
    if (!sb || !state.user) return false;
    state.syncing = true;
    try {
      const data = {
        user_id: state.user.id,
        marks: store.get('marks', []),
        favRec: store.get('favRec', []),
        done: store.get('done', {}),
        best: store.get('best', 0),
        hifzLearned: store.get('hifzLearned', {}),
        hifzLevel: store.get('hifzLevel', 'medium'),
        wird: store.get('wird', { goal: 5, done: {}, total: 0 }),
        loc: store.get('loc', null),
        method: store.get('method', 'auto'),
        school: store.get('school', '0'),
        hAdj: store.get('hAdj', 0),
        theme: store.get('theme', 'dark'),
        notify: store.get('notify', false),
        autoNext: store.get('autoNext', true),
        last: store.get('last', null),
        updated_at: new Date().toISOString()
      };
      const { error } = await sb.from('wakti_user_data').upsert(data, { onConflict: 'user_id' });
      if (error) throw error;
      state.lastSync = Date.now();
      state.syncing = false;
      return true;
    } catch (e) {
      console.error('Sync save error:', e);
      state.syncing = false;
      return false;
    }
  }

  async function loadUserData() {
    if (!sb || !state.user) return false;
    try {
      const { data, error } = await sb
        .from('wakti_user_data')
        .select('*')
        .eq('user_id', state.user.id)
        .maybeSingle();
      if (error) throw error;
      if (!data) return false;

      if (Array.isArray(data.marks)) store.set('marks', data.marks);
      if (Array.isArray(data.favRec)) store.set('favRec', data.favRec);
      if (data.done && typeof data.done === 'object') store.set('done', data.done);
      if (typeof data.best === 'number') store.set('best', data.best);
      if (data.hifzLearned && typeof data.hifzLearned === 'object') store.set('hifzLearned', data.hifzLearned);
      if (typeof data.hifzLevel === 'string') store.set('hifzLevel', data.hifzLevel);
      if (data.wird && typeof data.wird === 'object') store.set('wird', data.wird);
      if (data.loc && typeof data.loc === 'object') store.set('loc', data.loc);
      if (typeof data.method === 'string') store.set('method', data.method);
      if (typeof data.school === 'string') store.set('school', data.school);
      if (typeof data.hAdj === 'number') store.set('hAdj', data.hAdj);
      if (typeof data.theme === 'string') store.set('theme', data.theme);
      if (typeof data.notify === 'boolean') store.set('notify', data.notify);
      if (typeof data.autoNext === 'boolean') store.set('autoNext', data.autoNext);
      if (data.last && typeof data.last === 'object') store.set('last', data.last);
      return true;
    } catch (e) {
      console.error('Sync load error:', e);
      return false;
    }
  }

  function startAutoSync() {
    setInterval(() => {
      if (state.user && !state.syncing) saveUserData();
    }, 30000);
  }

  /* ------------------ UI updates ------------------ */
  function updateAccountUI() {
    const status = document.getElementById('accountStatus');
    const btnText = document.getElementById('accountBtnText');
    const btn = document.getElementById('accountBtn');
    if (!status || !btnText || !btn) return;

    if (state.user) {
      const email = state.user.email || 'Utilisateur';
      status.textContent = 'Connecte : ' + email;
      status.style.color = 'var(--mint)';
      btnText.textContent = 'Se deconnecter';
      btn.classList.remove('primary');
      btn.onclick = () => signOut();
    } else {
      status.textContent = 'Non connecte (donnees locales)';
      status.style.color = 'var(--muted)';
      btnText.textContent = 'Se connecter';
      btn.classList.add('primary');
      btn.onclick = () => {
        const dlg = document.getElementById('loginDialog');
        if (dlg && dlg.showModal) dlg.showModal();
      };
    }
  }

  function closeLoginDialog() {
    const dlg = document.getElementById('loginDialog');
    if (dlg && dlg.close) dlg.close();
  }

  /* ------------------ Listeners UI ------------------ */
  function hookUI() {
    document.addEventListener('click', e => {
      const provider = e.target.closest('[data-provider]');
      if (provider) {
        const p = provider.dataset.provider;
        if (p === 'email') {
          const form = document.getElementById('loginEmailForm');
          if (form) form.hidden = !form.hidden;
        } else {
          signInWithOAuth(p);
        }
        return;
      }
      if (e.target.closest('#loginClose')) { closeLoginDialog(); return; }
    });

    document.addEventListener('submit', async e => {
      if (e.target.id !== 'loginEmailForm') return;
      e.preventDefault();
      const email = document.getElementById('loginEmail').value;
      const pwd = document.getElementById('loginPassword').value;
      const hint = document.getElementById('loginHint');
      try {
        await signInWithEmail(email, pwd);
        closeLoginDialog();
      } catch (err) {
        if (hint) hint.textContent = 'Erreur : ' + err.message;
      }
    });

    document.addEventListener('click', async e => {
      if (!e.target.closest('#loginSignup')) return;
      const email = document.getElementById('loginEmail').value;
      const pwd = document.getElementById('loginPassword').value;
      const hint = document.getElementById('loginHint');
      if (!email || !pwd) {
        if (hint) hint.textContent = 'Remplis email + mot de passe';
        return;
      }
      try {
        await signUpWithEmail(email, pwd);
        if (hint) hint.textContent = 'Verifie ta boite mail pour confirmer !';
      } catch (err) {
        if (hint) hint.textContent = 'Erreur : ' + err.message;
      }
    });
  }

  /* ------------------ Init ------------------ */
  async function init() {
    createLoginDialog();
    hookUI();

    // Charger la config depuis le serveur
    const config = await loadConfig();
    if (!config) {
      console.warn('[Auth] Config non disponible, mode local uniquement');
      updateAccountUI();
      state.ready = true;
      window.WaktiAuth = {
        ready: true,
        configured: false,
        state: state,
        openLogin: () => {
          const dlg = document.getElementById('loginDialog');
          if (dlg && dlg.showModal) {
            dlg.showModal();
            const hint = document.getElementById('loginHint');
            if (hint) hint.textContent = 'Supabase n\'est pas encore configure.';
          }
        }
      };
      return;
    }

    // Creer le client Supabase
    sb = window.supabase.createClient(config.url, config.anonKey);

    // Verifier la session actuelle
    const { data: { session } } = await sb.auth.getSession();
    if (session) {
      state.session = session;
      state.user = session.user;
      const loaded = await loadUserData();
      if (loaded) setTimeout(() => window.location.reload(), 500);
    }

    sb.auth.onAuthStateChange(async (event, session) => {
      state.session = session;
      state.user = session ? session.user : null;
      updateAccountUI();
      if (event === 'SIGNED_IN' && session) {
        const loaded = await loadUserData();
        if (loaded) setTimeout(() => window.location.reload(), 800);
      }
    });

    updateAccountUI();
    startAutoSync();
    state.ready = true;

    window.WaktiAuth = {
      ready: true,
      configured: true,
      sb: sb,
      state: state,
      signOut: signOut,
      openLogin: () => {
        const dlg = document.getElementById('loginDialog');
        if (dlg && dlg.showModal) dlg.showModal();
      },
      save: saveUserData,
      load: loadUserData
    };
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
"""

with open('js/auth.js', 'w', encoding='utf-8', newline='\n') as f:
    f.write(AUTH_JS)

print('OK js/auth.js cree (nouveau format Supabase)')
