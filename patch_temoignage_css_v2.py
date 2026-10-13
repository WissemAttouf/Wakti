#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('css/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

NEW_CSS = """

/* =====================================================================
   Témoignages : badge "En attente" + date + style "own"
===================================================================== */

.testimonial-card.own {
  border-color: var(--gold);
  background: linear-gradient(135deg, var(--hl), var(--card));
  position: relative;
}

.testimonial-card.own::before {
  content: "TON TÉMOIGNAGE";
  position: absolute;
  top: -8px;
  right: 16px;
  padding: 3px 10px;
  border-radius: 999px;
  background: var(--gold);
  color: var(--accent-ink);
  font-size: 0.68rem;
  font-weight: 700;
  letter-spacing: 0.05em;
}

.testimonial-card .pending {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 0.72rem;
  color: var(--muted);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.testimonial-card .pending::before {
  content: "⏳";
  font-size: 0.8rem;
}

.testimonial-date {
  margin-top: 10px;
  padding-top: 10px;
  border-top: 1px dashed var(--line);
  font-size: 0.75rem;
  color: var(--muted);
  font-style: italic;
}

/* Compteur de témoignages */
#testimonialsCount {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 999px;
  background: var(--hl);
  color: var(--gold);
  font-size: 0.8rem;
  font-weight: 700;
  margin-bottom: 20px;
  letter-spacing: 0.02em;
}

.testimonials-live h3 {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  flex-wrap: wrap;
}
"""

if 'testimonial-card.own' not in css:
    css = css.rstrip() + NEW_CSS
    with open('css/style.css', 'w', encoding='utf-8', newline='\n') as f:
        f.write(css)
    print("OK CSS temoignages v2 ajoute")
else:
    print("CSS deja present")
