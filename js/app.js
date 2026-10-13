

/* ===== WAKTI ACTION LOGGING HELPERS ===== */
function waktiLog(action, target, metadata) {
  if (window.WaktiAuth && typeof window.WaktiAuth.logActivity === 'function') {
    window.WaktiAuth.logActivity(action, target, metadata);
  }
}
// FIN WAKTI ACTION LOGGING HELPERS
"use strict";

/* =====================================================================
   Wakti — Application complete (monolithique)
   Coran, horaires de priere, calendrier hegirien
===================================================================== */

/* =====================================================================
   1. UTILITAIRES
===================================================================== */
const $  = (s, r = document) => r.querySelector(s);
const $$ = (s, r = document) => [...r.querySelectorAll(s)];
const esc = s => String(s).replace(/[&<>"']/g, c => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
}[c]));
const pad = n => String(n).padStart(2, '0');
const AR_DIGITS = '٠١٢٣٤٥٦٧٨٩';
const toAr = n => String(n).replace(/\d/g, d => AR_DIGITS[d]);
const stripAr = s => String(s)
  .replace(/[\u064B-\u065F\u0670\u06D6-\u06ED\u0640]/g, '')
  .replace(/[\u0671\u0623\u0625\u0622]/g, '\u0627')
  .replace(/\u0649/g, '\u064A')
  .replace(/\u0629/g, '\u0647');
const stripLat = s => String(s)
  .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
  .toLowerCase().replace(/[^a-z0-9]/g, '');
const fmtTime = s => {
  if (!isFinite(s) || s < 0) s = 0;
  s = Math.floor(s);
  const m = Math.floor(s / 60);
  const sec = s % 60;
  return m + ':' + String(sec).padStart(2, '0');
};

const store = {
  get(k, d) {
    try {
      const v = localStorage.getItem('wakti:' + k);
      return v == null ? d : JSON.parse(v);
    } catch (e) { return d; }
  },
  set(k, v) {
    try { localStorage.setItem('wakti:' + k, JSON.stringify(v)); } catch (e) {}
  }
};

/* =====================================================================
   Toast simple (message rapide)
===================================================================== */
function toast(msg, ms = 2800) {
  const t = $('#toast');
  if (!t) return;
  t.innerHTML = '<span class="toast-msg">' + esc(msg) + '</span>';
  t.classList.remove('has-action');
  t.classList.add('show');
  clearTimeout(toast._t);
  toast._t = setTimeout(() => t.classList.remove('show'), ms);
}

/* =====================================================================
   Toast avec action (Annuler, Restaurer, etc.)
   Retourne une Promise : resolve(true) si l utilisateur clique l action,
                          resolve(false) si le toast expire.
===================================================================== */
function toastAction(msg, actionLabel, durationMs = 5000) {
  return new Promise(resolve => {
    const t = $('#toast');
    if (!t) { resolve(false); return; }

    // Creer le HTML du toast
    t.innerHTML =
      '<span class="toast-msg">' + esc(msg) + '</span>' +
      '<button class="toast-action" type="button">' + esc(actionLabel) + '</button>' +
      '<span class="toast-bar"><i></i></span>';

    t.classList.add('has-action', 'show');
    t.style.setProperty('--toast-duration', durationMs + 'ms');

    // Forcer le redemarrage de l animation de la barre
    const bar = t.querySelector('.toast-bar i');
    if (bar) {
      bar.style.animation = 'none';
      void bar.offsetHeight;
      bar.style.animation = '';
    }

    const actionBtn = t.querySelector('.toast-action');
    let done = false;

    const finish = (result) => {
      if (done) return;
      done = true;
      clearTimeout(timer);
      t.classList.remove('show', 'has-action');
      actionBtn.removeEventListener('click', onAction);
      resolve(result);
    };

    const onAction = () => finish(true);
    actionBtn.addEventListener('click', onAction);

    const timer = setTimeout(() => finish(false), durationMs);
  });
}

async function getJSON(url, opts = {}) {
  const { retries = 2, timeout = 12000 } = opts;
  let last;
  for (let i = 0; i <= retries; i++) {
    const ctl = new AbortController();
    const t = setTimeout(() => ctl.abort(), timeout);
    try {
      const r = await fetch(url, { signal: ctl.signal });
      clearTimeout(t);
      if (!r.ok) throw new Error('HTTP ' + r.status);
      const j = await r.json();
      if (j && j.code && j.code !== 200) throw new Error(j.status || 'Erreur API');
      return j;
    } catch (e) {
      clearTimeout(t);
      last = e;
      if (i < retries) await new Promise(res => setTimeout(res, 500 * (i + 1)));
    }
  }
  throw last;
}

/* =====================================================================
   2. DATES
===================================================================== */
const utc = (y, m, d) => new Date(Date.UTC(y, m - 1, d, 12));
const keyOf = (y, m, d) => y + '-' + pad(m) + '-' + pad(d);

function addDays(y, m, d, n) {
  const dt = utc(y, m, d);
  dt.setUTCDate(dt.getUTCDate() + n);
  return { y: dt.getUTCFullYear(), m: dt.getUTCMonth() + 1, d: dt.getUTCDate() };
}

function zonedNow(tz) {
  const mk = z => new Intl.DateTimeFormat('en-GB', {
    timeZone: z || undefined, hourCycle: 'h23',
    year: 'numeric', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', second: '2-digit'
  });
  let f;
  try { f = mk(tz); } catch (e) { f = mk(null); }
  const p = Object.fromEntries(f.formatToParts(new Date()).map(x => [x.type, x.value]));
  return { y: +p.year, m: +p.month, d: +p.day, h: +p.hour % 24, mi: +p.minute, s: +p.second };
}

const fmtLong = new Intl.DateTimeFormat('fr-FR', {
  weekday: 'long', day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC'
});
const fmtMonth = new Intl.DateTimeFormat('fr-FR', {
  month: 'long', year: 'numeric', timeZone: 'UTC'
});

/* =====================================================================
   3. CALENDRIER HEGIRIEN
===================================================================== */
const HM_FR = ['Mouharram','Safar','Rabi al-awwal','Rabi ath-thani','Joumada al-oula','Joumada ath-thania','Rajab','Chaabane','Ramadan','Chawwal','Dhou al-qida','Dhou al-hijja'];
const HM_AR = ['محرم','صفر','ربيع الأول','ربيع الآخر','جمادى الأولى','جمادى الآخرة','رجب','شعبان','رمضان','شوال','ذو القعدة','ذو الحجة'];
const WD_AR = ['الأحد','الاثنين','الثلاثاء','الأربعاء','الخميس','الجمعة','السبت'];
const EVENTS = {
  '1-1':'Nouvel An hegirien','10-1':'Achoura','12-3':'Mawlid','27-7':'Isra et Miraj',
  '15-8':'Nuit de la mi-Chaabane','1-9':'Debut du Ramadan','27-9':'Nuit du Destin',
  '1-10':'Aid al-Fitr','9-12':'Jour de Arafat','10-12':'Aid al-Adha'
};
const hFmt = new Intl.DateTimeFormat('en-u-ca-islamic-umalqura-nu-latn', {
  timeZone: 'UTC', day: 'numeric', month: 'numeric', year: 'numeric'
});
const hMemo = new Map();

function hijriOf(y, m, d) {
  const k = y + '-' + m + '-' + d + '|' + state.hAdj;
  if (hMemo.has(k)) return hMemo.get(k);
  const dt = utc(y, m, d);
  dt.setUTCDate(dt.getUTCDate() + Number(state.hAdj || 0));
  let r = null;
  try {
    const p = Object.fromEntries(hFmt.formatToParts(dt).map(x => [x.type, x.value]));
    r = { d: +p.day, m: +p.month, y: +p.year };
    if (!(r.y > 1300 && r.y < 1700 && r.m >= 1 && r.m <= 12)) r = null;
  } catch (e) { r = null; }
  hMemo.set(k, r);
  return r;
}

/* =====================================================================
   4. ETAT GLOBAL
===================================================================== */
const state = {
  loc: store.get('loc', null),
  method: store.get('method', 'auto'),
  school: store.get('school', '0'),
  hAdj: store.get('hAdj', 0),
  notify: store.get('notify', false),
  autoNext: store.get('autoNext', true),
  tz: store.get('tz', null),
  times: null, tomorrow: null, dateKey: null,
  loading: false, error: '', lastTry: 0, offline: false,
  fired: {}, armed: false
};

/* =====================================================================
   5. DONNEES : SOURATES (114)
===================================================================== */
const SURAHS = [
['الفاتحة','Al-Fatiha',7,'L Ouverture'],['البقرة','Al-Baqara',286,'La Vache'],['آل عمران','Al-Imran',200,'La Famille d Imran'],
['النساء','An-Nisa',176,'Les Femmes'],['المائدة','Al-Maida',120,'La Table servie'],['الأنعام','Al-Anam',165,'Les Bestiaux'],
['الأعراف','Al-Araf',206,'Les Murailles'],['الأنفال','Al-Anfal',75,'Le Butin'],['التوبة','At-Tawba',129,'Le Repentir'],
['يونس','Yunus',109,'Jonas'],['هود','Hud',123,'Hud'],['يوسف','Yusuf',111,'Joseph'],
['الرعد','Ar-Rad',43,'Le Tonnerre'],['إبراهيم','Ibrahim',52,'Abraham'],['الحجر','Al-Hijr',99,'Al-Hijr'],
['النحل','An-Nahl',128,'Les Abeilles'],['الإسراء','Al-Isra',111,'Le Voyage nocturne'],['الكهف','Al-Kahf',110,'La Caverne'],
['مريم','Maryam',98,'Marie'],['طه','Ta-Ha',135,'Ta-Ha'],['الأنبياء','Al-Anbiya',112,'Les Prophetes'],
['الحج','Al-Hajj',78,'Le Pelerinage'],['المؤمنون','Al-Muminun',118,'Les Croyants'],['النور','An-Nur',64,'La Lumiere'],
['الفرقان','Al-Furqan',77,'Le Discernement'],['الشعراء','Ash-Shuara',227,'Les Poetes'],['النمل','An-Naml',93,'Les Fourmis'],
['القصص','Al-Qasas',88,'Le Recit'],['العنكبوت','Al-Ankabut',69,'L Araignee'],['الروم','Ar-Rum',60,'Les Romains'],
['لقمان','Luqman',34,'Luqman'],['السجدة','As-Sajda',30,'La Prosternation'],['الأحزاب','Al-Ahzab',73,'Les Coalises'],
['سبأ','Saba',54,'Saba'],['فاطر','Fatir',45,'Le Createur'],['يس','Ya-Sin',83,'Ya-Sin'],['الصافات','As-Saffat',182,'Les Ranges'],
['ص','Sad',88,'Sad'],['الزمر','Az-Zumar',75,'Les Groupes'],['غافر','Ghafir',85,'Le Pardonneur'],
['فصلت','Fussilat',54,'Les Versets detailles'],['الشورى','Ash-Shura',53,'La Concertation'],['الزخرف','Az-Zukhruf',89,'L Ornement'],
['الدخان','Ad-Dukhan',59,'La Fumee'],['الجاثية','Al-Jathiya',37,'L Agenouillee'],['الأحقاف','Al-Ahqaf',35,'Al-Ahqaf'],
['محمد','Muhammad',38,'Muhammad'],['الفتح','Al-Fath',29,'La Victoire eclatante'],['الحجرات','Al-Hujurat',18,'Les Appartements'],
['ق','Qaf',45,'Qaf'],['الذاريات','Adh-Dhariyat',60,'Qui eparpillent'],['الطور','At-Tur',49,'Le Mont'],
['النجم','An-Najm',62,'L Etoile'],['القمر','Al-Qamar',55,'La Lune'],['الرحمن','Ar-Rahman',78,'Le Tout Misericordieux'],
['الواقعة','Al-Waqia',96,'L Evenement'],['الحديد','Al-Hadid',29,'Le Fer'],['المجادلة','Al-Mujadila',22,'La Discussion'],
['الحشر','Al-Hashr',24,'L Exode'],['الممتحنة','Al-Mumtahana',13,'L Eprouvee'],['الصف','As-Saff',14,'Le Rang'],
['الجمعة','Al-Jumua',11,'Le Vendredi'],['المنافقون','Al-Munafiqun',11,'Les Hypocrites'],['التغابن','At-Taghabun',18,'La Grande Perte'],
['الطلاق','At-Talaq',12,'Le Divorce'],['التحريم','At-Tahrim',12,'L Interdiction'],['الملك','Al-Mulk',30,'La Royaute'],
['القلم','Al-Qalam',52,'La Plume'],['الحاقة','Al-Haqqa',52,'Celle qui montre la verite'],['المعارج','Al-Maarij',44,'Les Degres'],
['نوح','Nuh',28,'Noe'],['الجن','Al-Jinn',28,'Les Djinns'],['المزمل','Al-Muzzammil',20,'L Enveloppe'],['المدثر','Al-Muddaththir',56,'Le Revetu'],['القيامة','Al-Qiyama',40,'La Resurrection'],['الإنسان','Al-Insan',31,'L Homme'],['المرسلات','Al-Mursalat',50,'Les Envoyes'],
['النبأ','An-Naba',40,'La Nouvelle'],['النازعات','An-Naziat',46,'Les Anges'],['عبس','Abasa',42,'Il s est renfrogne'],['التكوير','At-Takwir',29,'L Obscurcissement'],['الانفطار','Al-Infitar',19,'La Rupture'],['المطففين','Al-Mutaffifin',36,'Les Fraudeurs'],['الانشقاق','Al-Inshiqaq',25,'La Dechirure'],['البروج','Al-Buruj',22,'Les Constellations'],['الطارق','At-Tariq',17,'L Astre nocturne'],['الأعلى','Al-Ala',19,'Le Tres-Haut'],['الغاشية','Al-Ghashiya',26,'L Enveloppante'],['الفجر','Al-Fajr',30,'L Aube'],['البلد','Al-Balad',20,'La Cite'],['الشمس','Ash-Shams',15,'Le Soleil'],['الليل','Al-Layl',21,'La Nuit'],['الضحى','Ad-Duha',11,'Le Jour montant'],['الشرح','Ash-Sharh',8,'Le Reconfort'],['التين','At-Tin',8,'Le Figuier'],['العلق','Al-Alaq',19,'L Adherence'],['القدر','Al-Qadr',5,'La Destinee'],['البينة','Al-Bayyina',8,'La Preuve'],['الزلزلة','Az-Zalzala',8,'La Secousse'],['العاديات','Al-Adiyat',11,'Les Coursiers'],['القارعة','Al-Qaria',11,'Le Fracas'],['التكاثر','At-Takathur',8,'La Course aux richesses'],['العصر','Al-Asr',3,'Le Temps'],['الهمزة','Al-Humaza',9,'Les Calomniateurs'],['الفيل','Al-Fil',5,'L Elephant'],['قريش','Quraysh',4,'Quraysh'],['الماعون','Al-Maun',7,'L Ustensile'],['الكوثر','Al-Kawthar',3,'L Abondance'],['الكافرون','Al-Kafirun',6,'Les Infideles'],['النصر','An-Nasr',3,'Le Secours'],['المسد','Al-Masad',5,'Les Fibres'],['الإخلاص','Al-Ikhlas',4,'Le Monotheisme pur'],['الفلق','Al-Falaq',5,'L Aube naissante'],['الناس','An-Nas',6,'Les Hommes']
].map(([ar, tr, c, mean], i) => ({
  n: i + 1, ar, tr, c, mean,
  kAr: stripAr(ar),
  kLat: stripLat(tr)
}));

const FIRST_GLOBAL = (() => {
  let acc = 1;
  return SURAHS.map(s => { const f = acc; acc += s.c; return f; });
})();

/* =====================================================================
   6. DONNEES : RECITATEURS
===================================================================== */
const RECITERS = [
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
];

const RBY = Object.fromEntries(RECITERS.map(r => [r.id, r]));

/* =====================================================================
   7. PRIERES
===================================================================== */
const PRAYERS = [
  { k: 'Fajr',    fr: 'Fajr',     ar: 'الفجر',  track: true },
  { k: 'Sunrise', fr: 'Chourouq', ar: 'الشروق', track: false },
  { k: 'Dhuhr',   fr: 'Dhouhr',   ar: 'الظهر',  track: true },
  { k: 'Asr',     fr: 'Asr',      ar: 'العصر',  track: true },
  { k: 'Maghrib', fr: 'Maghrib',  ar: 'المغرب', track: true },
  { k: 'Isha',    fr: 'Icha',     ar: 'العشاء', track: true }
];
const PBY = Object.fromEntries(PRAYERS.map(p => [p.k, p]));
const TRACK = PRAYERS.filter(p => p.track).map(p => p.k);

const METHODS = [
  ['auto','Automatique'],['12','UOIF (France)'],['2','ISNA'],['3','Ligue islamique mondiale'],
  ['4','Umm al-Qura'],['5','Egypte'],['1','Karachi'],['13','Diyanet (Turquie)'],
  ['18','Tunisie'],['19','Algerie'],['21','Maroc'],['23','Jordanie']
];
const COUNTRIES = [
  ['FR','France'],['BE','Belgique'],['CH','Suisse'],['LU','Luxembourg'],['CA','Canada'],['TN','Tunisie'],['DZ','Algerie'],['MA','Maroc'],
  ['SN','Senegal'],['ML','Mali'],['CI','Cote d Ivoire'],['CM','Cameroun'],['NE','Niger'],['MR','Mauritanie'],['GN','Guinee'],['BF','Burkina Faso'],
  ['TD','Tchad'],['KM','Comores'],['DJ','Djibouti'],['MG','Madagascar'],['EG','Egypte'],['LY','Libye'],['SA','Arabie saoudite'],['AE','Emirats'],
  ['QA','Qatar'],['KW','Koweit'],['JO','Jordanie'],['LB','Liban'],['TR','Turquie'],['GB','Royaume-Uni'],['DE','Allemagne'],['ES','Espagne'],
  ['IT','Italie'],['NL','Pays-Bas'],['US','Etats-Unis']
];
const QUICK = [
  ['Paris','Paris','FR'],['Bruxelles','Brussels','BE'],['Geneve','Geneva','CH'],['Montreal','Montreal','CA'],['Tunis','Tunis','TN'],
  ['Alger','Algiers','DZ'],['Casablanca','Casablanca','MA'],['Dakar','Dakar','SN'],['La Mecque','Makkah','SA']
];

const TN_METHOD = '18';
const TN_TUNE = '0,2,0,0,1,0,0,0,0';

function parseTimings(t) {
  const out = {};
  for (const p of PRAYERS) {
    const mm = /(\d{1,2}):(\d{2})/.exec(t[p.k] || '');
    if (!mm) throw new Error('Horaire manquant : ' + p.k);
    out[p.k] = { s: +mm[1] * 3600 + +mm[2] * 60, str: pad(+mm[1]) + ':' + mm[2] };
  }
  return out;
}

/* =====================================================================
   8. THEME ET NAVIGATION
===================================================================== */
function setTheme(t) {
  // Supporte : dark | light | sabah | layl
  const validThemes = ['dark', 'light', 'sabah', 'layl'];
  if (!validThemes.includes(t)) t = 'dark';

  document.documentElement.dataset.theme = t;
  store.set('theme', t);

  // Meta theme-color
  const metaTheme = document.getElementById('metaThemeColor');
  if (metaTheme) {
    const metaColors = {
      dark: '#04201c',
      light: '#eef5f1',
      sabah: '#faf5ea',
      layl: '#0a1024'
    };
    metaTheme.content = metaColors[t] || '#04201c';
  }

  // Icone du bouton (soleil/lune)
  const ic = document.getElementById('themeIc');
  if (ic) {
    const isDark = (t === 'dark' || t === 'layl');
    ic.setAttribute('href', isDark ? '#i-sun' : '#i-moon');
  }

  // Mettre a jour le selecteur visuel
  if (typeof updateThemeSelector === 'function') {
    setTimeout(updateThemeSelector, 50);
  }
}

const themeBtn = document.getElementById('themeBtn');
if (themeBtn) themeBtn.addEventListener('click', () => {
  const current = document.documentElement.dataset.theme || 'dark';
  const themes = ['dark', 'light', 'sabah', 'layl'];
  const next = themes[(themes.indexOf(current) + 1) % themes.length];
  setTheme(next);
  const names = { dark: 'Sombre', light: 'Clair', sabah: 'Sabah', layl: 'Layl' };
  if (typeof toast === 'function') toast('Theme : ' + names[next], 1800);
  if (typeof vibrate === 'function') vibrate([10]);
});

const VIEWS = ['prieres', 'coran', 'calendrier', 'qibla', 'douas', 'aide'];
let currentView = 'prieres';

function showView(v) {
  currentView = v;
  $$('.view').forEach(s => s.classList.toggle('active', s.id === 'view-' + v));
  $$('[data-nav]').forEach(a => {
    const on = a.dataset.nav === v;
    a.classList.toggle('active', on);
    if (on) a.setAttribute('aria-current', 'page');
    else a.removeAttribute('aria-current');
  });
}

function route() {
  const h = location.hash.replace(/^#\/?/, '').split('/');
  const v = VIEWS.includes(h[0]) ? h[0] : 'prieres';
  showView(v);
  window.scrollTo(0, 0);
  if (v !== 'coran') return;
  const seg = h[1] || '';
  if (seg === 'recitateurs') {
    if (h[2]) openReciterProfile(h[2]);
    else { showCoranPanel('hub'); switchQTab('recitateurs'); }
  } else if (seg === 'marque-pages') {
    showCoranPanel('hub'); switchQTab('marque-pages');
  } else if (seg === 'lire') {
    const n = parseInt(h[2], 10);
    if (n >= 1 && n <= 114) openMushafForSurah(n);
    else { showCoranPanel('hub'); switchQTab('sourates'); }
  } else if (seg === 'ecouter') {
    const rid = h[2], n = parseInt(h[3], 10), i = parseInt(h[4], 10) || 0;
    if (RBY[rid] && n >= 1 && n <= 114) openLecteur(rid, n, i);
    else { showCoranPanel('hub'); switchQTab('sourates'); }
  } else {
    showCoranPanel('hub'); switchQTab('sourates');
  }
}

window.addEventListener('hashchange', route);

/* =====================================================================
   9. PRIERES : CHARGEMENT
===================================================================== */
function timingsURL(dateStr) {
  const l = state.loc;
  const q = [];
  const isTunisia = (l.country && l.country.toUpperCase() === 'TN') ||
                    (l.label && /tunis/i.test(l.label));
  if (isTunisia) {
    if (state.method === 'auto' || state.method === '18') q.push('method=' + TN_METHOD);
    else q.push('method=' + state.method);
    q.push('tune=' + TN_TUNE);
  } else if (state.method && state.method !== 'auto') {
    q.push('method=' + state.method);
  }
  if (state.school === '1') q.push('school=1');
  const extra = q.length ? '&' + q.join('&') : '';
  const base = 'https://api.aladhan.com/v1/';
  if (l.type === 'coords') return base + 'timings/' + dateStr + '?latitude=' + l.lat + '&longitude=' + l.lng + extra;
  return base + 'timingsByCity/' + dateStr + '?city=' + encodeURIComponent(l.city) + '&country=' + encodeURIComponent(l.country) + extra;
}

const locSig = () => JSON.stringify([state.loc, state.method, state.school]);

async function loadTimings() {
  if (!state.loc) { renderPlist(); return; }
  if (state.loading) return;
  state.loading = true;
  state.lastTry = Date.now();
  state.error = '';
  renderPlist();
  const z = zonedNow(state.tz);
  const t0 = { y: z.y, m: z.m, d: z.d };
  const t1 = addDays(t0.y, t0.m, t0.d, 1);
  const dk = keyOf(t0.y, t0.m, t0.d);
  const fmtDMY = ({ y, m, d }) => pad(d) + '-' + pad(m) + '-' + y;
  try {
    const [a, b] = await Promise.allSettled([
      getJSON(timingsURL(fmtDMY(t0))),
      getJSON(timingsURL(fmtDMY(t1)), { retries: 1 })
    ]);
    if (a.status !== 'fulfilled') throw a.reason;
    state.times = parseTimings(a.value.data.timings);
    const tz = a.value.data.meta && a.value.data.meta.timezone;
    if (tz) { state.tz = tz; store.set('tz', tz); }
    state.tomorrow = b.status === 'fulfilled'
      ? (() => { try { return parseTimings(b.value.data.timings); } catch (e) { return null; } })()
      : null;
    state.dateKey = dk;
    state.offline = false;
    store.set('tcache', { sig: locSig(), dk, times: state.times, tomorrow: state.tomorrow, tz: state.tz });
  } catch (e) {
    const c = store.get('tcache', null);
    if (c && c.sig === locSig() && c.dk === dk) {
      state.times = c.times;
      state.tomorrow = c.tomorrow;
      state.dateKey = dk;
      state.offline = true;
      toast('Hors ligne : horaires enregistres affiches.');
    } else {
      state.times = null;
      state.error = 'Impossible de recuperer les horaires.';
    }
  }
  state.loading = false;
  state.armed = false;
  renderPlist();
  renderDates();
  renderStreak();
  tick();
}

function renderPlist() {
  const ul = $('#plist');
  if (!ul) return;
  const locLbl = $('#locLabel');
  if (locLbl) locLbl.textContent = state.loc ? state.loc.label : 'Choisir ma ville';
  if (!state.loc) {
    ul.innerHTML = '<li class="pmsg"><p>Choisis ta ville pour afficher les horaires de priere.</p><button class="btn primary" data-open="loc">Choisir ma position</button></li>';
    return;
  }
  if (state.loading && !state.times) {
    ul.innerHTML = Array.from({ length: 6 }, () => '<li class="prow"><div class="skel"></div></li>').join('');
    return;
  }
  if (!state.times) {
    ul.innerHTML = '<li class="pmsg"><p>' + esc(state.error || 'Chargement...') + '</p><button class="btn" data-act="retry">Reessayer</button></li>';
    return;
  }
  ul.innerHTML = PRAYERS.map(p => {
    const btn = p.track
      ? '<button class="check" data-check="' + p.k + '" aria-pressed="false" aria-label="Marquer ' + p.fr + '"><svg class="ic"><use href="#i-check"/></svg></button>'
      : '<span></span>';
    return '<li class="prow' + (p.track ? '' : ' info') + '" data-k="' + p.k + '">' +
      '<span class="pn"><b lang="ar">' + p.ar + '</b><small>' + p.fr + '</small></span>' +
      '<time class="pt">' + state.times[p.k].str + '</time>' + btn + '</li>';
  }).join('');
  refreshDone();
}

function todayKey() {
  const z = zonedNow(state.tz);
  return keyOf(z.y, z.m, z.d);
}

function refreshDone() {
  const list = (store.get('done', {})[todayKey()]) || [];
  $$('#plist .prow[data-k]').forEach(li => {
    const on = list.includes(li.dataset.k);
    li.classList.toggle('done', on);
    const b = $('.check', li);
    if (b) b.setAttribute('aria-pressed', on);
  });
}

function toggleDone(k) {
  const z = zonedNow(state.tz);
  const tk = keyOf(z.y, z.m, z.d);
  const sec = z.h * 3600 + z.mi * 60 + z.s;
  const done = store.get('done', {});
  const list = done[tk] || [];
  const i = list.indexOf(k);
  if (i >= 0) list.splice(i, 1);
  else {
    if (state.times && sec < state.times[k].s) {
      toast('L heure de ' + PBY[k].fr + ' n est pas encore arrivee. Patience !');
      return;
    }
    list.push(k);
    if (list.length === 5) toast('Journee complete, Masha Allah !', 4000);
  }
  done[tk] = list;
  const keys = Object.keys(done).sort();
  while (keys.length > 200) delete done[keys.shift()];
  store.set('done', done);
  vibrate([10, 30, 10]);
  waktiLog('check_prayer', 'prayer:' + k, { date: tk });
  refreshDone();
  renderStreak();
}

function phaseOf(sec) {
  const t = state.times;
  if (!t) return 'night';
  if (sec >= t.Isha.s) return 'isha';
  if (sec < t.Fajr.s) return 'night';
  if (sec < t.Sunrise.s) return 'fajr';
  if (sec < t.Dhuhr.s) return 'duha';
  if (sec < t.Asr.s) return 'dhuhr';
  if (sec < t.Maghrib.s) return 'asr';
  return 'maghrib';
}

const C = 590.6;
let lastMinuteKey = '';

function tick() {
  const z = zonedNow(state.tz);
  const key = keyOf(z.y, z.m, z.d);
  if (state.times && key !== state.dateKey && !state.loading && Date.now() - state.lastTry > 30000) {
    loadTimings(); return;
  }
  if (!state.times) {
    if (state.loc && !state.loading && state.error && Date.now() - state.lastTry > 60000) loadTimings();
    return;
  }
  const sec = z.h * 3600 + z.mi * 60 + z.s;
  const t = state.times;
  let nextK = null;
  for (const k of TRACK) { if (t[k].s > sec) { nextK = k; break; } }
  let nextS, prevS, prevK;
  if (nextK) {
    nextS = t[nextK].s;
    const i = TRACK.indexOf(nextK);
    if (i > 0) { prevK = TRACK[i - 1]; prevS = t[prevK].s; }
    else { prevK = 'Isha'; prevS = t.Isha.s - 86400; }
  } else {
    nextK = 'Fajr';
    nextS = (state.tomorrow ? state.tomorrow.Fajr.s : t.Fajr.s) + 86400;
    prevK = 'Isha';
    prevS = t.Isha.s;
  }
  const currentK = (prevK === 'Fajr' && sec >= t.Sunrise.s) ? null : prevK;
  const left = Math.max(0, nextS - sec);
  const hh = Math.floor(left / 3600), mm = Math.floor(left % 3600 / 60), ss = left % 60;
  const cd = pad(hh) + ':' + pad(mm) + ':' + pad(ss);
  const elCd = $('#countdown');
  if (elCd) elCd.textContent = cd;
  const elNextAr = $('#nextAr');
  if (elNextAr) elNextAr.textContent = PBY[nextK].ar;
  const elNextFr = $('#nextFr');
  if (elNextFr) {
    const isFriday = new Date(Date.UTC(z.y, z.m - 1, z.d)).getUTCDay() === 5;
    elNextFr.textContent = (PBY[nextK].fr === 'Dhouhr' && isFriday) ? 'Dhouhr (Jumua)' : PBY[nextK].fr;
  }
  const nextStr = nextS >= 86400
    ? (state.tomorrow ? state.tomorrow.Fajr.str : t.Fajr.str)
    : t[nextK].str;
  const elNextAt = $('#nextAt');
  if (elNextAt) elNextAt.textContent = 'a ' + nextStr + (nextS >= 86400 ? ' demain' : '');
  const prog = Math.min(1, Math.max(0, (sec - prevS) / (nextS - prevS)));
  const ringProg = $('#ringProg');
  if (ringProg) ringProg.style.strokeDashoffset = (C * prog).toFixed(1);
  const ph = phaseOf(sec);
  const sky = $('#sky');
  if (sky && sky.dataset.phase !== ph) {
    sky.dataset.phase = ph;
    announcePhase(ph);
  }
  updateCountdownPulse(nextK, left);
  $$('#plist .prow[data-k]').forEach(li => {
    const k = li.dataset.k;
    li.classList.toggle('next', k === nextK);
    li.classList.toggle('current', k === currentK);
    li.classList.toggle('past', t[k].s <= sec);
  });
  document.title = cd + ' avant ' + PBY[nextK].fr + ' - Wakti';
  if (!state.armed) {
    TRACK.forEach(k => { if (sec >= t[k].s) state.fired[key + k] = true; });
    state.armed = true;
  } else {
    for (const k of TRACK) {
      if (sec >= t[k].s && sec - t[k].s < 90 && !state.fired[key + k]) {
        state.fired[key + k] = true;
        notifyPrayer(k);
      }
    }
  }
  const mk = key + z.h + ':' + z.mi;
  if (mk !== lastMinuteKey) {
    lastMinuteKey = mk;
    renderStreak();
    try { checkSmartReminders(); } catch (e) {}
    try { checkEventReminders(); } catch (e) {}
  }
}

function chime() {
  try {
    const ctx = new (window.AudioContext || window.webkitAudioContext)();
    [523.25, 659.25, 783.99].forEach((f, i) => {
      const o = ctx.createOscillator(), g = ctx.createGain();
      o.type = 'sine';
      o.frequency.value = f;
      o.connect(g);
      g.connect(ctx.destination);
      const t = ctx.currentTime + i * 0.24;
      g.gain.setValueAtTime(0, t);
      g.gain.linearRampToValueAtTime(.16, t + .04);
      g.gain.exponentialRampToValueAtTime(.0001, t + 1.3);
      o.start(t);
      o.stop(t + 1.4);
    });
  } catch (e) {}
}

function notifyPrayer(k) {
  if (!state.notify) return;
  const p = PBY[k];
  toast('C est l heure de la priere ' + p.fr + ' (' + p.ar + ')', 7000);
  chime();
  if ('Notification' in window && Notification.permission === 'granted') {
    try {
      new Notification('Wakti : ' + p.fr, {
        body: 'C est l heure de ' + p.fr + ' (' + p.ar + ').',
        tag: 'wakti-' + k
      });
    } catch (e) {}
  }
}

function renderDates() {
  const z = zonedNow(state.tz);
  const elG = $('#gregToday');
  if (elG) elG.textContent = fmtLong.format(utc(z.y, z.m, z.d));
  const h = hijriOf(z.y, z.m, z.d);
  const elH = $('#hijriToday');
  if (elH) elH.textContent = h ? toAr(h.d) + ' ' + HM_AR[h.m - 1] + ' ' + toAr(h.y) : '';
}

/* =====================================================================
   10. REGULARITE
===================================================================== */
const BADGES = [[1, '1 jour'], [3, '3 jours'], [7, '7 jours'], [14, '14 jours'], [30, '30 jours'], [100, '100 jours']];

function renderStreak() {
  const done = store.get('done', {});
  const z = zonedNow(state.tz);
  const tk = keyOf(z.y, z.m, z.d);
  const cnt = k => (done[k] || []).length;
  let cur = { y: z.y, m: z.m, d: z.d }, n = 0;
  if (cnt(tk) < 5) cur = addDays(cur.y, cur.m, cur.d, -1);
  while (cnt(keyOf(cur.y, cur.m, cur.d)) >= 5 && n < 3650) {
    n++;
    cur = addDays(cur.y, cur.m, cur.d, -1);
  }
  const best = Math.max(store.get('best', 0), n);
  store.set('best', best);
  const elN = $('#streakN');
  if (elN) elN.textContent = n;
  const elLbl = $('#streakLbl');
  if (elLbl) elLbl.textContent = n > 1 ? 'jours de suite' : 'jour de suite';
  const today = done[tk] || [];
  const elDots = $('#todayDots');
  if (elDots) elDots.innerHTML = TRACK.map(k => '<i class="' + (today.includes(k) ? 'on' : '') + '"></i>').join('');
  const c = today.length;
  const elMsg = $('#streakMsg');
  if (elMsg) elMsg.textContent = c === 5
    ? 'Journee complete. Masha Allah !'
    : c === 0
      ? 'Bismillah : coche chaque priere.'
      : c + ' priere' + (c > 1 ? 's' : '') + ' sur 5 aujourd hui.';
  const ini = ['D','L','M','M','J','V','S'];
  const elWeek = $('#week');
  if (elWeek) {
    elWeek.innerHTML = Array.from({ length: 7 }, (_, i) => {
      const dd = addDays(z.y, z.m, z.d, i - 6);
      const pct = Math.round(cnt(keyOf(dd.y, dd.m, dd.d)) / 5 * 100);
      return '<div class="wk"><div><i style="height:' + pct + '%"></i></div><span>' + ini[utc(dd.y, dd.m, dd.d).getUTCDay()] + '</span></div>';
    }).join('');
  }
  const elBadges = $('#badges');
  if (elBadges) elBadges.innerHTML = BADGES.map(([v, l]) =>
    '<span class="badge' + (best >= v ? ' got' : '') + '">' + (best >= v ? '★' : '☆') + ' ' + l + '</span>').join('');
}

/* =====================================================================
   11. VERSET DU JOUR
===================================================================== */
const VOD_LIST = ['2:255','2:286','2:152','2:153','2:186','2:216','3:139','3:159','3:200','13:28','14:7','16:90','20:114','29:69','39:53','40:60','49:13','65:3','93:3','94:5','94:6','12:87'];

async function loadVod() {
  const z = zonedNow(state.tz);
  const idx = Math.floor(Date.UTC(z.y, z.m - 1, z.d) / 86400000) % VOD_LIST.length;
  const ref = VOD_LIST[idx];
  const parts = ref.split(':').map(Number);
  const sn = parts[0], an = parts[1];
  const ck = 'vod:' + ref;
  let v = store.get(ck, null);
  if (!v) {
    try {
      const j = await getJSON('https://api.alquran.cloud/v1/ayah/' + ref + '/editions/quran-uthmani,fr.hamidullah', { retries: 1 });
      v = { ar: j.data[0].text, fr: j.data[1].text };
      store.set(ck, v);
    } catch (e) {
      const elAr = $('#vodAr');
      if (elAr) elAr.textContent = '';
      const elFr = $('#vodFr');
      if (elFr) elFr.textContent = 'Le verset du jour s affichera bientot.';
      return;
    }
  }
  const s = SURAHS[sn - 1];
  const elAr = $('#vodAr');
  if (elAr) elAr.textContent = v.ar;
  const elFr = $('#vodFr');
  if (elFr) elFr.textContent = v.fr;
  const elRef = $('#vodRef');
  if (elRef) {
    elRef.innerHTML = '<span>Sourate ' + esc(s.tr) + ', verset ' + an + '</span><button class="btn" id="vodOpen">Lire la sourate</button>';
    const btnOpen = $('#vodOpen');
    if (btnOpen) btnOpen.addEventListener('click', () => openChoice(sn, an - 1));
  }
}

/* =====================================================================
   12. LOCALISATION
===================================================================== */
function fillLocDialog() {
  const elCountry = $('#countryIn');
  if (elCountry) elCountry.innerHTML = COUNTRIES.map(([c, n]) => '<option value="' + c + '">' + esc(n) + '</option>').join('');
  const elQuick = $('#quickCities');
  if (elQuick) elQuick.innerHTML = QUICK.map(([lab, city, cc], i) =>
    '<button type="button" class="chip" data-quick="' + i + '">' + esc(lab) + '</button>').join('');
}

function setLoc(loc) {
  state.loc = loc;
  store.set('loc', loc);
  state.times = null;
  state.tomorrow = null;
  state.tz = null;
  store.set('tz', null);
  state.error = '';
  const dlgLoc = $('#dlgLoc');
  if (dlgLoc && dlgLoc.close) dlgLoc.close();
  loadTimings();
  if (state.notify && window.WaktiPush && window.WaktiPush.supported()) {
    window.WaktiPush.sync({
      city: loc.city || null,
      country: loc.country || null,
      method: state.method,
      school: state.school
    });
  }
}

const elQuickCities = $('#quickCities');
if (elQuickCities) elQuickCities.addEventListener('click', e => {
  const b = e.target.closest('[data-quick]');
  if (!b) return;
  const arr = QUICK[+b.dataset.quick];
  setLoc({ type: 'city', city: arr[1], country: arr[2], label: arr[0] });
});

const elCityForm = $('#cityForm');
if (elCityForm) elCityForm.addEventListener('submit', e => {
  e.preventDefault();
  const cityIn = $('#cityIn');
  const city = cityIn ? cityIn.value.trim() : '';
  if (!city) return;
  const ccSel = $('#countryIn');
  const cc = ccSel ? ccSel.value : 'FR';
  setLoc({ type: 'city', city, country: cc, label: city });
});

const elGeoBtn = $('#geoBtn');
if (elGeoBtn) elGeoBtn.addEventListener('click', () => {
  if (!navigator.geolocation) { toast('La geolocalisation n est pas disponible.'); return; }
  elGeoBtn.disabled = true;
  navigator.geolocation.getCurrentPosition(
    pos => {
      elGeoBtn.disabled = false;
      const lat = +pos.coords.latitude.toFixed(4);
      const lng = +pos.coords.longitude.toFixed(4);
      setLoc({ type: 'coords', lat, lng, label: 'Ma position', country: '' });
    },
    () => {
      elGeoBtn.disabled = false;
      toast('Position refusee. Choisis une ville.');
    },
    { timeout: 10000, maximumAge: 600000 }
  );
});

/* =====================================================================
   13. REGLAGES
===================================================================== */
function fillSettings() {
  const mSel = $('#methodSel');
  if (mSel) {
    mSel.innerHTML = METHODS.map(([v, n]) => '<option value="' + v + '">' + esc(n) + '</option>').join('');
    mSel.value = state.method;
  }
  const sSel = $('#schoolSel');
  if (sSel) sSel.value = state.school;
  const hSel = $('#hAdjSel');
  if (hSel) hSel.value = String(state.hAdj);
  const nSw = $('#notifSw');
  if (nSw) nSw.checked = !!state.notify;
  const aSw = $('#autoSw');
  if (aSw) aSw.checked = !!state.autoNext;
}

const elMethodSel = $('#methodSel');
if (elMethodSel) elMethodSel.addEventListener('change', e => {
  state.method = e.target.value;
  store.set('method', state.method);
  state.times = null;
  loadTimings();
});

const elSchoolSel = $('#schoolSel');
if (elSchoolSel) elSchoolSel.addEventListener('change', e => {
  state.school = e.target.value;
  store.set('school', state.school);
  state.times = null;
  loadTimings();
});

const elHAdjSel = $('#hAdjSel');
if (elHAdjSel) elHAdjSel.addEventListener('change', e => {
  state.hAdj = +e.target.value;
  store.set('hAdj', state.hAdj);
  hMemo.clear();
  renderDates();
  renderCalendar();
});

const elAutoSw = $('#autoSw');
if (elAutoSw) elAutoSw.addEventListener('change', e => {
  state.autoNext = e.target.checked;
  store.set('autoNext', state.autoNext);
});

const elNotifSw = $('#notifSw');
if (elNotifSw) elNotifSw.addEventListener('change', async e => {
  if (e.target.checked) {
    window.__waktiMeta = {
      city: state.loc && state.loc.city ? state.loc.city : null,
      country: state.loc && state.loc.country ? state.loc.country : null,
      method: state.method,
      school: state.school
    };
    if (window.WaktiPush && window.WaktiPush.supported()) {
      const result = await window.WaktiPush.enable(window.__waktiMeta);
      if (result.ok) {
        state.notify = true;
        chime();
        toast('Rappels actives. Tu recevras une notification a chaque priere.', 5000);
      } else if (result.reason === 'denied') {
        state.notify = false;
        e.target.checked = false;
        toast('Notifications refusees.', 5000);
      } else {
        state.notify = true;
        chime();
        toast('Rappels sonores actives.', 5000);
      }
    } else {
      if ('Notification' in window && Notification.permission === 'default') {
        try { await Notification.requestPermission(); } catch (er) {}
      }
      state.notify = true;
      chime();
      toast('Rappels sonores actives.', 5000);
    }
  } else {
    if (window.WaktiPush) await window.WaktiPush.disable();
    state.notify = false;
    store.set('notify', state.notify);
    vibrate([15]);

    const undone = await toastAction(
      'Rappels desactives.',
      'Reactiver',
      5000
    );

    if (undone) {
      e.target.checked = true;
      e.target.dispatchEvent(new Event('change'));
    }
    return;
  }
  store.set('notify', state.notify);
});

/* =====================================================================
   14. CORAN : ONGLETS
===================================================================== */
function showCoranPanel(which) {
  const qHub = $('#quranHub'); if (qHub) qHub.hidden = which !== 'hub';
  const rProf = $('#recProfile'); if (rProf) rProf.hidden = which !== 'recProfile';
  const qMus = $('#quranMushaf'); if (qMus) qMus.hidden = which !== 'mushaf';
  const qLec = $('#quranLecteur'); if (qLec) qLec.hidden = which !== 'lecteur';
}

function switchQTab(tab) {
  $$('.qtab').forEach(b => {
    const on = b.dataset.tab === tab;
    b.classList.toggle('active', on);
    b.setAttribute('aria-selected', on);
  });
  const tS = $('#tabSourates'); if (tS) tS.hidden = tab !== 'sourates';
  const tR = $('#tabRecitateurs'); if (tR) tR.hidden = tab !== 'recitateurs';
  const tM = $('#tabMarques'); if (tM) tM.hidden = tab !== 'marque-pages';
  if (tab === 'recitateurs') renderReciters();
  if (tab === 'marque-pages') renderBookmarksTab();
}

const elQuranHub = $('#quranHub');
if (elQuranHub) {
  elQuranHub.addEventListener('click', e => {
    const b = e.target.closest('.qtab');
    if (!b) return;
    const t = b.dataset.tab;
    location.hash = t === 'sourates' ? '#/coran' : '#/coran/' + t;
  });
}

/* =====================================================================
   15. CORAN : LISTE DES SOURATES
===================================================================== */
function renderSurahList() {
  const qIn = $('#q');
  if (!qIn) return;
  const raw = qIn.value.trim();
  let list = SURAHS;
  if (raw) {
    const qa = stripAr(raw), ql = stripLat(raw);
    list = SURAHS.filter(s =>
      (/^\d+$/.test(raw) && String(s.n).startsWith(raw)) ||
      (ql && s.kLat.includes(ql)) ||
      (/[\u0600-\u06FF]/.test(raw) && s.kAr.includes(qa))
    );
  }
  const noSurah = $('#noSurah');
  if (noSurah) noSurah.hidden = list.length > 0;
  const grid = $('#surahGrid');
  if (grid) {
    grid.innerHTML = list.map(s =>
      '<button class="scard" data-n="' + s.n + '">' +
      '<span class="snum"><span>' + s.n + '</span></span>' +
      '<span class="nm"><b>' + esc(s.tr) + '</b><small>' + esc(s.mean) + ' · ' + s.c + ' versets</small></span>' +
      '<span class="ar" lang="ar">' + s.ar + '</span>' +
      '</button>'
    ).join('');
  }
}

const elSearchQ = $('#q');
if (elSearchQ) elSearchQ.addEventListener('input', renderSurahList);

const elSurahGrid = $('#surahGrid');
if (elSurahGrid) elSurahGrid.addEventListener('click', e => {
  const b = e.target.closest('[data-n]');
  if (b) openChoice(+b.dataset.n);
});

let choiceCtx = null;

function openChoice(n, i) {
  choiceCtx = { n, i: i || 0 };
  const s = SURAHS[n - 1];
  const dlgT = $('#dlgChoiceT');
  if (dlgT) dlgT.textContent = 'Sourate ' + s.tr;
  const chSub = $('#chSubtitle');
  if (chSub) chSub.textContent = s.ar + ' · ' + s.c + ' versets';
  const dlgChoice = $('#dlgChoice');
  if (dlgChoice && dlgChoice.showModal) dlgChoice.showModal();
}

const elChRead = $('#chRead');
if (elChRead) elChRead.addEventListener('click', () => {
  const dlgChoice = $('#dlgChoice');
  if (dlgChoice && dlgChoice.close) dlgChoice.close();
  if (choiceCtx) location.hash = '#/coran/lire/' + choiceCtx.n;
});

const elChListen = $('#chListen');
if (elChListen) elChListen.addEventListener('click', () => {
  const dlgChoice = $('#dlgChoice');
  if (dlgChoice && dlgChoice.close) dlgChoice.close();
  if (choiceCtx) location.hash = '#/coran/ecouter/' + P.reciter + '/' + choiceCtx.n + '/' + choiceCtx.i;
});

function renderResume() {
  const last = store.get('last', null);
  const card = $('#resumeCard');
  if (card) card.hidden = !last;
  if (!last) return;
  const s = SURAHS[last.n - 1];
  const lbl = $('#resumeLbl'), txt = $('#resumeTxt');
  if (last.mode === 'lire') {
    if (lbl) lbl.textContent = 'Reprendre ta lecture';
    if (txt) txt.textContent = 'Sourate ' + s.tr;
  } else {
    if (lbl) lbl.textContent = 'Reprendre ton ecoute';
    if (txt) txt.textContent = 'Sourate ' + s.tr + ', verset ' + (last.i + 1) + ' · ' + (RBY[last.reciter] ? RBY[last.reciter].name : '');
  }
}

const elResumeBtn = $('#resumeBtn');
if (elResumeBtn) elResumeBtn.addEventListener('click', () => {
  const last = store.get('last', null);
  if (!last) return;
  location.hash = last.mode === 'lire'
    ? '#/coran/lire/' + last.n
    : '#/coran/ecouter/' + last.reciter + '/' + last.n + '/' + last.i;
});

/* =====================================================================
   16. CORAN : MARQUE-PAGES
===================================================================== */
function renderBookmarksTab() {
  const marks = store.get('marks', []);
  const bmEmpty = $('#bmEmpty');
  if (bmEmpty) bmEmpty.hidden = marks.length > 0;
  const bmList = $('#bmList');
  if (bmList) {
    bmList.innerHTML = marks.slice().reverse().map(m => {
      const parts = m.split(':').map(Number);
      const n = parts[0], i = parts[1];
      const s = SURAHS[n - 1];
      return '<div class="bm-item">' +
        '<button class="bm-open" data-mn="' + n + '" data-mi="' + i + '">' +
        '<span class="ar" lang="ar">' + s.ar + '</span>' +
        '<span class="nm"><b>' + esc(s.tr) + '</b><small>Verset ' + (i + 1) + '</small></span>' +
        '</button>' +
        '<button class="icon-btn" data-del="' + m + '" aria-label="Retirer"><svg class="ic"><use href="#i-close"/></svg></button>' +
        '</div>';
    }).join('');
  }
}

const elBmList = $('#bmList');
if (elBmList) {
  elBmList.addEventListener('click', async e => {
    const del = e.target.closest('[data-del]');
    if (del) {
      const key = del.dataset.del;
      const parts = key.split(':').map(Number);
      const surahName = SURAHS[parts[0] - 1]?.tr || 'Sourate';
      const verseNum = parts[1] + 1;

      // Suppression immediate de l UI
      let marks = store.get('marks', []);
      const backup = [...marks];
      marks = marks.filter(m => m !== key);
      store.set('marks', marks);
      renderBookmarksTab();
      vibrate([15]);

      // Toast avec annulation
      const undone = await toastAction(
        'Marque-page ' + surahName + ' : ' + verseNum + ' supprime',
        'Annuler',
        5000
      );

      if (undone) {
        // Restaurer
        store.set('marks', backup);
        renderBookmarksTab();
        vibrate([10, 30, 10]);
        toast('Marque-page restaure.', 2000);
      }
      return;
    }
    const b = e.target.closest('[data-mn]');
    if (b) openChoice(+b.dataset.mn, +b.dataset.mi);
  });
}

/* =====================================================================
   17. CORAN : RECITATEURS
===================================================================== */
function isFavRec(id) { return store.get('favRec', []).includes(id); }

async function toggleFavRec(id) {
  const r = RBY[id];
  if (!r) return;
  let f = store.get('favRec', []);
  const wasFav = f.includes(id);
  f = wasFav ? f.filter(x => x !== id) : [...f, id];
  store.set('favRec', f);
  vibrate([10]);

  if (wasFav) {
    const undone = await toastAction(
      r.name + ' retire des favoris.',
      'Remettre',
      5000
    );
    if (undone) {
      let f2 = store.get('favRec', []);
      if (!f2.includes(id)) f2 = [...f2, id];
      store.set('favRec', f2);
      renderReciters();
      vibrate([10, 30, 10]);
      toast('Remis dans tes favoris.', 2000);
    } else {
      renderReciters();
    }
  } else {
    toast(r.name + ' ajoute a tes favoris.', 2000);
    renderReciters();
  }
}

function renderReciters() {
  const fav = store.get('favRec', []);
  const list = [...RECITERS].sort((a, b) => fav.includes(b.id) - fav.includes(a.id));
  const grid = $('#recGrid');
  if (grid) {
    grid.innerHTML = list.map(r => {
      const avatar = r.img
        ? '<span class="avatar md has-img" style="--hue:' + r.hue + '"><img src="' + esc(r.img) + '" alt="" loading="lazy" onerror="this.parentElement.classList.remove(\'has-img\');this.parentElement.innerHTML=\'<b>' + esc(r.ar[0]) + '</b>\';"></span>'
        : '<span class="avatar md" style="--hue:' + r.hue + '"><b>' + esc(r.ar[0]) + '</b></span>';
      return '<div class="rec-card" data-rid="' + r.id + '" role="button" tabindex="0">' +
        '<button class="rec-fav' + (fav.includes(r.id) ? ' on' : '') + '" data-favrid="' + r.id + '"><svg class="ic"><use href="#i-star"/></svg></button>' +
        avatar +
        '<b>' + esc(r.name) + '</b>' +
        '<span class="flag">' + r.flag + ' ' + esc(r.country) + '</span>' +
        '<small>114 sourates enregistrees</small>' +
        '</div>';
    }).join('');
  }
}

const elRecGrid = $('#recGrid');
if (elRecGrid) {
  elRecGrid.addEventListener('click', e => {
    const f = e.target.closest('[data-favrid]');
    if (f) {
      toggleFavRec(f.dataset.favrid);
      renderReciters();
      return;
    }
    const b = e.target.closest('[data-rid]');
    if (b) location.hash = '#/coran/recitateurs/' + b.dataset.rid;
  });
}

const elRecBack = $('#recBack');
if (elRecBack) elRecBack.addEventListener('click', () => { location.hash = '#/coran/recitateurs'; });

let curRecId = null;

function dlCountFor(rid) {
  const dl = store.get('dlset', {});
  return SURAHS.reduce((a, s) => a + (dl[rid + ':' + s.n] ? 1 : 0), 0);
}

function renderRecStats() {
  const c = dlCountFor(curRecId);
  const st = $('#recStats');
  if (st) st.textContent = c > 0
    ? '114 sourates · ' + c + ' hors ligne'
    : '114 sourates enregistrees';
}

function renderRecSurahs() {
  const elSurahs = $('#recSurahs');
  if (!elSurahs) return;
  elSurahs.innerHTML = SURAHS.map(s => {
    const current = P.n != null && P.n === s.n && P.reciter === curRecId;
    const active = current && !audio.paused;
    const num = current ? '<span class="eq" aria-hidden="true"><i></i><i></i><i></i><i></i></span>' : s.n;
    return '<li class="rrow' + (current ? ' current' : '') + (active ? ' playing' : '') + '" data-n="' + s.n + '">' +
      '<span class="rr-num">' + num + '</span>' +
      '<span class="rr-nm"><span class="t">' + esc(s.tr) + '<span lang="ar">(' + s.ar + ')</span></span>' +
      '<small>' + esc(s.mean) + ' · ' + s.c + ' versets</small></span>' +
      '<button class="rr-play" data-play="' + s.n + '"><svg class="ic"><use href="#' + (active ? 'i-pause' : 'i-play') + '"/></svg></button>' +
      '</li>';
  }).join('');
}

function openReciterProfile(rid) {
  const r = RBY[rid];
  if (!r) { location.hash = '#/coran/recitateurs'; return; }
  curRecId = rid;
  showCoranPanel('recProfile');
  const hero = $('#recHero');
  if (hero) hero.style.setProperty('--hue', r.hue);
  const av = $('#recAvatar');
  if (av) {
    av.style.setProperty('--hue', r.hue);
    if (r.img) {
      av.classList.add('has-img');
      av.innerHTML = '<img src="' + esc(r.img) + '" alt="" loading="lazy" onerror="this.parentElement.classList.remove(\'has-img\');this.parentElement.innerHTML=\'<b>' + esc(r.ar[0]) + '</b>\';">';
    } else {
      av.classList.remove('has-img');
      av.innerHTML = '<b>' + esc(r.ar[0]) + '</b>';
    }
  }
  const nm = $('#recName');
  if (nm) nm.textContent = r.name;
  const cnt = $('#recCountry');
  if (cnt) cnt.textContent = r.flag + ' ' + r.country;
  const bio = $('#recBio');
  if (bio) bio.textContent = r.bio;
  const fav = isFavRec(rid);
  const elFav = $('#recFav');
  if (elFav) {
    elFav.classList.toggle('on', fav);
    elFav.setAttribute('aria-pressed', fav);
  }
  renderRecStats();
  renderRecSurahs();
  window.scrollTo(0, 0);
}

const elRecSurahs = $('#recSurahs');
if (elRecSurahs) {
  elRecSurahs.addEventListener('click', e => {
    const pb = e.target.closest('[data-play]') || e.target.closest('[data-n]');
    if (!pb) return;
    const n = +(pb.dataset.play || pb.dataset.n);
    if (P.reciter === curRecId && P.n === n) {
      togglePlay();
      return;
    }
    location.hash = '#/coran/ecouter/' + curRecId + '/' + n + '/0';
  });
}

const elRecPlayAll = $('#recPlayAll');
if (elRecPlayAll) elRecPlayAll.addEventListener('click', () => {
  location.hash = '#/coran/ecouter/' + curRecId + '/1/0';
});

const elRecFav = $('#recFav');
if (elRecFav) elRecFav.addEventListener('click', () => {
  toggleFavRec(curRecId);
  const fav = isFavRec(curRecId);
  elRecFav.classList.toggle('on', fav);
  elRecFav.setAttribute('aria-pressed', fav);
});

const elRecShare = $('#recShare');
if (elRecShare) elRecShare.addEventListener('click', async () => {
  const r = RBY[curRecId];
  if (!r) return;
  const text = 'Ecoute le Coran recite par ' + r.name + ' sur Wakti.';
  if (navigator.share) {
    try { await navigator.share({ title: 'Wakti', text }); } catch (e) {}
    return;
  }
  try {
    await navigator.clipboard.writeText(text);
    toast('Lien copie.');
  } catch (e) {
    toast('Partage indisponible.');
  }
});

/* =====================================================================
   18. CORAN : MUSHAF
===================================================================== */
function cleanAyah(n, i, text) {
  if (i !== 0 || n === 1 || n === 9) return text;
  const words = text.trim().split(/\s+/);
  if (words.slice(0, 4).map(stripAr).join(' ') === 'بسم الله الرحمن الرحيم') {
    return words.slice(4).join(' ');
  }
  return text;
}

const MUS = {
  page: null,
  size: store.get('musSize', 26),
  showTr: store.get('musTr', false)
};

function applyMusPrefs() {
  const qMus = $('#quranMushaf');
  if (!qMus) return;
  qMus.style.setProperty('--mus-size', MUS.size + 'px');
  qMus.classList.toggle('show-tr', MUS.showTr);
  const trTog = $('#musTrToggle');
  if (trTog) trTog.checked = MUS.showTr;
}

function isMushafOpen() {
  const qMus = $('#quranMushaf');
  return currentView === 'coran' && qMus && !qMus.hidden;
}

async function pageOfSurah(n) {
  const cache = store.get('pageOf', {});
  if (cache[n]) return cache[n];
  const j = await getJSON('https://api.alquran.cloud/v1/ayah/' + FIRST_GLOBAL[n - 1] + '/quran-uthmani', { retries: 1 });
  const p = (j.data && j.data.page) || 1;
  cache[n] = p;
  store.set('pageOf', cache);
  return p;
}

async function openMushafForSurah(n) {
  showCoranPanel('mushaf');
  applyMusPrefs();
  const pageEl = $('#musPage');
  if (pageEl) pageEl.innerHTML = '<div class="loading"><div class="skel"></div><div class="skel"></div><div class="skel"></div></div>';
  try {
    const p = await pageOfSurah(n);
    await openMushafPage(p);
    store.set('last', { mode: 'lire', n });
    waktiLog('read_surah', 'surah:' + n);
    renderResume();
  } catch (e) {
    if (pageEl) pageEl.innerHTML = '<div class="errbox"><p>Impossible d ouvrir cette sourate.</p><button class="btn primary" id="retryMus">Reessayer</button></div>';
    const rb = $('#retryMus');
    if (rb) rb.addEventListener('click', () => openMushafForSurah(n));
  }
}

const pageCache = new Map();

async function getPage(p) {
  p = Math.min(604, Math.max(1, p));

  if (pageCache.has(p)) return pageCache.get(p);

  const saved = store.get('pg' + p, null);
  if (saved && Array.isArray(saved) && saved.length) {
    pageCache.set(p, saved);
    return saved;
  }

  // L API ne supporte plus editions multiples, on fait 2 requetes separees
  try {
    // 1. Arabe (uthmani) - obligatoire
    const urlAr = 'https://api.alquran.cloud/v1/page/' + p + '/quran-uthmani';
    const jAr = await getJSON(urlAr, { retries: 1 });

    if (!jAr || !jAr.data || !jAr.data.ayahs) {
      throw new Error('Structure arabe invalide');
    }

    // 2. Francais (hamidullah) - optionnel (fallback si 404)
    let frAyahs = null;
    try {
      const urlFr = 'https://api.alquran.cloud/v1/page/' + p + '/fr.hamidullah';
      const jFr = await getJSON(urlFr, { retries: 0 });
      if (jFr && jFr.data && jFr.data.ayahs) {
        frAyahs = jFr.data.ayahs;
      }
    } catch (eFr) {
      console.warn('[getPage] Traduction FR indisponible pour page', p);
    }

    // 3. Fusionner
    const out = jAr.data.ayahs.map((a, idx) => ({
      text: a.text,
      n: a.numberInSurah,
      surah: a.surah.number,
      juz: a.juz,
      sajda: !!a.sajda,
      fr: (frAyahs && frAyahs[idx]) ? frAyahs[idx].text : ''
    }));

    pageCache.set(p, out);
    try { store.set('pg' + p, out); } catch (e) {}
    return out;

  } catch (e) {
    console.error('[getPage] Erreur pour page', p, ':', e.message);
    return null;
  }
}

async function openMushafPage(p) {
  const prevPage = MUS.page;
  p = Math.min(604, Math.max(1, p));
  MUS.page = p;
  // Slide animation
  if (prevPage != null && p !== prevPage) {
    slideMushaf(p > prevPage ? 'left' : 'right');
  }
  const pNum = $('#musPageNum');
  if (pNum) pNum.textContent = toAr(p) + ' · ' + p + ' / 604';
  const pBtn = $('#musPrevBtn');
  if (pBtn) pBtn.disabled = p <= 1;
  const nBtn = $('#musNextBtn');
  if (nBtn) nBtn.disabled = p >= 604;
  const pageEl = $('#musPage');
  if (pageEl) pageEl.innerHTML = '<div class="loading"><div class="skel"></div><div class="skel"></div><div class="skel"></div></div>';
  try {
    const data = await getPage(p);
    if (MUS.page !== p) return;
    renderMushafPage(data);
  } catch (e) {
    if (MUS.page !== p) return;
    if (pageEl) pageEl.innerHTML = '<div class="errbox"><p>Impossible de charger la page ' + p + '.</p><button class="btn primary" id="retryPage">Reessayer</button></div>';
    const rb = $('#retryPage');
    if (rb) rb.addEventListener('click', () => openMushafPage(p));
  }
}

function renderMushafPage(rows) {
  let html = '';
  let ar = '';
  let lastSurah = null;
  const frLines = [];

  rows.forEach(a => {
    if (a.surah !== lastSurah) {
      if (ar) { html += '<p class="mus-ar" lang="ar" dir="rtl">' + ar + '</p>'; ar = ''; }
      const s = SURAHS[a.surah - 1];
      html += '<div class="mus-band" lang="ar">' + s.ar + ' <span lang="fr">- ' + esc(s.tr) + '</span></div>';
      if (a.n === 1 && a.surah !== 1 && a.surah !== 9) {
        html += '<div class="mus-bismillah" lang="ar" dir="rtl">بِسْمِ ٱللَّهِ ٱلرَّحْمَٰنِ ٱلرَّحِيمِ</div>';
      }
      lastSurah = a.surah;
    }
    const txt = cleanAyah(a.surah, a.n - 1, a.text);
    ar += esc(txt) + ' <span class="end' + (a.sajda ? ' sajda' : '') + '" data-n="' + a.surah + ':' + (a.n - 1) + '" role="button" aria-label="Verset ' + a.n + '">' + toAr(a.n) + '</span> ';
    frLines.push('<div><b>' + a.surah + ':' + a.n + '</b>' + esc(a.fr) + '</div>');
  });

  if (ar) html += '<p class="mus-ar" lang="ar" dir="rtl">' + ar + '</p>';
  html += '<div class="mus-fr-list">' + frLines.join('') + '</div>';

  // Coins ornes (decorations)
  html += '<span class="mus-corner tl" aria-hidden="true"></span>';
  html += '<span class="mus-corner tr" aria-hidden="true"></span>';
  html += '<span class="mus-corner bl" aria-hidden="true"></span>';
  html += '<span class="mus-corner br" aria-hidden="true"></span>';

  // Marge de juz en arabe
  if (rows[0]) {
    const juzNum = rows[0].juz;
    html += '<span class="mus-juz-margin" lang="ar">الجزء ' + toAr(juzNum) + '</span>';
  }

  const pageEl = document.getElementById('musPage');
  if (pageEl) pageEl.innerHTML = html;

  const first = SURAHS[rows[0].surah - 1].tr;
  const lastS = SURAHS[rows[rows.length - 1].surah - 1].tr;
  const mSurah = document.getElementById('musSurah');
  if (mSurah) mSurah.textContent = first === lastS ? first : first + ' → ' + lastS;
  const mJuz = document.getElementById('musJuz');
  if (mJuz) mJuz.textContent = 'Jouzo ' + rows[0].juz + ' sur 30';
  markPlaying();
}

const elMusPage = $('#musPage');
if (elMusPage) {
  elMusPage.addEventListener('click', e => {
    const end = e.target.closest('.end');
    if (!end) return;
    const parts = end.dataset.n.split(':').map(Number);
    playAt(parts[0], parts[1]);
  });
}

const elMusPrevBtn = $('#musPrevBtn');
if (elMusPrevBtn) elMusPrevBtn.addEventListener('click', () => openMushafPage(MUS.page - 1));

const elMusNextBtn = $('#musNextBtn');
if (elMusNextBtn) elMusNextBtn.addEventListener('click', () => openMushafPage(MUS.page + 1));

const elMusJumpBtn = $('#musJumpBtn');
if (elMusJumpBtn) elMusJumpBtn.addEventListener('click', () => {
  const v = prompt('Aller a la page (1 a 604) :', MUS.page || 1);
  const p = parseInt(v, 10);
  if (p >= 1 && p <= 604) openMushafPage(p);
});

const elMusPlus = $('#musPlus');
if (elMusPlus) elMusPlus.addEventListener('click', () => {
  MUS.size = Math.min(44, MUS.size + 3);
  store.set('musSize', MUS.size);
  applyMusPrefs();
});

const elMusMinus = $('#musMinus');
if (elMusMinus) elMusMinus.addEventListener('click', () => {
  MUS.size = Math.max(16, MUS.size - 3);
  store.set('musSize', MUS.size);
  applyMusPrefs();
});

const elMusTrToggle = $('#musTrToggle');
if (elMusTrToggle) elMusTrToggle.addEventListener('change', e => {
  MUS.showTr = e.target.checked;
  store.set('musTr', MUS.showTr);
  applyMusPrefs();
});

const elMusBack = $('#musBack');
if (elMusBack) elMusBack.addEventListener('click', () => { location.hash = '#/coran'; });

/* =====================================================================
   19. CORAN : LECTEUR PLEIN ECRAN
===================================================================== */
function isLecteurOpen() {
  const qLec = $('#quranLecteur');
  return currentView === 'coran' && qLec && !qLec.hidden;
}

function renderLecReciters() {
  const elRecs = $('#lecReciters');
  if (!elRecs) return;
  elRecs.innerHTML = RECITERS.map(r => {
    const av = r.img
      ? '<span class="avatar has-img" style="--hue:' + r.hue + '"><img src="' + esc(r.img) + '" alt="" loading="lazy"></span>'
      : '<span class="avatar" style="--hue:' + r.hue + '"><b>' + esc(r.ar[0]) + '</b></span>';
    return '<button class="rchip' + (r.id === P.reciter ? ' on' : '') + '" data-rid="' + r.id + '">' + av + esc(r.name) + '</button>';
  }).join('');
}

const elLecReciters = $('#lecReciters');
if (elLecReciters) {
  elLecReciters.addEventListener('click', e => {
    const b = e.target.closest('[data-rid]');
    if (!b || b.dataset.rid === P.reciter) return;
    P.reciter = b.dataset.rid;
    store.set('reciter', P.reciter);
    renderLecReciters();
    if (P.n != null) playAt(P.n, P.idx);
    toast('Recitateur : ' + reciterName());
  });
}

async function openLecteur(rid, n, i) {
  P.reciter = rid;
  store.set('reciter', rid);
  showCoranPanel('lecteur');
  renderLecReciters();
  updatePlayerUI();
  if (P.n !== n || P.idx !== i || !audio.src) await playAt(n, i);
  store.set('last', { mode: 'ecouter', reciter: rid, n, i });
  waktiLog('listen_verse', 'surah:' + n + ':' + (i + 1), { reciter: rid });
  renderResume();
  
}

const elLecBack = $('#lecBack');
if (elLecBack) elLecBack.addEventListener('click', () => {
  if (history.length > 1) history.back();
  else location.hash = '#/coran';
});

const elLecPlay = $('#lecPlay');
if (elLecPlay) elLecPlay.addEventListener('click', togglePlay);

const elLecPrev = $('#lecPrev');
if (elLecPrev) elLecPrev.addEventListener('click', prevVerse);

const elLecNext = $('#lecNext');
if (elLecNext) elLecNext.addEventListener('click', nextVerse);

const elLecRead = $('#lecRead');
if (elLecRead) elLecRead.addEventListener('click', () => {
  if (P.n) location.hash = '#/coran/lire/' + P.n;
});

const elLecSpeed = $('#lecSpeed');
if (elLecSpeed) elLecSpeed.addEventListener('click', () => {
  const rates = [0.75, 1, 1.25, 1.5];
  P.rate = rates[(rates.indexOf(P.rate) + 1) % rates.length];
  store.set('rate', P.rate);
  audio.playbackRate = P.rate;
  audio.defaultPlaybackRate = P.rate;
  updatePlayerUI();
});

const elLecMark = $('#lecMark');
if (elLecMark) elLecMark.addEventListener('click', () => {
  if (P.n == null) return;
  const key = P.n + ':' + P.idx;
  let marks = store.get('marks', []);
  if (marks.includes(key)) {
    marks = marks.filter(m => m !== key);
    toast('Marque-page retire.');
  } else {
    marks.push(key);
    toast('Marque-page ajoute.');
  }
  store.set('marks', marks);
  updatePlayerUI();
});

const elPlInfoBtn = $('#plInfoBtn');
if (elPlInfoBtn) elPlInfoBtn.addEventListener('click', () => {
  if (P.n != null) location.hash = '#/coran/ecouter/' + P.reciter + '/' + P.n + '/' + P.idx;
});

/* =====================================================================
   20. MOTEUR AUDIO
===================================================================== */
const P = {
  n: null, idx: 0, token: 0,
  rate: store.get('rate', 1),
  reciter: store.get('reciter', 'alafasy'),
  fails: {}
};
if (!RBY[P.reciter]) P.reciter = 'alafasy';

const audio = new Audio();
audio.preload = 'auto';
const audioCache = new Map();

async function getAudioUrls(n, reciter) {
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
}

async function playAt(n, i) {
  P.n = n;
  P.idx = i;
  const my = ++P.token;
  const pl = $('#player');
  if (pl) pl.hidden = false;
  updatePlayerUI();
  audio.play().catch(() => {});
  let urls;
  try {
    urls = await getAudioUrls(n, P.reciter);
  } catch (e) {
    toast('Audio indisponible.');
    return;
  }
  if (my !== P.token) return;
  const targetIndex = (urls.length === 1) ? 0 : Math.min(i, urls.length - 1);
  const targetUrl = urls[targetIndex] || urls[0];
  if (!targetUrl) {
    toast('URL audio introuvable.');
    return;
  }
  if (audio.src !== targetUrl) {
    audio.src = targetUrl;
    audio.defaultPlaybackRate = P.rate;
    audio.playbackRate = P.rate;
  }
  try {
    await audio.play();
  } catch (e) {
    if (e.name !== 'AbortError') toast('Lecture impossible.');
  }
  if (my !== P.token) return;
  updatePlayerUI();
  setMedia();
  showVersePanel(n, i);
  updateLecteurLyrics(n, i);
}

function togglePlay() {
  if (P.n == null) return;
  if (!audio.src) { playAt(P.n, P.idx); return; }
  if (audio.paused) audio.play().catch(() => {});
  else audio.pause();
}

function isSingleFileMode() {
  // Tous les recitateurs utilisent maintenant cdnEdition (verset par verset)
  // donc plus de mode "sourate complete"
  return false;
}

function nextVerse() {
  if (P.n == null) return;

  // Mode sourate complète : pas de répétition
  if (isSingleFileMode()) { surahEnded(); return; }

  // Vérifier si on doit répéter
  if (shouldRepeat()) {
    decrementRepeat();
    const remaining = repeatState.remaining;
    if (remaining !== Infinity && remaining > 0) {
      toast('Encore ' + remaining + ' fois', 1500);
    }
    // Rejouer le même verset
    playAt(P.n, P.idx);
    return;
  }

  // Passer au verset suivant
  resetRepeat();
  if (P.idx + 1 < SURAHS[P.n - 1].c) playAt(P.n, P.idx + 1);
  else surahEnded();
}

function prevVerse() {
  if (P.n == null) return;
  if (isSingleFileMode()) {
    if (audio.currentTime > 3) { audio.currentTime = 0; return; }
    if (P.n > 1) playAt(P.n - 1, 0);
    else audio.currentTime = 0;
    return;
  }
  if (audio.currentTime > 3) { audio.currentTime = 0; return; }
  if (P.idx > 0) playAt(P.n, P.idx - 1);
  else if (P.n > 1) playAt(P.n - 1, 0);
  else audio.currentTime = 0;
}

function surahEnded() {
  if (!state.autoNext || P.n >= 114) { updatePlayerUI(); return; }
  playAt(P.n + 1, 0);
}

audio.addEventListener('ended', nextVerse);
audio.addEventListener('play', () => updatePlayerUI());
audio.addEventListener('pause', () => updatePlayerUI());

audio.addEventListener('timeupdate', () => {
  if (P.n == null) return;
  let pct;
  if (isSingleFileMode()) {
    pct = audio.duration ? (audio.currentTime / audio.duration * 100) : 0;
  } else {
    const c = SURAHS[P.n - 1].c;
    const frac = audio.duration ? audio.currentTime / audio.duration : 0;
    pct = ((P.idx + frac) / c * 100);
  }
  pct = Math.min(100, Math.max(0, pct));
  const plFill = $('#plFill');
  if (plFill) plFill.style.width = pct + '%';
  const lecFill = $('#lecFill');
  if (lecFill) lecFill.style.width = pct + '%';
  const lecProg = $('#lecProgress');
  if (lecProg) lecProg.style.setProperty('--pct', pct);
  const cur = audio.currentTime || 0;
  const dur = audio.duration || 0;
  const t1 = $('#lecTimeCur');
  if (t1) t1.textContent = fmtTime(cur);
  const t2 = $('#lecTimeTotal');
  if (t2) t2.textContent = isFinite(dur) && dur > 0 ? fmtTime(dur) : '--:--';
});

audio.addEventListener('loadedmetadata', () => {
  const t2 = $('#lecTimeTotal');
  if (t2 && isFinite(audio.duration)) t2.textContent = fmtTime(audio.duration);
});

function reciterName() {
  return RBY[P.reciter] ? RBY[P.reciter].name : '';
}

function updatePlayerUI() {
  const playing = !audio.paused && !!audio.src && P.n != null;
  const ic = playing ? '#i-pause' : '#i-play';
  const plPlayIc = $('#plPlayIc');
  if (plPlayIc) plPlayIc.setAttribute('href', ic);
  const pl = $('#player');
  if (pl) pl.classList.toggle('playing', playing);
  const rec = RBY[P.reciter];
  if (P.n != null) {
    const s = SURAHS[P.n - 1];
    const plTitle = $('#plTitle');
    if (plTitle) plTitle.textContent = s.ar + '  ' + s.tr;
    const plSub = $('#plSub');
    if (plSub) plSub.textContent = (rec && rec.server)
      ? 'Sourate complete · ' + reciterName()
      : 'Verset ' + (P.idx + 1) + ' sur ' + s.c + ' · ' + reciterName();
    if (rec) {
      const plAvatar = $('#plAvatar');
      if (plAvatar) {
        plAvatar.style.setProperty('--hue', rec.hue);
        const eqHtml = '<span class="eq" id="plEq" aria-hidden="true"><i></i><i></i><i></i><i></i></span>';
        if (rec.img) {
          plAvatar.classList.add('has-img');
          plAvatar.innerHTML = '<img src="' + esc(rec.img) + '" alt="" loading="lazy">' + eqHtml;
        } else {
          plAvatar.classList.remove('has-img');
          plAvatar.innerHTML = '<b>' + esc(rec.ar[0]) + '</b>' + eqHtml;
        }
      }
    }
  }
  const plSpeed = $('#plSpeed');
  if (plSpeed) plSpeed.textContent = P.rate + '×';
  if (isLecteurOpen() && P.n != null) {
    const s = SURAHS[P.n - 1];
    const lecPlayIc = $('#lecPlayIc');
    if (lecPlayIc) lecPlayIc.setAttribute('href', ic);
    const lecAr = $('#lecSurahAr');
    if (lecAr) lecAr.textContent = s.ar;
    const lecFr = $('#lecSurahFr');
    if (lecFr) lecFr.textContent = s.tr;
    const lecV = $('#lecVerse');
    if (lecV) lecV.textContent = (rec && rec.server)
      ? 'Sourate complete'
      : 'Verset ' + (P.idx + 1) + ' sur ' + s.c;
    if (rec) {
      const lecAvatar = $('#lecAvatar');
      if (lecAvatar) {
        lecAvatar.style.setProperty('--hue', rec.hue);
        if (rec.img) {
          lecAvatar.classList.add('has-img');
          lecAvatar.innerHTML = '<img src="' + esc(rec.img) + '" alt="" loading="lazy">';
        } else {
          lecAvatar.classList.remove('has-img');
          lecAvatar.innerHTML = '<b>' + esc(rec.ar[0]) + '</b>';
        }
      }
    }
    const lecSpeed = $('#lecSpeed');
    if (lecSpeed) lecSpeed.textContent = P.rate + '×';
    const qLec = $('#quranLecteur');
    if (qLec) qLec.classList.toggle('playing', playing);
    const marks = store.get('marks', []);
    const lecMark = $('#lecMark');
    if (lecMark) lecMark.classList.toggle('on', marks.includes(P.n + ':' + P.idx));
    const t2 = $('#lecTimeTotal');
    if (t2 && isFinite(audio.duration) && audio.duration > 0) t2.textContent = fmtTime(audio.duration);
  }
  markPlaying();
  const recProf = $('#recProfile');
  if (currentView === 'coran' && recProf && !recProf.hidden && curRecId != null) renderRecSurahs();
}

function markPlaying() {
  $$('.mus-ar .end.playing').forEach(el => el.classList.remove('playing'));
  if (P.n == null || !isMushafOpen()) return;
  const el = $('.mus-ar .end[data-n="' + P.n + ':' + P.idx + '"]');
  if (el) el.classList.add('playing');
}

const elPlPlay = $('#plPlay');
if (elPlPlay) elPlPlay.addEventListener('click', togglePlay);
const elPlNext = $('#plNext');
if (elPlNext) elPlNext.addEventListener('click', nextVerse);
const elPlPrev = $('#plPrev');
if (elPlPrev) elPlPrev.addEventListener('click', prevVerse);
const elPlSpeed = $('#plSpeed');
if (elPlSpeed) elPlSpeed.addEventListener('click', () => {
  const rates = [0.75, 1, 1.25, 1.5];
  P.rate = rates[(rates.indexOf(P.rate) + 1) % rates.length];
  store.set('rate', P.rate);
  audio.playbackRate = P.rate;
  audio.defaultPlaybackRate = P.rate;
  updatePlayerUI();
});
const elPlClose = $('#plClose');
if (elPlClose) elPlClose.addEventListener('click', () => {
  P.token++;
  audio.pause();
  audio.removeAttribute('src');
  audio.load();
  P.n = null;
  const pl = $('#player');
  if (pl) pl.hidden = true;
  const plFill = $('#plFill');
  if (plFill) plFill.style.width = '0';
  updatePlayerUI();
});

function seekFromEvent(e, el) {
  const rect = el.getBoundingClientRect();
  const x = (e.touches ? e.touches[0].clientX : e.clientX) - rect.left;
  const pct = Math.min(1, Math.max(0, x / rect.width));
  const dur = audio.duration || 0;
  if (!isFinite(dur) || dur <= 0) return;
  audio.currentTime = pct * dur;
}

['plBar', 'lecProgress'].forEach(id => {
  const el = document.getElementById(id);
  if (!el) return;
  let dragging = false;
  const start = e => { e.preventDefault(); dragging = true; el.classList.add('dragging'); seekFromEvent(e, el); };
  const move = e => { if (!dragging) return; e.preventDefault(); seekFromEvent(e, el); };
  const end = () => { if (!dragging) return; dragging = false; el.classList.remove('dragging'); };
  el.addEventListener('mousedown', start);
  el.addEventListener('mousemove', move);
  document.addEventListener('mouseup', end);
  el.addEventListener('touchstart', start, { passive: false });
  el.addEventListener('touchmove', move, { passive: false });
  el.addEventListener('touchend', end);
  el.addEventListener('touchcancel', end);
});

function setMedia() {
  if (!('mediaSession' in navigator) || typeof MediaMetadata === 'undefined' || P.n == null) return;
  const s = SURAHS[P.n - 1];
  const title = isSingleFileMode()
    ? s.tr + ' (Sourate complete)'
    : s.tr + ', verset ' + (P.idx + 1);
  navigator.mediaSession.metadata = new MediaMetadata({
    title: title,
    artist: reciterName(),
    album: 'Wakti'
  });
  try {
    navigator.mediaSession.setActionHandler('play', () => audio.play());
    navigator.mediaSession.setActionHandler('pause', () => audio.pause());
    navigator.mediaSession.setActionHandler('previoustrack', prevVerse);
    navigator.mediaSession.setActionHandler('nexttrack', nextVerse);
  } catch (e) {}
}

/* =====================================================================
   21. CALENDRIER
===================================================================== */
const cal = { y: 0, m: 0, sel: null };

function initCal() {
  const z = zonedNow(state.tz);
  cal.y = z.y;
  cal.m = z.m;
  cal.sel = { y: z.y, m: z.m, d: z.d };
}

function hijriRangeTitle() {
  const dim = utc(cal.y, cal.m + 1, 0).getUTCDate();
  const a = hijriOf(cal.y, cal.m, 1);
  const b = hijriOf(cal.y, cal.m, dim);
  if (!a || !b) return { ar: '', fr: '' };
  if (a.m === b.m && a.y === b.y) {
    return { ar: HM_AR[a.m - 1] + ' ' + toAr(a.y), fr: HM_FR[a.m - 1] + ' ' + a.y };
  }
  if (a.y === b.y) {
    return { ar: HM_AR[a.m - 1] + ' - ' + HM_AR[b.m - 1] + ' ' + toAr(a.y), fr: '' };
  }
  return { ar: HM_AR[a.m - 1] + ' ' + toAr(a.y) + ' - ' + HM_AR[b.m - 1] + ' ' + toAr(b.y), fr: '' };
}

function renderCalendar() {
  if (!cal.y) initCal();
  const t = hijriRangeTitle();
  const elAr = $('#calAr');
  if (elAr) elAr.textContent = t.ar;
  const elFr = $('#calFr');
  if (elFr) elFr.textContent = fmtMonth.format(utc(cal.y, cal.m, 1));
  const first = utc(cal.y, cal.m, 1);
  const dim = utc(cal.y, cal.m + 1, 0).getUTCDate();
  const startDow = (first.getUTCDay() + 6) % 7;
  const weeks = Math.ceil((startDow + dim) / 7);
  const z = zonedNow(state.tz);
  let html = ['Lun','Mar','Mer','Jeu','Ven','Sam','Dim'].map(d => '<div class="dow">' + d + '</div>').join('');
  for (let i = 0; i < weeks * 7; i++) {
    const dt = new Date(Date.UTC(cal.y, cal.m - 1, 1 - startDow + i, 12));
    const y = dt.getUTCFullYear();
    const m = dt.getUTCMonth() + 1;
    const d = dt.getUTCDate();
    const h = hijriOf(y, m, d);
    const dow = (dt.getUTCDay() + 6) % 7;
    const out = m !== cal.m;
    const isToday = y === z.y && m === z.m && d === z.d;
    const isSel = cal.sel && cal.sel.y === y && cal.sel.m === m && cal.sel.d === d;
    const ev = h && EVENTS[h.d + '-' + h.m];
    html += '<button class="day' + (out ? ' out' : '') + (dow === 4 ? ' fri' : '') + (isToday ? ' today' : '') + (isSel ? ' sel' : '') + '" data-d="' + y + '-' + m + '-' + d + '">' +
      (ev ? '<span class="dot"></span>' : '') +
      '<span class="g">' + d + '</span>' +
      (h ? '<span class="h" lang="ar">' + toAr(h.d) + '</span>' + (h.d === 1 ? '<span class="hm" lang="ar">' + HM_AR[h.m - 1] + '</span>' : '') : '') +
      '</button>';
  }
  const grid = $('#calGrid');
  if (grid) grid.innerHTML = html;
  renderDetail();
}

function renderDetail() {
  const s = cal.sel;
  if (!s) return;
  const dt = utc(s.y, s.m, s.d);
  const h = hijriOf(s.y, s.m, s.d);
  const z = zonedNow(state.tz);
  const diff = Math.round((dt - utc(z.y, z.m, z.d)) / 86400000);
  const rel = diff === 0 ? 'Aujourd hui' : diff === 1 ? 'Demain' : diff === -1 ? 'Hier' : diff > 0 ? 'Dans ' + diff + ' jours' : 'Il y a ' + (-diff) + ' jours';
  const ev = h && EVENTS[h.d + '-' + h.m];
  const isoVal = s.y + '-' + pad(s.m) + '-' + pad(s.d);
  const elDetail = $('#detail');
  if (elDetail) {
    elDetail.innerHTML =
      '<div class="wd-ar" lang="ar">' + WD_AR[dt.getUTCDay()] + '</div>' +
      '<div class="hj" lang="ar" dir="rtl">' + (h ? toAr(h.d) + ' ' + HM_AR[h.m - 1] + ' ' + toAr(h.y) : '—') + '</div>' +
      '<div class="hj-fr">' + (h ? h.d + ' ' + esc(HM_FR[h.m - 1]) + ' ' + h.y : 'Date indisponible') + '</div>' +
      '<hr>' +
      '<div class="gr">' + esc(fmtLong.format(dt)) + '</div>' +
      '<div class="rel">' + rel + '</div>' +
      (ev ? '<div class="evt">' + esc(ev) + '</div>' : '') +
      '<p class="note">Les dates hegiriennes suivent le calendrier Umm al-Qura.</p>' +
      '<div class="goto"><label for="gotoDate">Convertir une date</label><input id="gotoDate" type="date" value="' + isoVal + '"></div>';
    const gotoDate = $('#gotoDate');
    if (gotoDate) {
      gotoDate.addEventListener('change', e => {
        const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(e.target.value);
        if (!m) return;
        cal.y = +m[1];
        cal.m = +m[2];
        cal.sel = { y: +m[1], m: +m[2], d: +m[3] };
        renderCalendar();
      });
    }
  }
}

const elCalGrid = $('#calGrid');
if (elCalGrid) {
  elCalGrid.addEventListener('click', e => {
    const b = e.target.closest('[data-d]');
    if (!b) return;
    const parts = b.dataset.d.split('-').map(Number);
    cal.sel = { y: parts[0], m: parts[1], d: parts[2] };
    if (parts[1] !== cal.m || parts[0] !== cal.y) { cal.y = parts[0]; cal.m = parts[1]; }
    renderCalendar();
  });
}

const elCalPrev = $('#calPrev');
if (elCalPrev) elCalPrev.addEventListener('click', () => {
  cal.m--;
  if (cal.m < 1) { cal.m = 12; cal.y--; }
  renderCalendar();
});

const elCalNext = $('#calNext');
if (elCalNext) elCalNext.addEventListener('click', () => {
  cal.m++;
  if (cal.m > 12) { cal.m = 1; cal.y++; }
  renderCalendar();
});

const elCalToday = $('#calToday');
if (elCalToday) elCalToday.addEventListener('click', () => {
  initCal();
  renderCalendar();
});

/* =====================================================================
   22. GESTION DES DIALOGUES
===================================================================== */
document.addEventListener('click', e => {
  const o = e.target.closest('[data-open]');
  if (o) {
    let d;
    if (o.dataset.open === 'loc') d = $('#dlgLoc');
    else if (o.dataset.open === 'backup') d = $('#dlgBackup');
    else d = $('#dlgSet');
    if (d && !d.open && d.showModal) d.showModal();
    return;
  }
  if (e.target.closest('[data-close]')) {
    const dlg = e.target.closest('dialog');
    if (dlg && dlg.close) dlg.close();
    return;
  }
  if (e.target.closest('[data-act="retry"]')) { loadTimings(); return; }
  const c = e.target.closest('[data-check]');
  if (c) toggleDone(c.dataset.check);
});

$$('dialog').forEach(d => d.addEventListener('click', e => {
  if (e.target === d && d.close) d.close();
}));







/* =====================================================================
   Phase 5.1 — Panneau verset + repetition
===================================================================== */

/* Cache des versets fetchés */
const verseCache = new Map();

/* État de la répétition */
const repeatState = {
  mode: 'once',      // 'once' | '3' | '5' | 'infinite'
  remaining: 1,      // Nombre de fois restantes (pour 3×, 5×)
  currentN: null,    // Sourate en cours
  currentIdx: null   // Verset en cours
};

/* Fetch un verset (arabe + traduction) */
async function fetchVerse(n, i) {
  const key = n + ':' + i;
  if (verseCache.has(key)) return verseCache.get(key);

  const s = SURAHS[n - 1];
  if (i < 0 || i >= s.c) return null;

  // Numéro global du verset
  const globalNum = FIRST_GLOBAL[n - 1] + i;

  try {
    const j = await getJSON(
      'https://api.alquran.cloud/v1/ayah/' + n + ':' + (i + 1) + '/editions/quran-uthmani,fr.hamidullah',
      { retries: 1 }
    );
    const v = {
      ar: j.data[0].text,
      fr: j.data[1].text
    };
    verseCache.set(key, v);
    return v;
  } catch (e) {
    return null;
  }
}

/* Afficher le panneau verset */
async function showVersePanel(n, i) {
  const panel = document.getElementById('lecVersePanel');
  if (!panel) return;

  // Mode "sourate complète" (mp3quran) : pas de panneau
  const rec = RBY[P.reciter];
  if (rec && rec.server) {
    panel.hidden = true;
    return;
  }

  panel.hidden = false;
  const s = SURAHS[n - 1];

  const badge = document.getElementById('lvpBadge');
  if (badge) badge.textContent = 'Verset ' + (i + 1) + ' / ' + s.c;

  const arEl = document.getElementById('lvpAr');
  const frEl = document.getElementById('lvpFr');
  if (arEl) arEl.textContent = '...';
  if (frEl) frEl.textContent = 'Chargement...';

  const v = await fetchVerse(n, i);
  if (!v) {
    if (arEl) arEl.textContent = 'Texte indisponible';
    if (frEl) frEl.textContent = '';
    return;
  }
  if (arEl) arEl.textContent = v.ar;
  if (frEl) frEl.textContent = v.fr;
}

/* Masquer le panneau verset */
function hideVersePanel() {
  const panel = document.getElementById('lecVersePanel');
  if (panel) panel.hidden = true;
}

/* Mettre à jour les boutons de repetition */
function updateRepeatButtons() {
  const buttons = document.querySelectorAll('.repeat-btn');
  buttons.forEach(b => {
    const mode = b.dataset.repeat;
    const isActive = (
      (mode === '1' && repeatState.mode === 'once') ||
      (mode === '3' && repeatState.mode === '3') ||
      (mode === '5' && repeatState.mode === '5') ||
      (mode === 'infinite' && repeatState.mode === 'infinite')
    );
    b.classList.toggle('active', isActive);
  });
}

/* Appliquer le mode de repetition */
function setRepeatMode(mode) {
  repeatState.mode = mode;
  if (mode === '3') repeatState.remaining = 3;
  else if (mode === '5') repeatState.remaining = 5;
  else if (mode === 'infinite') repeatState.remaining = Infinity;
  else repeatState.remaining = 1;
  updateRepeatButtons();
}

/* Verifier si on doit repeter le verset courant */
function shouldRepeat() {
  if (repeatState.mode === 'once') return false;
  if (repeatState.mode === 'infinite') return true;
  return repeatState.remaining > 0;
}

/* Decrementer le compteur de repetition */
function decrementRepeat() {
  if (repeatState.mode === 'once') return;
  if (repeatState.mode === 'infinite') return;
  repeatState.remaining--;
}

/* Reset la repetition quand on change de verset manuellement */
function resetRepeat() {
  if (repeatState.mode === '3') repeatState.remaining = 3;
  else if (repeatState.mode === '5') repeatState.remaining = 5;
}

/* Initialiser les boutons */
function initRepeatButtons() {
  const buttons = document.querySelectorAll('.repeat-btn');
  buttons.forEach(b => {
    b.addEventListener('click', () => {
      setRepeatMode(b.dataset.repeat);
      vibrate([10]);
      const labels = {
        '1': 'Lecture simple',
        '3': 'Répétition 3 fois',
        '5': 'Répétition 5 fois',
        'infinite': 'Répétition infinie'
      };
      toast(labels[b.dataset.repeat] || 'Mode change', 1500);
    });
  });
  updateRepeatButtons();

  // Bouton fermer
  const close = document.getElementById('lvpClose');
  if (close) close.addEventListener('click', () => {
    hideVersePanel();
  });
}



/* =====================================================================
   Phase 5.2 — Mode Hifz (memorisation)
===================================================================== */

const hifzState = {
  active: false,
  n: null,
  i: 0,
  level: 'medium',   // 'easy' | 'medium' | 'hard'
  revealed: false
};

/* Recupere les versets appris depuis localStorage */
function getLearned() {
  return store.get('hifzLearned', {});
}

function setLearned(obj) {
  store.set('hifzLearned', obj);
}

function isLearned(n, i) {
  const learned = getLearned();
  return learned[n + ':' + i] === true;
}

function markVerseLearned(n, i, learned) {
  const all = getLearned();
  const key = n + ':' + i;
  if (learned) {
    all[key] = true;
  } else {
    delete all[key];
  }
  setLearned(all);
  if (learned) waktiLog('mark_hifz', 'verse:' + n + ':' + (i + 1));
}

/* Compte les versets appris d'une sourate */
function countLearnedInSurah(n) {
  const all = getLearned();
  let count = 0;
  for (let i = 0; i < SURAHS[n - 1].c; i++) {
    if (all[n + ':' + i]) count++;
  }
  return count;
}

/* Compte total des versets appris */
function countTotalLearned() {
  const all = getLearned();
  return Object.keys(all).length;
}

/* Ouvre le mode Hifz */
async function openHifz(n, i) {
  n = n || P.n || 1;
  i = i || 0;

  console.log('[Hifz] Ouverture pour sourate', n, 'verset', i);

  hifzState.active = true;
  hifzState.n = n;
  hifzState.i = i;
  hifzState.level = store.get('hifzLevel', 'medium');
  hifzState.revealed = false;

  // 1. Mettre l'overlay au premier plan
  const overlay = document.getElementById('hifzOverlay');
  if (!overlay) {
    console.error('[Hifz] Overlay introuvable !');
    toast('Erreur : overlay Hifz introuvable', 3000);
    return;
  }
  overlay.hidden = false;
  overlay.style.zIndex = '9999';
  overlay.style.opacity = '1';  // Forcer la visibilite

  // 2. NE PAS masquer le lecteur (l'overlay est dans <body>)

  // 3. Mettre a jour les infos
  updateHifzUI();

  // 4. Charger le verset
  try {
    await renderHifzVerse();
  } catch (e) {
    console.error('[Hifz] Erreur chargement verset:', e);
    const arEl = document.getElementById('hifzAr');
    if (arEl) arEl.textContent = 'Erreur de chargement';
  }

  // 5. Setup les event listeners
  setupHifzListeners();

  console.log('[Hifz] Pret');
}

/* Ferme le mode Hifz */
function closeHifz() {
  hifzState.active = false;
  const overlay = document.getElementById('hifzOverlay');
  if (overlay) {
    overlay.hidden = true;
    overlay.style.zIndex = '';
    overlay.style.opacity = '';
  }
}

/* Met a jour les infos (titre, progression) */
function updateHifzUI() {
  const s = SURAHS[hifzState.n - 1];
  const surahEl = document.getElementById('hifzSurah');
  if (surahEl) surahEl.textContent = s.tr + ' · ' + s.ar;

  const progressEl = document.getElementById('hifzProgressText');
  if (progressEl) progressEl.textContent = 'Verset ' + (hifzState.i + 1) + ' sur ' + s.c;

  const fill = document.getElementById('hifzBarFill');
  if (fill) {
    const pct = ((hifzState.i + 1) / s.c) * 100;
    fill.style.width = pct + '%';
  }

  // Badge "appris"
  const badge = document.getElementById('hifzLearnedBadge');
  if (badge) {
    badge.hidden = !isLearned(hifzState.n, hifzState.i);
  }

  // Bouton marquer comme appris
  const markBtn = document.getElementById('hifzMarkLearned');
  if (markBtn) {
    markBtn.classList.toggle('on', isLearned(hifzState.n, hifzState.i));
  }

  // Boutons de niveau
  document.querySelectorAll('.hifz-level').forEach(b => {
    b.classList.toggle('active', b.dataset.level === hifzState.level);
  });
}

/* Charge et affiche le verset */
async function renderHifzVerse() {
  const arEl = document.getElementById('hifzAr');
  const frEl = document.getElementById('hifzFr');
  if (!arEl || !frEl) return;

  arEl.textContent = 'Chargement...';
  frEl.textContent = '';

  const v = await fetchVerse(hifzState.n, hifzState.i);
  if (!v) {
    arEl.textContent = 'Texte indisponible';
    frEl.textContent = '';
    return;
  }

  // Nettoyer le bismillah
  let arabicText = v.ar;
  if (hifzState.n !== 1 && hifzState.n !== 9 && hifzState.i === 0) {
    const words = arabicText.trim().split(/\s+/);
    if (words.slice(0, 4).map(stripAr).join(' ') === 'بسم الله الرحمن الرحيم') {
      arabicText = words.slice(4).join(' ');
    }
  }

  // Stocker les mots arabes
  const words = arabicText.trim().split(/\s+/);
  hifzState.words = words;
  hifzState.french = v.fr;

  applyHifzLevel();
}

/* Applique le niveau de difficulte */
function applyHifzLevel() {
  const arEl = document.getElementById('hifzAr');
  const frEl = document.getElementById('hifzFr');
  if (!arEl || !frEl) return;

  const level = hifzState.level;
  const revealed = hifzState.revealed;
  const words = hifzState.words || [];

  if (level === 'easy' || revealed) {
    // Tout visible
    arEl.classList.remove('hidden-all');
    frEl.classList.remove('hidden-all');
    arEl.textContent = words.join(' ');
    frEl.textContent = hifzState.french || '';
    return;
  }

  if (level === 'hard') {
    // Tout masque
    arEl.classList.add('hidden-all');
    frEl.classList.add('hidden-all');
    arEl.textContent = words.join(' ');
    frEl.textContent = hifzState.french || '';
    return;
  }

  if (level === 'medium') {
    // Masquer environ 60% des mots (alternes)
    arEl.classList.remove('hidden-all');
    frEl.classList.remove('hidden-all');

    // Construire le HTML avec des mots masques
    let html = '';
    words.forEach((w, idx) => {
      // Masquer 6 mots sur 10 (en gardant les 2 premiers et les 2 derniers visibles)
      const isFirst = idx < 2;
      const isLast = idx >= words.length - 2;
      const shouldHide = !isFirst && !isLast && (idx % 10 < 6);

      if (shouldHide) {
        html += '<span class="hidden-word">' + esc(w) + '</span> ';
      } else {
        html += esc(w) + ' ';
      }
    });
    arEl.innerHTML = html.trim();

    // Masquer environ 40% de la traduction (mots cles)
    const frWords = (hifzState.french || '').split(/\s+/);
    let frHtml = '';
    frWords.forEach((w, idx) => {
      const shouldHide = (idx > 3) && (idx % 10 < 4);
      if (shouldHide) {
        frHtml += '<span class="hidden-word">' + esc(w) + '</span> ';
      } else {
        frHtml += esc(w) + ' ';
      }
    });
    frEl.innerHTML = frHtml.trim();
  }
}

/* Passe au verset suivant */
async function nextHifzVerse() {
  const s = SURAHS[hifzState.n - 1];

  // Proposer de marquer comme appris si pas encore fait
  if (!isLearned(hifzState.n, hifzState.i)) {
    const shouldMark = confirm('Marquer ce verset comme appris ?');
    if (shouldMark) {
      markVerseLearned(hifzState.n, hifzState.i, true);
      vibrate([10, 30, 10]);
      toast('Verset marque comme appris !', 2000);
    }
  }

  if (hifzState.i + 1 >= s.c) {
    // Fin de la sourate
    toast('Tu as termine la sourate ' + s.tr + ' ! Masha\'Allah !', 5000);
    vibrate([50, 50, 50, 50, 50]);
    closeHifz();
    return;
  }

  hifzState.i++;
  hifzState.revealed = false;
  updateHifzUI();
  await renderHifzVerse();
}

/* Revele le verset */
function revealHifz() {
  hifzState.revealed = true;
  applyHifzLevel();
  vibrate([10]);
}

/* Setup les listeners (une seule fois) */
let hifzListenersReady = false;
function setupHifzListeners() {
  if (hifzListenersReady) return;
  hifzListenersReady = true;

  // Fermer
  const closeBtn = document.getElementById('hifzClose');
  if (closeBtn) closeBtn.addEventListener('click', closeHifz);

  // Marquer comme appris
  const markBtn = document.getElementById('hifzMarkLearned');
  if (markBtn) markBtn.addEventListener('click', () => {
    const wasLearned = isLearned(hifzState.n, hifzState.i);
    markVerseLearned(hifzState.n, hifzState.i, !wasLearned);
    vibrate(wasLearned ? [15] : [10, 30, 10]);
    toast(wasLearned ? 'Marque comme non appris.' : 'Marque comme appris !', 2000);
    updateHifzUI();
  });

  // Niveaux
  document.querySelectorAll('.hifz-level').forEach(b => {
    b.addEventListener('click', () => {
      hifzState.level = b.dataset.level;
      store.set('hifzLevel', hifzState.level);
      hifzState.revealed = false;
      updateHifzUI();
      applyHifzLevel();
      vibrate([10]);
    });
  });

  // Reveal
  const revealBtn = document.getElementById('hifzReveal');
  if (revealBtn) revealBtn.addEventListener('click', revealHifz);

  // Suivant
  const nextBtn = document.getElementById('hifzNext');
  if (nextBtn) nextBtn.addEventListener('click', nextHifzVerse);

  // Cliquer sur le texte masque pour reveler
  const content = document.getElementById('hifzContent');
  if (content) content.addEventListener('click', e => {
    if (hifzState.level === 'hard' && !hifzState.revealed) {
      revealHifz();
    }
  });

  // (Le bouton Hifz est branche dans init(), pas ici)
}



/* =====================================================================
   Phase 5.4 — Tafsir au clic
===================================================================== */

const tafsirCache = new Map();

/* Charge le tafsir d'un verset */
async function fetchTafsir(surah, ayah) {
  const key = surah + ':' + ayah;
  if (tafsirCache.has(key)) return tafsirCache.get(key);

  try {
    // Tafsir Al-Muyassar via API alquran.cloud
    const url = 'https://api.alquran.cloud/v1/ayah/' + surah + ':' + ayah + '/ar.muyassar';
    const j = await getJSON(url, { retries: 1 });
    const tafsir = j.data.text;
    tafsirCache.set(key, tafsir);
    return tafsir;
  } catch (e) {
    console.warn('Tafsir fetch error:', e);
    return null;
  }
}

/* Ouvre le panneau tafsir */
async function openTafsir(surah, ayah) {
  const panel = document.getElementById('tafsirPanel');
  if (!panel) return;

  panel.hidden = false;

  const refEl = document.getElementById('tafsirRef');
  const arEl = document.getElementById('tafsirAr');

  const s = SURAHS[surah - 1];
  if (refEl) refEl.textContent = s.tr + ' · ' + surah + ':' + (ayah + 1);

  if (arEl) {
    arEl.innerHTML = '<div class="tafsir-loading"><div class="skel"></div><div class="skel"></div></div>';
  }

  const tafsir = await fetchTafsir(surah, ayah + 1);
  if (tafsir) {
    if (arEl) arEl.textContent = tafsir;
  } else {
    if (arEl) arEl.innerHTML = '<p style="color: var(--muted); text-align: center;">Tafsir indisponible pour ce verset.</p>';
  }

  vibrate([10]);
}

/* Ferme le panneau tafsir */
function closeTafsir() {
  const panel = document.getElementById('tafsirPanel');
  if (panel) panel.hidden = true;
  // Retirer le marqueur "actif"
  document.querySelectorAll('.mus-ar .end.tafsir-active').forEach(el => {
    el.classList.remove('tafsir-active');
  });
}

/* Branche les listeners du tafsir (une seule fois) */
let tafsirHooked = false;
function hookTafsir() {
  if (tafsirHooked) return;
  tafsirHooked = true;

  const closeBtn = document.getElementById('tafsirClose');
  if (closeBtn) closeBtn.addEventListener('click', closeTafsir);

  const backdrop = document.getElementById('tafsirBackdrop');
  if (backdrop) backdrop.addEventListener('click', closeTafsir);

  // ESC pour fermer
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && !document.getElementById('tafsirPanel').hidden) {
      closeTafsir();
    }
  });

  // Long-press sur un verset du mushaf pour ouvrir le tafsir
  const musPage = document.getElementById('musPage');
  if (musPage) {
    let pressTimer = null;
    let pressedEl = null;

    const startPress = (el, surah, ayah) => {
      pressedEl = el;
      el.classList.add('tafsir-active');
      pressTimer = setTimeout(() => {
        vibrate([15]);
        openTafsir(surah, ayah);
        pressTimer = null;
      }, 600);
    };

    const cancelPress = () => {
      if (pressTimer) {
        clearTimeout(pressTimer);
        pressTimer = null;
      }
      if (pressedEl) {
        pressedEl.classList.remove('tafsir-active');
        pressedEl = null;
      }
    };

    // Desktop : long-press souris
    musPage.addEventListener('mousedown', e => {
      const end = e.target.closest('.end');
      if (!end) return;
      const parts = end.dataset.n.split(':').map(Number);
      startPress(end, parts[0], parts[1]);
    });
    musPage.addEventListener('mouseup', cancelPress);
    musPage.addEventListener('mouseleave', cancelPress);

    // Mobile : long-press tactile
    musPage.addEventListener('touchstart', e => {
      const end = e.target.closest('.end');
      if (!end) return;
      const parts = end.dataset.n.split(':').map(Number);
      startPress(end, parts[0], parts[1]);
    }, { passive: true });
    musPage.addEventListener('touchend', cancelPress);
    musPage.addEventListener('touchcancel', cancelPress);
  }
}



/* =====================================================================
   Phase 5.5 — Qibla + Horaires detailles
===================================================================== */

/* Coordonnees de La Mecque */
const KAABA = { lat: 21.4225, lng: 39.8262 };

let qiblaActive = false;
let qiblaDeviceHeading = null;

/* Calcule l angle de la Qibla depuis une position donnee */
function calcQiblaAngle(lat, lng) {
  const toRad = d => d * Math.PI / 180;
  const toDeg = r => r * 180 / Math.PI;

  const phiK = toRad(KAABA.lat);
  const lambdaK = toRad(KAABA.lng);
  const phi = toRad(lat);
  const lambda = toRad(lng);

  const deltaLambda = lambdaK - lambda;
  const y = Math.sin(deltaLambda);
  const x = Math.cos(phi) * Math.tan(phiK) - Math.sin(phi) * Math.cos(deltaLambda);

  let bearing = toDeg(Math.atan2(y, x));
  return (bearing + 360) % 360;
}

/* Active la boussole */
async function enableQibla() {
  if (!state.loc) {
    toast('Choisis d abord ta position dans les reglages.');
    return;
  }

  const lat = state.loc.lat;
  const lng = state.loc.lng;

  if (!lat || !lng) {
    toast('Position GPS necessaire pour la Qibla.');
    return;
  }

  // Calculer l angle
  const angle = calcQiblaAngle(lat, lng);
  const angleEl = document.getElementById('qiblaAngle');
  if (angleEl) angleEl.textContent = Math.round(angle);

  // Demander la permission DeviceOrientation (iOS)
  if (typeof DeviceOrientationEvent !== 'undefined' &&
      typeof DeviceOrientationEvent.requestPermission === 'function') {
    try {
      const perm = await DeviceOrientationEvent.requestPermission();
      if (perm !== 'granted') {
        toast('Permission refusee. Active la boussole dans les reglages.');
        return;
      }
    } catch (e) {
      toast('Boussole indisponible sur cet appareil.');
      return;
    }
  }

  // Brancher l ecouteur
  if (!qiblaActive) {
    window.addEventListener('deviceorientationabsolute', onQiblaOrientation, true);
    window.addEventListener('deviceorientation', onQiblaOrientation, true);
    qiblaActive = true;
  }

  const desc = document.getElementById('qiblaDesc');
  if (desc) desc.textContent = 'Tourne lentement ton appareil jusqu a ce qu il soit aligne avec la Kaaba.';

  // Fallback si pas de capteur : afficher seulement l angle fixe
  const isMobile = /Mobi|Android/i.test(navigator.userAgent);
  if (!isMobile) {
    if (desc) desc.textContent = 'Sur desktop, seul l angle (calcule) est affiche. Utilise un mobile pour la boussole active.';
  }
}

function onQiblaOrientation(event) {
  let heading = event.webkitCompassHeading || (360 - event.alpha);

  if (heading == null || isNaN(heading)) return;

  qiblaDeviceHeading = heading;

  const compass = document.getElementById('qiblaCompass');
  const needle = document.getElementById('qiblaNeedle');
  if (!needle) return;

  // Calculer la position a afficher
  const angle = parseFloat(document.getElementById('qiblaAngle').textContent) || 0;

  // Faire tourner la boussole selon l orientation de l appareil
  if (compass) {
    compass.style.transform = 'rotate(' + (-heading) + 'deg)';
    // Le cadran tourne avec l appareil, l aiguille reste fixe vers la Qibla
  }

  // Faire tourner l aiguille vers la Qibla relative
  const needleRotation = angle - heading;
  if (needle) {
    needle.style.transform = 'translate(-50%, -50%) rotate(' + needleRotation + 'deg)';
  }

  // Indicateur d alignement (si l ecart est faible)
  const diff = Math.abs(((angle - heading + 540) % 360) - 180);
  const isAligned = diff < 10;

  if (compass) compass.classList.toggle('aligned', isAligned);

  // Vibration a l alignement
  if (isAligned && !onQiblaOrientation._lastAligned) {
    vibrate([30, 50, 30]);
    onQiblaOrientation._lastAligned = true;
  } else if (!isAligned) {
    onQiblaOrientation._lastAligned = false;
  }
}

/* Charge les horaires detailles (Imsak, dernier tiers, etc.) */
async function loadDetailedTimes() {
  if (!state.loc) return;
  if (!state.times) return;

  try {
    // Utiliser l API aladhan pour les horaires detailles
    const l = state.loc;
    const now = new Date();
    const d = pad(now.getDate());
    const m = pad(now.getMonth() + 1);
    const y = now.getFullYear();
    const dateStr = d + '-' + m + '-' + y;

    const q = [];
    q.push('method=18'); // Tunisie par defaut
    q.push('tune=0,2,0,0,1,0,0,0,0');
    q.push('school=' + state.school);
    const extra = q.length ? '&' + q.join('&') : '';

    let url;
    if (l.type === 'coords') {
      url = 'https://api.aladhan.com/v1/timings/' + dateStr + '?latitude=' + l.lat + '&longitude=' + l.lng + extra;
    } else {
      url = 'https://api.aladhan.com/v1/timingsByCity/' + dateStr + '?city=' + encodeURIComponent(l.city) + '&country=' + encodeURIComponent(l.country) + extra;
    }

    const j = await getJSON(url, { retries: 1 });
    const t = j.data.timings;

    const imsak = (t.Imsak || '').slice(0, 5);
    const firstthird = (t.Firstthird || '').slice(0, 5);
    const lastthird = (t.Lastthird || '').slice(0, 5);
    const midnight = (t.Midnight || '').slice(0, 5);

    const setTxt = (id, val) => {
      const el = document.getElementById(id);
      if (el) el.textContent = val || '--:--';
    };

    setTxt('qtImsak', imsak);
    setTxt('qtLastThird', lastthird);
    setTxt('qtMidnight', midnight);
    setTxt('qtLastNight', firstthird); // Le "dernier tiers" commence a "Firstthird" dans certaines conventions
  } catch (e) {
    console.warn('Detailed times error:', e);
  }
}

/* Hook Qibla dans init */
function hookQibla() {
  const btn = document.getElementById('qiblaEnable');
  if (btn) btn.addEventListener('click', enableQibla);

  // Recharger les horaires detailles quand on ouvre la vue qibla
  const observer = new MutationObserver(() => {
    const view = document.getElementById('view-qibla');
    if (view && view.classList.contains('active')) {
      loadDetailedTimes();
    }
  });

  const views = document.querySelectorAll('.view');
  views.forEach(v => observer.observe(v, { attributes: true, attributeFilter: ['class'] }));
}



/* =====================================================================
   Phase 5.6 — Douas quotidiennes (API fitrahive/dua-dhikr)
===================================================================== */

// Cache des douas
let douasCache = null;
let douasCategories = null;
let douasCurrentCategory = 'all';
let douasAll = [];

// API endpoints
const DOUAS_API = 'https://dua-dhikr.vercel.app';

// Charger les catégories
async function loadDouasCategories() {
  if (douasCategories) return douasCategories;
  try {
    const res = await fetch(DOUAS_API + '/categories', {
      headers: { 'Accept-Language': 'fr' }
    });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const data = await res.json();
    douasCategories = Array.isArray(data) ? data : (data.data || []);
    return douasCategories;
  } catch (e) {
    console.warn('[Douas] Categories error:', e.message);
    return [];
  }
}

// Charger toutes les douas d'une catégorie
async function loadDouasByCategory(slug) {
  try {
    const url = DOUAS_API + '/categories/' + encodeURIComponent(slug);
    const res = await fetch(url, {
      headers: { 'Accept-Language': 'fr' }
    });
    if (!res.ok) throw new Error('HTTP ' + res.status);
    const data = await res.json();
    const list = Array.isArray(data) ? data : (data.data || data.duas || []);
    // Normaliser les champs
    return list.map(d => ({
      id: d.id || Math.random().toString(36).slice(2),
      title: d.title || d.name || '',
      arabic: d.arabic || d.arab || '',
      latin: d.latin || d.transliteration || '',
      translation: d.translation || d.fr || d.meaning || '',
      notes: d.notes || d.note || '',
      fawaid: d.fawaid || d.benefits || d.virtues || '',
      source: d.source || d.reference || d.hadith || '',
      category: d.category || slug
    }));
  } catch (e) {
    console.warn('[Douas] Load category error:', e.message);
    return [];
  }
}

// Charger TOUTES les douas (toutes catégories)
async function loadAllDouas() {
  if (douasAll.length > 0) return douasAll;
  
  const cats = await loadDouasCategories();
  const promises = cats.slice(0, 20).map(c => loadDouasByCategory(c.slug || c.id));
  const results = await Promise.allSettled(promises);
  
  const all = [];
  results.forEach(r => {
    if (r.status === 'fulfilled') all.push(...r.value);
  });
  
  // Dédupliquer par id
  const seen = new Set();
  douasAll = all.filter(d => {
    if (seen.has(d.id)) return false;
    seen.add(d.id);
    return true;
  });
  
  console.log('[Douas] Chargé', douasAll.length, 'douas');
  return douasAll;
}

// Afficher une doua
function douaHTML(d) {
  return '<article class="doua-card">' +
    '<h3 class="doua-title">' + esc(d.title) + '</h3>' +
    (d.arabic ? '<p class="doua-ar" lang="ar" dir="rtl">' + esc(d.arabic) + '</p>' : '') +
    (d.latin ? '<p class="doua-latin">' + esc(d.latin) + '</p>' : '') +
    (d.translation ? '<p class="doua-translation">' + esc(d.translation) + '</p>' : '') +
    (d.notes ? '<p class="doua-notes">' + esc(d.notes) + '</p>' : '') +
    (d.fawaid ? '<p class="doua-fawaid"><b>Bienfaits :</b> ' + esc(d.fawaid) + '</p>' : '') +
    (d.source ? '<p class="doua-source"><b>Source :</b> ' + esc(d.source) + '</p>' : '') +
    '<button class="doua-copy" data-copy="' + esc((d.arabic || '') + ' | ' + (d.translation || '')) + '" aria-label="Copier">' +
    '<svg class="ic"><use href="#i-copy"/></svg>' +
    '</button>' +
    '</article>';
}

// Filtrer et afficher
function renderDouas() {
  const container = document.getElementById('douasList');
  const noEl = document.getElementById('noDouas');
  if (!container) return;

  let list = douasAll;
  
  // Filtre par catégorie
  if (douasCurrentCategory !== 'all') {
    list = list.filter(d => d.category === douasCurrentCategory);
  }
  
  // Filtre par recherche
  const searchInput = document.getElementById('douasSearch');
  const q = searchInput ? searchInput.value.trim().toLowerCase() : '';
  if (q) {
    list = list.filter(d =>
      d.title.toLowerCase().includes(q) ||
      d.translation.toLowerCase().includes(q) ||
      d.arabic.includes(q)
    );
  }
  
  if (list.length === 0) {
    container.innerHTML = '';
    if (noEl) noEl.hidden = false;
    return;
  }
  
  if (noEl) noEl.hidden = true;
  container.innerHTML = list.map(douaHTML).join('');
}

// Ajouter les filtres de catégorie
async function renderDouasFilters() {
  const el = document.getElementById('douasFilters');
  if (!el) return;
  
  const cats = await loadDouasCategories();
  
  // Calculer le nombre par catégorie
  const counts = {};
  douasAll.forEach(d => {
    counts[d.category] = (counts[d.category] || 0) + 1;
  });
  
  let html = '<button class="doua-filter' + (douasCurrentCategory === 'all' ? ' active' : '') + '" data-category="all">Toutes <span class="count">' + douasAll.length + '</span></button>';
  
  cats.forEach(c => {
    const slug = c.slug || c.id;
    const name = c.name || c.title || slug;
    const count = counts[slug] || 0;
    const on = douasCurrentCategory === slug;
    html += '<button class="doua-filter' + (on ? ' active' : '') + '" data-category="' + esc(slug) + '">' + esc(name) + ' <span class="count">' + count + '</span></button>';
  });
  
  el.innerHTML = html;
}

// Initialiser
async function initDouas() {
  const container = document.getElementById('douasList');
  if (!container) return;
  
  // Charger toutes les douas
  await loadAllDouas();
  
  // Afficher les filtres
  await renderDouasFilters();
  
  // Afficher les douas
  renderDouas();
  
  // Hook recherche
  const searchInput = document.getElementById('douasSearch');
  if (searchInput && !searchInput.dataset.hooked) {
    searchInput.dataset.hooked = '1';
    searchInput.addEventListener('input', renderDouas);
  }
  
  // Hook filtres
  const filters = document.getElementById('douasFilters');
  if (filters && !filters.dataset.hooked) {
    filters.dataset.hooked = '1';
    filters.addEventListener('click', e => {
      const btn = e.target.closest('[data-category]');
      if (!btn) return;
      douasCurrentCategory = btn.dataset.category;
      filters.querySelectorAll('.doua-filter').forEach(b => {
        b.classList.toggle('active', b.dataset.category === douasCurrentCategory);
      });
      renderDouas();
      vibrate([10]);
    });
  }
  
  // Hook bouton aléatoire
  const randBtn = document.getElementById('douasRandomBtn');
  if (randBtn && !randBtn.dataset.hooked) {
    randBtn.dataset.hooked = '1';
    randBtn.addEventListener('click', () => {
      if (douasAll.length === 0) return;
      const random = douasAll[Math.floor(Math.random() * douasAll.length)];
      // Faire défiler vers la doua
      const cards = container.querySelectorAll('.doua-card');
      // Afficher un toast avec la doua
      toast(random.title + ' : ' + random.translation.slice(0, 60) + '...', 5000);
      vibrate([10, 30, 10]);
    });
  }
  
  // Hook copie
  if (!container.dataset.hooked) {
    container.dataset.hooked = '1';
    container.addEventListener('click', async e => {
      const btn = e.target.closest('[data-copy]');
      if (!btn) return;
      try {
        await navigator.clipboard.writeText(btn.dataset.copy);
        toast('Doua copiée !');
        vibrate([10]);
      } catch (err) {
        toast('Impossible de copier');
      }
    });
  }
}

// Recharger les douas quand on ouvre la vue
document.addEventListener('DOMContentLoaded', () => {
  setTimeout(() => {
    const observer = new MutationObserver(() => {
      const view = document.getElementById('view-douas');
      if (view && view.classList.contains('active') && !view.dataset.loaded) {
        view.dataset.loaded = '1';
        initDouas();
      }
    });
    document.querySelectorAll('.view').forEach(v => observer.observe(v, { attributes: true, attributeFilter: ['class'] }));
  }, 1000);
});

/* =====================================================================
   Phase 5.7 — Rappels contextuels intelligents
===================================================================== */

/* Verifier si on doit envoyer un rappel intelligent */
function checkSmartReminders() {
  if (!state.notify) return;
  if (!state.times) return;

  const z = zonedNow(state.tz);
  const sec = z.h * 3600 + z.mi * 60 + z.s;
  const t = state.times;
  const tk = todayKeyWird();
  const data = getWirdData();
  const wirdDone = data.done[tk] || 0;
  const wirdGoal = data.goal || 5;

  // Rappel 1 : Wird non fait a J-30min avant Maghrib
  if (wirdDone === 0 && wirdGoal > 0) {
    const beforeMaghrib = t.Maghrib.s - sec;
    if (beforeMaghrib > 0 && beforeMaghrib < 1800 && !state.fired['smartWird' + z.d]) {
      state.fired['smartWird' + z.d] = true;
      sendSmartNotification(
        'Ton Wird t attend 🌿',
        'Il te reste ' + Math.floor(beforeMaghrib / 60) + ' min avant Maghrib. Lis quelques versets ?',
        '/#/wird'
      );
    }
  }

  // Rappel 2 : 15 min avant chaque priere (si pas encore prie)
  const nextPrayer = PRAYERS.find(p => p.track && t[p.k].s > sec);
  if (nextPrayer) {
    const before = t[nextPrayer.k].s - sec;
    const key = 'smartPre' + nextPrayer.k + z.d;
    if (before > 0 && before < 900 && before > 750 && !state.fired[key]) {
      state.fired[key] = true;
      sendSmartNotification(
        'Dans 15 min : ' + nextPrayer.fr + ' 🕌',
        'Prepare-toi pour la priere de ' + nextPrayer.fr + ' (' + nextPrayer.ar + ').',
        '/#/prieres'
      );
    }
  }

  // Rappel 3 : Le soir, si le Wird n'est pas fini
  if (wirdDone > 0 && wirdDone < wirdGoal && sec > t.Isha.s && sec < t.Isha.s + 3600) {
    const key = 'smartWirdEnd' + z.d;
    if (!state.fired[key]) {
      state.fired[key] = true;
      sendSmartNotification(
        'Wird presque fini 🌱',
        'Tu as lu ' + wirdDone + ' sur ' + wirdGoal + ' versets. Encore un petit effort ?',
        '/#/wird'
      );
    }
  }
}

function sendSmartNotification(title, body, url) {
  toast(title + ' — ' + body, 7000);
  chime();
  if ('Notification' in window && Notification.permission === 'granted') {
    try {
      new Notification(title, { body, tag: 'wakti-smart', icon: '/img/icons/icon-192.png' });
    } catch (e) {}
  }
}



/* =====================================================================
   Phase 5.8 — Rappels d'evenements hegiriens
===================================================================== */

/* Verifier les evenements a J-1 */
function checkEventReminders() {
  if (!state.notify) return;

  const z = zonedNow(state.tz);
  const tomorrow = addDays(z.y, z.m, z.d, 1);
  const hTomorrow = hijriOf(tomorrow.y, tomorrow.m, tomorrow.d);

  if (!hTomorrow) return;

  const key = hTomorrow.d + '-' + hTomorrow.m;
  const event = EVENTS[key];

  if (!event) return;

  const firedKey = 'event-' + key + z.y + z.m + z.d;
  if (state.fired[firedKey]) return;
  state.fired[firedKey] = true;

  sendSmartNotification(
    'Demain : ' + event + ' 🌙',
    'Prepare-toi pour ' + event + ' (demain).',
    '/#/calendrier'
  );
}



/* =====================================================================
   Phase 5.9 — Mode Mosquee
===================================================================== */

let mosqueInterval = null;

function openMosqueMode() {
  const modal = document.getElementById('mosqueMode');
  if (!modal) return;
  modal.hidden = false;

  renderMosque();
  if (mosqueInterval) clearInterval(mosqueInterval);
  mosqueInterval = setInterval(renderMosque, 1000);

  // Fermer avec ESC
  const escHandler = e => {
    if (e.key === 'Escape') closeMosqueMode();
  };
  document.addEventListener('keydown', escHandler);
  modal._escHandler = escHandler;
}

function closeMosqueMode() {
  const modal = document.getElementById('mosqueMode');
  if (modal) {
    modal.hidden = true;
    if (modal._escHandler) document.removeEventListener('keydown', modal._escHandler);
  }
  if (mosqueInterval) {
    clearInterval(mosqueInterval);
    mosqueInterval = null;
  }
}

function renderMosque() {
  const z = zonedNow(state.tz);

  // Heure
  const clock = document.getElementById('mosqueClock');
  if (clock) {
    clock.textContent = pad(z.h) + ':' + pad(z.mi) + ':' + pad(z.s);
  }

  // Date
  const date = document.getElementById('mosqueDate');
  if (date) {
    date.textContent = fmtLong.format(utc(z.y, z.m, z.d));
  }

  // Lieu
  const loc = document.getElementById('mosqueLoc');
  if (loc) loc.textContent = state.loc ? state.loc.label : 'Ma position';

  // Prochaine priere
  if (state.times) {
    const sec = z.h * 3600 + z.mi * 60 + z.s;
    const t = state.times;
    let nextK = null;
    for (const k of TRACK) { if (t[k].s > sec) { nextK = k; break; } }
    if (!nextK) nextK = 'Fajr';

    const nextName = document.getElementById('mosqueNextName');
    const nextTime = document.getElementById('mosqueNextTime');
    if (nextName) nextName.textContent = PBY[nextK].ar + '  ' + PBY[nextK].fr;
    if (nextTime) nextTime.textContent = t[nextK].str;
  }

  // Liste des prieres
  const list = document.getElementById('mosqueList');
  if (list && state.times) {
    const sec = z.h * 3600 + z.mi * 60 + z.s;
    const t = state.times;
    let nextK = null;
    for (const k of TRACK) { if (t[k].s > sec) { nextK = k; break; } }
    if (!nextK) nextK = 'Fajr';

    list.innerHTML = PRAYERS.map(p => {
      const isNext = p.k === nextK;
      return '<div class="mosque-p' + (isNext ? ' next' : '') + '">' +
        '<div class="mp-ar" lang="ar">' + p.ar + '</div>' +
        '<div class="mp-fr">' + p.fr + '</div>' +
        '<div class="mp-time">' + t[p.k].str + '</div>' +
        '</div>';
    }).join('');
  }
}

function hookMosque() {
  const openBtn = document.getElementById('openMosqueBtn');
  if (openBtn) openBtn.addEventListener('click', () => {
    openMosqueMode();
    const dlgSet = document.getElementById('dlgSet');
    if (dlgSet && dlgSet.close) dlgSet.close();
  });

  const closeBtn = document.getElementById('mosqueClose');
  if (closeBtn) closeBtn.addEventListener('click', closeMosqueMode);
}

/* =====================================================================
   25. MICRO-INTERACTIONS
===================================================================== */

/* Vibration (haptique) : fonctionne sur Android Chrome */
function vibrate(pattern) {
  if (navigator.vibrate) {
    try { navigator.vibrate(pattern); } catch (e) {}
  }
}

/* Toast poetique lors du changement de phase */
const PHASE_MESSAGES = {
  fajr:    { ar: 'الفجر', fr: 'L aube pointe. Le Fajr t appelle.' },
  duha:    { ar: 'الضحى', fr: 'Le matin s illumine. Belle journee !' },
  dhuhr:   { ar: 'الظهر', fr: 'Le soleil est au zenith. Dhourh approche.' },
  asr:     { ar: 'العصر', fr: 'L apres-midi declin. Le Asr est la.' },
  maghrib: { ar: 'المغرب', fr: 'Le soleil se couche. Maghrib t attend.' },
  isha:    { ar: 'العشاء', fr: 'La nuit tombe. Le Isha t appelle.' },
  night:   { ar: 'الليل', fr: 'La nuit est paisible. Repose-toi bien.' }
};

let lastPhase = null;

function announcePhase(newPhase) {
  if (newPhase === lastPhase) return;
  lastPhase = newPhase;
  const msg = PHASE_MESSAGES[newPhase];
  if (!msg) return;
  // Petit delai pour ne pas spammer
  setTimeout(() => {
    toast(msg.ar + ' · ' + msg.fr, 5000);
  }, 1500);
}

/* Slide animation pour les pages du mushaf */
function slideMushaf(direction) {
  const pageEl = document.getElementById('musPage');
  if (!pageEl) return;
  pageEl.classList.remove('slide-left', 'slide-right');
  void pageEl.offsetHeight;
  pageEl.classList.add(direction === 'left' ? 'slide-left' : 'slide-right');
  setTimeout(() => {
    pageEl.classList.remove('slide-left', 'slide-right');
  }, 500);
}

/* Pulse du compteur si priere dans moins de 5 minutes */
function updateCountdownPulse(nextK, leftSec) {
  const countEl = document.getElementById('countdown');
  if (!countEl) return;
  if (leftSec < 300 && leftSec > 0) {
    countEl.classList.add('urgent');
  } else {
    countEl.classList.remove('urgent');
  }
}

/* =====================================================================
   24. ONBOARDING 3 ECRANS
===================================================================== */
const OB_KEY = 'onboardingDone';

function isOnboardingDone() {
  return store.get(OB_KEY, false) === true;
}

function markOnboardingDone() {
  store.set(OB_KEY, true);
}

function showObScreen(n) {
  const screens = document.querySelectorAll('.ob-screen');
  screens.forEach(s => {
    s.hidden = (+s.dataset.screen !== n);
    // Re-trigger animation
    if (!s.hidden) {
      s.style.animation = 'none';
      void s.offsetHeight;
      s.style.animation = '';
    }
  });
  // Points
  document.querySelectorAll('.ob-dot').forEach(d => {
    d.classList.toggle('active', +d.dataset.dot === n);
  });
  // Bouton passer (caché sur écran 3)
  const skip = document.getElementById('obSkip');
  if (skip) skip.hidden = (n === 3);
  // Titre du document
  const titles = ['Bienvenue sur Wakti', 'Localisation', 'Notifications'];
  document.title = (titles[n - 1] || 'Wakti') + ' — Wakti';
}

function closeOnboarding() {
  const dlg = document.getElementById('onboarding');
  if (dlg && dlg.close) dlg.close();
  // Restaurer le titre original
  document.title = 'Wakti — Coran, heures de prière et calendrier';
}

function startOnboarding() {
  const dlg = document.getElementById('onboarding');
  if (!dlg) return;
  if (!dlg.open && dlg.showModal) {
    dlg.showModal();
    showObScreen(1);
  }
}

// Boutons
function setupOnboarding() {
  const skip = document.getElementById('obSkip');
  if (skip) skip.addEventListener('click', () => {
    markOnboardingDone();
    closeOnboarding();
    // Ouvrir le dialogue de connexion
    setTimeout(() => {
      if (window.WaktiAuth && window.WaktiAuth.openLogin) {
        window.WaktiAuth.openLogin();
      } else {
        const dlg = document.getElementById('loginDialog');
        if (dlg && dlg.showModal) dlg.showModal();
      }
    }, 400);
  });

  // Points de navigation
  document.querySelectorAll('.ob-dot').forEach(d => {
    d.addEventListener('click', () => showObScreen(+d.dataset.dot));
  });

  // Écran 2 : Géolocalisation
  const geo = document.getElementById('obGeo');
  if (geo) geo.addEventListener('click', () => {
    if (!navigator.geolocation) {
      toast('La géolocalisation n\'est pas disponible sur cet appareil.');
      showObScreen(3);
      return;
    }
    geo.disabled = true;
    geo.textContent = 'Localisation en cours...';
    navigator.geolocation.getCurrentPosition(
      pos => {
        geo.disabled = false;
        const lat = +pos.coords.latitude.toFixed(4);
        const lng = +pos.coords.longitude.toFixed(4);
        setLoc({ type: 'coords', lat, lng, label: 'Ma position', country: '' });
        showObScreen(3);
      },
      () => {
        geo.disabled = false;
        geo.innerHTML = '<svg class="ic"><use href="#i-locate"/></svg>Utiliser ma position';
        toast('Position refusée. Tu peux choisir ta ville manuellement.');
      },
      { timeout: 10000, maximumAge: 600000 }
    );
  });

  // Écran 2 : Saisie manuelle
  const manual = document.getElementById('obManual');
  if (manual) manual.addEventListener('click', () => {
    closeOnboarding();
    const dlgLoc = document.getElementById('dlgLoc');
    if (dlgLoc && dlgLoc.showModal) dlgLoc.showModal();
    // Marquer l'onboarding comme terminé pour ne pas le rouvrir
    markOnboardingDone();
  });

  // Écran 3 : Notifications
  const notif = document.getElementById('obNotif');
  if (notif) notif.addEventListener('click', async () => {
    notif.disabled = true;
    notif.textContent = 'Activation...';
    window.__waktiMeta = {
      city: state.loc && state.loc.city ? state.loc.city : null,
      country: state.loc && state.loc.country ? state.loc.country : null,
      method: state.method,
      school: state.school
    };
    let enabled = false;
    if (window.WaktiPush && window.WaktiPush.supported()) {
      const r = await window.WaktiPush.enable(window.__waktiMeta);
      enabled = r.ok;
    } else if ('Notification' in window) {
      const perm = await Notification.requestPermission();
      enabled = (perm === 'granted');
    }
    if (enabled) {
      state.notify = true;
      store.set('notify', true);
      const sw = document.getElementById('notifSw');
      if (sw) sw.checked = true;
      chime();
      toast('Rappels activés. À bientôt pour la prière ! 🕌', 4000);
    } else {
      toast('Rappels non activés. Tu peux les activer plus tard dans les réglages.');
    }
    markOnboardingDone();
    closeOnboarding();
  });

  // Écran 3 : Plus tard
  const skipNotif = document.getElementById('obSkipNotif');
  if (skipNotif) skipNotif.addEventListener('click', () => {
    markOnboardingDone();
    closeOnboarding();
  });

  // Empêcher la fermeture par ESC (obliger à utiliser les boutons)
  const dlg = document.getElementById('onboarding');
  if (dlg) dlg.addEventListener('cancel', e => e.preventDefault());
}

// Exposer pour l'init
window.__waktiOnboarding = {
  isDone: isOnboardingDone,
  start: startOnboarding,
  setup: setupOnboarding
};

/* =====================================================================
   23. DEMARRAGE
===================================================================== */


/* Branche le bouton Hifz dans le lecteur (appele depuis init) */
function hookHifzButton() {
  const hifzBtn = document.getElementById('lecHifz');
  if (!hifzBtn) {
    console.warn('[Hifz] Bouton lecHifz introuvable');
    return;
  }
  if (hifzBtn.dataset.hooked === '1') return;
  hifzBtn.dataset.hooked = '1';
  hifzBtn.addEventListener('click', (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (P.n != null) {
      setupHifzListeners();
      openHifz(P.n, P.idx);
    } else {
      toast('Lance d abord un verset a memoriser.', 3000);
    }
  });
  console.log('[Hifz] Bouton branche avec succes');
}



/* =====================================================================
   Phase 7.2 — Selecteur de theme (Sombre / Clair / Sabah / Layl)
===================================================================== */

function updateThemeSelector() {
  const current = document.documentElement.dataset.theme || 'dark';
  document.querySelectorAll('.theme-option').forEach(btn => {
    const on = btn.dataset.theme === current;
    btn.classList.toggle('active', on);
    btn.setAttribute('aria-pressed', on);
  });
}

function hookThemeSelector() {
  const sel = document.getElementById('themeSelector');
  if (!sel) return;
  sel.addEventListener('click', e => {
    const btn = e.target.closest('.theme-option');
    if (!btn) return;
    const theme = btn.dataset.theme;
    setTheme(theme);
    updateThemeSelector();
    vibrate([10]);
    const names = { dark: 'Sombre', light: 'Clair', sabah: 'Sabah (aube)', layl: 'Layl (nuit)' };
    toast('Theme : ' + (names[theme] || theme), 2000);
  });
  updateThemeSelector();
}



/* =====================================================================
   Phase 7.3 — Lecteur immersif : paroles + waveform
===================================================================== */

/* Cache pour les versets (partage avec le Hifz) */
async function updateLecteurLyrics(n, i) {
  const el = document.getElementById('lecLyrics');
  const elRef = document.getElementById('lecLyricsRef');
  const elAr = document.getElementById('lecLyricsAr');
  const elFr = document.getElementById('lecLyricsFr');
  if (!el) return;

  // Mode sourate complete : cacher les paroles
  const rec = RBY[P.reciter];
  if (rec && rec.server) {
    el.hidden = true;
    return;
  }

  el.hidden = false;
  const s = SURAHS[n - 1];
  if (elRef) elRef.textContent = 'Verset ' + (i + 1) + ' / ' + s.c;
  if (elAr) elAr.textContent = 'Chargement...';
  if (elFr) elFr.textContent = '';

  const v = await fetchVerse(n, i);
  if (!v) {
    if (elAr) elAr.textContent = 'Texte indisponible';
    return;
  }

  if (elAr) elAr.textContent = v.ar;
  if (elFr) elFr.textContent = v.fr;
}

/* =====================================================================
   Phase 7.5 — Grille recitateurs : filtres + badge
===================================================================== */

let recFilterCountry = 'all';

function getReciterCountries() {
  const map = new Map();
  RECITERS.forEach(r => {
    const c = r.country;
    map.set(c, (map.get(c) || 0) + 1);
  });
  return map;
}

function renderReciterFilters() {
  const el = document.getElementById('recFilters');
  if (!el) return;

  const countries = getReciterCountries();
  const sorted = [...countries.entries()].sort((a, b) => b[1] - a[1]);

  let html = '<button class="rec-filter' + (recFilterCountry === 'all' ? ' active' : '') + '" data-country="all">' +
    'Tous <span class="count">' + RECITERS.length + '</span></button>';

  sorted.forEach(([c, n]) => {
    const reciter = RECITERS.find(r => r.country === c);
    const flag = reciter ? reciter.flag : '';
    const on = recFilterCountry === c;
    html += '<button class="rec-filter' + (on ? ' active' : '') + '" data-country="' + esc(c) + '">' +
      flag + ' ' + esc(c) + ' <span class="count">' + n + '</span></button>';
  });

  el.innerHTML = html;
}

function hookReciterFilters() {
  const el = document.getElementById('recFilters');
  if (!el) return;
  el.addEventListener('click', e => {
    const btn = e.target.closest('[data-country]');
    if (!btn) return;
    recFilterCountry = btn.dataset.country;
    renderReciterFilters();
    renderReciters();
    if (typeof vibrate === 'function') vibrate([10]);
  });
}

/* Override renderReciters pour ajouter filtres + badges + bio */
function renderRecitersEnhanced() {
  const fav = store.get('favRec', []);
  let list = [...RECITERS];

  if (recFilterCountry && recFilterCountry !== 'all') {
    list = list.filter(r => r.country === recFilterCountry);
  }

  list.sort((a, b) => fav.includes(b.id) - fav.includes(a.id));

  const grid = document.getElementById('recGrid');
  if (!grid) return;

  grid.innerHTML = list.map(r => {
    const avatar = r.img
      ? '<span class="avatar md has-img" style="--hue:' + r.hue + '"><img src="' + esc(r.img) + '" alt="" loading="lazy" onerror="this.parentElement.classList.remove(\'has-img\');this.parentElement.innerHTML=\'<b>' + esc(r.ar[0]) + '</b>\';"></span>'
      : '<span class="avatar md" style="--hue:' + r.hue + '"><b>' + esc(r.ar[0]) + '</b></span>';

    const isFav = fav.includes(r.id);
    const riwaya = 'Hafs';

    return '<div class="rec-card" data-rid="' + r.id + '" role="button" tabindex="0">' +
      '<button class="rec-fav' + (isFav ? ' on' : '') + '" data-favrid="' + r.id + '" aria-pressed="' + isFav + '"><svg class="ic"><use href="#i-star"/></svg></button>' +
      avatar +
      '<b>' + esc(r.name) + '</b>' +
      '<span class="flag">' + r.flag + ' ' + esc(r.country) + '</span>' +
      '<span class="badge-rec">' + riwaya + '</span>' +
      '<span class="bio-short">' + esc(r.bio) + '</span>' +
      '<small>114 sourates</small>' +
      '</div>';
  }).join('');
}

/* Remplacer la fonction globale renderReciters */
window._origRenderReciters = renderReciters;
renderReciters = renderRecitersEnhanced;

/* Hook l'init des filtres */
function initReciterFilters() {
  renderReciterFilters();
  hookReciterFilters();
}

function init() {
  setTheme(store.get('theme', 'dark'));
  fillLocDialog();
  fillSettings();
  renderSurahList();
  renderResume();
  renderReciters();
  switchQTab('sourates');
  renderDates();
  renderStreak();
  renderPlist();
  initCal();
  renderCalendar();
  route();
  loadTimings();
  loadVod();
  setInterval(tick, 1000);
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden) { renderDates(); tick(); }
  });
  // Phase 5.1 : boutons de repetition
  initRepeatButtons();
  hookTafsir();
  hookQibla();
  // initDouas(); // chargé automatiquement
  hookMosque();
  hookThemeSelector();
  initReciterFilters();
  hookHifzButton();

  // Onboarding : setup
  if (window.__waktiOnboarding) {
    window.__waktiOnboarding.setup();
  }

  // Onboarding : ouvrir si pas encore fait
  // Onboarding : ne pas ouvrir si l'utilisateur est connecté
const isAuthConnected = window.WaktiAuth?.state?.user != null;

if (window.__waktiOnboarding && !window.__waktiOnboarding.isDone() && !isAuthConnected) {
  setTimeout(() => {
    window.__waktiOnboarding.start();
  }, 300);
} else if (!state.loc && !isAuthConnected) {
  // Utilisateur pas connecté et pas de location
  setTimeout(() => {
    const dlgLoc = $('#dlgLoc');
    if (!state.loc && dlgLoc && !dlgLoc.open && currentView === 'prieres' && dlgLoc.showModal) {
      dlgLoc.showModal();
    }
  }, 500);
}

// Si connecté mais pas de location, ouvrir la localisation
if (isAuthConnected && !state.loc) {
  setTimeout(() => {
    const dlgLoc = $('#dlgLoc');
    if (dlgLoc && !dlgLoc.open && dlgLoc.showModal) {
      dlgLoc.showModal();
    }
  }, 800);
}
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}


/* ===== WAKTI ADHAN SYSTEM v2 ===== */
(function() {
  if (!('serviceWorker' in navigator)) return;

  const adhanState = { enabled: true, lastPlayed: 0, currentAudio: null };

  try {
    const stored = localStorage.getItem('wakti:adhanEnabled');
    if (stored !== null) adhanState.enabled = JSON.parse(stored);
  } catch (e) {}

  // Fonction pour jouer l'adhan avec fallback
  function playAdhan(audioPath) {
    const now = Date.now();
    if (now - adhanState.lastPlayed < 30000) {
      console.log('[Adhan] Ignore (30s anti-spam)');
      return;
    }
    adhanState.lastPlayed = now;

    if (!adhanState.enabled) {
      console.log('[Adhan] Desactive par l\'utilisateur');
      return;
    }

    // Arreter l'audio en cours
    if (adhanState.currentAudio) {
      try { adhanState.currentAudio.pause(); } catch (e) {}
    }

    const audio = new Audio(audioPath);
    audio.volume = 1.0;
    adhanState.currentAudio = audio;

    audio.play()
      .then(() => {
        console.log('[Adhan] Lecture demarree :', audioPath);
        // Toast
        if (typeof toast === 'function') {
          toast('🕌 Adhan en cours...', 3000);
        }
      })
      .catch(err => {
        console.warn('[Adhan] Lecture bloquee :', err.message);
        // Vibration de fallback
        if (navigator.vibrate) navigator.vibrate([500, 200, 500, 200, 500]);
        // Notifier l'utilisateur
        if (typeof toast === 'function') {
          toast('Cliquez sur la page pour activer l\'audio', 5000);
        }
      });
  }

  // Ecouter les messages du Service Worker
  navigator.serviceWorker.addEventListener('message', event => {
    const data = event.data || {};
    if (data.type !== 'PLAY_ADHAN') return;
    console.log('[Adhan] Message recu :', data);
    playAdhan(data.audio || '/audio/adhan-standard.mp3');
  });

  // Detecter quand l'app revient au premier plan
  document.addEventListener('visibilitychange', () => {
    if (!document.hidden && adhanState.currentAudio && adhanState.currentAudio.paused) {
      // L'utilisateur revient : on peut essayer de rejouer
      adhanState.currentAudio.play().catch(() => {});
    }
  });

  window.WaktiAdhan = {
    isEnabled: () => adhanState.enabled,
    setEnabled: (v) => {
      adhanState.enabled = !!v;
      try { localStorage.setItem('wakti:adhanEnabled', JSON.stringify(adhanState.enabled)); } catch (e) {}
    },
    test: () => {
      playAdhan('/audio/adhan-standard.mp3');
    },
    testFajr: () => {
      playAdhan('/audio/adhan-fajr.mp3');
    }
  };

  console.log('[Adhan] Listener pret (v2)');
})();


(function() {
  const toggle = document.getElementById('adhanSw');
  if (!toggle) return;

  try {
    const stored = localStorage.getItem('wakti:adhanEnabled');
    if (stored !== null) toggle.checked = JSON.parse(stored);
  } catch (e) {}

  toggle.addEventListener('change', () => {
    const enabled = toggle.checked;
    try {
      localStorage.setItem('wakti:adhanEnabled', JSON.stringify(enabled));
    } catch (e) {}
    if (window.WaktiAdhan) window.WaktiAdhan.setEnabled(enabled);
    if (typeof toast === 'function') {
      toast(enabled ? 'Adhan active' : 'Adhan desactive', 2000);
    }
  });
})();

/* ===== WAKTI TESTIMONIALS SYSTEM v2 ===== */
(function() {
  // Attendre que Supabase soit prêt
  function waitForSupabase(cb) {
    if (window.WaktiAuth && window.WaktiAuth.sb) {
      cb(window.WaktiAuth.sb);
    } else {
      setTimeout(() => waitForSupabase(cb), 200);
    }
  }

  // Échapper le HTML
  function escapeHtml(s) {
    return String(s).replace(/[&<>"']/g, c => ({
      '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;'
    }[c]));
  }

  // Formatage de la date
  function formatDate(isoStr) {
    try {
      const d = new Date(isoStr);
      const now = new Date();
      const diffMs = now - d;
      const diffMin = Math.floor(diffMs / 60000);
      const diffH = Math.floor(diffMin / 60);
      const diffD = Math.floor(diffH / 24);

      if (diffMin < 1) return "à l'instant";
      if (diffMin < 60) return `il y a ${diffMin} min`;
      if (diffH < 24) return `il y a ${diffH}h`;
      if (diffD < 7) return `il y a ${diffD}j`;
      return d.toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' });
    } catch (e) {
      return '';
    }
  }

  // Affiche un témoignage (avec état approuvé ou non)
  function testimonialHTML(t, isOwn) {
    const stars = '★'.repeat(t.rating) + '☆'.repeat(5 - t.rating);
    const location = t.author_city ? ', ' + escapeHtml(t.author_city) : '';
    const isApproved = t.approved === true;
    
    let badge = '';
    if (isApproved) {
      badge = '<span class="verified">Vérifié</span>';
    } else if (isOwn) {
      badge = '<span class="pending">En attente</span>';
    }

    // Ajouter la classe "own" pour vos propres témoignages
    const className = 'testimonial-card' + (isOwn ? ' own' : '');

    return '<div class="' + className + '" data-id="' + (t.id || '') + '">' +
      '<div class="stars">' + stars + '</div>' +
      '<p>"' + escapeHtml(t.message) + '"</p>' +
      '<cite>— ' + escapeHtml(t.author_name) + location + ' ' + badge + '</cite>' +
      '<div class="testimonial-date">' + formatDate(t.created_at) + '</div>' +
      '</div>';
  }

  // Charge les témoignages (approuvés + propres)
  async function loadTestimonials(sb) {
    const user = window.WaktiAuth?.state?.user;
    
    try {
      // 1. Charger les témoignages approuvés (publics)
      const { data: approved, error: err1 } = await sb
        .from('wakti_testimonials')
        .select('id, author_name, author_city, rating, message, approved, created_at')
        .eq('approved', true)
        .order('created_at', { ascending: false })
        .limit(10);
      
      if (err1) console.warn('[Testimonials] Approved load error:', err1.message);
      
      // 2. Charger les témoignages de l'utilisateur (même non approuvés)
      let own = [];
      if (user) {
        const { data: ownData, error: err2 } = await sb
          .from('wakti_testimonials')
          .select('id, author_name, author_city, rating, message, approved, created_at')
          .eq('user_id', user.id)
          .order('created_at', { ascending: false })
          .limit(10);
        
        if (err2) console.warn('[Testimonials] Own load error:', err2.message);
        own = ownData || [];
      }
      
      // 3. Fusionner : les propres témoignages en premier (avec marqueur)
      const ownIds = new Set(own.map(t => t.id));
      const approvedFiltered = (approved || []).filter(t => !ownIds.has(t.id));
      
      // Marquer les témoignages propres
      const ownMarked = own.map(t => ({ ...t, _isOwn: true }));
      const approvedMarked = approvedFiltered.map(t => ({ ...t, _isOwn: false }));
      
      // Trier par date
      const all = [...ownMarked, ...approvedMarked].sort((a, b) => 
        new Date(b.created_at) - new Date(a.created_at)
      );
      
      return all;
    } catch (e) {
      console.warn('[Testimonials] Load error:', e.message);
      return [];
    }
  }

  // Affiche les témoignages
  function renderTestimonials(list) {
    const container = document.getElementById('testimonials-container');
    const section = document.getElementById('testimonials-live');
    const countEl = document.getElementById('testimonialsCount');
    if (!container || !section) return;

    if (!list || list.length === 0) {
      section.hidden = true;
      return;
    }

    section.hidden = false;
    container.innerHTML = list.map(t => testimonialHTML(t, t._isOwn)).join('');
    
    // Mettre à jour le compteur
    if (countEl) {
      const publicCount = list.filter(t => t.approved).length;
      countEl.textContent = publicCount + (publicCount > 1 ? ' témoignages' : ' témoignage');
    }
    
    // Mettre à jour le titre selon le contexte
    const titleEl = section.querySelector('h3');
    if (titleEl) {
      const hasOwn = list.some(t => t._isOwn && !t.approved);
      if (hasOwn) {
        titleEl.innerHTML = '💬 Tes témoignages & ceux des utilisateurs';
      } else {
        titleEl.innerHTML = '💬 Ce que disent nos utilisateurs';
      }
    }
  }

  // Initialise le formulaire
  function setupForm(sb) {
    const dialog = document.getElementById('testimonialDialog');
    const openBtn = document.getElementById('openTestimonialForm');
    const closeBtn = document.getElementById('testimonialClose');
    const cancelBtn = document.getElementById('testimonialCancel');
    const form = document.getElementById('testimonialForm');
    const messageInput = document.getElementById('tMessage');
    const charCount = document.getElementById('tCharCount');
    const ratingInput = document.getElementById('ratingInput');
    const ratingHidden = document.getElementById('tRating');
    const hint = document.getElementById('testimonialHint');
    const submitBtn = document.getElementById('testimonialSubmit');

    if (!dialog || !openBtn) return;

    // Ouvrir
    openBtn.addEventListener('click', () => {
      const user = window.WaktiAuth?.state?.user;
      if (!user) {
        if (typeof toast === 'function') {
          toast('Connecte-toi d\'abord pour laisser un témoignage', 4000);
        }
        if (window.WaktiAuth?.openLogin) {
          setTimeout(() => window.WaktiAuth.openLogin(), 500);
        }
        return;
      }
      const meta = user.user_metadata || {};
      const prefName = meta.full_name || meta.name || meta.user_name || '';
      if (prefName && !document.getElementById('tName').value) {
        document.getElementById('tName').value = prefName.split(' ')[0];
      }
      dialog.showModal();
    });

    // Fermer
    const closeFn = () => {
      if (dialog.close) dialog.close();
      hint.textContent = '';
      hint.className = 'testimonial-hint';
    };
    closeBtn?.addEventListener('click', closeFn);
    cancelBtn?.addEventListener('click', closeFn);

    // Compteur de caractères
    messageInput?.addEventListener('input', () => {
      const len = messageInput.value.length;
      charCount.textContent = len;
      charCount.parentElement.style.color = len > 500 ? '#e88' : '';
    });

    // Étoiles
    ratingInput?.addEventListener('click', e => {
      const btn = e.target.closest('.star-btn');
      if (!btn) return;
      const rating = parseInt(btn.dataset.rating, 10);
      ratingHidden.value = rating;
      ratingInput.querySelectorAll('.star-btn').forEach(s => {
        const r = parseInt(s.dataset.rating, 10);
        s.classList.toggle('active', r <= rating);
      });
      if (typeof vibrate === 'function') vibrate([10]);
    });

    // Soumettre
    form?.addEventListener('submit', async e => {
      e.preventDefault();
      const name = document.getElementById('tName').value.trim();
      const city = document.getElementById('tCity').value.trim();
      const rating = parseInt(ratingHidden.value, 10) || 5;
      const message = messageInput.value.trim();

      if (name.length < 2) {
        hint.textContent = 'Ton prénom doit faire au moins 2 caractères.';
        hint.className = 'testimonial-hint error';
        return;
      }
      if (message.length < 10) {
        hint.textContent = 'Ton témoignage doit faire au moins 10 caractères.';
        hint.className = 'testimonial-hint error';
        return;
      }
      if (message.length > 500) {
        hint.textContent = 'Ton témoignage ne doit pas dépasser 500 caractères.';
        hint.className = 'testimonial-hint error';
        return;
      }

      submitBtn.disabled = true;
      hint.textContent = 'Envoi en cours...';
      hint.className = 'testimonial-hint';

      try {
        const user = window.WaktiAuth?.state?.user;
        const { data, error } = await sb.from('wakti_testimonials').insert({
          user_id: user.id,
          author_name: name,
          author_city: city || null,
          rating: rating,
          message: message,
          approved: false
        }).select();

        if (error) throw error;

        hint.textContent = '✅ Merci ! Ton témoignage est publié ci-dessous.';
        hint.className = 'testimonial-hint success';
        if (typeof toast === 'function') {
          toast('Merci pour ton témoignage ! 🌙', 4000);
        }
        if (typeof vibrate === 'function') vibrate([10, 30, 10]);

        // Fermer le dialogue
        setTimeout(() => {
          form.reset();
          document.getElementById('tRating').value = 5;
          ratingInput.querySelectorAll('.star-btn').forEach(s => {
            s.classList.toggle('active', parseInt(s.dataset.rating, 10) <= 5);
          });
          charCount.textContent = '0';
          closeFn();
        }, 1500);

        // Recharger les témoignages immédiatement
        setTimeout(() => {
          loadTestimonials(sb).then(renderTestimonials);
          
          // Faire défiler jusqu'à la section des témoignages
          const section = document.getElementById('testimonials-live');
          if (section) {
            section.scrollIntoView({ behavior: 'smooth', block: 'start' });
          }
        }, 500);
      } catch (e) {
        console.error('[Testimonials] Insert error:', e);
        hint.textContent = 'Erreur : ' + (e.message || 'impossible d\'envoyer');
        hint.className = 'testimonial-hint error';
      } finally {
        submitBtn.disabled = false;
      }
    });

    // Charger les témoignages initiaux
    loadTestimonials(sb).then(renderTestimonials);
  }

  // Écouter les changements d'auth pour recharger
  function watchAuth(sb) {
    if (window.WaktiAuth?.sb?.auth?.onAuthStateChange) {
      sb.auth.onAuthStateChange(() => {
        setTimeout(() => {
          loadTestimonials(sb).then(renderTestimonials);
        }, 500);
      });
    }
  }

  // Démarrer
  waitForSupabase(sb => {
    setupForm(sb);
    watchAuth(sb);
  });

  // Exposer pour debug
  window.WaktiTestimonials = {
    reload: () => waitForSupabase(sb => loadTestimonials(sb).then(renderTestimonials))
  };
})();
/* ===== FIN WAKTI TESTIMONIALS SYSTEM v2 ===== */
