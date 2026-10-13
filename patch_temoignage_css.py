#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('css/style.css', 'r', encoding='utf-8') as f:
    css = f.read()

NEW_CSS = """

/* =====================================================================
   Dialogue formulaire de témoignage
===================================================================== */

.testimonial-dlg {
  width: min(480px, 94vw);
  max-height: 92vh;
  border: 0;
  border-radius: 24px;
  padding: 0;
  background: var(--panel);
  color: var(--ink);
  overflow: hidden;
  box-shadow: 0 24px 60px -20px rgba(0, 0, 0, .6);
  animation: testimonialEnter 400ms cubic-bezier(.34, 1.56, .64, 1);
}

@keyframes testimonialEnter {
  from { opacity: 0; transform: scale(.92) translateY(20px); }
  to   { opacity: 1; transform: scale(1) translateY(0); }
}

.testimonial-dlg::backdrop {
  background: rgba(0, 0, 0, 0.7);
  -webkit-backdrop-filter: blur(8px);
  backdrop-filter: blur(8px);
}

.testimonial-form-wrap {
  padding: 32px 28px 24px;
  position: relative;
  overflow-y: auto;
  max-height: 92vh;
}

.testimonial-close {
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
}

.testimonial-close:hover {
  color: var(--gold);
  border-color: var(--gold);
  transform: rotate(90deg);
}

.testimonial-header {
  text-align: center;
  margin-bottom: 24px;
}

.testimonial-emoji {
  font-size: 2.5rem;
  margin-bottom: 10px;
  line-height: 1;
}

.testimonial-header h2 {
  font-size: 1.4rem;
  font-weight: 700;
  margin-bottom: 8px;
  letter-spacing: -0.01em;
}

.testimonial-header p {
  color: var(--muted);
  font-size: 0.9rem;
  line-height: 1.5;
  max-width: 36ch;
  margin: 0 auto;
}

.testimonial-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.testimonial-field {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.testimonial-field label {
  font-size: 0.88rem;
  color: var(--muted);
  font-weight: 600;
}

.testimonial-field input,
.testimonial-field textarea {
  padding: 12px 14px;
  border-radius: 12px;
  border: 1px solid var(--line);
  background: var(--card2);
  color: var(--ink);
  font: inherit;
  font-size: 0.95rem;
  resize: vertical;
}

.testimonial-field input:focus,
.testimonial-field textarea:focus {
  outline: none;
  border-color: var(--gold);
}

.testimonial-field textarea {
  min-height: 100px;
  max-height: 200px;
  line-height: 1.5;
}

.char-counter {
  text-align: right;
  font-size: 0.78rem;
  color: var(--muted);
  font-variant-numeric: tabular-nums;
}

/* Notation étoiles */
.rating-input {
  display: flex;
  gap: 6px;
  justify-content: center;
  padding: 8px 0;
}

.star-btn {
  background: transparent;
  border: 0;
  font-size: 2rem;
  color: var(--line);
  cursor: pointer;
  padding: 4px;
  line-height: 1;
  transition: all 150ms;
}

.star-btn:hover,
.star-btn.active {
  color: var(--gold);
  transform: scale(1.15);
}

.star-btn:active {
  transform: scale(0.95);
}

/* Actions */
.testimonial-actions {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-top: 4px;
}

.testimonial-hint {
  min-height: 1.2em;
  font-size: 0.85rem;
  text-align: center;
  color: var(--muted);
  margin: 0;
}

.testimonial-hint.success {
  color: var(--mint);
  font-weight: 600;
}

.testimonial-hint.error {
  color: #e88;
}

/* Legal */
.testimonial-legal {
  display: flex;
  align-items: flex-start;
  gap: 8px;
  color: var(--muted);
  font-size: 0.78rem;
  line-height: 1.5;
  text-align: left;
  padding: 12px;
  background: var(--card);
  border-radius: 10px;
  margin: 4px 0 0;
}

.testimonial-legal svg {
  flex: none;
  margin-top: 2px;
  color: var(--mint);
}

.testimonial-legal strong {
  color: var(--mint);
  font-weight: 600;
}

/* Responsive */
@media (max-width: 480px) {
  .testimonial-form-wrap { padding: 26px 20px 20px; }
  .testimonial-header h2 { font-size: 1.2rem; }
  .star-btn { font-size: 1.7rem; }
  .testimonial-actions { grid-template-columns: 1fr; }
}

/* Card témoignage dans la liste */
.testimonial-card {
  padding: 22px;
  border-radius: var(--r);
  border: 1px solid var(--line);
  background: var(--card);
  text-align: left;
  transition: border-color 200ms, transform 200ms;
}

.testimonial-card:hover {
  border-color: var(--gold);
  transform: translateY(-3px);
}

.testimonial-card .stars {
  color: var(--gold);
  font-size: 0.95rem;
  margin-bottom: 10px;
  letter-spacing: 0.05em;
}

.testimonial-card p {
  font-style: italic;
  line-height: 1.6;
  color: var(--ink);
  margin-bottom: 12px;
  font-size: 0.93rem;
  word-break: break-word;
}

.testimonial-card cite {
  font-style: normal;
  color: var(--gold);
  font-weight: 600;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  gap: 8px;
  flex-wrap: wrap;
}

.testimonial-card .verified {
  display: inline-flex;
  align-items: center;
  gap: 3px;
  font-size: 0.72rem;
  color: var(--mint);
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.testimonial-card .verified::before {
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

.testimonial-empty {
  text-align: center;
  padding: 30px 20px;
  color: var(--muted);
  font-style: italic;
  font-size: 0.92rem;
}
"""

if '.testimonial-dlg' not in css:
    css = css.rstrip() + NEW_CSS
    with open('css/style.css', 'w', encoding='utf-8', newline='\n') as f:
        f.write(css)
    print("OK CSS temoignages ajoute")
else:
    print("CSS deja present")
