#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

print("[1/3] Deplacement du Hifz dans index.html")

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Trouver le bloc Hifz overlay complet
start_marker = '<!-- Mode Hifz (overlay) -->'
start = html.find(start_marker)

if start == -1:
    print("  ERREUR : marqueur de debut introuvable")
    exit(1)

# Trouver la fin : chercher la prochaine fermeture de div correspondante
# On sait que le bloc finit par 3 divs imbriquees : hifz-learned-badge, hifzOverlay, quranLecteur
# Cherchons la sequence : </div>\n    </div>\n  </section>
# Plus simple : capturer jusqu'a la prochaine </section>
end = html.find('</section>', start)
if end == -1:
    print("  ERREUR : fin introuvable")
    exit(1)

# Le bloc Hifz est entre start et end
block = html[start:end].rstrip()
# Retirer la derniere div fermante (car elle ferme le parent quranLecteur, pas le Hifz)
if block.endswith('</div>'):
    block = block[:-6].rstrip()

print(f"  Bloc Hifz extrait ({len(block)} caracteres)")

# Retirer le bloc du HTML
html = html[:start] + html[end:]

# Nettoyer les divs vides laissees
html = html.replace('</div>\n  </section>', '</section>', 1)
html = re.sub(r'\n\s*\n\s*\n', '\n\n', html)

# Re-inserer le bloc avant </body>
body_end = html.find('</body>')
if body_end == -1:
    print("  ERREUR : </body> introuvable")
    exit(1)

html = html[:body_end] + '\n' + block + '\n\n' + html[body_end:]

with open('index.html', 'w', encoding='utf-8', newline='\n') as f:
    f.write(html)

print("  OK Hifz deplace avant </body>")


print("\n[2/3] Verification structure")

with open('index.html', 'r', encoding='utf-8') as f:
    html2 = f.read()

hifz_pos = html2.find('id="hifzOverlay"')
reader_pos = html2.find('id="quranLecteur"')
body_pos = html2.find('</body>')

print(f"  quranLecteur position : {reader_pos}")
print(f"  hifzOverlay position : {hifz_pos}")
print(f"  </body> position : {body_pos}")

if hifz_pos > body_pos - 5000 and hifz_pos < body_pos:
    print("  OK Hifz est bien avant </body>")
elif hifz_pos > reader_pos:
    print("  OK Hifz est apres quranLecteur")
else:
    print("  ATTENTION : position suspecte")


print("\n[3/3] Modification de app.js (correction opacity)")

with open('js/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# 1. Dans openHifz : retirer l'opacity 0
OLD_OPEN = """  overlay.hidden = false;
  overlay.style.zIndex = '9999';"""

NEW_OPEN = """  overlay.hidden = false;
  overlay.style.zIndex = '9999';
  overlay.style.opacity = '1';  // Forcer la visibilite"""

if OLD_OPEN in js:
    js = js.replace(OLD_OPEN, NEW_OPEN)
    print("  OK opacity forcee a 1 dans openHifz")
else:
    print("  ATTENTION : bloc openHifz introuvable")

# 2. Dans openHifz : NE PAS cacher le lecteur (l'overlay est maintenant en dehors)
OLD_HIDE = """  // 2. Masquer le lecteur classique completement (pas juste visibility)
  const qLec = document.getElementById('quranLecteur');
  if (qLec) {
    qLec.style.display = 'none';
  }"""

NEW_HIDE = """  // 2. NE PAS masquer le lecteur (l'overlay est dans <body>)"""

if OLD_HIDE in js:
    js = js.replace(OLD_HIDE, NEW_HIDE)
    print("  OK lecteur n'est plus cache")
else:
    # Chercher une variante
    pattern = re.compile(
        r'// 2\. Masquer le lecteur classique.*?qLec\.style\.display = \'none\';\s*\}',
        re.DOTALL
    )
    if pattern.search(js):
        js = pattern.sub('// 2. Lecteur non cache (overlay dans <body>)', js)
        print("  OK lecteur n'est plus cache (regex)")
    else:
        print("  ATTENTION : bloc cache-lecteur introuvable")

# 3. Dans openHifz : retirer la visibilite hidden du lecteur
OLD_VIS = """  const qLec = document.getElementById('quranLecteur');
  if (qLec) qLec.style.visibility = 'hidden';"""

if OLD_VIS in js:
    js = js.replace(OLD_VIS, '// pas de masquage du lecteur')
    print("  OK visibility lecteur preservee")

# 4. closeHifz : retirer reset display et opacity
OLD_CLOSE = """function closeHifz() {
  hifzState.active = false;
  const overlay = document.getElementById('hifzOverlay');
  if (overlay) {
    overlay.hidden = true;
    overlay.style.zIndex = '';
  }
  const qLec = document.getElementById('quranLecteur');
  if (qLec) {
    qLec.style.display = '';
  }
}"""

NEW_CLOSE = """function closeHifz() {
  hifzState.active = false;
  const overlay = document.getElementById('hifzOverlay');
  if (overlay) {
    overlay.hidden = true;
    overlay.style.zIndex = '';
    overlay.style.opacity = '';
  }
}"""

if OLD_CLOSE in js:
    js = js.replace(OLD_CLOSE, NEW_CLOSE)
    print("  OK closeHifz simplifie")
else:
    print("  ATTENTION : closeHifz introuvable")

with open('js/app.js', 'w', encoding='utf-8', newline='\n') as f:
    f.write(js)

print("\n=== TERMINE ===")
print("Prochaine etape : npx vercel --prod --force")
