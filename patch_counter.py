#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

OLD = """    <div class="testimonials-live" id="testimonials-live" hidden>
      <h3>💬 Ce que disent nos utilisateurs</h3>
      <div class="testimonials" id="testimonials-container"></div>
    </div>"""

NEW = """    <div class="testimonials-live" id="testimonials-live" hidden>
      <h3>💬 Ce que disent nos utilisateurs</h3>
      <div id="testimonialsCount"></div>
      <div class="testimonials" id="testimonials-container"></div>
    </div>"""

if OLD in html:
    html = html.replace(OLD, NEW)
    with open('index.html', 'w', encoding='utf-8', newline='\n') as f:
        f.write(html)
    print("OK compteur ajoute")
else:
    print("ATTENTION : bloc testimonials-live introuvable")
