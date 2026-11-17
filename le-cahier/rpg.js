/* Le Cahier — le personnage.
   Rien n'est inventé ici : chaque caractéristique est calculée sur ce que
   l'apprenant a réellement rappelé, écrit, entendu ou dit. */

const AVATARS = ["🦊", "🦉", "🐈", "🐢", "🦅", "🐺", "🦔", "🐙", "🦌", "🐝"];

const RANKS = [
  {lv:1,  t:"Débutant",      e:"Beginner"},
  {lv:3,  t:"Apprenti",      e:"Apprentice"},
  {lv:6,  t:"Voyageur",      e:"Traveller"},
  {lv:10, t:"Bavard",        e:"Talker"},
  {lv:15, t:"Lettré",        e:"Well-read"},
  {lv:21, t:"Orateur",       e:"Orator"},
  {lv:28, t:"Érudit",        e:"Scholar"},
  {lv:36, t:"Plume",         e:"Stylist"},
  {lv:45, t:"Académicien",   e:"Academician"}
];

const xpLevel = (xp) => Math.floor(Math.sqrt(Math.max(0, xp) / 50)) + 1;
const xpFor = (lv) => Math.round(50 * Math.pow(lv - 1, 2));
const rankOf = (lv) => RANKS.filter(r => r.lv <= lv).pop() || RANKS[0];

/* ---------- caractéristiques, tirées des vraies données ---------- */
function heroStats(){
  const p = S.P;
  const pct = (a, b) => (b > 0 ? Math.max(0, Math.min(100, Math.round(a / b * 100))) : null);

  let mature = 0, conjT = 0, conjH = 0, vocT = 0, vocH = 0, earT = 0, earH = 0;
  registry().forEach(it => {
    const s = p.srs[it.id];
    if(!s) return;
    if((s[1] || 0) >= 21) mature++;
    const t = s[5] || 0, h = s[6] || 0;
    if(!t) return;
    if(it.kind === "conj"){ conjT += t; conjH += h; }
    else if(it.kind === "trou"){ vocT += t; vocH += h; }
    else if(it.kind === "dictee"){ earT += t; earH += h; }
  });

  const ret = p.recall.rev ? p.recall.ok / p.recall.rev : 0;
  const memory = p.recall.rev < 10 ? null
    : Math.round(ret * 100 * (0.55 + 0.45 * Math.min(1, mature / 60)));

  const ear = (p.dictee.words > 20 || earT > 5)
    ? pct(p.dictee.right + earH, p.dictee.words + earT) : null;
  const pen = p.phrase.n ? pct(p.phrase.ok, p.phrase.n) : null;
  const tongue = p.parle.n ? Math.round(p.parle.points / p.parle.n / 20 * 100) : null;

  return [
    {k:"memory",  fr:"Mémoire",    en:"Memory",      v:memory},
    {k:"grammar", fr:"Grammaire",  en:"Grammar",     v:pct(conjH, conjT)},
    {k:"vocab",   fr:"Vocabulaire", en:"Vocabulary", v:pct(vocH, vocT)},
    {k:"ear",     fr:"Oreille",    en:"Ear",         v:ear},
    {k:"pen",     fr:"Plume",      en:"Pen",         v:pen},
    {k:"tongue",  fr:"Langue",     en:"Tongue",      v:tongue}
  ];
}

/* ---------- gains ---------- */
function heroDay(){
  const t = dayNum();
  const d = S.P.hero.day;
  if(d.n !== t){ S.P.hero.day = {n:t, xp:0, recalls:0, clean:0, convo:0, phrase:0, grid:0, exam:0}; }
  return S.P.hero.day;
}

function xpGain(n, kind){
  if(!n) return;
  /* Le bonus de classe ne s'applique qu'à ce que la classe aime faire. */
  const cls = heroClass();
  if(cls && kind && cls.bonus.kinds.indexOf(kind) >= 0 && n > 0) n = Math.round(n * cls.bonus.mult);
  const d = heroDay();
  const before = xpLevel(S.P.hero.xp);
  S.P.hero.xp += n;
  d.xp += n;
  if(kind && d[kind] != null) d[kind]++;
  if(kind === "recalls") d.recalls = d.recalls;
  const after = xpLevel(S.P.hero.xp);
  if(after > before) S.P.hero.justLevelled = after;
  if(typeof paintHero === "function" && !$("panel-perso").hidden) paintHero();
}

/* Appelé à chaque rappel : produire de mémoire rapporte plus que reconnaître. */
function xpForRecall(q, iv, helped){
  const base = q >= 5 ? 12 : q >= 4 ? 10 : q >= 3 ? 5 : 2;
  const bonus = (q >= 3 && iv >= 21) ? 6 : 0;
  return base + bonus - (helped ? 3 : 0);
}

/* ---------- quêtes du jour ---------- */
const QUESTS = [
  {k:"recalls", n:20, fr:"Faire 20 rappels", en:"Make 20 recalls", xp:40},
  {k:"recalls", n:40, fr:"Faire 40 rappels", en:"Make 40 recalls", xp:90},
  {k:"clean",   n:8,  fr:"8 rappels justes du premier coup", en:"8 recalls right first time", xp:50},
  {k:"convo",   n:1,  fr:"Tenir une conversation entière", en:"Hold a full conversation", xp:70},
  {k:"phrase",  n:3,  fr:"Écrire 3 phrases justes", en:"Write 3 correct sentences", xp:60},
  {k:"grid",    n:1,  fr:"Finir une grille de mots croisés", en:"Finish a crossword grid", xp:45},
  {k:"exam",    n:1,  fr:"Passer une épreuve d'examen", en:"Sit one exam paper", xp:80}
];

function todayQuests(){
  const d = heroDay();
  if(S.P.hero.questDay !== d.n){
    const pool = QUESTS.map((q, i) => i);
    for(let i = pool.length - 1; i > 0; i--){ const j = (Math.random() * (i + 1)) | 0; [pool[i], pool[j]] = [pool[j], pool[i]]; }
    S.P.hero.questDay = d.n;
    S.P.hero.quests = pool.slice(0, 3);
    S.P.hero.claimed = [];
  }
  return (S.P.hero.quests || []).map(i => QUESTS[i]).filter(Boolean);
}

/* Rend les quêtes qui viennent d'être accomplies, pour qu'on puisse les fêter. */
function claimQuests(){
  const d = heroDay(), won = [];
  todayQuests().forEach((q, i) => {
    if((S.P.hero.claimed || []).includes(i)) return;
    if((d[q.k] || 0) >= q.n){
      S.P.hero.claimed.push(i);
      addXp(q.xp);
      won.push(q);
    }
  });
  return won;
}

/* Gagner de l'XP sans repasser par xpGain (pas de bonus, pas de compteur du jour)
   tout en gardant la montée de niveau : récompenses de quêtes et de hauts faits. */
function addXp(n){
  const h = S.P.hero, before = xpLevel(h.xp);
  h.xp += n;
  const after = xpLevel(h.xp);
  if(after > before) h.justLevelled = after;
}

/* ---------- la fiche ---------- */
function radar(stats){
  const cx = 145, cy = 100, R = 76, n = stats.length;
  const pt = (i, r) => {
    const a = -Math.PI / 2 + i * 2 * Math.PI / n;
    return [cx + Math.cos(a) * r, cy + Math.sin(a) * r];
  };
  const ring = (f) => stats.map((_, i) => pt(i, R * f).map(v => v.toFixed(1)).join(",")).join(" ");
  const shape = stats.map((s, i) => pt(i, R * Math.max(0.04, (s.v || 0) / 100)).map(v => v.toFixed(1)).join(",")).join(" ");

  let svg = '<svg viewBox="0 0 290 200" width="100%" height="200" role="img" aria-label="Character stats">';
  [0.25, 0.5, 0.75, 1].forEach(f => {
    svg += '<polygon class="rgrid" points="' + ring(f) + '"/>';
  });
  stats.forEach((s, i) => {
    const [x, y] = pt(i, R);
    svg += '<line class="rgrid" x1="' + cx + '" y1="' + cy + '" x2="' + x.toFixed(1) + '" y2="' + y.toFixed(1) + '"/>';
  });
  svg += '<polygon class="rshape" points="' + shape + '"/>';
  stats.forEach((s, i) => {
    const [x, y] = pt(i, R * Math.max(0.04, (s.v || 0) / 100));
    svg += '<circle class="rdot" cx="' + x.toFixed(1) + '" cy="' + y.toFixed(1) + '" r="2.6"/>';
  });
  stats.forEach((s, i) => {
    const [x, y] = pt(i, R + 17);
    const anchor = x < cx - 6 ? "end" : x > cx + 6 ? "start" : "middle";
    const label = (typeof LANG !== "undefined" && LANG === "en") ? s.en : s.fr;
    svg += '<text class="rlab" x="' + x.toFixed(1) + '" y="' + (y + 3).toFixed(1) + '" text-anchor="' + anchor + '">'
      + label + (s.v == null ? "" : " " + s.v) + "</text>";
  });
  return svg + "</svg>";
}

function paintHero(){
  const en = typeof LANG !== "undefined" && LANG === "en";
  const h = S.P.hero;
  claimQuests();
  const lv = xpLevel(h.xp), rank = rankOf(lv);
  const cur = xpFor(lv), next = xpFor(lv + 1);

  $("hAvatar").textContent = h.avatar || AVATARS[0];
  $("hName").value = h.name || "";
  $("hTitle").textContent = (en ? rank.e : rank.t) + " · " + (en ? "level " : "niveau ") + lv;
  $("hXp").textContent = h.xp + " XP";
  $("hBarFill").style.width = Math.max(2, Math.round((h.xp - cur) / Math.max(1, next - cur) * 100)) + "%";
  $("hNext").textContent = (next - h.xp) + " XP " + (en ? "to level " : "avant le niveau ") + (lv + 1);

  const stats = heroStats();
  $("hRadar").innerHTML = radar(stats);
  const list = $("hStats");
  list.innerHTML = "";
  stats.forEach(s => {
    const row = document.createElement("div");
    row.className = "lvrow";
    row.appendChild(Object.assign(document.createElement("span"),
      {className:"weakname", textContent:en ? s.en : s.fr}));
    const track = document.createElement("div");
    track.className = "lvtrack";
    const fill = document.createElement("div");
    fill.className = "lvfill";
    fill.style.width = (s.v || 0) + "%";
    track.appendChild(fill);
    row.appendChild(track);
    row.appendChild(Object.assign(document.createElement("span"),
      {className:"lvnum", textContent:s.v == null ? "—" : s.v}));
    list.appendChild(row);
  });

  const d = heroDay();
  paintQuestList($("hQuests"));
  $("hToday").textContent = (en ? "Today: " : "Aujourd'hui : ") + d.xp + " XP, "
    + (d.recalls || 0) + (en ? " recalls" : " rappels");
  paintHeat();

  const cls = heroClass();
  $("hClass").textContent = cls ? (en ? cls.en : cls.fr) : (en ? "No class yet" : "Pas encore de classe");
  $("hClassNote").textContent = cls ? (en ? cls.enTag : cls.frTag) : (en ? "Pick one below." : "Choisis-en une ci-dessous.");
  paintClasses($("hClasses"), h.cls, (k) => { h.cls = k; save(); paintHero(); paintHud(); });
  paintMedals();
  save();
}

/* L'année, jour par jour : une case par jour, une colonne par semaine, du lundi
   au dimanche. La teinte suit le nombre de rappels — rien d'autre n'est compté. */
function paintHeat(){
  const host = $("hHeat");
  if(!host) return;
  const en = typeof LANG !== "undefined" && LANG === "en";
  const t = dayNum(), h = S.P.hist || {};
  const dow = (dn) => ((dn + 3) % 7 + 7) % 7;          /* lundi = 0 */
  const start = t - dow(t) - 52 * 7;
  host.innerHTML = "";
  let active = 0, total = 0;
  for(let d = start; d <= t; d++){
    const day = h[d];
    let n = 0;
    if(day) Object.keys(day).forEach(k => { n += day[k][0] || 0; });
    if(n){ active++; total += n; }
    const c = document.createElement("i");
    c.className = n >= 50 ? "h4" : n >= 25 ? "h3" : n >= 10 ? "h2" : n ? "h1" : "";
    c.title = new Date(d * 864e5).toLocaleDateString(en ? "en-CA" : "fr-CA") + " · " + n
      + (en ? " recalls" : " rappels");
    host.appendChild(c);
  }
  host.scrollLeft = host.scrollWidth;
  $("hHeatLeg").textContent = active + (en ? " active days in the last year · " : " jours actifs sur l'année · ")
    + total + (en ? " recalls" : " rappels");
}

let HERO_READY = false;

function persoInit(){
  if(HERO_READY) return paintHero();
  HERO_READY = true;
  const box = $("hPick");
  AVATARS.forEach(a => {
    const b = document.createElement("button");
    b.className = "avbtn"; b.type = "button"; b.textContent = a;
    b.addEventListener("click", () => { S.P.hero.avatar = a; save(); paintHero(); });
    box.appendChild(b);
  });
  $("hName").addEventListener("input", () => {
    S.P.hero.name = $("hName").value.slice(0, 24);
    save();
  });
  $("hLevelUp").addEventListener("click", () => { $("hLevelUp").hidden = true; });
  paintHero();
}

/* =========================================================================
   Le jeu : classes, HUD, hauts faits, fenêtres.
   Rien ici ne touche à la répétition espacée : le jeu se nourrit de ce que
   l'apprenant fait déjà, il ne le remplace pas et ne le décide pas.
   ========================================================================= */
const CLASSES = [
  {k:"erudit", fr:"Érudit", en:"Scholar", ic:"i-biblio", bonus:{kinds:["recalls"], mult:1.10},
   frTag:"La mémoire d’abord : +10 % d’XP sur chaque rappel.", enTag:"Memory first: +10% XP on every recall."},
  {k:"scribe", fr:"Scribe", en:"Scribe", ic:"i-forge", bonus:{kinds:["phrase"], mult:1.25},
   frTag:"La plume : +25 % d’XP sur les phrases justes.", enTag:"The quill: +25% XP on correct sentences."},
  {k:"troubadour", fr:"Troubadour", en:"Troubadour", ic:"i-taverne", bonus:{kinds:["convo"], mult:1.25},
   frTag:"La parole : +25 % d’XP sur les conversations.", enTag:"The voice: +25% XP on conversations."},
  {k:"voyageur", fr:"Voyageur", en:"Wayfarer", ic:"i-donjon", bonus:{kinds:["grid", "exam"], mult:1.25},
   frTag:"L’épreuve : +25 % d’XP sur grilles et examens.", enTag:"The trial: +25% XP on grids and exams."}
];
const heroClass = () => CLASSES.find(c => c.k === (S.P.hero && S.P.hero.cls)) || null;

const ACH = [
  {k:"spark",  ic:"i-flamme", fr:"Première étincelle", en:"First spark", dfr:"Un premier rappel", den:"One first recall", t:c => c.rev >= 1},
  {k:"hundred", fr:"Cent coups", en:"A hundred blows", dfr:"100 rappels", den:"100 recalls", t:c => c.rev >= 100},
  {k:"five",   fr:"Cinq cents", en:"Five hundred", dfr:"500 rappels", den:"500 recalls", t:c => c.rev >= 500},
  {k:"week",   fr:"Sept jours de feu", en:"Seven days of fire", dfr:"Série de 7 jours", den:"A 7-day streak", t:c => c.streak >= 7},
  {k:"month",  fr:"Veilleur", en:"Night watch", dfr:"Série de 30 jours", den:"A 30-day streak", t:c => c.streak >= 30},
  {k:"speak",  fr:"Première parole", en:"First words", dfr:"Une conversation menée à terme", den:"One finished conversation", t:c => c.convos >= 1},
  {k:"voice",  fr:"Voix posée", en:"Steady voice", dfr:"5 missions du jour", den:"5 daily missions", t:c => c.missions >= 5},
  {k:"quill",  fr:"Plume sûre", en:"Sure quill", dfr:"10 phrases justes", den:"10 correct sentences", t:c => c.phraseOk >= 10},
  {k:"memory", fr:"Mémoire d’éléphant", en:"Elephant memory", dfr:"25 cartes tenues 3 semaines", den:"25 cards held for 3 weeks", t:c => c.mature >= 25},
  {k:"hoard",  fr:"Collectionneur", en:"Collector", dfr:"50 mots dans ton paquet", den:"50 words in your deck", t:c => c.words >= 50},
  {k:"ring",   fr:"Anneau d’or", en:"Golden ring", dfr:"Fermer l’anneau du jour", den:"Close the day’s ring", t:c => c.rings >= 1},
  {k:"tier",   fr:"Seuil franchi", en:"Threshold crossed", dfr:"Atteindre le palier B1", den:"Reach tier B1", t:c => c.level >= 3},
  {k:"ear",    fr:"Greffier", en:"Clerk", dfr:"10 dictées", den:"10 dictations", t:c => c.dictee >= 10},
  {k:"vault",  fr:"Archiviste", en:"Archivist", dfr:"Exporter ton cahier", den:"Export your notebook", t:c => c.backup},
  {k:"page",   ic:"i-chroniques", fr:"Première page", en:"First page", dfr:"Lire une page du récit", den:"Read one page of the story", t:c => c.pages >= 1},
  {k:"chap",   ic:"i-chroniques", fr:"Fin de chapitre", en:"Chapter’s end", dfr:"Terminer un chapitre du récit", den:"Finish a chapter of the story", t:c => c.chapters >= 1},
  {k:"act",    fr:"Acte accompli", en:"Act complete", dfr:"Terminer un acte du récit", den:"Finish an act of the story", t:c => c.acts >= 1}
];

function achCtx(){
  const p = S.P;
  let mature = 0;
  Object.keys(p.srs || {}).forEach(id => {
    const s = p.srs[id];
    if(Array.isArray(s) && s[0] !== LEECH_DAY && (s[1] || 0) >= 21) mature++;
  });
  return {rev:p.recall.rev, streak:p.streak, convos:p.parle.n, missions:p.parle.missions || 0,
    phraseOk:p.phrase.ok, mature, words:(S.mots || []).length, rings:p.rings || 0, level:p.level,
    backup:!!p.backupAt, dictee:p.dictee.done,
    pages:typeof recitPagesRead === "function" ? recitPagesRead() : 0,
    chapters:typeof recitChaptersDone === "function" ? recitChaptersDone() : 0,
    acts:typeof recitActsDone === "function" ? recitActsDone() : 0};
}

const rpgEn = () => typeof LANG !== "undefined" && LANG === "en";

/* ---- le HUD : visage, nom, classe, XP ---- */
function paintHud(){
  const h = S.P.hero, en = rpgEn();
  const lv = xpLevel(h.xp), rank = rankOf(lv), cur = xpFor(lv), next = xpFor(lv + 1);
  const cls = heroClass();
  $("hudAvatar").textContent = h.avatar || AVATARS[0];
  $("hudLv").textContent = lv;
  const nm = $("hudName");
  nm.dataset.keep = "1";
  nm.textContent = h.name || (en ? "Adventurer" : "Aventurier");
  $("hudClass").textContent = cls ? (en ? cls.en : cls.fr) : "";
  const pct = Math.max(2, Math.round((h.xp - cur) / Math.max(1, next - cur) * 100));
  $("hudXpFill").style.width = pct + "%";
  $("hudXp").textContent = (h.xp - cur) + " / " + (next - cur) + " XP";
  $("hudXpBar").setAttribute("aria-valuenow", String(pct));
  $("hudRank").textContent = (en ? rank.e : rank.t) + " · " + (en ? "level " : "niveau ") + lv;
}

/* ---- les quêtes du jour : même liste sur Quêtes et sur la fiche ---- */
function paintQuestList(host){
  if(!host) return;
  const en = rpgEn(), d = heroDay();
  host.innerHTML = "";
  todayQuests().forEach(q => {
    const got = Math.min(q.n, d[q.k] || 0), done = got >= q.n;
    const row = document.createElement("div");
    row.className = "quest" + (done ? " done" : "");
    row.appendChild(Object.assign(document.createElement("span"), {className:"qmark", textContent:done ? "✓" : "○"}));
    row.appendChild(Object.assign(document.createElement("span"), {className:"qtext", textContent:en ? q.en : q.fr}));
    row.appendChild(Object.assign(document.createElement("span"),
      {className:"qprog", textContent:got + "/" + q.n + " · " + q.xp + " XP"}));
    host.appendChild(row);
  });
}

/* ---- les classes ---- */
function paintClasses(host, current, onPick){
  if(!host) return;
  const en = rpgEn();
  host.innerHTML = "";
  CLASSES.forEach(c => {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "cls";
    b.setAttribute("aria-pressed", c.k === current ? "true" : "false");
    b.innerHTML = '<svg class="ti" viewBox="0 0 24 24" aria-hidden="true"><use href="#' + c.ic + '"/></svg><b></b><span></span>';
    b.querySelector("b").textContent = en ? c.en : c.fr;
    b.querySelector("span").textContent = en ? c.enTag : c.frTag;
    b.addEventListener("click", () => onPick(c.k));
    host.appendChild(b);
  });
}

/* ---- les hauts faits ---- */
function paintMedals(){
  const host = $("hAch");
  if(!host) return;
  const en = rpgEn(), h = S.P.hero, got = h.ach || {};
  host.innerHTML = "";
  let n = 0;
  ACH.forEach(a => {
    const on = !!got[a.k];
    if(on) n++;
    const d = document.createElement("div");
    d.className = "medal" + (on ? "" : " locked");
    d.innerHTML = '<span class="mi"><svg class="ti" viewBox="0 0 24 24" aria-hidden="true"><use href="#'
      + (on ? (a.ic || "i-medaille") : "i-cadenas") + '"/></svg></span><div><b></b><small></small></div>';
    d.querySelector("b").textContent = en ? a.en : a.fr;
    d.querySelector("small").textContent = en ? a.den : a.dfr;
    host.appendChild(d);
  });
  $("hAchLeg").textContent = n + " / " + ACH.length + (en ? " unlocked" : " débloqués");
}

/* ---- avis, fenêtres ---- */
function toast(title, sub, icon){
  const box = $("toasts");
  if(!box) return;
  const t = document.createElement("div");
  t.className = "toast";
  t.setAttribute("role", "status");
  t.innerHTML = '<span class="mi"><svg class="ti" viewBox="0 0 24 24" aria-hidden="true"><use href="#'
    + (icon || "i-medaille") + '"/></svg></span><div><b></b><small></small></div>';
  t.querySelector("b").textContent = title;
  t.querySelector("small").textContent = sub || "";
  box.appendChild(t);
  setTimeout(() => { t.classList.add("out"); setTimeout(() => t.remove(), 320); }, 6500);
  while(box.children.length > 3) box.firstChild.remove();
}

const openModal = () => document.querySelector(".modal:not([hidden])");

function showLevelUp(lv){
  const en = rpgEn(), h = S.P.hero, rank = rankOf(lv), prev = rankOf(lv - 1);
  const nextRank = RANKS.find(r => r.lv > lv);
  $("mdLevelN").textContent = lv;
  $("mdLevelT").textContent = en ? rank.e : rank.t;
  $("mdLevelTxt").textContent = rank.t !== prev.t
    ? (en ? "A new title: you are now " + rank.e + "." : "Un nouveau titre : tu deviens " + rank.t + ".")
    : nextRank
      ? (en ? (nextRank.lv - lv) + " more level" + (nextRank.lv - lv > 1 ? "s" : "") + " until " + nextRank.e + "."
        : "Encore " + (nextRank.lv - lv) + " niveau" + (nextRank.lv - lv > 1 ? "x" : "") + " avant " + nextRank.t + ".")
      : (en ? "You have reached the highest title." : "Tu as atteint le plus haut titre.");
  h.justLevelled = null;
  $("mdLevel").hidden = false;
  $("mdLevelGo").focus();
  save();
}

function closeModal(id){
  $(id).hidden = true;
  heroCelebrate();      /* un autre événement attendait peut-être derrière */
}

/* Après chaque réponse : quêtes accomplies, hauts faits, montée de niveau. */
function heroCelebrate(){
  const h = S.P.hero;
  if(!h || S.celebrating) return;
  S.celebrating = true;
  try{
    const en = rpgEn();
    h.ach = (h.ach && typeof h.ach === "object") ? h.ach : {};
    let changed = false;

    claimQuests().forEach(q => {
      changed = true;
      toast(en ? "Quest complete" : "Quête accomplie", (en ? q.en : q.fr) + " · +" + q.xp + " XP", "i-quetes");
    });

    const c = achCtx(), fresh = [];
    ACH.forEach(a => { if(!h.ach[a.k] && a.t(c)){ h.ach[a.k] = dayNum(); fresh.push(a); } });
    if(fresh.length){
      changed = true;
      addXp(20 * fresh.length);
      if(fresh.length <= 2){
        fresh.forEach(a => toast((en ? "Achievement: " : "Haut fait : ") + (en ? a.en : a.fr),
          (en ? a.den : a.dfr) + " · +20 XP", a.ic || "i-medaille"));
      }else{
        toast(fresh.length + (en ? " achievements unlocked" : " hauts faits débloqués"),
          fresh.slice(0, 3).map(a => en ? a.en : a.fr).join(", ") + (fresh.length > 3 ? "…" : "") + " · +" + 20 * fresh.length + " XP",
          "i-medaille");
      }
    }
    if(changed){ save(); paintHud(); }
    if(h.justLevelled && !openModal()) showLevelUp(h.justLevelled);
  }finally{ S.celebrating = false; }
}

/* ---- la création du personnage ---- */
function openCreate(){
  const h = S.P.hero;
  const pick = {avatar:h.avatar || AVATARS[0], cls:h.cls || "erudit"};
  $("mdName").value = h.name || "";
  const paintPicks = () => {
    const av = $("mdAvatars");
    av.innerHTML = "";
    AVATARS.forEach(a => {
      const b = document.createElement("button");
      b.type = "button";
      b.className = "avbtn" + (a === pick.avatar ? " on" : "");
      b.textContent = a;
      b.setAttribute("aria-pressed", a === pick.avatar ? "true" : "false");
      b.addEventListener("click", () => { pick.avatar = a; paintPicks(); });
      av.appendChild(b);
    });
    paintClasses($("mdClasses"), pick.cls, (k) => { pick.cls = k; paintPicks(); });
  };
  paintPicks();
  S.createPick = pick;
  $("mdCreate").hidden = false;
  $("mdName").focus();
}

function finishCreate(save_){
  const h = S.P.hero, en = rpgEn();
  if(save_ && S.createPick){
    h.name = $("mdName").value.trim().slice(0, 24);
    h.avatar = S.createPick.avatar;
    h.cls = S.createPick.cls;
  }
  h.created = dayNum();
  save();
  paintHud();
  $("mdCreate").hidden = true;
  if(save_){
    const cls = heroClass();
    toast((en ? "Welcome, " : "Bienvenue, ") + (h.name || (en ? "adventurer" : "aventurier")),
      cls ? (en ? cls.en + " — " + cls.enTag : cls.fr + " — " + cls.frTag) : "", "i-perso");
  }
  if(typeof paintHero === "function" && $("panel-perso") && !$("panel-perso").hidden) paintHero();
  heroCelebrate();
  /* Le héros existe : l'histoire peut commencer. */
  if(save_ && typeof recitAfterCreate === "function") recitAfterCreate();
}

/* À appeler quand l'état est sûr (après la synchro du compte) : jamais deux fois. */
function maybeCreate(){
  const h = S.P.hero;
  if(!h || h.created || openModal()) return;
  openCreate();
}

let RPG_READY = false;
function rpgInit(){
  if(RPG_READY) return;
  RPG_READY = true;
  $("hudPortrait").addEventListener("click", () => setMode("perso"));
  $("mdLevelGo").addEventListener("click", () => closeModal("mdLevel"));
  $("mdCreateGo").addEventListener("click", () => finishCreate(true));
  $("mdCreateSkip").addEventListener("click", () => finishCreate(false));
  $("mdName").addEventListener("keydown", (e) => { if(e.key === "Enter"){ e.preventDefault(); finishCreate(true); } });
  document.addEventListener("keydown", (e) => {
    const m = openModal();
    if(!m) return;
    if(e.key === "Escape"){
      e.preventDefault();
      if(m.id === "mdLevel") closeModal("mdLevel");
      else if(m.id === "mdPage") recitEscape(m);
      else finishCreate(false);
      return;
    }
    if(e.key !== "Tab") return;
    const f = [...m.querySelectorAll("button,input,select,textarea")].filter(x => !x.disabled && x.offsetParent !== null);
    if(!f.length) return;
    const i = f.indexOf(document.activeElement);
    if(e.shiftKey && i <= 0){ f[f.length - 1].focus(); e.preventDefault(); }
    else if(!e.shiftKey && i === f.length - 1){ f[0].focus(); e.preventDefault(); }
  });
}
