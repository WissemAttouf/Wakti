#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

with open('js/auth.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Nouveau HTML du dialogue de connexion
NEW_DIALOG_HTML = """const html = `
      <dialog id="loginDialog" class="login-dlg" aria-labelledby="loginTitle">
        <div class="login-content">

          <button class="login-close" id="loginClose" aria-label="Fermer">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 6l12 12M18 6L6 18"/></svg>
          </button>

          <div class="login-header">
            <div class="login-logo">
              <svg viewBox="0 0 40 40" width="64" height="64" aria-hidden="true">
                <defs>
                  <linearGradient id="lgLogin" x1="0" y1="0" x2="1" y2="1">
                    <stop offset="0" stop-color="#f6dc95"/>
                    <stop offset="1" stop-color="#c8963a"/>
                  </linearGradient>
                  <mask id="cmLogin">
                    <rect width="40" height="40" fill="#fff"/>
                    <circle cx="24" cy="15" r="11" fill="#000"/>
                  </mask>
                </defs>
                <circle cx="18" cy="21" r="14" fill="url(#lgLogin)" mask="url(#cmLogin)"/>
                <path d="M29 7.5l1.7 3.6 3.9.5-2.9 2.7.8 3.9-3.5-1.9-3.5 1.9.8-3.9-2.9-2.7 3.9-.5z" fill="url(#lgLogin)"/>
              </svg>
            </div>
            <h2 id="loginTitle">Bienvenue sur Wakti</h2>
            <p class="login-sub">Connecte-toi pour retrouver tes données sur tous tes appareils</p>
          </div>

          <div class="login-features">
            <div class="login-feature">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M6 3h12v18l-6-4-6 4z"/></svg>
              <span>Marque-pages</span>
            </div>
            <div class="login-feature">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M2 3h6a4 4 0 014 4v14a3 3 0 00-3-3H2z"/><path d="M22 3h-6a4 4 0 00-4 4v14a3 3 0 013-3h7z"/></svg>
              <span>Wird</span>
            </div>
            <div class="login-feature">
              <svg viewBox="0 0 24 24" width="16" height="16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M9 3a3 3 0 00-3 3v1a3 3 0 00-2 5 3 3 0 002 5 3 3 0 003 3h3V3H9z"/><path d="M15 3a3 3 0 013 3v1a3 3 0 012 5 3 3 0 01-2 5 3 3 0 01-3 3h-3V3h3z"/></svg>
              <span>Hifz</span>
            </div>
          </div>

          <div class="login-providers">
            <button class="login-provider" data-provider="google">
              <svg width="20" height="20" viewBox="0 0 24 24" aria-hidden="true">
                <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
              </svg>
              <span>Continuer avec Google</span>
            </button>

            <button class="login-provider" data-provider="github">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
              </svg>
              <span>Continuer avec GitHub</span>
            </button>

            <button class="login-provider" data-provider="discord">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="#5865F2" aria-hidden="true">
                <path d="M20.317 4.37a19.79 19.79 0 00-4.885-1.515.074.074 0 00-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 00-5.487 0 12.64 12.64 0 00-.617-1.25.077.077 0 00-.079-.037A19.736 19.736 0 003.677 4.37a.07.07 0 00-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 00.031.057 19.9 19.9 0 005.993 3.03.078.078 0 00.084-.028c.462-.63.874-1.295 1.226-1.994a.076.076 0 00-.041-.106 13.107 13.107 0 01-1.872-.892.077.077 0 01-.008-.128 10.2 10.2 0 00.372-.292.074.074 0 01.077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 01.078.01c.12.098.246.198.373.292a.077.077 0 01-.006.127 12.299 12.299 0 01-1.873.892.077.077 0 00-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 00.084.028 19.839 19.839 0 006.002-3.03.077.077 0 00.032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 00-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z"/>
              </svg>
              <span>Continuer avec Discord</span>
            </button>
          </div>

          <button class="login-skip" id="loginSkip" type="button">
            Continuer sans compte
          </button>

          <p class="login-legal">
            <svg viewBox="0 0 24 24" width="14" height="14" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" aria-hidden="true"><rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 018 0v4"/></svg>
            Wakti synchronise tes données sur ton compte. <strong>Aucune donnée n'est partagée avec des tiers.</strong>
          </p>

        </div>
      </dialog>
    `;"""

# Remplacer TOUT le bloc `const html = \`...\`;` par le nouveau
pattern = re.compile(r'const html = `.*?`;', re.DOTALL)
if pattern.search(js):
    js_new = pattern.sub(NEW_DIALOG_HTML, js, count=1)
    with open('js/auth.js', 'w', encoding='utf-8', newline='\n') as f:
        f.write(js_new)
    print('OK dialogue de connexion remplace')
else:
    print('ERREUR : bloc html introuvable dans auth.js')
