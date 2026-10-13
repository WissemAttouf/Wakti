#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

with open('js/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# RECITERS corriges : Maher avec le bon nom, Bader passe en mp3quran (pas de Hifz)
NEW_RECITERS = """const RECITERS = [
  { id: 'alafasy', name: 'Mishary Rashid Alafasy', ar: 'مشاري العفاسي', country: 'Koweit', flag: '🇰🇼', hue: 42, bio: 'Recitation fluide et melodieuse.', everyayahFolder: 'Alafasy_128kbps', server: null, cdnEdition: null, img: 'img/reciters/rashid.jpg' },
  { id: 'husary', name: 'Mahmoud Khalil Al-Husary', ar: 'محمود خليل الحصري', country: 'Egypte', flag: '🇪🇬', hue: 168, bio: 'Reference pour la diction.', everyayahFolder: 'Husary_128kbps', server: null, cdnEdition: null, img: 'img/reciters/Mahmoud Khalil Al-Husary.jpg' },
  { id: 'abdul_basit', name: 'Abdul Basit Abdus-Samad', ar: 'عبد الباسط عبد الصمد', country: 'Egypte', flag: '🇪🇬', hue: 48, bio: 'Maitre inconteste du Tajwid.', everyayahFolder: 'Abdul_Basit_Murattal_192kbps', server: null, cdnEdition: null, img: 'img/reciters/Abdul Basit Abdus-Samad.jpg' },
  { id: 'minshawi', name: 'Mohamed Siddiq Al-Minshawi', ar: 'محمد صديق المنشاوي', country: 'Egypte', flag: '🇪🇬', hue: 40, bio: 'Recitation emouvante.', everyayahFolder: 'Minshawy_Murattal_128kbps', server: null, cdnEdition: null, img: 'img/reciters/Mohamed Siddiq Al-Minshawi.jpg' },
  { id: 'sudais', name: 'Abdurrahman As-Sudais', ar: 'عبدالرحمن السديس', country: 'Arabie saoudite', flag: '🇸🇦', hue: 165, bio: 'Imam de la Grande Mosquee.', everyayahFolder: 'Abdurrahmaan_As-Sudais_192kbps', server: null, cdnEdition: null, img: 'img/reciters/soudaysi.jpg' },
  { id: 'shuraim', name: 'Saud Al-Shuraim', ar: 'سعود الشريم', country: 'Arabie saoudite', flag: '🇸🇦', hue: 160, bio: 'Ancien Imam de la Grande Mosquee.', everyayahFolder: 'Saood_ash-Shuraym_128kbps', server: null, cdnEdition: null, img: 'img/reciters/Saud Al-Shuraim.jpg' },
  { id: 'muaiqly', name: 'Maher Al-Muaiqly', ar: 'ماهر المعيقلي', country: 'Arabie saoudite', flag: '🇸🇦', hue: 44, bio: 'Imam de la Grande Mosquee.', everyayahFolder: 'MaherAlMuaiqly128kbps', server: null, cdnEdition: null, img: 'img/reciters/Maher Al-Muaiqly.jpg' },
  { id: 'shatri', name: 'Abu Bakr Al-Shatri', ar: 'أبو بكر الشاطري', country: 'Arabie saoudite', flag: '🇸🇦', hue: 170, bio: 'Style rythme et captivant.', everyayahFolder: 'Abu_Bakr_Ash-Shaatree_128kbps', server: null, cdnEdition: null, img: 'img/reciters/Abu Bakr Al-Shatri.jpg' },
  { id: 'dosari', name: 'Yasser Al-Dosari', ar: 'ياسر الدوسري', country: 'Arabie saoudite', flag: '🇸🇦', hue: 200, bio: 'Imam a la Grande Mosquee.', everyayahFolder: 'Yasser_Ad-Dussary_128kbps', server: null, cdnEdition: null, img: 'img/reciters/Yasser Al-Dosari.jpg' },
  { id: 'qatami', name: 'Nasser Al-Qatami', ar: 'ناصر القطامي', country: 'Arabie saoudite', flag: '🇸🇦', hue: 180, bio: 'Ton chaleureux.', everyayahFolder: 'Nasser_Alqatami_128kbps', server: null, cdnEdition: null, img: 'img/reciters/Nasser Al-Qatami.jpg' },
  { id: 'hudhaify', name: 'Ali Al-Hudhaify', ar: 'علي بن عبدالرحمن الحذيفي', country: 'Arabie saoudite', flag: '🇸🇦', hue: 150, bio: 'Imam de la Mosquee du Prophete.', everyayahFolder: 'Hudhaify_128kbps', server: null, cdnEdition: null, img: 'img/reciters/Ali Al-Hudhaify.jpg' },
  { id: 'bader_turki', name: 'Bader Al-Turki', ar: 'بدر التركي', country: 'Arabie saoudite', flag: '🇸🇦', hue: 210, bio: 'Imam et recitateur saoudien.', everyayahFolder: null, server: 'https://server10.mp3quran.net/bader/Rewayat-Hafs-A-n-Assem/', cdnEdition: null, img: 'img/reciters/bader.jpg' }
];"""

pattern = re.compile(r'const RECITERS = \[.*?\];', re.DOTALL)
if pattern.search(js):
    js = pattern.sub(NEW_RECITERS, js, count=1)
    print("OK RECITERS corriges")
    print("  - Maher Al-Muaiqly : MaherAlMuaiqly128kbps (nom correct)")
    print("  - Bader Al-Turki : server mp3quran (pas de Hifz)")
else:
    print("ERREUR : RECITERS introuvable")

with open('js/app.js', 'w', encoding='utf-8', newline='\n') as f:
    f.write(js)
