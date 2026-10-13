#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('css/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

NEW_CSS = """

/* =====================================================================
   Section "Mon compte" dans les Reglages
===================================================================== */

#accountField {
  border-top: 1px solid var(--line);
  padding-top: 16px;
  margin-top: 12px;
}

#accountField .lab {
  display: block;
  font-size: 0.92rem;
  color: var(--muted);
  margin-bottom: 10px;
  font-weight: 600;
}

#accountStatus {
  margin-bottom: 12px;
  line-height: 1.5;
}

.account-profile {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 14px;
  background: var(--card2);
  border: 1px solid var(--line);
}

.account-avatar {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  flex: none;
  display: grid;
  place-items: center;
  overflow: hidden;
  background: radial-gradient(circle at 32% 26%, var(--gold), #a2741e);
  color: var(--accent-ink);
  font-weight: 700;
  font-size: 1.3rem;
  border: 2px solid var(--gold);
  box-shadow: 0 4px 12px -4px rgba(230, 189, 99, 0.6);
}

.account-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.account-avatar b {
  font-family: var(--font-ui);
  font-weight: 800;
}

.account-meta {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.account-name {
  font-size: 1rem;
  font-weight: 700;
  color: var(--ink);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.account-provider {
  font-size: 0.78rem;
  color: var(--muted);
  text-transform: capitalize;
  letter-spacing: 0.02em;
}

#accountBtn.ghost {
  background: transparent;
  border: 1px solid var(--line);
  color: var(--muted);
  transition: all 200ms ease;
}

#accountBtn.ghost:hover {
  border-color: #e88;
  color: #e88;
  background: rgba(204, 68, 68, 0.08);
}
"""

# Verifier si le CSS existe deja
if 'account-profile' in css:
    print('CSS deja present, rien a faire')
else:
    css += NEW_CSS
    with open('css/style.css', 'w', encoding='utf-8', newline='\n') as f:
        f.write(css)
    print('OK CSS Mon compte ajoute dans style.css')
