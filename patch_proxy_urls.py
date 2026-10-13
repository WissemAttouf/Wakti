#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import re

with open('js/app.js', 'r', encoding='utf-8') as f:
    js = f.read()

pattern = re.compile(r'async function getAudioUrls\(n, reciter\)\s*\{.*?\n\}', re.DOTALL)

NEW_GET_URLS = """async function getAudioUrls(n, reciter) {
  const key = n + '|' + reciter;
  if (audioCache.has(key)) return audioCache.get(key);
  const recObj = RBY[reciter];
  let urls;

  const viaProxy = (url) => '/api/audio-proxy?url=' + encodeURIComponent(url);

  if (recObj && recObj.everyayahFolder) {
    const first = FIRST_GLOBAL[n - 1];
    const count = SURAHS[n - 1].c;
    urls = Array.from({ length: count }, (_, i) => {
      let sNum = 1, aNum = first + i;
      for (let s = 0; s < SURAHS.length; s++) {
        if (aNum <= SURAHS[s].c) { sNum = s + 1; break; }
        aNum -= SURAHS[s].c;
      }
      const surahPad = String(sNum).padStart(3, '0');
      const ayahPad = String(aNum).padStart(3, '0');
      return viaProxy('https://everyayah.com/data/' + recObj.everyayahFolder + '/' + surahPad + ayahPad + '.mp3');
    });
  } else if (recObj && recObj.server) {
    const numPad = String(n).padStart(3, '0');
    urls = [viaProxy(recObj.server + numPad + '.mp3')];
  } else {
    urls = [''];
  }
  audioCache.set(key, urls);
  return urls;
}"""

if pattern.search(js):
    js = pattern.sub(NEW_GET_URLS, js, count=1)
    print("OK getAudioUrls utilise le proxy")
else:
    print("ERREUR : getAudioUrls introuvable")

with open('js/app.js', 'w', encoding='utf-8', newline='\n') as f:
    f.write(js)
