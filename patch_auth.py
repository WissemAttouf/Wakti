#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

with open('js/auth.js', 'r', encoding='utf-8') as f:
    js = f.read()

NEW_UI = """function updateAccountUI() {
  const status = document.getElementById('accountStatus');
  const btnText = document.getElementById('accountBtnText');
  const btn = document.getElementById('accountBtn');
  if (!status || !btnText || !btn) return;

  if (state.user) {
    // ---- UTILISATEUR CONNECTÉ ----
    const meta = state.user.user_metadata || {};
    const userName =
      meta.user_name ||
      meta.preferred_username ||
      meta.name ||
      meta.full_name ||
      (state.user.email ? state.user.email.split('@')[0] : 'Utilisateur');

    const avatarUrl = meta.avatar_url || meta.picture || null;
    const provider = (state.user.app_metadata && state.user.app_metadata.provider) || 'email';
    const providerLabels = { google: 'Google', github: 'GitHub', discord: 'Discord', email: 'Email' };
    const providerLabel = providerLabels[provider] || provider;

    const firstLetter = (userName || '?').trim().charAt(0).toUpperCase() || '?';

    status.innerHTML =
      '<div class="account-profile">' +
        '<div class="account-avatar">' +
          (avatarUrl
            ? '<img src="' + avatarUrl + '" alt="" loading="lazy" onerror="this.parentElement.classList.remove(\\'has-img\\');this.parentElement.innerHTML=\\'<b>' + firstLetter + '</b>\\';">'
            : '<b>' + firstLetter + '</b>') +
        '</div>' +
        '<div class="account-meta">' +
          '<b class="account-name">' + userName + '</b>' +
          '<small class="account-provider">via ' + providerLabel + '</small>' +
        '</div>' +
      '</div>';

    btnText.textContent = 'Se deconnecter';
    btn.classList.remove('primary');
    btn.classList.add('ghost');
    btn.onclick = () => {
      if (confirm('Veux-tu vraiment te deconnecter ?')) signOut();
    };

  } else {
    // ---- NON CONNECTÉ ----
    status.innerHTML =
      '<p style="color:var(--muted);font-size:.9rem;line-height:1.5">' +
        'Connecte-toi pour synchroniser tes donnees (marque-pages, Wird, progression Hifz) sur tous tes appareils.' +
      '</p>';
    btnText.textContent = 'Se connecter';
    btn.classList.add('primary');
    btn.classList.remove('ghost');
    btn.onclick = () => {
      const dlg = document.getElementById('loginDialog');
      if (dlg && dlg.showModal) dlg.showModal();
    };
  }
}"""

# Regex : match function updateAccountUI() { ... } jusqu'au premier } de fermeture (niveau 0)
pattern = re.compile(
    r'function updateAccountUI\(\)\s*\{.*?\n\}',
    re.DOTALL
)

match = pattern.search(js)
if not match:
    print('ERREUR : updateAccountUI introuvable dans auth.js')
else:
    old_block = match.group(0)
    js_new = js.replace(old_block, NEW_UI)
    with open('js/auth.js', 'w', encoding='utf-8', newline='\n') as f:
        f.write(js_new)
    print('OK updateAccountUI remplacee dans auth.js')
