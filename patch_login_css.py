#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

with open('css/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

# Supprimer l'ancien bloc de CSS du dialogue de connexion (si present)
pattern = re.compile(
    r'/\* =+ *\n\s*Authentification Supabase[^\n]*\n=+ \*/.*?(?=/\* ={5,}|\Z)',
    re.DOTALL
)
css = pattern.sub('', css)

NEW_CSS = """
/* =====================================================================
   Dialogue de connexion (redesign moderne)
===================================================================== */

.login-dlg {
  width: min(440px, 94vw);
  max-height: 92vh;
  border: 0;
  border-radius: 24px;
  padding: 0;
  background: var(--panel);
  color: var(--ink);
  overflow: hidden;
  box-shadow: 0 24px 60px -20px rgba(0, 0, 0, .6);
  animation: loginEnter 400ms cubic-bezier(.34, 1.56, .64, 1);
}

@keyframes loginEnter {
  from { opacity: 0; transform: scale(.92) translateY(20px); }
  to   { opacity: 1; transform: scale(1) translateY(0); }
}

.login-dlg::backdrop {
  background: rgba(0, 0, 0, 0.7);
  -webkit-backdrop-filter: blur(8px);
  backdrop-filter: blur(8px);
  animation: backdropFade 300ms ease-out;
}

@keyframes backdropFade {
  from { opacity: 0; }
  to   { opacity: 1; }
}

.login-content {
  padding: 36px 28px 28px;
  position: relative;
  overflow-y: auto;
  max-height: 92vh;
}

.login-close {
  position: absolute;
  top: 16px;
  right: 16px;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid var(--line);
  background: var(--card);
  color: var(--muted);
  display: grid;
  place-items: center;
  cursor: pointer;
  transition: all 200ms;
  z-index: 10;
}

.login-close:hover {
  color: var(--gold);
  border-color: var(--gold);
  transform: rotate(90deg);
}

/* En-tete */
.login-header {
  text-align: center;
  margin-bottom: 24px;
}

.login-logo {
  display: inline-block;
  margin-bottom: 12px;
  filter: drop-shadow(0 8px 20px rgba(230, 189, 99, 0.4));
  animation: logoFloat 3s ease-in-out infinite;
}

@keyframes logoFloat {
  0%, 100% { transform: translateY(0); }
  50%      { transform: translateY(-4px); }
}

.login-header h2 {
  font-size: 1.5rem;
  font-weight: 700;
  margin-bottom: 8px;
  letter-spacing: -0.01em;
}

.login-sub {
  color: var(--muted);
  font-size: 0.9rem;
  line-height: 1.5;
  max-width: 34ch;
  margin: 0 auto;
}

/* Features (petits badges) */
.login-features {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-bottom: 24px;
  flex-wrap: wrap;
}

.login-feature {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 999px;
  background: var(--hl);
  color: var(--gold);
  font-size: 0.78rem;
  font-weight: 600;
  letter-spacing: 0.02em;
}

.login-feature svg {
  flex: none;
}

/* Providers */
.login-providers {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-bottom: 16px;
}

.login-provider {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px 18px;
  border-radius: 14px;
  border: 1px solid var(--line);
  background: var(--card2);
  color: var(--ink);
  cursor: pointer;
  font-size: 0.95rem;
  font-weight: 600;
  font-family: inherit;
  transition: all 200ms cubic-bezier(.4, 0, .2, 1);
  text-align: left;
  position: relative;
  overflow: hidden;
}

.login-provider::before {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(90deg, transparent, var(--hl), transparent);
  transform: translateX(-100%);
  transition: transform 600ms;
}

.login-provider:hover::before {
  transform: translateX(100%);
}

.login-provider:hover {
  border-color: var(--gold);
  transform: translateY(-1px);
  box-shadow: 0 8px 20px -10px rgba(230, 189, 99, 0.4);
}

.login-provider:active {
  transform: translateY(0) scale(.98);
}

.login-provider svg {
  flex: none;
  width: 20px;
  height: 20px;
}

.login-provider span {
  flex: 1;
  text-align: left;
}

/* Bouton skip */
.login-skip {
  width: 100%;
  padding: 12px;
  margin-bottom: 20px;
  border: 0;
  background: transparent;
  color: var(--muted);
  font-family: inherit;
  font-size: 0.88rem;
  font-weight: 600;
  cursor: pointer;
  transition: color 200ms;
  text-decoration: underline;
  text-decoration-color: transparent;
  text-underline-offset: 4px;
}

.login-skip:hover {
  color: var(--gold);
  text-decoration-color: var(--gold);
}

/* Legal */
.login-legal {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  color: var(--muted);
  font-size: 0.78rem;
  line-height: 1.5;
  text-align: left;
  padding: 14px;
  background: var(--card);
  border-radius: 12px;
  border: 1px solid var(--line);
  margin: 0;
}

.login-legal svg {
  flex: none;
  margin-top: 2px;
  color: var(--mint);
}

.login-legal strong {
  color: var(--mint);
  font-weight: 600;
}

/* Responsive mobile */
@media (max-width: 480px) {
  .login-content { padding: 30px 22px 22px; }
  .login-header h2 { font-size: 1.35rem; }
  .login-sub { font-size: 0.85rem; }
  .login-provider { padding: 13px 16px; font-size: 0.92rem; }
  .login-feature { font-size: 0.72rem; padding: 5px 10px; }
}
"""

# Ajouter le nouveau CSS
css = css.rstrip() + "\n" + NEW_CSS

with open('css/style.css', 'w', encoding='utf-8', newline='\n') as f:
    f.write(css)

print('OK CSS dialogue remplace')
