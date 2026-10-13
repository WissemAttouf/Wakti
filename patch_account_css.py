#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('css/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

NEW_CSS = """

/* =====================================================================
   Section "Mon compte" — Version amelioree
===================================================================== */

#accountField {
  border-top: 1px solid var(--line);
  padding-top: 18px;
  margin-top: 14px;
}

#accountField .lab {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.92rem;
  color: var(--muted);
  margin-bottom: 14px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

#accountField .lab::before {
  content: "";
  width: 3px;
  height: 14px;
  background: var(--gold);
  border-radius: 3px;
}

#accountStatus {
  margin-bottom: 14px;
  line-height: 1.5;
}

.account-profile {
  display: flex;
  align-items: center;
  gap: 14px;
  padding: 14px;
  border-radius: 16px;
  background: linear-gradient(135deg, var(--card2) 0%, var(--card) 100%);
  border: 1px solid var(--line);
  position: relative;
  overflow: hidden;
}

.account-profile::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--gold), var(--mint));
  opacity: 0.7;
}

.account-avatar {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  flex: none;
  display: grid;
  place-items: center;
  overflow: hidden;
  background: radial-gradient(circle at 32% 26%, var(--gold), #a2741e);
  color: var(--accent-ink);
  font-weight: 700;
  font-size: 1.4rem;
  border: 2px solid var(--gold);
  box-shadow: 0 4px 14px -4px rgba(230, 189, 99, 0.6);
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
  gap: 3px;
}

.account-name {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--ink);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.2;
}

.account-provider {
  font-size: 0.78rem;
  color: var(--gold);
  text-transform: capitalize;
  letter-spacing: 0.02em;
  font-weight: 600;
}

.account-email {
  font-size: 0.75rem;
  color: var(--muted);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

#accountBtn.ghost {
  background: transparent;
  border: 1px solid var(--line);
  color: var(--muted);
  transition: all 200ms ease;
  padding: 12px;
  font-weight: 600;
}

#accountBtn.ghost:hover {
  border-color: #e88;
  color: #e88;
  background: rgba(204, 68, 68, 0.08);
}

#accountBtn.primary {
  box-shadow: 0 4px 14px -6px rgba(230, 189, 99, 0.5);
}
"""

if 'account-profile::before' in css:
    print('CSS deja present')
else:
    css = css.rstrip() + NEW_CSS
    with open('css/style.css', 'w', encoding='utf-8', newline='\n') as f:
        f.write(css)
    print('OK CSS Mon compte ameliore')
