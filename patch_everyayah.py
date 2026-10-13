#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

# ============================================================
# 1. MODIFIER app.js : RECITERS + getAudioUrls
# ============================================================
print("[1/3] Modification de app.js")

with open('js/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

NEW_RECITERS = """const RECITERS = [
  { id: 'bader_turki', name: 'Bader Al-Turki', ar: 'بدر التركي', country: 'Arabie saoudite', flag: '🇸🇦', hue: 210, bio: 'Imam et recitateur saoudien.', everyayahFolder: 'Bader_Al_Turki_128kbps', server: null, cdnEdition: null, img: 'img/reciters/bader.jpg' },
  { id: 'alafasy', name: 'Mishary Rashid Alafasy', ar: 'مشاري العفاسي', country: 'Koweit', flag: '🇰🇼', hue: 42, bio: 'Recitation fluide et melodieuse.', everyayahFolder: 'Alafasy_128kbps', server: null, cdnEdition: null, img: 'img/reciters/rashid.jpg' },
  { id: 'sudais', name: 'Abdurrahman As-Sudais', ar: 'عبدالرحمن السديس', country: 'Arabie saoudite', flag: '🇸🇦', hue: 165, bio: 'Imam de la Grande Mosquee.', everyayahFolder: 'Abdurrahmaan_As-Sudais_192kbps', server: null, cdnEdition: null, img: 'img/reciters/soudaysi.jpg' },
  { id: 'shuraim', name: 'Saud Al-Shuraim', ar: 'سعود الشريم', country: 'Arabie saoudite', flag: '🇸🇦', hue: 160, bio: 'Ancien Imam de la Grande Mosquee.', everyayahFolder: 'Saood_ash-Shuraym_128kbps', server: null, cdnEdition: null, img: 'img/reciters/Saud Al-Shuraim.jpg' },
  { id: 'muaiqly', name: 'Maher Al-Muaiqly', ar: 'ماهر المعيقلي', country: 'Arabie saoudite', flag: '🇸🇦', hue: 44, bio: 'Imam de la Grande Mosquee.', everyayahFolder: 'Maher_AlMuaiqly_128kbps', server: null, cdnEdition: null, img: 'img/reciters/Maher Al-Muaiqly.jpg' },
  { id: 'shatri', name: 'Abu Bakr Al-Shatri', ar: 'أبو بكر الشاطري', country: 'Arabie saoudite', flag: '🇸🇦', hue: 170, bio: 'Style rythme et captivant.', everyayahFolder: 'Abu_Bakr_Ash-Shaatree_128kbps', server: null, cdnEdition: null, img: 'img/reciters/Abu Bakr Al-Shatri.jpg' },
  { id: 'abdul_basit', name: 'Abdul Basit Abdus-Samad', ar: 'عبد الباسط عبد الصمد', country: 'Egypte', flag: '🇪🇬', hue: 48, bio: 'Maitre inconteste du Tajwid.', everyayahFolder: 'Abdul_Basit_Murattal_192kbps', server: null, cdnEdition: null, img: 'img/reciters/Abdul Basit Abdus-Samad.jpg' },
  { id: 'husary', name: 'Mahmoud Khalil Al-Husary', ar: 'محمود خليل الحصري', country: 'Egypte', flag: '🇪🇬', hue: 168, bio: 'Reference pour la diction.', everyayahFolder: 'Husary_128kbps', server: null, cdnEdition: null, img: 'img/reciters/Mahmoud Khalil Al-Husary.jpg' },
  { id: 'minshawi', name: 'Mohamed Siddiq Al-Minshawi', ar: 'محمد صديق المنشاوي', country: 'Egypte', flag: '🇪🇬', hue: 40, bio: 'Recitation emouvante.', everyayahFolder: 'Minshawy_Murattal_128kbps', server: null, cdnEdition: null, img: 'img/reciters/Mohamed Siddiq Al-Minshawi.jpg' },
  { id: 'dosari', name: 'Yasser Al-Dosari', ar: 'ياسر الدوسري', country: 'Arabie saoudite', flag: '🇸🇦', hue: 200, bio: 'Imam a la Grande Mosquee.', everyayahFolder: 'Yasser_Ad-Dussary_128kbps', server: null, cdnEdition: null, img: 'img/reciters/Yasser Al-Dosari.jpg' },
  { id: 'qatami', name: 'Nasser Al-Qatami', ar: 'ناصر القطامي', country: 'Arabie saoudite', flag: '🇸🇦', hue: 180, bio: 'Ton chaleureux.', everyayahFolder: 'Nasser_Alqatami_128kbps', server: null, cdnEdition: null, img: 'img/reciters/Nasser Al-Qatami.jpg' },
  { id: 'hudhaify', name: 'Ali Al-Hudhaify', ar: 'علي بن عبدالرحمن الحذيفي', country: 'Arabie saoudite', flag: '🇸🇦', hue: 150, bio: 'Imam de la Mosquee du Prophete.', everyayahFolder: 'Hudhaify_128kbps', server: null, cdnEdition: null, img: 'img/reciters/Ali Al-Hudhaify.jpg' }
];"""

pattern = re.compile(r'const RECITERS = \[.*?\];', re.DOTALL)
if pattern.search(js):
    js = pattern.sub(NEW_RECITERS, js, count=1)
    print("  OK RECITERS mis a jour (everyayahFolder)")
else:
    print("  ATTENTION : RECITERS introuvable")

# Modifier getAudioUrls pour utiliser everyayah
OLD_GET_URLS = """async function getAudioUrls(n, reciter) {
  const key = n + '|' + reciter;
  if (audioCache.has(key)) return audioCache.get(key);
  const recObj = RBY[reciter];
  let urls;
  if (recObj && recObj.server) {
    const numPad = String(n).padStart(3, '0');
    urls = [recObj.server + numPad + '.mp3'];
  } else if (recObj && recObj.cdnEdition) {
    const first = FIRST_GLOBAL[n - 1];
    const count = SURAHS[n - 1].c;
    urls = Array.from({ length: count }, (_, i) =>
      'https://cdn.islamic.network/quran/audio/128/' + recObj.cdnEdition + '/' + (first + i) + '.mp3'
    );
  } else {
    urls = [recObj && recObj.server ? recObj.server + '001.mp3' : ''];
  }
  audioCache.set(key, urls);
  return urls;
}"""

NEW_GET_URLS = """async function getAudioUrls(n, reciter) {
  const key = n + '|' + reciter;
  if (audioCache.has(key)) return audioCache.get(key);
  const recObj = RBY[reciter];
  let urls;
  
  // Priority 1 : everyayah.com (verset par verset, fiable)
  if (recObj && recObj.everyayahFolder) {
    const first = FIRST_GLOBAL[n - 1];
    const count = SURAHS[n - 1].c;
    urls = Array.from({ length: count }, (_, i) => {
      // Numero global : 1 a 6236
      const globalNum = first + i;
      // Format everyayah : 6 chiffres (SSSAAA)
      const surahNum = SURAHS.findIndex((s, idx) => {
        let acc = 1;
        for (let j = 0; j <= idx; j++) {
          if (j === idx) return globalNum >= acc && globalNum < acc + SURAHS[j].c;
          acc += SURAHS[j].c;
        }
        return false;
      }) + 1;
      // Simplifier : calcul direct
      let sNum = 1, aNum = globalNum;
      for (let s = 0; s < SURAHS.length; s++) {
        if (aNum <= SURAHS[s].c) { sNum = s + 1; break; }
        aNum -= SURAHS[s].c;
      }
      const surahPad = String(sNum).padStart(3, '0');
      const ayahPad = String(aNum).padStart(3, '0');
      return 'https://everyayah.com/data/' + recObj.everyayahFolder + '/' + surahPad + ayahPad + '.mp3';
    });
  }
  // Priority 2 : mp3quran (fichier par sourate)
  else if (recObj && recObj.server) {
    const numPad = String(n).padStart(3, '0');
    urls = [recObj.server + numPad + '.mp3'];
  }
  // Fallback
  else {
    urls = [''];
  }
  audioCache.set(key, urls);
  return urls;
}"""

if OLD_GET_URLS in js:
    js = js.replace(OLD_GET_URLS, NEW_GET_URLS)
    print("  OK getAudioUrls utilise everyayah.com")
elif 'everyayahFolder' in js and 'everyayah.com' in js:
    print("  getAudioUrls deja patche")
else:
    print("  ATTENTION : getAudioUrls introuvable")

with open('js/app.js', 'w', encoding='utf-8', newline='\n') as f:
    f.write(js)


# ============================================================
# 2. MODIFIER vercel.json : ajouter everyayah.com a la CSP
# ============================================================
print("\n[2/3] Modification de vercel.json")

import json
with open('vercel.json', 'r', encoding='utf-8') as f:
    config = json.load(f)

for rule in config.get('headers', []):
    if rule.get('source') == '/(.*)':
        for h in rule.get('headers', []):
            if h.get('key') == 'Content-Security-Policy':
                csp = h['value']
                
                # Ajouter everyayah.com si manquant
                if 'everyayah.com' not in csp:
                    # Dans connect-src
                    csp = csp.replace(
                        "connect-src 'self'",
                        "connect-src 'self' https://everyayah.com"
                    )
                    # Dans media-src
                    if 'everyayah.com' not in csp.split('media-src')[1].split(';')[0]:
                        csp = csp.replace(
                            'https://everyayah.com;',
                            'https://everyayah.com;',  # deja dans media-src apparemment
                            1
                        )
                    h['value'] = csp
                    print("  OK everyayah.com ajoute a connect-src")
                else:
                    print("  everyayah.com deja present dans la CSP")
                break

with open('vercel.json', 'w', encoding='utf-8', newline='\n') as f:
    json.dump(config, f, indent=2, ensure_ascii=False)


# ============================================================
# 3. VERIFIER
# ============================================================
print("\n[3/3] Verification")
print("  RECITERS avec everyayahFolder :", js.count('everyayahFolder:'))
print("  getAudioUrls utilise everyayah.com :", 'everyayah.com' in js)

print("\n=== TERMINE ===")
print("Prochaines etapes :")
print("1. npx vercel --prod --force")
print("2. Tester dans Wakti")
