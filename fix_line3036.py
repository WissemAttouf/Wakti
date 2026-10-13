#!/usr/bin/env python3
# -*- coding: utf-8 -*-

print("=== CORRECTION DE LA LIGNE 3036 ===\n")

with open('js/app.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Chercher le pattern cassé : un retour à la ligne dans une string JS
# Le pattern cassé ressemble à :
# esc((d.arabic || '') + '
# (newline)
# (newline)
# ' + (d.translation || ''))

# Solution : remplacer par une concaténation propre
OLD_PATTERNS = [
    # Pattern 1 : avec 2 retours à la ligne
    """esc((d.arabic || '') + '

' + (d.translation || ''))""",
    # Pattern 2 : avec 1 retour à la ligne
    """esc((d.arabic || '') + '
' + (d.translation || ''))""",
]

NEW = """esc((d.arabic || '') + ' | ' + (d.translation || ''))"""

fixed = False
for old in OLD_PATTERNS:
    if old in content:
        content = content.replace(old, NEW)
        print(f"OK Pattern cassé remplacé")
        fixed = True
        break

if not fixed:
    print("Pattern exact non trouvé, on essaie par regex...")
    
    import re
    # Chercher la ligne du data-copy
    pattern = re.compile(
        r"'<button class=\"doua-copy\" data-copy=\"' \+ esc\(\(d\.arabic \|\| ''\) \+ '.*?' \+ \(d\.translation \|\| ''\)\)",
        re.DOTALL
    )
    
    match = pattern.search(content)
    if match:
        old_full = match.group(0)
        # Reconstruire proprement
        new_full = """'<button class="doua-copy" data-copy="' + esc((d.arabic || '') + ' | ' + (d.translation || ''))"""
        content = content.replace(old_full, new_full)
        print("OK Pattern cassé remplacé (par regex)")
        fixed = True
    else:
        # Chercher une autre approche : trouver "data-copy=" et regarder
        idx = content.find('doua-copy')
        if idx > 0:
            print(f"Trouvé 'doua-copy' à la position {idx}")
            print("Contexte :")
            print(content[idx-50:idx+300])
            print()
            
            # Compter les retours à la ligne dans la string
            start = content.find("data-copy=\"", idx)
            if start > 0:
                # Trouver la fin de la string (prochaine '))
                end = content.find("')", start + 20)
                if end > 0:
                    old_segment = content[start:end+2]
                    new_segment = 'data-copy="' + "let me not guess"
                    # Plus simple : reconstruire tout le douaHTML
                    print("Reconstruction complète de douaHTML...")
                    fixed = False

if not fixed:
    # Solution alternative : reconstruire le douaHTML de zéro
    print("\nReconstruction complète de la fonction douaHTML...")
    
    import re
    # Trouver la fonction douaHTML et la remplacer
    pattern = re.compile(
        r'function douaHTML\(d\) \{.*?\n\}',
        re.DOTALL
    )
    
    NEW_DOUAHTML = '''function douaHTML(d) {
  const copyText = (d.arabic || '') + ' | ' + (d.translation || '');
  return '<article class="doua-card">' +
    '<h3 class="doua-title">' + esc(d.title) + '</h3>' +
    (d.arabic ? '<p class="doua-ar" lang="ar" dir="rtl">' + esc(d.arabic) + '</p>' : '') +
    (d.latin ? '<p class="doua-latin">' + esc(d.latin) + '</p>' : '') +
    (d.translation ? '<p class="doua-translation">' + esc(d.translation) + '</p>' : '') +
    (d.notes ? '<p class="doua-notes">' + esc(d.notes) + '</p>' : '') +
    (d.fawaid ? '<p class="doua-fawaid"><b>Bienfaits :</b> ' + esc(d.fawaid) + '</p>' : '') +
    (d.source ? '<p class="doua-source"><b>Source :</b> ' + esc(d.source) + '</p>' : '') +
    '<button class="doua-copy" data-copy="' + esc(copyText) + '" aria-label="Copier">' +
    '<svg class="ic"><use href="#i-copy"/></svg>' +
    '</button>' +
    '</article>';
}'''
    
    if pattern.search(content):
        content = pattern.sub(NEW_DOUAHTML, content)
        print("OK Fonction douaHTML reconstruite")
        fixed = True
    else:
        print("❌ Fonction douaHTML introuvable")

if fixed:
    with open('js/app.js', 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print("\nOK app.js corrigé et sauvegardé")
else:
    print("\n❌ Impossible de corriger automatiquement")

print("\n=== VERIFICATION ===")
import subprocess
try:
    result = subprocess.run(
        ['node', '--check', 'js/app.js'],
        capture_output=True,
        text=True,
        timeout=10
    )
    if result.returncode == 0:
        print("✅ Syntaxe valide !")
    else:
        print("❌ Encore une erreur :")
        print(result.stderr)
except Exception as e:
    print(f"Test impossible : {e}")
