/* Le Cahier — les sons (paires minimales) et les cartes faites main.
   D'abord l'oreille : tant qu'on n'entend pas la différence, on ne la dira
   pas et on ne l'écrira pas. */

const CONTRASTS = [
  {k:"yu", t:"/y/ vs /u/", why:"tu / tout — la bouche est serrée pour /y/, ronde et reculée pour /u/.",
   p:[["tu","tout"],["rue","roue"],["vu","vous"],["su","sous"],["bu","bout"],["pu","pou"]]},
  {k:"ou", t:"/ø/ vs /u/", why:"feu / fou — /ø/ garde les lèvres arrondies mais la langue en avant.",
   p:[["feu","fou"],["deux","doux"],["peu","pou"],["ceux","sous"]]},
  {k:"sz", t:"/s/ vs /z/", why:"poisson / poison — un seul s entre deux voyelles se dit /z/.",
   p:[["poisson","poison"],["dessert","désert"],["coussin","cousin"],["baisser","baiser"]]},
  {k:"ss", t:"/ʃ/ vs /s/", why:"chou / sou — le ch français ne claque pas comme en anglais.",
   p:[["chou","sou"],["chaud","sot"],["cache","casse"],["chaîne","scène"]]},
  {k:"an", t:"/ɑ̃/ vs /ɔ̃/", why:"banc / bon — deux nasales que l'anglais ne distingue pas du tout.",
   p:[["banc","bon"],["dans","don"],["temps","thon"],["vent","vont"],["lent","long"]]},
  {k:"in", t:"/ɛ̃/ vs /ɑ̃/", why:"vin / vent — la première est tendue et haute, la seconde ouverte.",
   p:[["vin","vent"],["lin","lent"],["main","ment"],["pain","pan"]]},
  {k:"io", t:"/ɛ̃/ vs /ɔ̃/", why:"bain / bon — très proches à l'oreille anglophone.",
   p:[["bain","bon"],["sain","son"],["teint","ton"],["frein","front"]]},
  {k:"oo", t:"/ɔ/ vs /o/", why:"pomme / paume — ouvert court contre fermé long.",
   p:[["pomme","paume"],["sotte","saute"],["cotte","côte"],["notre","nôtre"]]},
  {k:"gn", t:"masculin / féminin à l'oreille", why:"petit / petite — la consonne finale ne se dit qu'au féminin.",
   p:[["petit","petite"],["grand","grande"],["français","française"],["premier","première"]]}
];

/* Liste à plat : l'identifiant d'une paire est sa position. */
const PAIRS = [];
CONTRASTS.forEach(c => c.p.forEach(pair => PAIRS.push({c:c.k, t:c.t, a:pair[0], b:pair[1]})));

let SN = null;

function sonItem(id){ return PAIRS[+id.slice(1)] || null; }

function sonAsk(pair, idx){
  SN = SN || {};
  SN.pair = pair; SN.idx = idx;
  SN.said = Math.random() < .5 ? pair.a : pair.b;
  speakFr(SN.said, .9);
}

function sonPanel(){
  const en = typeof LANG !== "undefined" && LANG === "en";
  const box = $("snBody");
  box.innerHTML = "";
  const i = (Math.random() * PAIRS.length) | 0;
  const pair = PAIRS[i];
  SN = {answered:false};
  sonAsk(pair, i);

  box.appendChild(Object.assign(document.createElement("p"),
    {className:"eyebrow", textContent:pair.t}));

  const row = document.createElement("div");
  row.className = "artchoice";
  [pair.a, pair.b].forEach(w => {
    const b = document.createElement("button");
    b.className = "art"; b.textContent = w;
    b.addEventListener("click", () => sonAnswer(w, b, i));
    row.appendChild(b);
  });
  box.appendChild(row);

  const tools = document.createElement("div");
  tools.className = "after";
  const again = document.createElement("button");
  again.className = "ghost";
  again.textContent = en ? "Play again" : "Réécouter";
  again.addEventListener("click", () => speakFr(SN.said, .9));
  const slow = document.createElement("button");
  slow.className = "ghost";
  slow.textContent = en ? "Slower" : "Lentement";
  slow.addEventListener("click", () => speakFr(SN.said, .55));
  tools.append(again, slow);
  box.appendChild(tools);

  $("snNote").textContent = en ? "Which one did you hear?" : "Lequel des deux as-tu entendu ?";
}

function sonAnswer(word, btn, idx){
  if(SN.answered) return;
  SN.answered = true;
  const ok = word === SN.said;
  const en = typeof LANG !== "undefined" && LANG === "en";
  [...btn.parentElement.children].forEach(b => {
    b.disabled = true;
    if(b.textContent === SN.said) b.classList.add("right");
    else if(b === btn) b.classList.add("wrong");
  });
  srsUpdate("m" + idx, srsGrade(ok, 0, false));
  const c = CONTRASTS.find(x => x.k === SN.pair.c);
  $("snNote").innerHTML = (ok ? (en ? "<b>Correct</b> — " : "<b>Juste</b> — ")
    : (en ? "<b>No</b> — it was " : "<b>Non</b> — c'était ")) + "« " + SN.said + " ». "
    + (c ? c.why : "");
  paintSonStats();
  const next = document.createElement("button");
  next.className = "go";
  next.textContent = en ? "Next pair" : "Paire suivante";
  next.addEventListener("click", sonPanel);
  $("snBody").appendChild(next);
  next.focus();
}

function paintSonStats(){
  const en = typeof LANG !== "undefined" && LANG === "en";
  const box = $("snStats");
  box.innerHTML = "";
  CONTRASTS.forEach(c => {
    let t = 0, h = 0;
    PAIRS.forEach((p, i) => {
      if(p.c !== c.k) return;
      const s = S.P.srs["m" + i];
      if(!s) return;
      t += s[5] || 0; h += s[6] || 0;
    });
    const row = document.createElement("div");
    row.className = "lvrow";
    row.appendChild(Object.assign(document.createElement("span"),
      {className:"weakname", textContent:c.t}));
    const track = document.createElement("div");
    track.className = "lvtrack";
    const fill = document.createElement("div");
    fill.className = "lvfill" + (t && h / t < .8 ? " weak" : "");
    fill.style.width = (t ? Math.round(h / t * 100) : 0) + "%";
    track.appendChild(fill);
    row.appendChild(track);
    row.appendChild(Object.assign(document.createElement("span"),
      {className:"lvnum", textContent:t ? Math.round(h / t * 100) + "% · " + t : "—"}));
    box.appendChild(row);
  });
}

let SN_READY = false;
function sonsInit(){
  if(SN_READY) return paintSonStats();
  SN_READY = true;
  if(typeof dVoice === "function" && !dVoice()) $("snWarn").hidden = false;
  sonPanel();
  paintSonStats();
}

/* ---------- cartes faites main, façon Fluent Forever ----------
   Un mot donne plusieurs cartes, jamais de traduction dessus :
   - r : le mot (vu et entendu) vers l'image — la reconnaissance, et la
         première fiche qu'on voit d'un mot neuf ;
   - p : l'image vers le mot — la production ;
   - s : le son et l'image vers l'orthographe ;
   - g : le genre, quand c'est un nom. */

function motCards(m){
  const ids = ["wr_" + m.id, "wp_" + m.id, "ws_" + m.id];
  if(m.g) ids.push("wg_" + m.id);
  return ids;
}
const motById = (id) => (S.mots || []).find(x => x.id === id.slice(3)) || null;

const MOT_LABEL = {r:"Mot → image", p:"Image → mot", s:"Son → orthographe", g:"Le ou la"};
const MOT_CAP = 900;

/* « le chien », « la pomme », « l'arbre », « un vélo » : l'article donne le
   genre et sort du mot lui-même. */
function splitArt(s){
  const t = String(s || "").trim().replace(/\s+/g, " ");
  const m = t.match(/^(?:(le|la|les|un|une)\s+|(l['’])\s*)(.+)$/i);
  if(!m || !m[3]) return {word:t, g:""};
  const a = (m[1] || m[2]).toLowerCase();
  const g = a === "le" || a === "un" ? "m" : a === "la" || a === "une" ? "f" : "";
  return {word:m[3].trim(), g};
}
const motNorm = (s) => splitArt(s).word.toLowerCase();
const motFind = (s) => (S.mots || []).find(m => motNorm(m.fr) === motNorm(s)) || null;

function motMake(fr, pic, note, gender, pos, from){
  const sp = splitArt(fr);
  const m = {
    id:Date.now().toString(36) + Math.floor(Math.random() * 99),
    fr:sp.word.slice(0, 60),
    pic:String(pic || "").trim().slice(0, 12),
    note:String(note || "").trim().slice(0, 120),
    g:gender || sp.g || "", pos:pos || "", from:from || "", lv:S.P.level, at:Date.now()
  };
  if(m.g) m.pos = "nom";
  if(!m.fr) return null;
  S.mots = [m].concat(S.mots || []).slice(0, MOT_CAP);
  saveMots();
  srsReset();
  paintMargin();
  return m;
}

/* Ce que le cahier sait déjà d'un mot : l'image et le genre du socle,
   ou au moins une image. */
function motGuess(word){
  const w = motNorm(word);
  if(!w) return null;
  if(typeof BASE !== "undefined"){
    for(const th of BASE){
      const hit = th.w.find(x => x[0].toLowerCase() === w);
      if(hit) return {pic:hit[2], g:hit[1]};
    }
  }
  const p = typeof picOf === "function" ? picOf(w) : "";
  return p ? {pic:p, g:""} : null;
}

let QK_N = 0;

/* Le formulaire, utilisable partout — surtout juste après une faute.
   Fabriquer la carte fait partie de l'apprentissage : on choisit l'image,
   on se rappelle un souvenir, on voit le mot avec son image de genre. */
function cardForm(host, prefill, onDone){
  host.innerHTML = "";
  const n = QK_N++ ? "-" + QK_N : "";
  const en = typeof LANG !== "undefined" && LANG === "en";
  const box = document.createElement("div");
  box.className = "mkbox";

  const mk = (id, label, ph, val) => {
    const l = document.createElement("label");
    l.className = "fld";
    l.appendChild(Object.assign(document.createElement("span"), {textContent:label}));
    const i = document.createElement("input");
    i.className = "seinput"; i.id = id + n; i.autocomplete = "off"; i.spellcheck = false;
    i.placeholder = ph || ""; i.value = val || "";
    l.appendChild(i);
    return [l, i];
  };

  const [lw, iw] = mk("qkWord", en ? "The French word" : "Le mot français", "le tiroir", prefill || "");
  iw.lang = "fr";
  const [lp, ip] = mk("qkPic", en ? "A picture" : "Une image", "🗄");
  const [ln, inn] = mk("qkNote", en ? "Your own memory of it — optional" : "Ton souvenir à toi — facultatif",
    en ? "the drawer that sticks in the kitchen" : "le tiroir qui coince dans la cuisine");

  const grid = document.createElement("div");
  grid.className = "mkgrid";
  grid.append(lw, lp);
  box.append(grid);

  const gl = document.createElement("div");
  gl.className = "fld";
  gl.appendChild(Object.assign(document.createElement("span"),
    {textContent:en ? "Gender — if it's a noun" : "Genre — si c'est un nom"}));
  const gsel = document.createElement("div");
  gsel.className = "chips";
  let gender = "", picAuto = false, genderSet = false;
  const setG = (v) => {
    gender = v;
    [...gsel.children].forEach(c => {
      const on = c.dataset.g === v;
      c.classList.toggle("on", on);
      c.setAttribute("aria-pressed", on ? "true" : "false");
    });
    paintCue();
  };
  [["", en ? "none" : "aucun"], ["m", "le"], ["f", "la"]].forEach(([v, lab]) => {
    const b = document.createElement("button");
    b.type = "button"; b.className = "chip"; b.textContent = lab; b.dataset.g = v;
    if(v) b.lang = "fr";
    b.addEventListener("click", () => { genderSet = true; setG(v); });
    gsel.appendChild(b);
  });
  gl.appendChild(gsel);
  box.append(gl);

  const cue = document.createElement("p");
  cue.className = "gcue";
  cue.hidden = true;
  box.append(cue, ln);

  function paintCue(){
    const w = splitArt(iw.value).word;
    if(!gender || !w || typeof genderCue !== "function"){ cue.hidden = true; return; }
    cue.hidden = false;
    genderCue(cue, w, gender, true);
  }

  iw.addEventListener("input", () => {
    const sp = splitArt(iw.value);
    const guess = motGuess(sp.word);
    if(sp.g && !genderSet) setG(sp.g);
    else if(guess && guess.g && !genderSet) setG(guess.g);
    else if(!genderSet) setG("");
    if(guess && guess.pic && (!ip.value.trim() || picAuto)){ ip.value = guess.pic; picAuto = true; }
    else if(!guess && picAuto){ ip.value = ""; picAuto = false; }
    paintCue();
  });
  ip.addEventListener("input", () => { picAuto = false; });

  const row = document.createElement("div");
  row.className = "after";
  const go = document.createElement("button");
  go.className = "go";
  go.textContent = en ? "Make the card" : "Faire la carte";
  const say = document.createElement("button");
  say.className = "ghost";
  say.textContent = en ? "Hear it" : "Écouter";
  say.addEventListener("click", () => {
    const w = splitArt(iw.value).word;
    if(w) speakFr((typeof artOf === "function" ? artOf({fr:w, g:gender}) : "") + w, .9);
  });
  const note = document.createElement("p");
  note.className = "note";

  go.addEventListener("click", () => {
    const w = splitArt(iw.value).word;
    if(!w){ note.textContent = en ? "Write the French word first." : "Écris d'abord le mot français."; return; }
    const dup = motFind(w);
    if(dup){
      note.textContent = (en ? "Already in your deck: " : "Déjà dans ton paquet : ")
        + (dup.pic ? dup.pic + " " : "") + (typeof artOf === "function" ? artOf(dup) : "") + dup.fr + ".";
      return;
    }
    if(!ip.value.trim() && !inn.value.trim()){
      note.textContent = en ? "Give it a picture or a memory of your own — that is what replaces the translation."
        : "Donne-lui une image ou un souvenir à toi : c'est ce qui remplace la traduction.";
      ip.focus();
      return;
    }
    const m = motMake(w, ip.value, inn.value, gender, "", prefill ? "faute" : "main");
    if(!m) return;
    const k = motCards(m).length;
    note.textContent = en
      ? "Card made — " + k + " cards scheduled: word → picture, picture → word, sound" + (m.g ? ", gender." : ".")
      : "Carte faite — " + k + " cartes planifiées : mot → image, image → mot, son" + (m.g ? ", genre." : ".");
    iw.value = ""; ip.value = ""; inn.value = "";
    picAuto = false; genderSet = false; setG("");
    drawMots();
    if(onDone) onDone(m);
    iw.focus();
  });
  iw.addEventListener("keydown", (e) => { if(e.key === "Enter"){ e.preventDefault(); ip.focus(); } });
  row.append(go, say);
  box.append(row, note);
  host.appendChild(box);
  setG("");
  if(prefill) iw.dispatchEvent(new Event("input"));
  setTimeout(() => iw.focus(), 30);
}

/* Le bouton qui apparaît juste après une faute. */
function missButton(host, word){
  if(!host || !word) return;
  const en = typeof LANG !== "undefined" && LANG === "en";
  const b = document.createElement("button");
  b.className = "ghost mkmini";
  b.textContent = (en ? "+ Card from « " : "+ Carte sur « ") + word + " »";
  b.addEventListener("click", () => {
    const slot = document.createElement("div");
    b.replaceWith(slot);
    cardForm(slot, word, () => { slot.innerHTML = ""; });
  });
  host.appendChild(b);
}

/* ---------- enregistrement et synchronisation du paquet ----------
   Un mot supprimé laisse une trace (son identifiant) pour qu'un autre
   appareil ne le fasse pas revenir. */
function motDel(){
  if(!Array.isArray(S.motDel)){
    try{
      const v = JSON.parse(localStorage.getItem("le-cahier-mots-del-v1"));
      S.motDel = Array.isArray(v) ? v.map(String).slice(-500) : [];
    }catch(e){ S.motDel = []; }
  }
  return S.motDel;
}

function saveMots(){
  try{
    localStorage.setItem("le-cahier-mots-v1", JSON.stringify(S.mots));
    localStorage.setItem("le-cahier-mots-del-v1", JSON.stringify(motDel()));
  }catch(e){}
  if(!S.db || !S.uid) return;
  clearTimeout(S.mTimer);
  S.mTimer = setTimeout(async () => {
    try{ await S.db.doc("data/users/" + S.uid + "/mots").set({mots:S.mots, del:motDel(), at:Date.now()}); }
    catch(e){}
  }, 900);
}

function readMots(){
  try{
    const v = JSON.parse(localStorage.getItem("le-cahier-mots-v1"));
    return Array.isArray(v) ? v.filter(m => m && m.fr && m.id).slice(0, MOT_CAP) : [];
  }catch(e){ return []; }
}

function motDelete(id){
  const m = (S.mots || []).find(x => x.id === id);
  if(!m) return;
  motCards(m).forEach(cid => { delete S.P.srs[cid]; });
  S.mots = S.mots.filter(x => x.id !== id);
  S.motDel = motDel().concat([id]).slice(-500);
  saveMots(); save(); srsReset(); paintMargin();
}

function motEdit(id, patch){
  const m = (S.mots || []).find(x => x.id === id);
  if(!m) return null;
  const had = !!m.g;
  if(patch.fr != null){
    const sp = splitArt(patch.fr);
    if(sp.word) m.fr = sp.word.slice(0, 60);
    if(sp.g && patch.g == null) m.g = sp.g;
  }
  if(patch.pic != null) m.pic = String(patch.pic).trim().slice(0, 12);
  if(patch.note != null) m.note = String(patch.note).trim().slice(0, 120);
  if(patch.g != null) m.g = patch.g;
  m.pos = m.g ? "nom" : (m.pos === "nom" ? "" : m.pos);
  if(had && !m.g) delete S.P.srs["wg_" + m.id];
  m.at = Date.now();
  saveMots(); save(); srsReset(); paintMargin();
  return m;
}

/* Au branchement du compte : union des deux paquets, le plus récent gagne
   mot par mot, et ce qui a été supprimé quelque part le reste partout. */
async function syncMots(){
  if(!S.db || !S.uid) return;
  try{
    const snap = await S.db.doc("data/users/" + S.uid + "/mots").get();
    if(!snap.exists){ if((S.mots || []).length) saveMots(); return; }
    const data = snap.data() || {};
    const del = new Set(motDel().concat(Array.isArray(data.del) ? data.del.map(String) : []));
    const cloud = Array.isArray(data.mots) ? data.mots.filter(m => m && m.fr && m.id) : [];
    const byId = {};
    cloud.forEach(m => { byId[m.id] = m; });
    const seen = {}, merged = [];
    (S.mots || []).forEach(m => {
      const c = byId[m.id];
      merged.push(c && (c.at || 0) > (m.at || 0) ? c : m);
      seen[m.id] = 1;
    });
    cloud.forEach(m => { if(!seen[m.id]) merged.push(m); });
    S.motDel = [...del].slice(-500);
    S.mots = merged.filter(m => !del.has(m.id)).slice(0, MOT_CAP);
    const same = S.mots.length === cloud.length
      && S.mots.every(m => byId[m.id] && (byId[m.id].at || 0) === (m.at || 0));
    if(same){
      try{ localStorage.setItem("le-cahier-mots-v1", JSON.stringify(S.mots)); }catch(e){}
    }else saveMots();
    srsReset();
    drawMots();
    paintMargin();
    if(typeof paintBase === "function" && SB_READY) paintBase();
  }catch(e){}
}

function drawMots(){
  if(typeof paintCartes === "function") paintCartes();
}
