/* Le Cahier — répétition espacée (SM-2 adapté)
   État par carte : [échéance (jour), intervalle (jours), facilité ×10, réussites, oublis] */

const DAY_MS = 864e5;
const SRS_CAP = 90;      // plafond de révisions par séance
const SRS_RELEARN = 5;   // une carte ratée revient après N cartes
const COMEBACK_CAP = 20; // après trois jours d'absence, on reprend par vingt
const LEECH_LAPS = 6;    // ratée six fois : la carte est une sangsue
const LEECH_DAY = 9e6;   // « échéance » d'une carte suspendue : jamais
const SRS_FUZZ = .08;    // ±8 % sur les intervalles ≥ 3 j : les échéances s'étalent

function dayNum(d){
  d = d || new Date();
  return Math.round(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()) / DAY_MS);
}
/* « 2026-11-12 » → numéro de jour local, sans passer par Date.parse (qui lirait UTC). */
function dayOfStr(s){
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(s || ""));
  return m ? dayNum(new Date(+m[1], +m[2] - 1, +m[3])) : null;
}

let REG = null;
const srsReset = () => { REG = null; if(typeof MOTSET !== "undefined") MOTSET = null; };

function registry(){
  if(REG) return REG;
  REG = [];
  const cloze = ALL();
  cloze.forEach(i => REG.push({id:i.id, kind:"trou"}));
  cloze.forEach(i => REG.push({id:"s" + i.id, kind:"dictee"}));
  cloze.forEach(i => { if(i.g) REG.push({id:"x" + i.id, kind:"trad"}); });
  GENRE.forEach((g, n) => REG.push({id:"g" + n, kind:"genre"}));
  POOL.forEach((f, n) => REG.push({id:"k" + n, kind:"conj"}));
  PAIRS.forEach((p, n) => REG.push({id:"m" + n, kind:"son"}));
  (S.mots || []).forEach(m => motCards(m).forEach(id => REG.push({id, kind:"mot"})));
  /* La phrase entière à remettre en ordre : ni trop courte (rien à ordonner),
     ni trop longue (du bricolage). Même règle que le panneau L'Ordre. */
  cloze.forEach(i => {
    if(!i.s || !i.a) return;
    const n = i.s.replace("___", i.a).trim().split(/\s+/).length;
    if(n >= 4 && n <= 14) REG.push({id:"o" + i.id, kind:"ordre"});
  });
  /* La même phrase, à imiter à voix haute. */
  cloze.forEach(i => { if(i.s && i.a) REG.push({id:"i" + i.id, kind:"imiter"}); });
  if(typeof DECIDE !== "undefined") DECIDE.forEach((d, n) => REG.push({id:"y" + n, kind:"decider"}));
  return REG;
}

function srsItem(id){
  if(id[0] === "m") { const p = sonItem(id); return p ? {kind:"son", data:p} : null; }
  if(id[0] === "w") { const m = motById(id); return m ? {kind:"mot", data:m, t:id[1]} : null; }
  if(id[0] === "g") return {kind:"genre", data:GENRE[+id.slice(1)]};
  if(id[0] === "k") return {kind:"conj", data:POOL[+id.slice(1)]};
  if(id[0] === "s"){
    const c = ALL().find(i => i.id === id.slice(1));
    return c ? {kind:"dictee", data:c} : null;
  }
  if(id[0] === "x"){
    const c = ALL().find(i => i.id === id.slice(1));
    return c ? {kind:"trad", data:c} : null;
  }
  if(id[0] === "o"){
    const c = ALL().find(i => i.id === id.slice(1));
    return c ? {kind:"ordre", data:c} : null;
  }
  if(id[0] === "i"){
    const c = ALL().find(i => i.id === id.slice(1));
    return c ? {kind:"imiter", data:c} : null;
  }
  if(id[0] === "y"){
    const d = (typeof DECIDE !== "undefined") ? DECIDE[+id.slice(1)] : null;
    return d ? {kind:"decider", data:d} : null;
  }
  const c = ALL().find(i => i.id === id);
  return c ? {kind:"trou", data:c} : null;
}

/* Intervalles : 1 jour, 3 jours, puis × la facilité de la carte.
   Un échec remet l'intervalle à zéro et rabote la facilité — le temps
   entre deux rappels suit ce que la carte montre, pas un calendrier fixe. */
/* Calcul pur : l'état d'avant et la note donnent l'état d'après.
   Sert aussi à afficher, sous chaque bouton, quand la carte reviendrait. */
function srsNext(prev, q){
  prev = prev || [0, 0, 25, 0, 0, 0, 0];
  let [, iv, e10, n, lap] = prev;
  let e = e10 / 10;
  if(q < 3){
    e = Math.max(1.3, e - 0.2);
    n = 0; iv = 0; lap++;
  }else{
    e = Math.max(1.3, Math.min(3.2, e + (0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))));
    n++;
    iv = n === 1 ? 1 : n === 2 ? 3 : Math.min(365, Math.round(iv * e));
  }
  return {iv, e, n, lap};
}
const srsPreview = (id, q) => srsNext(S.P.srs[id], q).iv;

/* L'échéance réelle reçoit un peu de hasard : deux cartes apprises le même
   jour ne reviennent plus forcément le même jour, et le mur des « 90 à revoir »
   ne se forme plus. L'intervalle gardé, lui, reste exact pour le calcul suivant. */
function fuzzDays(iv){
  if(iv < 3) return iv;
  const f = 1 + (Math.random() * 2 - 1) * SRS_FUZZ;
  return Math.max(3, Math.round(iv * f));
}

function kindOfId(id){
  const it = srsItem(id);
  return it ? it.kind : "autre";
}

function srsUpdate(id, q){
  const isNew = !S.P.srs[id];
  const t = srsDay();
  if(isNew) S.P.day.fresh++;
  const prev = S.P.srs[id] || [0, 0, 25, 0, 0, 0, 0];
  const tries = (prev[5] || 0) + 1, hits = (prev[6] || 0) + (q >= 3 ? 1 : 0);
  const {iv, e, n, lap} = srsNext(prev, q);
  /* Une sangsue : ratée pour la sixième fois, elle dort au lieu de revenir
     demain pour la septième. Elle repasse une dernière fois dans cette séance ;
     réussie, elle reprend sa place ; ratée encore, c'est Le Profil qui la réveille. */
  const leech = q < 3 && lap >= LEECH_LAPS && (prev[4] || 0) >= LEECH_LAPS - 1 && prev[0] !== t;
  const due = leech ? LEECH_DAY : (q < 3 ? t : t + fuzzDays(iv));
  S.P.srs[id] = [due, iv, Math.round(e * 10), n, lap, tries, hits];

  S.P.recall.rev++;
  if(q >= 3) S.P.recall.ok++;
  /* Le journal : par jour et par type, ce qui a été rappelé et ce qui a tenu.
     C'est lui qui dit si la rétention des trente derniers jours tient la cible. */
  S.P.hist = S.P.hist || {};
  const day = S.P.hist[t] = S.P.hist[t] || {};
  const k = kindOfId(id);
  const row = day[k] = day[k] || [0, 0];
  row[0]++;
  if(q >= 3) row[1]++;

  if(typeof xpGain === "function"){
    xpGain(xpForRecall(q, iv), "recalls");
    if(q >= 4) heroDay().clean++;
  }
  return iv;
}

const isLeech = (id) => { const s = S.P.srs[id]; return !!s && s[0] === LEECH_DAY; };

function leechList(){
  return registry().filter(it => isLeech(it.id)).map(it => it.id);
}

function leechResume(id){
  const s = S.P.srs[id];
  if(!s) return;
  s[0] = srsDay();
  s[1] = 0; s[3] = 0;
}

/* Rétention récente, pour un type ou pour tout : sur trente jours glissants,
   la part des rappels qui ont tenu. Cible 85–90 %. */
function retention30(kind){
  const t = dayNum(), h = S.P.hist || {};
  let rev = 0, ok = 0;
  Object.keys(h).forEach(d => {
    if(t - (+d) >= 30 || t - (+d) < 0) return;
    const day = h[d];
    Object.keys(day).forEach(k => {
      if(kind && k !== kind) return;
      rev += day[k][0] || 0; ok += day[k][1] || 0;
    });
  });
  return {rev, ok, acc:rev ? ok / rev : null};
}

/* Note dérivée du rappel : une réponse produite de mémoire et sans aide
   vaut plus qu'une réponse reconnue parmi des propositions. La fenêtre du
   « facile » suit la longueur de ce qu'il fallait produire : un mot en cinq
   secondes, une phrase de soixante signes en douze. */
function srsGrade(ok, ms, helped, len){
  if(!ok) return 1;
  if(helped) return 3;
  const win = 5000 + 110 * (len || 0);
  return ms > 0 && ms < win ? 5 : 4;
}

function srsDay(){
  const t = dayNum();
  if(S.P.day.n !== t){ S.P.day.n = t; S.P.day.fresh = 0; }
  return t;
}

function srsStats(){
  const t = srsDay();
  const reg = registry();
  let due = 0, learned = 0;
  reg.forEach(it => {
    const s = S.P.srs[it.id];
    if(!s) return;
    learned++;
    if(s[0] <= t) due++;
  });
  const r = S.P.recall;
  const cb = comebackInfo();
  return {
    due:Math.min(due, cb ? COMEBACK_CAP : SRS_CAP), dueAll:due, learned, total:reg.length,
    fresh:Math.max(0, newPerDay() - S.P.day.fresh),
    retention:r.rev ? Math.round(r.ok / r.rev * 100) : null,
    comeback:cb
  };
}

/* Trois jours sans ouvrir le cahier : on ne rend pas quatre-vingt-dix cartes,
   on en rend vingt. Les autres ne sont pas perdues — elles suivent demain.
   Le plafond tient toute la journée de la reprise, même après la première carte. */
function comebackInfo(){
  const t = dayNum();
  if(S.P.comebackDay === t) return {away:S.P.comebackAway || 3};
  const last = dayOfStr(S.P.last);
  if(last == null || !S.P.days) return null;
  const away = t - last;
  if(away < 3) return null;
  S.P.comebackDay = t;
  S.P.comebackAway = away;
  return {away};
}

/* Demain, après-demain… combien de cartes reviennent */
function srsForecast(days){
  const t = dayNum(), out = new Array(days).fill(0);
  registry().forEach(it => {
    const s = S.P.srs[it.id];
    if(!s) return;
    const k = s[0] - t;
    if(k >= 1 && k <= days) out[k - 1]++;
  });
  return out;
}

function shuffleIds(a){
  const r = a.slice();
  for(let i = r.length - 1; i > 0; i--){ const j = (Math.random() * (i + 1)) | 0; [r[i], r[j]] = [r[j], r[i]]; }
  return r;
}

/* Les cartes neuves arrivent en alternant les types, jamais par paquets.
   Les mots de ton paquet suivent leurs propres règles, façon Fluent Forever :
   - un mot neuf entre par sa fiche de reconnaissance (on le voit, on l'entend,
     on retourne la fiche) ; ses autres cartes attendent qu'il ait été vu ;
   - jamais deux cartes neuves du même mot dans la même séance ;
   - tu l'as mis dans ton paquet, donc le niveau ne le bloque pas ;
   - tes cartes faites main passent avant le socle. */
function pickFresh(limit, only){
  const byKind = {};
  registry().forEach(it => {
    if(S.P.srs[it.id]) return;
    if(only && it.kind !== only) return;
    if(it.kind === "mot"){
      if(it.id[1] !== "r" && !S.P.srs["wr_" + it.id.slice(3)]) return;
    }else{
      const l = levelOf(it.id);
      if(l > S.P.level || l < S.P.level - 1) return;
    }
    (byKind[it.kind] = byKind[it.kind] || []).push(it.id);
  });
  /* Un type qui flanche ne reçoit pas plus de cartes neuves — il en reçoit
     moins. Sous 80 % de rétention sur trente jours il passe en dernier ;
     sous 70 %, rien de neuf aujourd'hui : les cartes dues suffisent à le
     travailler. (Revoir seulement ton paquet passe outre : tu l'as demandé.) */
  const ret = {};
  Object.keys(byKind).forEach(k => { ret[k] = retention30(k); });
  const shaky = (k) => ret[k].rev >= 10 && ret[k].acc < .80;
  const held = (k) => ret[k].rev >= 10 && ret[k].acc < .70 && only !== k;
  S.intakeHeld = Object.keys(byKind).filter(held);
  const kinds = Object.keys(byKind).filter(k => !held(k))
    .sort((a, b) => (shaky(a) ? 1 : 0) - (shaky(b) ? 1 : 0));
  kinds.forEach(k => byKind[k] = shuffleIds(byKind[k]));
  /* Les phrases de l'histoire d'abord : on vient de les lire en contexte, c'est le
     meilleur moment pour les mettre en mémoire. Le tri est stable : le reste garde son désordre. */
  const rcFirst = (id) => /^[sxoi]?r\d\d[a-h]$/.test(id) ? 0 : 1;
  kinds.forEach(k => { if(k !== "mot") byKind[k].sort((a, b) => rcFirst(a) - rcFirst(b)); });
  if(byKind.mot){
    const own = (id) => { const m = motById(id); return m && m.from !== "socle" ? 0 : 1; };
    byKind.mot.sort((a, b) => own(a) - own(b));
  }
  const words = {};
  const take = (k) => {
    const list = byKind[k];
    if(k !== "mot") return list.shift();
    const j = list.findIndex(id => !words[id.slice(3)]);
    if(j < 0){ list.length = 0; return null; }
    const id = list.splice(j, 1)[0];
    words[id.slice(3)] = 1;
    return id;
  };
  const out = [];
  let i = 0;
  while(out.length < limit && kinds.some(k => byKind[k].length)){
    const k = kinds[i++ % kinds.length];
    if(byKind[k].length){ const id = take(k); if(id) out.push(id); }
  }
  return out;
}

/* Entrelacement : deux cartes du même type ne se suivent pas si on peut l'éviter.
   Alterner les types coûte plus d'effort sur le moment et retient mieux ensuite. */
function interleave(ids){
  const kindOf = {};
  registry().forEach(it => kindOf[it.id] = it.kind);
  const pool = shuffleIds(ids), out = [];
  while(pool.length){
    let k = pool.findIndex(id => !out.length || kindOf[id] !== kindOf[out[out.length - 1]]);
    if(k < 0) k = 0;
    out.push(pool.splice(k, 1)[0]);
  }
  return out;
}

function srsQueue(only){
  const t = srsDay();
  const due = registry().filter(it => {
    if(only && it.kind !== only) return false;
    const s = S.P.srs[it.id];
    return s && s[0] <= t;
  }).map(it => it.id);
  const cb = only ? null : comebackInfo();
  const cap = cb ? COMEBACK_CAP : SRS_CAP;
  const sorted = due.sort((a, b) => S.P.srs[a][0] - S.P.srs[b][0]).slice(0, cap);
  /* Jour de reprise : les cartes dues d'abord, une seule neuve au plus. */
  const want = Math.max(0, newPerDay() - S.P.day.fresh);
  const fresh = pickFresh(cb ? Math.min(1, want) : want, only);
  return {queue:interleave(sorted.concat(fresh)), due:sorted.length, fresh:fresh.length,
    left:Math.max(0, due.length - sorted.length), comeback:cb};
}
