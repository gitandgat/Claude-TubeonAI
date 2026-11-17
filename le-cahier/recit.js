/* Le Cahier — le récit : apprendre en suivant une histoire.

   La boucle tient en quatre temps :
     1. tu fais tes cartes (cinq rappels suffisent) — la page du jour se descelle ;
     2. tu lis la scène, tu réponds en français à un choix, tu écoutes ;
     3. trois phrases de la page entrent dans le planning de révision ;
     4. demain, ces phrases reviennent en séance — et la page suivante attend.
   L'histoire ne remplace aucun exercice : elle donne un contexte aux mots, et
   c'est la mémoire (les rappels) qui fait avancer l'intrigue.

   Les données de l'histoire vivent dans recit-data.js (CAST, RECIT). */

const RC_NEED = 5;            /* rappels du jour qui descellent la page */
const RC_XP_PAGE = 25;
const RC_VOICE_KEY = "le-cahier-recit-voice";
const RC_RATE = .95;          /* la voix enregistrée est déjà posée : à peine plus lente */
const ROMAN = ["", "I", "II", "III", "IV", "V", "VI"];

let RC = null;                /* le lecteur ouvert : {page, i, beats, waiting, …} */
let RC_LAST_STATE = null;
let RC_READY = false;

const rcEn = () => typeof rpgEn === "function" ? rpgEn() : false;

function rcEl(tag, cls, text){
  const e = document.createElement(tag);
  if(cls) e.className = cls;
  if(text != null) e.textContent = text;
  return e;
}
/* Tout ce qui est du français de l'histoire porte lang="fr" : l'interface
   ne le traduit jamais, et le toucher-un-mot (tap.js) le lit tel quel. */
function rcFr(tag, cls, text){
  const e = rcEl(tag, cls, text);
  e.lang = "fr";
  return e;
}

function rcName(en){
  const n = (S.P.hero && S.P.hero.name || "").trim();
  return n || (en ? "traveller" : "voyageur");
}
const rcSub = (s, en) => String(s || "").replace(/\{nom\}/g, rcName(en));

/* Ce qui est dit à voix haute : la réplique sans le prénom. Un enregistrement ne peut pas
   contenir le nom de chacun : « Tu vois, {nom} ? » est enregistré « Tu vois ? ». Cette
   fonction sert aussi au moteur qui fabrique les voix (engine/recit_textes.cjs) : la clé
   dStrip() doit être la même des deux côtés. */
function rcSpoken(s){
  let t = String(s || "");
  const lead = /^\{nom\}\s*,\s*/.test(t);
  t = t.replace(/\s*,\s*\{nom\}(?=\s*[,.?!…:;])/g, "")
    .replace(/\{nom\}\s*,\s*/g, "")
    .replace(/\s*\{nom\}\s*/g, " ")
    .replace(/\s{2,}/g, " ").trim();
  return lead ? t.charAt(0).toUpperCase() + t.slice(1) : t;
}

/* ---------- l'état : ce qui est lu, ce qui est ouvert ---------- */
function recitRead(){
  const r = S.P.recit;
  return (r && r.read && typeof r.read === "object") ? r.read : {};
}
const recitPage = (id) => RECIT.pages.find(p => p.id === id) || null;
const recitNext = () => { const r = recitRead(); return RECIT.pages.find(p => !r[p.id]) || null; };
const recitChapter = (n) => RECIT.chapitres.find(c => c.n === n) || null;
const recitAct = (n) => RECIT.actes.find(a => a.n === n) || null;

function recitReadToday(){
  const r = recitRead(), t = dayNum();
  const ids = Object.keys(r).filter(id => r[id] === t);
  /* la plus avancée des pages lues aujourd'hui */
  let best = null;
  RECIT.pages.forEach(p => { if(ids.indexOf(p.id) >= 0) best = p; });
  return best;
}

/* open · sealed · wait · end. La première page est offerte ; les suivantes se
   méritent par cinq rappels, une par jour — l'attente fait partie du récit. */
function recitState(){
  const next = recitNext();
  if(!next) return {k:"end"};
  const r = recitRead();
  if(!Object.keys(r).length) return {k:"open", next, first:true};
  const today = recitReadToday();
  if(today) return {k:"wait", next, today};
  const done = (typeof heroDay === "function" ? heroDay().recalls : 0) || 0;
  const st = srsStats();
  const have = (st.due || 0) + (st.fresh || 0);
  const left = Math.max(0, RC_NEED - done);
  if(left === 0 || have === 0) return {k:"open", next};
  return {k:"sealed", next, left:Math.min(left, have)};
}

function recitPrev(page){
  const i = RECIT.pages.indexOf(page);
  return i > 0 ? RECIT.pages[i - 1] : null;
}

/* ---------- les cartes : seules les pages lues entrent dans le planning ---------- */
const RECIT_ALL = [];
RECIT.pages.forEach(p => {
  (p.cards || []).forEach((c, k) => {
    RECIT_ALL.push({id:"r" + p.id.slice(1) + "abcdefgh"[k], s:c.s, a:c.a, d:c.d, g:c.g,
      lv:c.lv || p.lv || 2, page:p.id, src:"recit"});
  });
});

let RC_CARDS_SRC = null, RC_CARDS_N = -1, RC_CARDS = [];
function recitCards(){
  const read = recitRead(), n = Object.keys(read).length;
  if(read !== RC_CARDS_SRC || n !== RC_CARDS_N){
    RC_CARDS_SRC = read; RC_CARDS_N = n;
    RC_CARDS = RECIT_ALL.filter(c => read[c.page]);
  }
  return RC_CARDS;
}

/* Combien de mots de l'histoire ont tenu : la carte à trous a franchi 3 jours. */
function recitSaved(){
  const cards = recitCards();
  const saved = cards.filter(c => { const s = S.P.srs[c.id]; return s && s[1] >= 3 && s[0] !== LEECH_DAY; }).length;
  return {saved, total:cards.length};
}

/* ---------- progression, pour les hauts faits ---------- */
const recitPagesRead = () => Object.keys(recitRead()).filter(id => recitPage(id)).length;
function recitChapterDone(n){
  const r = recitRead(), ps = RECIT.pages.filter(p => p.ch === n);
  return ps.length > 0 && ps.every(p => r[p.id]);
}
/* Le prologue n'est pas un chapitre : on ne fête pas une seule page. */
const recitChaptersDone = () => RECIT.chapitres.filter(c => c.n > 0 && recitChapterDone(c.n)).length;
function recitActDone(n){
  return RECIT.chapitres.filter(c => c.acte === n).every(c => recitChapterDone(c.n));
}
const recitActsDone = () => RECIT.actes.filter(a => recitActDone(a.n)).length;

/* ---------- ce que le feuilleton des Chroniques doit savoir ---------- */
function recitBible(){
  const r = recitRead();
  const done = RECIT.pages.filter(p => r[p.id]);
  if(!done.length) return "";
  const b = RECIT.bible;
  return "Univers (à respecter, c'est la suite d'une histoire déjà commencée) : " + b.world + "\n"
    + "Personnages : " + b.cast + "\n"
    + "Le héros, qui est le lecteur, s'appelle " + (rcName(false) === "voyageur" ? "« le voyageur » (sans nom)" : rcName(false)) + ".\n"
    + "Ce qui s'est déjà passé : " + done.map(p => rcSub(p.resume, false)).join(" ") + "\n"
    + (recitNext() ? "" : b.next + "\n");
}

/* ---------- la carte de la page du jour (Quêtes) ---------- */
function recitChapterLabel(ch, en){
  if(!ch) return "";
  return (ch.n === 0 ? (en ? "Prologue" : "Prologue") : (en ? "Chapter " : "Chapitre ") + ch.n) + " · " + (en ? ch.en : ch.fr);
}

function recitPips(page){
  const r = recitRead(), nxt = recitNext(), box = rcEl("div", "rc-pips");
  box.setAttribute("role", "img");
  const n = recitPagesRead();
  box.setAttribute("aria-label", rcEn() ? n + " of " + RECIT.pages.length + " pages read"
    : n + " pages lues sur " + RECIT.pages.length);
  RECIT.pages.forEach((p, i) => {
    const pip = rcEl("span", "rc-pip" + (r[p.id] ? " on" : "") + (nxt && nxt.id === p.id ? " now" : "")
      + (i > 0 && RECIT.pages[i - 1].ch !== p.ch ? " gap" : ""));
    pip.title = rcEn() ? p.titreEn : p.titre;
    box.appendChild(pip);
  });
  return box;
}

function recitPaintCard(){
  const host = $("jStory");
  if(!host) return;
  const en = rcEn(), st = recitState();
  host.innerHTML = "";
  host.dataset.state = st.k;
  /* La page du jour va être lue : sa piste se charge pendant qu'on regarde la carte. */
  if(st.k === "open" && st.next) recitPreload(st.next);

  const page = st.next || RECIT.pages[RECIT.pages.length - 1];
  const act = recitAct(recitChapter(page.ch).acte);
  const romanAct = ROMAN[act.n] || String(act.n);

  const head = rcEl("div", "rc-head");
  const ic = rcEl("span", "rc-ic");
  ic.innerHTML = '<svg class="ti" viewBox="0 0 24 24" aria-hidden="true"><use href="#'
    + (st.k === "sealed" ? "i-cadenas" : "i-chroniques") + '"/></svg>';
  const kick = rcEl("p", "rc-kicker", (en ? "The Story · Act " : "Le Récit · Acte ") + romanAct + " — " + (en ? act.en : act.fr));
  head.append(ic, kick);
  host.appendChild(head);

  const title = rcEl("h3", "rc-title", recitChapterLabel(recitChapter(page.ch), en));
  title.id = "jStoryT";
  host.appendChild(title);

  const body = rcEl("div", "rc-body");
  let teaser = null, action = null;

  if(st.k === "open"){
    body.appendChild(rcEl("p", "rc-lead", st.first
      ? (en ? "The story begins. One page a day — your cards open the next." : "L'histoire commence. Une page par jour : tes cartes ouvrent la suivante.")
      : (en ? "Today's page is open: " : "La page du jour est ouverte : ") + (en ? page.titreEn : page.titre) + "."));
    const prev = recitPrev(page);
    teaser = prev || null;
    action = {label:st.first ? (en ? "Step into the story" : "Entrer dans l'histoire") : (en ? "Read today's page" : "Lire la page du jour"),
      go:() => recitOpen(page.id, false), primary:true};
  }else if(st.k === "sealed"){
    body.appendChild(rcEl("p", "rc-lead", en ? "Today's page is sealed." : "La page du jour est scellée."));
    body.appendChild(rcEl("p", "rc-sub", en
      ? st.left + " more card" + (st.left > 1 ? "s" : "") + " in Battle to break the seal."
      : "Encore " + st.left + " carte" + (st.left > 1 ? "s" : "") + " en Séance pour briser le sceau."));
    teaser = recitPrev(page);
    action = {label:en ? "Break the seal" : "Briser le sceau", go:() => setMode("seance"), primary:true};
  }else if(st.k === "wait"){
    body.appendChild(rcEl("p", "rc-lead", en ? "Page read. More tomorrow." : "Page lue. La suite demain."));
    teaser = st.today;
    action = {label:en ? "Read it again" : "Relire la page", go:() => recitOpen(st.today.id, true), primary:false};
  }else{
    const a = RECIT.actes[RECIT.actes.length - 1];
    body.appendChild(rcEl("p", "rc-lead", en ? "You have read everything, for now." : "Tu as tout lu, pour l'instant."));
    body.appendChild(rcFr("p", "rc-hook nt", a.fin));
    if(en) body.appendChild(rcEl("p", "rc-en", a.finEn));
    action = {label:en ? "The Chronicles go on" : "Les Chroniques continuent", go:() => setMode("histoire"), primary:true};
  }

  if(teaser){
    const t = rcEl("div", "rc-tease");
    t.appendChild(rcEl("span", "rc-tlab", en ? "Next:" : "À suivre :"));
    t.appendChild(rcFr("span", "rc-hook nt", rcSub(teaser.hook, false)));
    if(en) t.appendChild(rcEl("span", "rc-en", rcSub(teaser.hookEn, true)));
    body.appendChild(t);
  }
  host.appendChild(body);

  const foot = rcEl("div", "rc-foot");
  foot.appendChild(recitPips(page));
  const sv = recitSaved();
  if(sv.total) foot.appendChild(rcEl("span", "rc-saved", sv.saved + " / " + sv.total
    + (en ? " words saved from the Mist" : " mots sauvés de la Brume")));
  if(action){
    const b = rcEl("button", action.primary ? "go" : "ghost", action.label);
    b.type = "button";
    b.addEventListener("click", action.go);
    foot.appendChild(b);
  }
  host.appendChild(foot);
}

/* La puce du HUD : la quête en cours, visible sur tous les onglets. */
function recitPaintHud(){
  const b = $("hudQuest");
  if(!b) return;
  const en = rcEn(), st = recitState();
  let k = en ? "Story" : "Récit", t = "", go = null;
  if(st.k === "open"){
    t = (st.first ? (en ? "Begin the story" : "Commencer l'histoire")
      : (en ? "Today's page is open" : "La page du jour est ouverte")) + " ▸";
    go = () => recitOpen(st.next.id, false);
  }else if(st.k === "sealed"){
    t = en ? "Page sealed · " + st.left + " more card" + (st.left > 1 ? "s" : "")
      : "Page scellée · encore " + st.left + " carte" + (st.left > 1 ? "s" : "");
    go = () => setMode("seance");
  }else if(st.k === "wait"){
    t = en ? "Page read · more tomorrow" : "Page lue · la suite demain";
    go = () => setMode("jour");
  }else{
    t = en ? "The Chronicles go on" : "Les Chroniques continuent";
    go = () => setMode("histoire");
  }
  b.hidden = false;
  b.dataset.state = st.k;
  $("hudQuestK").textContent = k;
  $("hudQuestT").textContent = t;
  b.onclick = go;
}

/* Appelé à chaque repeinture de la marge : la carte, le guide, le lecteur. */
function recitRefresh(){
  if(typeof S === "undefined" || !S.P || !S.P.recit) return;
  const st = recitState();
  if(RC_LAST_STATE === "sealed" && st.k === "open" && typeof toast === "function"){
    const en = rcEn();
    toast(en ? "Page unlocked" : "Page déverrouillée",
      en ? "Today's page is waiting in Quests." : "La page du jour t'attend dans Quêtes.", "i-chroniques");
  }
  RC_LAST_STATE = st.k;
  recitPaintHud();
  const jour = $("panel-jour");
  if(jour && !jour.hidden){
    recitPaintCard();
    if(typeof paintGuide === "function") paintGuide();
  }
  rcRelabel();
}

/* ---------- le lecteur : une scène qui se dévoile ligne après ligne ---------- */
const rcVoiceOn = () => { try{ return localStorage.getItem(RC_VOICE_KEY) !== "0"; }catch(e){ return true; } };

/* Toujours la réplique d'origine (avec {nom}) : rcSpoken() en fait le texte enregistré.
   speakFr() joue l'enregistrement s'il existe, sinon la synthèse. */
function rcSpeak(raw){
  if(!RC || !RC.voice || typeof speakFr !== "function") return;
  speakFr(rcSpoken(raw), RC_RATE);
}

/* Charge la piste de la page à l'avance : la première réplique part sans attendre. */
function recitPreload(page){
  if(typeof vrPrepare !== "function" || typeof VOIX_REC === "undefined" || typeof dStrip !== "function") return;
  const first = page.lines.find(l => l.w !== "?");
  const seg = first && VOIX_REC[dStrip(rcSpoken(first.fr))];
  if(seg && typeof seg[2] === "string") vrPrepare(seg[2]);
}
function rcHush(){
  try{ if("speechSynthesis" in window) speechSynthesis.cancel(); }catch(e){}
  if(typeof vrHalt === "function") vrHalt();
}

function rcScroll(){
  const log = $("rcLog");
  if(!log) return;
  const calm = typeof matchMedia === "function" && matchMedia("(prefers-reduced-motion: reduce)").matches;
  if(log.scrollTo) log.scrollTo({top:log.scrollHeight, behavior:calm ? "auto" : "smooth"});
  else log.scrollTop = log.scrollHeight;
}

function rcWho(b){
  if(b.hero){
    return {name:rcName(false), face:(S.P.hero && S.P.hero.avatar) || "🦊", cls:"who-H"};
  }
  const c = CAST[b.w] || CAST.N;
  return {name:c.name, face:c.face, cls:"who-" + b.w};
}

function rcLine(b, silent){
  const log = $("rcLog"), en = rcEn();
  const raw = b.fr, fr = rcSub(raw, false), gloss = rcSub(b.en, true);
  let row;
  if(b.w === "N"){
    row = rcEl("div", "rc-row rc-n");
    row.append(rcFr("p", "rc-fr nt", fr), rcEl("p", "rc-en", gloss));
  }else{
    const who = rcWho(b);
    row = rcEl("div", "rc-row rc-s " + who.cls);
    const face = rcEl("span", "rc-face", who.face);
    face.setAttribute("aria-hidden", "true");
    const bub = rcEl("div", "rc-b");
    bub.appendChild(rcEl("b", "rc-nm", who.name));
    bub.append(rcFr("p", "rc-fr nt", fr), rcEl("p", "rc-en", gloss));
    const say = rcEl("button", "rc-say", "🔊");
    say.type = "button";
    say.setAttribute("aria-label", en ? "Listen to this line" : "Écouter cette réplique");
    say.addEventListener("click", () => { const v = RC && RC.voice; if(RC) RC.voice = true; rcSpeak(raw); if(RC) RC.voice = v; });
    row.append(face, bub, say);
  }
  log.appendChild(row);
  rcScroll();
  if(!silent) rcSpeak(raw);
  return row;
}

function rcShuffle(a){
  const r = a.slice();
  for(let i = r.length - 1; i > 0; i--){ const j = (Math.random() * (i + 1)) | 0; [r[i], r[j]] = [r[j], r[i]]; }
  return r;
}

function rcChoice(b){
  const en = rcEn(), log = $("rcLog");
  RC.waiting = true;
  RC.tries = 0;
  const free = b.c.every(o => o[2]);
  const box = rcEl("div", "rc-row rc-choice");
  box.setAttribute("role", "group");
  const q = free ? (en ? "Choose your reply" : "Choisis ta réplique") : (en ? "What do you say?" : "Que réponds-tu ?");
  box.setAttribute("aria-label", q);
  box.appendChild(rcEl("p", "rc-q", q));

  rcShuffle(b.c.map((o, i) => i)).forEach((idx, k) => {
    const o = b.c[idx];
    const btn = rcEl("button", "rc-opt");
    btn.type = "button";
    btn.dataset.key = String(k + 1);
    btn.append(rcEl("span", "rc-key", String(k + 1)), rcFr("span", "rc-optfr", o[0]));
    btn.addEventListener("click", () => {
      RC.tries++;
      if(!o[2]){
        btn.classList.add("wrong");
        btn.disabled = true;
        const f = rcEl("p", "rc-miss", (en ? "That means: “" : "Ça veut dire : « ") + o[1] + (en ? "”. Not quite — try again." : " ». Pas tout à fait — réessaie."));
        f.setAttribute("role", "status");
        box.appendChild(f);
        rcScroll();
        return;
      }
      const first = RC.tries === 1;
      if(!free){
        RC.score.push(first ? 1 : 0);
        if(!RC.replay) xpGain(first ? 10 : 3, null);
      }
      box.remove();
      rcLine({w:"H", hero:true, fr:o[0], en:o[1]});
      RC.waiting = false;
      rcSetNext();
      $("rcNext").focus();
    });
    box.appendChild(btn);
  });
  log.appendChild(box);
  rcScroll();
  const firstBtn = box.querySelector(".rc-opt");
  if(firstBtn) firstBtn.focus();
  rcSetNext();
}

function rcSetNext(){
  const nb = $("rcNext");
  if(!nb || !RC) return;
  const en = rcEn();
  $("rcProg").style.width = Math.round((RC.done ? 1 : Math.min(1, RC.i / RC.beats.length)) * 100) + "%";
  nb.disabled = false;
  if(RC.done){ nb.textContent = en ? "Close" : "Fermer"; nb.dataset.act = "close"; }
  else if(RC.waiting){ nb.disabled = true; nb.textContent = en ? "Choose your reply" : "Choisis ta réplique"; nb.dataset.act = ""; }
  else if(RC.i >= RC.beats.length){ nb.textContent = en ? "Finish the page ✓" : "Terminer la page ✓"; nb.dataset.act = "finish"; }
  else{ nb.textContent = en ? "Next ▸" : "Suivant ▸"; nb.dataset.act = "next"; }
}

/* Les libellés suivent la langue de l'interface, même fenêtre ouverte. */
function rcRelabel(){
  const m = $("mdPage");
  if(!m || m.hidden || !RC) return;
  const en = rcEn(), p = RC.page, ch = recitChapter(p.ch), act = recitAct(ch.acte);
  $("rcK").textContent = (en ? "Act " : "Acte ") + (ROMAN[act.n] || act.n) + " · " + recitChapterLabel(ch, en);
  $("rcSub").textContent = en ? p.titreEn : "";
  $("rcSub").hidden = !en;
  $("rcPlaceEn").textContent = en ? p.lieuEn : "";
  $("rcPlaceEn").hidden = !en;
  $("rcClose").setAttribute("aria-label", en ? "Close the page" : "Fermer la page");
  $("rcVoice").title = en ? "Read aloud" : "Lecture à voix haute";
  $("rcVoice").setAttribute("aria-label", $("rcVoice").title);
  $("rcTr").title = en ? "Show the English translation" : "Afficher la traduction anglaise";
  $("rcTr").setAttribute("aria-label", $("rcTr").title);
  rcSetNext();
}

function rcAdvance(){
  if(!RC || RC.waiting || RC.done) return;
  if(RC.i >= RC.beats.length){ rcFinish(); return; }
  const b = RC.beats[RC.i++];
  if(b.w === "?") rcChoice(b);
  else rcLine(b);
  rcSetNext();
}

function rcNextClick(){
  if(!RC) return;
  if(RC.done){ recitClose(); return; }
  rcAdvance();
}

function rcFinish(){
  if(!RC || RC.done) return;
  RC.done = true;
  rcHush();
  const en = rcEn(), p = RC.page, log = $("rcLog");
  const box = rcEl("div", "rc-row rc-end");
  const isNew = !RC.replay;
  let chapterWon = null, actWon = null;

  if(isNew){
    const wasCh = recitChapterDone(p.ch), wasAct = recitActDone(recitChapter(p.ch).acte);
    S.P.recit.read[p.id] = dayNum();
    S.P.recit.acc[p.id] = [RC.score.filter(Boolean).length, RC.score.length];
    srsReset();                       /* les trois phrases entrent dans le registre */
    xpGain(RC_XP_PAGE, null);
    scored(true);                     /* lire la page compte pour la série */
    save();
    if(!wasCh && p.ch > 0 && recitChapterDone(p.ch)) chapterWon = recitChapter(p.ch);
    if(!wasAct && recitActDone(recitChapter(p.ch).acte)) actWon = recitAct(recitChapter(p.ch).acte);
  }

  box.appendChild(rcEl("p", "rc-endk", en ? "End of the page" : "Fin de la page"));

  if(isNew && RC.score.length){
    const ok = RC.score.filter(Boolean).length;
    box.appendChild(rcEl("p", "rc-endl", (en ? "Comprehension: " : "Compréhension : ") + ok + "/" + RC.score.length
      + (en ? " first try" : " du premier coup")));
  }

  const cards = RECIT_ALL.filter(c => c.page === p.id);
  if(cards.length){
    box.appendChild(rcEl("p", "rc-endh", isNew
      ? (en ? "Three sentences join your notebook" : "Trois phrases entrent dans ton cahier")
      : (en ? "The sentences of this page" : "Les phrases de cette page")));
    const ul = rcEl("ul", "rc-cards");
    cards.forEach(c => {
      const li = rcEl("li");
      const full = c.s.replace("___", c.a);
      const fr = rcFr("span", "rc-cfr nt");
      const i = c.s.indexOf("___");
      fr.append(document.createTextNode(c.s.slice(0, i)), rcEl("mark", "", c.a), document.createTextNode(c.s.slice(i + 3)));
      const hear = rcEl("button", "rc-say rc-say-c", "🔊");
      hear.type = "button";
      hear.setAttribute("aria-label", en ? "Listen to this sentence" : "Écouter cette phrase");
      hear.addEventListener("click", () => speakFr(full, RC_RATE));
      const txt = rcEl("div", "rc-ctxt");
      txt.append(fr, rcEl("span", "rc-en", c.g));
      li.append(txt, hear);
      li.title = full;
      ul.appendChild(li);
    });
    box.appendChild(ul);
    box.appendChild(rcEl("p", "rc-endn", isNew
      ? (en ? "You'll see them in Battle: that's how words become stones." : "Tu les reverras en Séance : c'est comme ça que les mots deviennent des pierres.")
      : (en ? "They are already in your notebook." : "Elles sont déjà dans ton cahier.")));
  }

  if(isNew) box.appendChild(rcEl("p", "rc-xp", "+" + RC_XP_PAGE + " XP"));

  if(actWon){
    box.appendChild(rcEl("p", "rc-act", (en ? "End of Act " : "Fin de l'acte ") + (ROMAN[actWon.n] || actWon.n)));
    box.appendChild(rcFr("p", "rc-hook nt", actWon.fin));
    if(en) box.appendChild(rcEl("p", "rc-en", actWon.finEn));
  }else{
    const t = rcEl("div", "rc-tease");
    t.appendChild(rcEl("span", "rc-tlab", en ? "Next:" : "À suivre :"));
    t.appendChild(rcFr("span", "rc-hook nt", rcSub(p.hook, false)));
    if(en) t.appendChild(rcEl("span", "rc-en", rcSub(p.hookEn, true)));
    box.appendChild(t);
  }
  log.appendChild(box);
  rcScroll();
  rcSetNext();
  $("rcNext").focus();

  if(typeof toast === "function"){
    if(chapterWon) toast(en ? "Chapter complete" : "Chapitre terminé", recitChapterLabel(chapterWon, en), "i-chroniques");
    if(actWon) toast(en ? "Act complete" : "Acte terminé", (en ? actWon.en : actWon.fr), "i-medaille");
  }
}

function recitOpen(id, replay){
  const page = recitPage(id);
  if(!page) return false;
  const m = typeof openModal === "function" ? openModal() : null;
  if(m && m.id !== "mdPage") return false;
  if(RC){ rcHush(); RC = null; }
  RC = {page, i:0, beats:page.lines, waiting:false, done:false, replay:!!replay, score:[], tries:0,
    voice:rcVoiceOn(), opener:document.activeElement};
  recitPreload(page);

  $("rcCard").classList.toggle("show-en", !!S.P.recit.tr);
  $("rcTr").setAttribute("aria-pressed", S.P.recit.tr ? "true" : "false");
  $("rcVoice").setAttribute("aria-pressed", RC.voice ? "true" : "false");
  $("rcVoice").textContent = RC.voice ? "🔊" : "🔇";
  const t = $("rcT");
  t.textContent = page.titre;
  t.lang = "fr";
  $("rcPlace").textContent = page.lieu;
  $("rcPlace").lang = "fr";
  $("rcLog").innerHTML = "";
  $("mdPage").hidden = false;
  rcRelabel();
  rcAdvance();
  $("rcNext").focus();
  return true;
}

function recitClose(){
  if(!RC) return;
  const opener = RC.opener;
  rcHush();
  RC = null;
  $("mdPage").hidden = true;
  recitRefresh();
  if(typeof paintHud === "function") paintHud();
  if(typeof heroCelebrate === "function") heroCelebrate();
  if(opener && opener.focus && document.contains(opener)){ try{ opener.focus(); }catch(e){} }
}

const recitEscape = (m) => { if(m && m.id === "mdPage") recitClose(); };

/* Le héros vient d'être créé : l'histoire s'ouvre sur la première scène. */
function recitAfterCreate(){
  if(recitRead().p00) return;
  setTimeout(() => { if(!recitRead().p00) recitOpen("p00", false); }, 450);
}

/* ---------- le livre : relire les pages (Chroniques) ---------- */
function recitPaintBook(){
  const host = $("rcBook"), list = $("rcBookList");
  if(!host || !list) return;
  const en = rcEn(), r = recitRead();
  const pages = RECIT.pages.filter(p => r[p.id]);
  host.hidden = !pages.length;
  if(!pages.length) return;
  $("rcBookH").textContent = en ? "The Story · pages read" : "Le Récit · les pages lues";
  list.innerHTML = "";
  pages.forEach(p => {
    const ch = recitChapter(p.ch);
    const b = rcEl("button", "rc-bookrow");
    b.type = "button";
    b.append(rcEl("span", "rc-bk", (p.ch === 0 ? "P" : String(p.ch)) + "."),
      rcFr("span", "rc-bt", p.titre),
      rcEl("span", "rc-bc", (en ? ch.en : ch.fr) + (en ? " · " + p.titreEn : "")),
      rcEl("span", "rc-bgo", en ? "Reread" : "Relire"));
    b.addEventListener("click", () => recitOpen(p.id, true));
    list.appendChild(b);
  });
}

function recitInit(){
  if(RC_READY) return;
  RC_READY = true;
  $("rcNext").addEventListener("click", rcNextClick);
  $("rcClose").addEventListener("click", recitClose);
  $("rcVoice").addEventListener("click", () => {
    if(!RC) return;
    RC.voice = !RC.voice;
    try{ localStorage.setItem(RC_VOICE_KEY, RC.voice ? "1" : "0"); }catch(e){}
    $("rcVoice").setAttribute("aria-pressed", RC.voice ? "true" : "false");
    $("rcVoice").textContent = RC.voice ? "🔊" : "🔇";
    if(!RC.voice) rcHush();
  });
  $("rcTr").addEventListener("click", () => {
    const on = !S.P.recit.tr;
    S.P.recit.tr = on;
    $("rcCard").classList.toggle("show-en", on);
    $("rcTr").setAttribute("aria-pressed", on ? "true" : "false");
    save();
  });
  /* → avance, 1-2-3 choisit une réplique : on lit sans quitter le clavier. */
  document.addEventListener("keydown", (e) => {
    if(!RC || $("mdPage").hidden || e.ctrlKey || e.metaKey || e.altKey) return;
    if(e.key === "ArrowRight"){
      if(!RC.waiting){ e.preventDefault(); rcNextClick(); }
      return;
    }
    if(RC.waiting && /^[1-4]$/.test(e.key)){
      const b = $("rcLog").querySelector('.rc-opt[data-key="' + e.key + '"]:not(:disabled)');
      if(b){ e.preventDefault(); b.click(); }
    }
  });
}
