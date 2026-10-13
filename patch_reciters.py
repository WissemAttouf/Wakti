#!/usr/bin/env python3
# -*- coding: utf-8 -*-

with open('js/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

# Nouvelle liste RECITERS avec cdnEdition pour tous
NEW_RECITERS = """const RECITERS = [
  { id: 'bader_turki', name: 'Bader Al-Turki', ar: 'بدر التركي', country: 'Arabie saoudite', flag: '🇸🇦', hue: 210, bio: 'Imam et recitateur saoudien.', server: null, cdnEdition: 'ar.badr', img: 'img/reciters/bader.jpg' },
  { id: 'alafasy', name: 'Mishary Rashid Alafasy', ar: 'مشاري العفاسي', country: 'Koweit', flag: '🇰🇼', hue: 42, bio: 'Recitation fluide et melodieuse.', server: null, cdnEdition: 'ar.alafasy', img: 'img/reciters/rashid.jpg' },
  { id: 'sudais', name: 'Abdurrahman As-Sudais', ar: 'عبدالرحمن السديس', country: 'Arabie saoudite', flag: '🇸🇦', hue: 165, bio: 'Imam de la Grande Mosquee.', server: null, cdnEdition: 'ar.abdurrahmaansudais', img: 'img/reciters/soudaysi.jpg' },
  { id: 'shuraim', name: 'Saud Al-Shuraim', ar: 'سعود الشريم', country: 'Arabie saoudite', flag: '🇸🇦', hue: 160, bio: 'Ancien Imam de la Grande Mosquee.', server: null, cdnEdition: 'ar.saoodshuraym', img: 'img/reciters/Saud Al-Shuraim.jpg' },
  { id: 'muaiqly', name: 'Maher Al-Muaiqly', ar: 'ماهر المعيقلي', country: 'Arabie saoudite', flag: '🇸🇦', hue: 44, bio: 'Imam de la Grande Mosquee.', server: null, cdnEdition: 'ar.mahermuaiqly', img: 'img/reciters/Maher Al-Muaiqly.jpg' },
  { id: 'shatri', name: 'Abu Bakr Al-Shatri', ar: 'أبو بكر الشاطري', country: 'Arabie saoudite', flag: '🇸🇦', hue: 170, bio: 'Style rythme et captivant.', server: null, cdnEdition: 'ar.shaatree', img: 'img/reciters/Abu Bakr Al-Shatri.jpg' },
  { id: 'abdul_basit', name: 'Abdul Basit Abdus-Samad', ar: 'عبد الباسط عبد الصمد', country: 'Egypte', flag: '🇪🇬', hue: 48, bio: 'Maitre inconteste du Tajwid.', server: null, cdnEdition: 'ar.abdulbasitmurattal', img: 'img/reciters/Abdul Basit Abdus-Samad.jpg' },
  { id: 'husary', name: 'Mahmoud Khalil Al-Husary', ar: 'محمود خليل الحصري', country: 'Egypte', flag: '🇪🇬', hue: 168, bio: 'Reference pour la diction.', server: null, cdnEdition: 'ar.husary', img: 'img/reciters/Mahmoud Khalil Al-Husary.jpg' },
  { id: 'minshawi', name: 'Mohamed Siddiq Al-Minshawi', ar: 'محمد صديق المنشاوي', country: 'Egypte', flag: '🇪🇬', hue: 40, bio: 'Recitation emouvante.', server: null, cdnEdition: 'ar.minshawi', img: 'img/reciters/Mohamed Siddiq Al-Minshawi.jpg' },
  { id: 'dosari', name: 'Yasser Al-Dosari', ar: 'ياسر الدوسري', country: 'Arabie saoudite', flag: '🇸🇦', hue: 200, bio: 'Imam a la Grande Mosquee.', server: null, cdnEdition: 'ar.yasseraldossari', img: 'img/reciters/Yasser Al-Dosari.jpg' },
  { id: 'qatami', name: 'Nasser Al-Qatami', ar: 'ناصر القطامي', country: 'Arabie saoudite', flag: '🇸🇦', hue: 180, bio: 'Ton chaleureux.', server: null, cdnEdition: 'ar.nasseralqatami', img: 'img/reciters/Nasser Al-Qatami.jpg' },
  { id: 'hudhaify', name: 'Ali Al-Hudhaify', ar: 'علي بن عبدالرحمن الحذيفي', country: 'Arabie saoudite', flag: '🇸🇦', hue: 150, bio: 'Imam de la Mosquee du Prophete.', server: null, cdnEdition: 'ar.hudhaify', img: 'img/reciters/Ali Al-Hudhaify.jpg' }
];"""

# Regex : remplacer le tableau RECITERS
import re
pattern = re.compile(r'const RECITERS = \[.*?\];', re.DOTALL)
match = pattern.search(js)

if match:
    js = js.replace(match.group(0), NEW_RECITERS)
    print("OK RECITERS mis a jour avec cdnEdition pour tous")
else:
    print("ERREUR : tableau RECITERS introuvable")

with open('js/app.js', 'w', encoding='utf-8', newline='\n') as f:
    f.write(js)
