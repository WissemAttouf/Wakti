#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('js/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# isSingleFileMode : toujours false maintenant
OLD = """function isSingleFileMode() {
  const r = RBY[P.reciter];
  return !!(r && r.server);
}"""

NEW = """function isSingleFileMode() {
  // Tous les recitateurs utilisent maintenant cdnEdition (verset par verset)
  // donc plus de mode "sourate complete"
  return false;
}"""

if OLD in js:
    js = js.replace(OLD, NEW)
    print("OK isSingleFileMode desactive")
else:
    print("ATTENTION : isSingleFileMode introuvable")

with open('js/app.js', 'w', encoding='utf-8', newline='\n') as f:
    f.write(js)
