#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('css/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

NEW_CSS = """

/* =====================================================================
   Section Caractéristiques objectives
===================================================================== */

.features-highlight {
  margin-top: 60px;
  padding: 50px 0;
  border-top: 1px solid var(--line);
  text-align: center;
}

.features-highlight h2 {
  font-size: clamp(1.5rem, 3vw, 2rem);
  font-weight: 700;
  color: var(--gold);
  margin-bottom: 12px;
  letter-spacing: -0.01em;
}

.features-highlight .section-sub {
  color: var(--muted);
  font-size: 1rem;
  margin-bottom: 40px;
  max-width: 52ch;
  margin-left: auto;
  margin-right: auto;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
  gap: 20px;
  max-width: 1000px;
  margin: 0 auto;
  text-align: left;
}

.feature-card {
  padding: 24px 20px;
  border-radius: var(--r);
  border: 1px solid var(--line);
  background: var(--card);
  transition: all 300ms cubic-bezier(.4, 0, .2, 1);
  position: relative;
  overflow: hidden;
}

.feature-card::before {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, var(--gold), var(--mint));
  opacity: 0;
  transition: opacity 300ms;
}

.feature-card:hover {
  border-color: var(--gold);
  transform: translateY(-4px);
  box-shadow: 0 12px 30px -12px rgba(230, 189, 99, 0.3);
}

.feature-card:hover::before {
  opacity: 1;
}

.feature-icon {
  font-size: 2rem;
  margin-bottom: 12px;
  line-height: 1;
}

.feature-card h3 {
  font-size: 1.05rem;
  font-weight: 700;
  color: var(--gold);
  margin-bottom: 8px;
  letter-spacing: -0.01em;
}

.feature-card p {
  font-size: 0.9rem;
  color: var(--muted);
  line-height: 1.55;
  margin: 0;
}

/* =====================================================================
   Témoignages réels (à activer quand disponibles)
===================================================================== */

.testimonials-live {
  margin-top: 50px;
  padding-top: 40px;
  border-top: 1px dashed var(--line);
}

.testimonials-live h3 {
  font-size: 1.3rem;
  font-weight: 700;
  color: var(--gold);
  margin-bottom: 24px;
  text-align: center;
}

.testimonials-live .testimonials {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
  gap: 20px;
  max-width: 900px;
  margin: 0 auto;
}

.testimonials-live blockquote {
  padding: 22px;
  border-radius: var(--r);
  border: 1px solid var(--line);
  background: var(--card);
  text-align: left;
  margin: 0;
  transition: border-color 200ms, transform 200ms;
}

.testimonials-live blockquote:hover {
  border-color: var(--gold);
  transform: translateY(-3px);
}

.testimonials-live .stars {
  color: var(--gold);
  font-size: 0.95rem;
  margin-bottom: 10px;
  letter-spacing: 0.05em;
}

.testimonials-live blockquote p {
  font-style: italic;
  line-height: 1.6;
  color: var(--ink);
  margin-bottom: 12px;
  font-size: 0.93rem;
}

.testimonials-live blockquote cite {
  font-style: normal;
  color: var(--gold);
  font-weight: 600;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 8px;
}

.testimonials-live .verified {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 0.75rem;
  color: var(--mint);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.testimonials-live .verified::before {
  content: "✓";
  display: inline-grid;
  place-items: center;
  width: 14px;
  height: 14px;
  border-radius: 50%;
  background: var(--mint);
  color: #032018;
  font-size: 0.7rem;
}

/* =====================================================================
   Appel à témoignage
===================================================================== */

.testimonials-cta {
  margin-top: 40px;
  padding: 28px 24px;
  border-radius: var(--r);
  background: linear-gradient(135deg, var(--hl), var(--card));
  border: 1px solid var(--line);
  max-width: 600px;
  margin-left: auto;
  margin-right: auto;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.testimonials-cta p {
  color: var(--ink);
  font-size: 0.95rem;
  line-height: 1.5;
  margin: 0;
}

.testimonials-cta b {
  color: var(--gold);
  font-weight: 700;
}

.testimonials-cta .btn {
  padding: 12px 24px;
  font-size: 0.95rem;
}

/* =====================================================================
   Responsive
===================================================================== */

@media (max-width: 640px) {
  .features-grid {
    grid-template-columns: 1fr;
    gap: 14px;
  }
  .feature-card {
    padding: 20px 16px;
  }
  .features-highlight {
    padding: 40px 0;
  }
}
"""

if '.features-highlight' not in css:
    css = css.rstrip() + NEW_CSS
    with open('css/style.css', 'w', encoding='utf-8', newline='\n') as f:
        f.write(css)
    print("OK CSS features + temoignages ajoute")
else:
    print("CSS deja present")
