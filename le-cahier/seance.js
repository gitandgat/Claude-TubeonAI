/* Le Cahier — la séance du jour : rappel actif, types entrelacés */

let SE = null;

const KIND_LABEL = {trou:"Phrase à trou", dictee:"Dictée", genre:"Masculin ou féminin",
  conj:"Conjugaison", son:"Deux sons", mot:"Ta carte", trad:"Toute la phrase",
  ordre:"L'ordre des mots", decider:"Décider", imiter:"Imiter"};
const el = (tag, cls, txt) => {
  const e = document.createElement(tag);
  if(cls) e.className = cls;
  if(txt != null) e.textContent = txt;
  return e;
};
const phon = (s) => s.trim().toLowerCase().replace(/[^a-z\u00e0-\u00ff\u0153'\- ]/g, "").replace(/\s+/g, " ");
const same = (a, b) => phon(a) === phon(b) && phon(a) !== "";
const accentOnly = (a, b) => !same(a, b) && dStrip(a) === dStrip(b) && dStrip(a) !== "";

/* La forme du mot : un point par lettre, les espaces gardés. On voit ce
   qu'on cherche — la longueur, les mots — sans qu'on vous le donne. */
/* La « photo » d'une carte : l'image posée sur une plaque colorée, la teinte
   tirée du mot lui-même — chaque carte a donc sa couleur, toujours la même. */
/* Une image pour la phrase, prise dans la phrase elle-même : on cherche les
   mots qu'on sait montrer. Deux au plus — une scène, pas un sapin de Noël.
   Dans un texte à trou on écarte la réponse : l'image aide, elle ne donne pas. */
function scenePic(c, hideAnswer){
  if(!c || !c.s) return "";
  /* Une scène fabriquée pour cette phrase passe avant tout le reste. */
  if(c.pic && !hideAnswer) return c.pic;
  const out = [], seen = {};
  const ans = String(c.a || "").toLowerCase();
  const words = String(c.s).toLowerCase().split(/[^a-z\u00e0-\u00ff\u0153'-]+/).filter(w => w.length > 2);
  const mine = {};
  (S.mots || []).forEach(m => { if(m.pic) mine[m.fr.toLowerCase()] = m.pic; });
  const look = (w) => mine[w] || (typeof picOf === "function" ? picOf(w) : "");

  if(!hideAnswer && ans){
    const p = look(ans);
    if(p){ out.push(p); seen[p] = 1; }
  }
  for(const w of words){
    if(out.length >= 2) break;
    if(hideAnswer && (w === ans || ans.indexOf(w) >= 0)) continue;
    const p = look(w);
    if(p && !seen[p]){ out.push(p); seen[p] = 1; }
  }
  return out.join(" ");
}

/* Une vraie photo sur la phrase l'emporte sur toute vignette. */
function scenePhoto(c, size){
  if(!c || !c.img || typeof photoUrl !== "function") return null;
  const s = size || 190;
  const img = el("img");
  img.src = photoUrl(c.img);
  img.alt = "";
  img.loading = "lazy";
  img.style.cssText = "width:" + s + "px;height:" + Math.round(s * .66) + "px;object-fit:cover;"
    + "border-radius:14px;display:block;margin:0 0 14px;"
    + "box-shadow:0 1px 2px rgba(20,16,40,.16),0 14px 28px -18px rgba(20,16,40,.55)";
  img.addEventListener("error", () => img.remove());
  return img;
}

function sceneStrip(pics, size){
  const d = el("div", "scene-pic", pics);
  d.style.cssText = "font-size:" + (size || "2.6rem") + ";line-height:1;letter-spacing:.14em;"
    + "margin:0 0 12px;filter:drop-shadow(0 2px 4px rgba(20,16,40,.18))";
  return d;
}

function picHue(w){
  let h = 0;
  String(w || "").split("").forEach(c => { h = (h * 31 + c.charCodeAt(0)) % 360; });
  return h;
}

function picPlate(pic, word, size, img){
  const s = size || 164;
  const h = picHue(word);
  const wrap = el("div", "plate");
  wrap.style.cssText = "width:" + s + "px;height:" + s + "px;border-radius:" + Math.round(s * .17)
    + "px;display:grid;place-items:center;margin:0 0 18px;position:relative;overflow:hidden;"
    + "background:radial-gradient(120% 110% at 28% 22%,hsl(" + h + " 72% 93%) 0%,hsl("
    + ((h + 26) % 360) + " 58% 82%) 55%,hsl(" + ((h + 48) % 360) + " 48% 72%) 100%);"
    + "box-shadow:0 1px 2px rgba(20,16,40,.14),0 14px 28px -16px rgba(20,16,40,.5),"
    + "inset 0 0 0 1px rgba(255,255,255,.55);";
  let glyph;
  if(img && typeof photoUrl === "function"){
    glyph = el("img");
    glyph.src = photoUrl(img);
    glyph.alt = word || "";
    glyph.loading = "lazy";
    glyph.style.cssText = "width:100%;height:100%;object-fit:cover;display:block";
    glyph.addEventListener("error", () => {
      /* la photo a disparu : on retombe sur l'image */
      glyph.replaceWith(Object.assign(el("div", null, pic || "·"),
        {style:"font-size:" + Math.round(s * .46) + "px;line-height:1"}));
    });
  }else{
    glyph = el("div", null, pic || "·");
    glyph.style.cssText = "font-size:" + Math.round(s * .46) + "px;line-height:1;"
      + "filter:drop-shadow(0 3px 5px rgba(20,16,40,.22));transform:translateY(-2px)";
  }
  const gloss = el("div");
  gloss.style.cssText = "position:absolute;inset:0;pointer-events:none;border-radius:inherit;"
    + "background:linear-gradient(160deg,rgba(255,255,255,.45) 0%,rgba(255,255,255,0) 46%)";
  wrap.append(glyph, gloss);
  return wrap;
}

/* D'où vient cette carte ? Quand on la rate, on veut pouvoir y retourner. */
const FROM_LABEL = {
  socle:["du socle", "from the base deck"],
  "625":["de la liste du livre", "from the book's list"],
  capture:["de tes captures", "from your captures"],
  histoire:["de ton histoire", "from your story"],
  faute:["d'une faute que tu as faite", "from a mistake you made"]
};

function sourceOf(id, data){
  const en = typeof LANG !== "undefined" && LANG === "en";
  const base = /^[sxoi]/.test(id) ? id.slice(1) : id;
  if(id[0] === "w"){
    const m = (typeof motById === "function") ? motById(id) : null;
    const f = m && FROM_LABEL[m.from];
    return f ? {label:f[en ? 1 : 0]} : null;
  }
  if(base[0] === "v") return {label:en ? "from your video" : "de ta vidéo",
    href:/^https?:\/\//i.test((data && data.src) || "") ? data.src : null};
  if(base[0] === "c") return {label:en ? "from your conversation" : "de ta conversation"};
  if(base[0] === "q") return {label:en ? "from your captures" : "de tes captures"};
  if(base[0] === "p") return {label:en ? "made for you" : "faite sur mesure pour toi"};
  if(base[0] === "n") return {label:en ? "from this week's new sentences" : "des phrases de la semaine"};
  if(base[0] === "r"){
    const c = typeof RECIT_ALL !== "undefined" ? RECIT_ALL.find(x => x.id === base) : null;
    const pg = c && typeof recitPage === "function" ? recitPage(c.page) : null;
    return {label:(en ? "from your story" : "de ton récit") + (pg ? " — « " + pg.titre + " »" : "")};
  }
  return null;
}

/* Le bloc « revoir » : le contexte entier, et le chemin du retour. */
function referBack(it, id){
  const en = typeof LANG !== "undefined" && LANG === "en";
  const d = it.data;
  const box = el("div", "referback");
  box.style.cssText = "margin:18px 0 0;padding:14px 16px;border-left:3px solid var(--rule-major);"
    + "background:var(--paper-2);border-radius:0 7px 7px 0;max-width:52ch";
  box.appendChild(Object.assign(el("p", null,
    en ? "Look at it again" : "Reviens dessus"),
    {style:"font-family:'IBM Plex Mono',monospace;font-size:.6rem;letter-spacing:.16em;"
      + "text-transform:uppercase;color:var(--ink-faint);margin:0 0 8px"}));

  /* la phrase entière, trou comblé */
  if(it.kind === "trou" || it.kind === "dictee" || it.kind === "trad"
    || it.kind === "ordre" || it.kind === "imiter"){
    const phR = scenePhoto(d, 150);
    if(phR) box.appendChild(phR);
    else { const scR = scenePic(d, false); if(scR) box.appendChild(sceneStrip(scR, "2rem")); }
    const full = String(d.s || "").replace("___", d.a);
    const p = el("p");
    p.style.cssText = "margin:0 0 6px;font-size:1.05rem;line-height:1.6";
    p.lang = "fr";
    const i = full.indexOf(d.a);
    if(i >= 0){
      p.append(full.slice(0, i),
        Object.assign(el("b", null, d.a), {style:"color:var(--margin-red)"}),
        full.slice(i + d.a.length));
    }else p.textContent = full;
    box.appendChild(p);
    if(d.g) box.appendChild(Object.assign(el("p", null, d.g),
      {style:"margin:0;font-style:italic;color:var(--ink-soft);font-size:.92rem"}));
  }

  const src = sourceOf(id, d);
  if(src){
    const line = el("p");
    line.style.cssText = "margin:10px 0 0;font-size:.86rem;color:var(--ink-faint)";
    line.append((en ? "This card comes " : "Cette carte vient ") + src.label);
    if(src.href){
      line.append(" ");
      const a = el("a", null, "↗");
      a.href = src.href; a.target = "_blank"; a.rel = "noopener";
      line.appendChild(a);
    }
    box.appendChild(line);
  }

  box.appendChild(Object.assign(el("p", null, en
    ? "It comes back in a few cards — read it once now, don't just move on."
    : "Elle revient dans quelques cartes — relis-la maintenant, ne passe pas."),
    {style:"margin:10px 0 0;font-size:.84rem;font-style:italic;color:var(--ink-faint)"}));
  return box;
}

function wordShape(a, letters){
  return String(a || "").split("").map((ch, i) => {
    if(/\s/.test(ch)) return "\u2003";
    if(!/[a-z\u00e0-\u00ff\u0153]/i.test(ch)) return ch;
    return i < (letters || 0) ? ch : "\u00b7";
  }).join("");
}

function seanceInit(){
  $("seRestart").addEventListener("click", () => startSeance());
  startSeance();
}

/* only : "mot" pour ne réviser que les cartes de ton paquet */
function startSeance(only){
  only = typeof only === "string" ? only : null;
  const {queue, due, fresh, left, comeback} = srsQueue(only);
  SE = {q:queue, i:0, done:0, right:0, total:queue.length, due, fresh, left, comeback, t0:0,
    helped:false, answered:false, only, flipped:false, xp0:(S.P.hero && S.P.hero.xp) || 0, misses:0};
  $("seRestart").hidden = true;
  if(!queue.length) return finish(true);
  renderCard();
}

/* Le combat : chaque carte est un adversaire. La barre est sa vie, elle baisse à chaque
   rappel juste ; une carte ratée revient (c'est voulu), la vie ne baisse pas.
   Les cœurs comptent les coups reçus — décoratifs : jamais de « game over ». */
const FOE = {
  fr:{trou:"Spectre du trou", dictee:"Écho fuyant", trad:"Sphinx bilingue", genre:"Jumeaux hésitants",
      conj:"Hydre des temps", son:"Sirène aux deux voix", mot:"Gardien des images", ordre:"Golem désordonné",
      decider:"Chimère à deux formes", imiter:"Mime moqueur"},
  en:{trou:"Gap Wraith", dictee:"Fleeing Echo", trad:"Bilingual Sphinx", genre:"Wavering Twins",
      conj:"Tense Hydra", son:"Two-voiced Siren", mot:"Keeper of Images", ordre:"Scrambled Golem",
      decider:"Two-faced Chimera", imiter:"Mocking Mime"}
};

function paintHearts(){
  const box = $("seHearts");
  if(!box) return;
  const lost = Math.min(5, (SE && SE.misses) || 0);
  box.innerHTML = "";
  for(let i = 0; i < 5; i++){
    const sv = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    sv.setAttribute("viewBox", "0 0 24 24");
    if(i >= 5 - lost) sv.setAttribute("class", "lost");
    sv.innerHTML = '<use href="#i-coeur"/>';
    box.appendChild(sv);
  }
  box.setAttribute("aria-label", "Endurance " + (5 - lost) + "/5");
}

function progress(){
  const en = typeof LANG !== "undefined" && LANG === "en";
  SE.hpMax = Math.max(SE.hpMax || SE.total, SE.q.length);
  const left = Math.max(0, SE.q.length - SE.i - (SE.answered ? 1 : 0));
  $("seFill").style.width = (SE.hpMax ? Math.round(left / SE.hpMax * 100) : 0) + "%";
  $("seCount").textContent = (en ? "HP " : "PV ") + left + " / " + SE.hpMax;
  paintHearts();
}

function renderCard(){
  const id = SE.q[SE.i];
  const it = srsItem(id);
  if(!it){ SE.i++; return SE.i < SE.q.length ? renderCard() : finish(false); }

  /* Un type de carte sans dessinateur ne doit pas casser la séance en cours :
     on le saute comme une carte introuvable. Le cahier s'écrit à plusieurs
     mains, et un type enregistré avant sa carte ne doit rien faire tomber. */
  const draw = ({trou:cardTrou, dictee:cardDictee, genre:cardGenre, conj:cardConj,
    son:cardSon, mot:cardMot, trad:cardTrad,
    ordre:cardOrdre, decider:cardDecider, imiter:cardImiter})[it.kind];
  if(typeof draw !== "function"){
    SE.i++;
    return SE.i < SE.q.length ? renderCard() : finish(false);
  }

  SE.helped = false; SE.answered = false; SE.flipped = false; SE.t0 = Date.now(); SE.cur = it; SE.curId = id;
  const fresh = !S.P.srs[id];
  const lab = it.kind === "mot" && typeof MOT_LABEL === "object"
    ? (MOT_LABEL[it.t] || KIND_LABEL.mot) : KIND_LABEL[it.kind];
  $("seKind").innerHTML = lab + (fresh ? " · <b>nouvelle</b>" : "");
  $("seFoe").textContent = (FOE[typeof LANG !== "undefined" && LANG === "en" ? "en" : "fr"][it.kind]) || "Gardien de l’oubli";
  $("seNote").textContent = "";
  $("seCard").innerHTML = "";
  $("seAfter").innerHTML = "";
  progress();
  if(typeof vrHalt === "function") vrHalt();
  if("speechSynthesis" in window) speechSynthesis.cancel();

  draw(it.data);
}

function textInput(placeholder){
  const wrap = el("label", "fld");
  wrap.appendChild(el("span", null, "De mémoire"));
  const inp = el("input");
  inp.id = "seIn"; inp.className = "seinput"; inp.placeholder = placeholder;
  inp.autocomplete = "off"; inp.spellcheck = false;
  inp.addEventListener("keydown", (e) => {
    if(e.key === "Enter"){ e.preventDefault(); SE.answered ? nextCard() : submit(); }
  });
  wrap.appendChild(inp);
  $("seCard").appendChild(wrap);
  setTimeout(() => inp.focus(), 30);
  return inp;
}

/* ---------- le retour en direct ----------
   Ce qu'on tape se dessine dans la phrase, la longueur se voit, et la bonne
   réponse se valide toute seule. On ne dit jamais « cette lettre-là est
   bonne » : sinon on devine le mot lettre par lettre au lieu de le produire. */
function typedShape(want, typed){
  const w = String(want || ""), t = String(typed || "");
  return w.split("").map((ch, i) => {
    if(/\s/.test(ch)) return "\u2003";
    if(i < t.length) return t[i];
    if(!/[a-z\u00e0-\u00ff\u0153]/i.test(ch)) return ch;
    return "\u00b7";
  }).join("") + (t.length > w.length ? t.slice(w.length) : "");
}

function liveGauge(){
  const g = el("span", "livegauge");
  g.style.cssText = "font-family:'IBM Plex Mono',monospace;font-size:.68rem;"
    + "color:var(--ink-faint);font-variant-numeric:tabular-nums;margin-left:2px";
  return g;
}

function liveWire(inp, want, mirror, byWord){
  if(!inp || !want) return;
  const gauge = liveGauge();
  inp.parentNode.appendChild(gauge);
  const target = byWord ? dTok(want).length : String(want).length;
  const tick = () => {
    const v = inp.value;
    if(SE.answered) return;
    if(mirror) mirror.textContent = typedShape(want, v);
    const have = byWord ? dTok(v).length : v.length;
    gauge.textContent = have + " / " + target + (byWord ? " mots" : "");
    const over = have > target;
    gauge.style.color = over ? "var(--misplaced)" : "var(--ink-faint)";
    inp.style.borderColor = over ? "var(--misplaced)" : "";
    /* Tapé exactement juste, accents compris : on valide sans bouton. */
    if(v.trim() === String(want).trim()) setTimeout(() => { if(!SE.answered) submit(); }, 90);
  };
  inp.addEventListener("input", tick);
  tick();
}

function actions(list){
  const box = $("seAfter");
  box.innerHTML = "";
  list.forEach(([label, cls, fn]) => {
    const b = el("button", cls, label);
    b.addEventListener("click", fn);
    box.appendChild(b);
  });
}

/* ---- phrase à trou : on écrit d'abord, les propositions ne viennent qu'après ---- */
function cardTrou(c){
  const ph0 = scenePhoto(c);
  if(ph0) $("seCard").appendChild(ph0);
  else { const sc0 = scenePic(c, true); if(sc0) $("seCard").appendChild(sceneStrip(sc0)); }
  const [before, after] = c.s.split("___");
  const p = el("p", "sentence");
  const blank = el("span", "blank");
  blank.id = "seBlank";
  blank.textContent = wordShape(c.a, 0);
  blank.style.letterSpacing = ".2em";
  blank.style.fontFamily = '"IBM Plex Mono", monospace';
  blank.style.fontSize = ".88em";
  p.append(before, blank, after);
  $("seCard").appendChild(p);
  /* Le sens d'abord : retrouver le mot français qu'on veut dire, ce n'est pas deviner. */
  if(c.g) $("seCard").appendChild(el("p", "gloss", c.g));
  const inpT = textInput("le mot qui manque");
  liveWire(inpT, c.a, $("seBlank"), false);
  SE.hint = 0;
  actions([["Vérifier", "go", submit], ["Un indice", "ghost", trouHint]]);
}

/* Trois crans : une lettre, deux lettres, puis les propositions.
   Chaque cran se paie — la carte revient plus tôt. */
/* Quatre crans, du moins cher au plus cher :
   la nature du mot, la première lettre, la dernière + le son, les propositions. */
function wordKind(a){
  const w = String(a || "").trim();
  if(/(er|ir|re)$/.test(w) && w.split(" ").length === 1) return "un verbe à l'infinitif";
  if(/^(le |la |l'|un |une |des )/.test(w)) return "un nom";
  if(/(ment)$/.test(w)) return "un adverbe";
  if(/^(en |à |de |dans |sur |sous |pour |avec |sans )/.test(w)) return "une locution";
  return w.split(" ").length > 1 ? "une expression de " + w.split(" ").length + " mots" : "";
}

function shapeEnd(a){
  const s = wordShape(a, 1).split("");
  const last = String(a || "").length - 1;
  if(last > 1) s[last] = String(a)[last];
  return s.join("");
}

function trouHint(){
  if(SE.answered) return;
  const c = SE.cur.data;
  SE.hint = (SE.hint || 0) + 1;
  SE.helped = true;
  const en = typeof LANG !== "undefined" && LANG === "en";
  const b = $("seBlank");
  const cost = en ? " This card comes back sooner." : " Cette carte reviendra plus tôt.";

  if(SE.hint === 1){
    const k = wordKind(c.a);
    $("seNote").textContent = (k ? (en ? "It's " : "C'est ") + k + "." : "")
      + (en ? " " + String(c.a).replace(/[^ ]/g, "").length + "" : "") + cost;
    if(!k && b) b.textContent = wordShape(c.a, 1);
    return;
  }
  if(SE.hint === 2){ if(b) b.textContent = wordShape(c.a, 1); $("seNote").textContent =
    (en ? "First letter." : "La première lettre.") + cost; return; }
  if(SE.hint === 3){
    if(b) b.textContent = shapeEnd(c.a);
    speakFr(c.a, .85);
    $("seNote").textContent = (en ? "First and last letter, and you hear it."
      : "Première et dernière lettre, et tu l'entends.") + cost;
    return;
  }
  showOptions();
}

function showOptions(){
  if(SE.answered) return;
  SE.helped = true;
  const c = SE.cur.data;
  const box = el("div", "options");
  const opts = [c.a, ...c.d];
  for(let i = opts.length - 1; i > 0; i--){ const j = (Math.random() * (i + 1)) | 0; [opts[i], opts[j]] = [opts[j], opts[i]]; }
  opts.forEach(w => {
    const b = el("button", "opt", w);
    b.addEventListener("click", () => { $("seIn").value = w; submit(); });
    box.appendChild(b);
  });
  $("seCard").appendChild(box);
  $("seNote").textContent = "Reconnaître coûte moins que retrouver : cette carte reviendra plus tôt.";
  actions([["Vérifier", "go", submit]]);
}

/* ---- conjugaison : production pure ---- */
function cardConj(f){
  const p = el("p", "xclue");
  p.innerHTML = "<b>" + f.v + "</b> · " + (f.p ? f.p + " · " + f.t : f.t);
  $("seCard").appendChild(p);
  liveWire(textInput("la forme conjuguée"), f.a, null, false);
  actions([["Vérifier", "go", submit], ["Un indice", "ghost", () => {
    if(SE.answered) return;
    SE.helped = true;
    $("seIn").value = SE.cur.data.a.slice(0, 2);
    $("seIn").focus();
    $("seNote").textContent = "Deux lettres données.";
  }]]);
}

/* ---- genre ---- */
function cardGenre(g){
  $("seCard").appendChild(el("p", "noun", g.n));
  const cue = el("p", "gloss");
  cueInto(cue, g.n, g.t);
  $("seCard").appendChild(cue);
  const box = el("div", "artchoice");
  ["le", "la"].forEach(a => {
    const b = el("button", "art", a);
    b.addEventListener("click", () => { if(!SE.answered) seJudge(a === "le" ? "m" : "f", g.g, b); });
    box.appendChild(b);
  });
  $("seCard").appendChild(box);
  $("seAfter").innerHTML = "";
}

/* ---- paire minimale : on entend ou on n'entend pas ---- */
function cardSon(p){
  const said = Math.random() < .5 ? p.a : p.b;
  SE.said = said;
  const row = el("div", "dplay");
  const play = el("button", "dbig", "\u25b6 \u00c9couter");
  play.addEventListener("click", () => speakFr(said, .9));
  const slow = el("button", "ghost", "Lentement");
  slow.addEventListener("click", () => speakFr(said, .55));
  row.append(play, slow);
  $("seCard").appendChild(row);
  const box = el("div", "artchoice");
  [p.a, p.b].forEach(w => {
    const b = el("button", "art", w);
    b.addEventListener("click", () => { if(!SE.answered) seJudge(w, said, b); });
    box.appendChild(b);
  });
  $("seCard").appendChild(box);
  $("seAfter").innerHTML = "";
  setTimeout(() => speakFr(said, .9), 140);
}

/* ---- tes cartes, façon Fluent Forever ---- */
function cardMot(m){
  const t = (SE.cur && SE.cur.t) || "p";
  if(t === "r") return cardFiche(m);
  if(t === "g"){
    const n = el("p", "noun", m.fr);
    n.lang = "fr";
    $("seCard").appendChild(n);
    if(m.pic) $("seCard").appendChild(el("p", "motpic small", m.pic));
    const box = el("div", "artchoice");
    ["le", "la"].forEach(a => {
      const b = el("button", "art", a);
      b.lang = "fr";
      b.addEventListener("click", () => { if(!SE.answered) seJudge(a === "le" ? "m" : "f", m.g, b); });
      box.appendChild(b);
    });
    $("seCard").appendChild(box);
    $("seAfter").innerHTML = "";
    return;
  }
  const said = artOf(m) + m.fr;
  if(t === "s"){
    /* Le son et l'image ensemble : l'image lève les homophones (verre, vert, ver). */
    if(m.pic) $("seCard").appendChild(picPlate(m.pic, m.fr, 96, m.img));
    const row = el("div", "dplay");
    const play = el("button", "dbig", "▶ Écouter");
    play.addEventListener("click", () => speakFr(said, .9));
    const slow = el("button", "ghost", "Lentement");
    slow.addEventListener("click", () => speakFr(said, .55));
    row.append(play, slow);
    $("seCard").appendChild(row);
    setTimeout(() => speakFr(said, .9), 140);
  }else{
    if(m.pic) $("seCard").appendChild(picPlate(m.pic, m.fr, null, m.img));
    if(m.note){
      const n = el("p", "gloss", m.note);
      n.dataset.keep = "1";
      $("seCard").appendChild(n);
    }
  }
  liveWire(textInput(m.g ? "le mot, avec son article" : "le mot"),
    (typeof artOf === "function" ? artOf(m) : "") + m.fr, null, false);
  actions([["Vérifier", "go", submit]]);
}

/* ---- la fiche : le mot, vu et entendu ; on retourne, on se note ---- */
function cardFiche(m){
  const said = artOf(m) + m.fr;
  const f = el("div", "fiche");
  const face = el("div", "fiche-face");
  const w = el("p", "fiche-mot", said);
  w.lang = "fr";
  const say = el("button", "fiche-say", "▶");
  say.type = "button";
  say.setAttribute("aria-label", "Écouter");
  say.title = "Écouter";
  say.addEventListener("click", () => speakFr(said, .9));
  face.append(w, say);
  f.appendChild(face);
  f.appendChild(el("p", "fiche-ask",
    "Qu’est-ce que c’est ? Vois l’image dans ta tête, puis retourne la fiche."));
  $("seCard").appendChild(f);
  actions([["Retourner la fiche", "go", ficheFlip]]);
  const b = $("seAfter").firstChild;
  if(b) setTimeout(() => b.focus(), 30);
  setTimeout(() => speakFr(said, .9), 140);
}

function ficheFlip(){
  if(!SE || SE.flipped || SE.answered) return;
  SE.flipped = true;
  const m = SE.cur.data;
  const f = $("seCard").querySelector(".fiche");
  if(!f) return;
  const ask = f.querySelector(".fiche-ask");
  if(ask) ask.remove();
  const back = el("div", "fiche-back");
  if(m.pic) back.appendChild(picPlate(m.pic, m.fr, 132, m.img));
  if(m.note){
    const n = el("p", "fiche-note", m.note);
    n.dataset.keep = "1";
    back.appendChild(n);
  }
  if(m.g){
    const c = el("p", "gcue");
    genderCue(c, m.fr, m.g);
    back.appendChild(c);
  }
  if(!m.pic && !m.note) back.appendChild(el("p", "fiche-note", "Pas d’image sur cette carte — ajoute-en une dans Mes cartes."));
  f.appendChild(back);
  f.classList.add("flipped");

  const box = $("seAfter");
  box.innerHTML = "";
  const grades = el("div", "grades");
  [["Raté", 1, "g1"], ["Difficile", 3, "g3"], ["Bien", 4, "g4"], ["Facile", 5, "g5"]].forEach(([lab, q, cls]) => {
    const b = el("button", "grade " + cls);
    b.type = "button";
    b.appendChild(el("span", "grade-lab", lab));
    b.appendChild(el("span", "grade-iv", q < 3 ? "dans un instant" : ivText(srsPreview(SE.curId, q))));
    b.addEventListener("click", () => {
      if(SE.answered) return;
      seJudge(q >= 3 ? "ok" : "no", "ok", null, null, q);
    });
    grades.appendChild(b);
  });
  box.appendChild(grades);
  const good = grades.querySelector(".g4");
  if(good) good.focus();
}

/* « demain », « dans 3 j », « dans 2 mois » */
function ivText(d){
  const en = typeof LANG !== "undefined" && LANG === "en";
  if(d <= 1) return en ? "tomorrow" : "demain";
  if(d < 30) return en ? "in " + d + " days" : "dans " + d + " j";
  if(d < 365){ const mo = Math.round(d / 30); return en ? "in " + mo + " mo" : "dans " + mo + " mois"; }
  return en ? "in a year" : "dans un an";
}

/* Juste si le mot est juste ; si tu donnes un article, il doit être le bon. */
function motCheck(v, m){
  const sp = splitArt(v);
  const wordOk = same(sp.word, m.fr);
  const artWrong = !!(sp.g && m.g && sp.g !== m.g);
  return {ok:wordOk && !artWrong, wordOk, artWrong, bare:!sp.g && !/^l['’]/i.test(v.trim()),
    accent:!wordOk && accentOnly(sp.word, m.fr)};
}

/* ---- toute la phrase : le rappel le plus exigeant du cahier ----
   On donne l'anglais, on écrit le français en entier. */
function cardTrad(c){
  const full = c.s.replace("___", c.a);
  SE.want = full;
  const phT = scenePhoto(c);
  if(phT) $("seCard").appendChild(phT);
  else { const scT = scenePic(c, false); if(scT) $("seCard").appendChild(sceneStrip(scT)); }
  $("seCard").appendChild(el("p", "phtask", c.g || ""));
  const wrap = el("label", "fld");
  wrap.appendChild(el("span", null, "La phrase française, en entier"));
  const ta = el("textarea");
  ta.id = "seIn"; ta.className = "seinput"; ta.rows = 3; ta.spellcheck = false;
  ta.addEventListener("keydown", (e) => {
    if(e.key === "Enter" && !e.shiftKey){ e.preventDefault(); SE.answered ? nextCard() : submit(); }
  });
  wrap.appendChild(ta);
  $("seCard").appendChild(wrap);
  liveWire(ta, full, null, true);
  SE.hint = 0;
  actions([["Vérifier", "go", submit], ["Un indice", "ghost", () => {
    if(SE.answered) return;
    SE.helped = true;
    SE.hint = (SE.hint || 0) + 1;
    const en = typeof LANG !== "undefined" && LANG === "en";
    const words = full.split(" ");
    const show = Math.min(words.length - 1, SE.hint * 2);
    $("seNote").textContent = words.slice(0, show).join(" ") + " …"
      + (en ? "  This card comes back sooner." : "  Cette carte reviendra plus tôt.");
  }]]);
  setTimeout(() => ta.focus(), 30);
}

/* ---- dictée ---- */
function cardDictee(c){
  const text = c.s.replace("___", c.a);
  SE.heard = text;
  const row = el("div", "dplay");
  const play = el("button", "dbig", "▶ Écouter");
  play.addEventListener("click", () => speakFr(text, .95));
  const slow = el("button", "ghost", "Lentement");
  slow.addEventListener("click", () => speakFr(text, .6));
  row.append(play, slow);
  $("seCard").appendChild(row);
  const wrap = el("label", "fld");
  wrap.appendChild(el("span", null, "Ce que tu entends"));
  const ta = el("textarea");
  ta.id = "seIn"; ta.rows = 2; ta.spellcheck = false;
  ta.addEventListener("keydown", (e) => {
    if(e.key === "Enter" && !e.shiftKey){ e.preventDefault(); SE.answered ? nextCard() : submit(); }
  });
  wrap.appendChild(ta);
  $("seCard").appendChild(wrap);
  liveWire(ta, text, null, true);
  actions([["Corriger", "go", submit]]);
  setTimeout(() => { speakFr(text, .95); ta.focus(); }, 120);
}

/* ---- l'ordre : la phrase entière, mot à mot ----
   Même règle que le panneau : un mot bien posé verdit, un mot mal posé
   jaunit sans dire où il allait. Reprendre un mot coûte comme une aide. */
function cardOrdre(c){
  const text = c.s.replace("___", c.a);
  const want = dTok(text);
  SE.ord = {text, want, placed:[], bank:shuffleIds(want.map((w, k) => ({w, k}))), slips:0};
  const phO = scenePhoto(c);
  if(phO) $("seCard").appendChild(phO);
  else { const scO = scenePic(c, false); if(scO) $("seCard").appendChild(sceneStrip(scO)); }
  if(c.g) $("seCard").appendChild(el("p", "phtask", c.g));
  const gauge = el("p", "orgauge"), line = el("div", "orline"), bank = el("div", "orbank");
  $("seCard").append(gauge, line, bank);
  const o = SE.ord;
  const right = (i) => o.placed[i] && o.placed[i].w === o.want[i];
  const full = () => o.placed.length === o.want.length;
  const paint = () => {
    line.innerHTML = "";
    o.placed.forEach((tk, i) => {
      const b = el("button", "orchip " + (right(i) ? "ok" : "off"), tk.w);
      b.type = "button"; b.lang = "fr";
      b.addEventListener("click", () => {
        if(SE.answered) return;
        o.placed.splice(i, 1); o.bank.push(tk); paint();
      });
      line.appendChild(b);
    });
    for(let i = o.placed.length; i < o.want.length; i++) line.appendChild(el("span", "orslot"));
    bank.innerHTML = "";
    o.bank.forEach((tk, i) => {
      const b = el("button", "orchip", tk.w);
      b.type = "button"; b.lang = "fr";
      b.addEventListener("click", () => {
        if(SE.answered) return;
        o.bank.splice(i, 1); o.placed.push(tk);
        if(tk.w !== o.want[o.placed.length - 1]) o.slips++;
        paint();
        /* Phrase complète et entièrement juste : inutile de faire cliquer en plus. */
        if(full() && o.placed.every((_, k) => right(k)))
          setTimeout(() => { if(!SE.answered) ordreSubmit(); }, 120);
      });
      bank.appendChild(b);
    });
    gauge.textContent = o.placed.filter((_, i) => right(i)).length + " / " + o.want.length + " en place";
  };
  paint();
  actions([["Vérifier", "go", ordreSubmit], ["Un mot", "ghost", () => {
    if(SE.answered || full()) return;
    const j = o.bank.findIndex(tk => tk.w === o.want[o.placed.length]);
    if(j < 0) return;
    SE.helped = true;
    o.placed.push(o.bank.splice(j, 1)[0]);
    paint();
    $("seNote").textContent = "Un mot donné — le rappel compte moins.";
    if(full()) setTimeout(() => { if(!SE.answered) ordreSubmit(); }, 120);
  }]]);
}

function ordreSubmit(){
  if(!SE || SE.answered || !SE.ord) return;
  const o = SE.ord;
  if(o.placed.length !== o.want.length){ $("seNote").textContent = "Place tous les mots d'abord."; return; }
  const ok = o.placed.every((tk, i) => tk.w === o.want[i]);
  if(o.slips) SE.helped = true;
  seJudge(ok ? "ok" : "no", "ok", null, ok ? null : "La phrase était « " + o.text + " »");
  [...$("seCard").querySelectorAll(".orchip")].forEach(b => { b.disabled = true; });
  /* On entend toujours la phrase juste à la fin : la prosodie fixe l'ordre. */
  setTimeout(() => speakFr(o.text, .95), 220);
}

/* ---- décider : deux formes justes, une seule qui dit ce que tu veux ----
   Sur une question de sens, on annonce d'abord l'intention ; c'est elle
   qui impose la forme. Se tromper, c'est dire autre chose que prévu. */
function cardDecider(d){
  SE.dec = {step:d.k === "sens" ? 1 : 2, mean:-1, want:-1};
  $("seCard").appendChild(el("p", "orgauge", d.tag));
  const stem = el("p", "sentence");
  stem.lang = "fr";
  stem.innerHTML = d.stem;
  const q = el("p", "ydq"), box = el("div", "ydopts");
  $("seCard").append(stem, q, box);
  const paint = () => {
    box.innerHTML = "";
    if(SE.dec.step === 1){
      q.textContent = "Qu'est-ce que tu veux dire ?";
      d.means.forEach((m, n) => box.appendChild(decBtn(m, false, () => {
        SE.dec.mean = n; SE.dec.step = 2; paint();
      })));
    }else{
      if(d.k === "sens"){
        q.innerHTML = "";
        q.append("Tu veux dire : ", el("i", null, d.means[SE.dec.mean]), ". Quelle forme ?");
      }else q.textContent = "Quelle forme passe ?";
      (d.k === "sens" ? d.forms : d.opts).forEach((o, n) => box.appendChild(decBtn(o, true, () => deciderPick(n))));
    }
  };
  paint();
  $("seAfter").innerHTML = "";
}

function decBtn(label, code, fn){
  const b = el("button", "ydopt" + (code ? " code" : ""));
  b.type = "button"; b.lang = "fr";
  b.innerHTML = label;
  b.addEventListener("click", () => { if(!SE.answered) fn(); });
  return b;
}

function deciderPick(n){
  const d = SE.cur.data;
  const want = d.k === "sens" ? SE.dec.mean : d.ok;
  SE.dec.want = want;
  const ok = n === want;
  [...$("seCard").querySelectorAll(".ydopt")].forEach((b, i) => {
    b.disabled = true;
    if(i === want) b.classList.add("ok");
    else if(i === n) b.classList.add("no");
  });
  seJudge(ok ? "ok" : "no", "ok", null, d.k === "sens"
    ? (ok ? "La forme suit bien ton intention." : "Cette forme est correcte, mais elle dit l'autre chose.")
    : null);
}

function deciderAfter(d){
  const want = SE.dec && SE.dec.want >= 0 ? SE.dec.want : d.ok;
  const why = el("p", "ydwhy");
  why.innerHTML = (d.k === "sens" ? d.why[want] : d.why)
    + ((typeof DEC_EN === "object" && DEC_EN[d.tag]) ? '<span class="ydwhyen">' + DEC_EN[d.tag] + "</span>" : "");
  $("seCard").appendChild(why);
  if(d.k === "sens" && /^[A-ZÀ-Ý]/.test(d.forms[want])) setTimeout(() => speakFr(d.forms[want], .95), 200);
}

/* ---- imiter : l'ombre de la voix ----
   On entend, on redit au même rythme, on se note. La séance ne juge pas
   un accent à ta place : la note est la tienne. */
function cardImiter(c){
  const text = c.s.replace("___", c.a);
  SE.want = text;
  const p = el("p", "sentence imtext");
  p.lang = "fr"; p.textContent = text;
  $("seCard").appendChild(p);
  const row = el("div", "dplay");
  const play = el("button", "dbig", "▶ Écouter");
  play.addEventListener("click", () => speakFr(text, 1));
  const slow = el("button", "ghost", "Lentement");
  slow.addEventListener("click", () => speakFr(text, .75));
  row.append(play, slow);
  $("seCard").appendChild(row);
  if(typeof imRecorderRow === "function"){
    const heard = el("div", "imheard");
    imRecorderRow($("seCard"), text, () => 1, () => (S.P.imiter && S.P.imiter.mode) || "apres",
      (r) => {
        if(r.heard && typeof imHeardInto === "function")
          SE.imHit = {hit:imHeardInto(heard, text, r.heard), n:dTok(text).length};
      });
    $("seCard").appendChild(heard);
  }
  SE.imHit = null;
  $("seCard").appendChild(el("p", "fiche-ask", "Redis-la à voix haute, au même rythme. Puis note-toi."));
  const box = $("seAfter");
  box.innerHTML = "";
  const grades = el("div", "grades");
  [["Raté", 1, "g1"], ["Difficile", 3, "g3"], ["Bien", 4, "g4"], ["Facile", 5, "g5"]].forEach(([lab, q, cls]) => {
    const b = el("button", "grade " + cls);
    b.type = "button";
    b.appendChild(el("span", "grade-lab", lab));
    b.appendChild(el("span", "grade-iv", q < 3 ? "dans un instant" : ivText(srsPreview(SE.curId, q))));
    b.addEventListener("click", () => {
      if(SE.answered) return;
      /* La transcription a entendu moins de six mots sur dix : pas plus que « Difficile ». */
      let qq = q;
      const h = SE.imHit;
      if(h && h.n && h.hit / h.n < .6 && qq > 3) qq = 3;
      seJudge(qq >= 3 ? "ok" : "no", "ok", null,
        qq !== q ? "Reconnu " + h.hit + "/" + h.n + " mots : la note plafonne à « Difficile »." : null, qq);
    });
    grades.appendChild(b);
  });
  box.appendChild(grades);
  setTimeout(() => speakFr(text, 1), 140);
}

/* ---- évaluation ---- */
function submit(){
  if(SE.answered) return;
  const it = SE.cur, v = ($("seIn") || {}).value || "";
  if(!v.trim()){ $("seNote").textContent = "Écris ta réponse — même une tentative compte."; return; }

  if(it.kind === "trad"){
    const exp = dTok(SE.want), got = dTok(v);
    let hit = 0;
    exp.forEach((w, n) => { if(got[n] && phon(got[n]) === phon(w)) hit++; });
    const ratio = hit / exp.length;
    return seJudge(ratio >= .85 ? "ok" : "no", "ok", null,
      ratio >= .85 ? "" : hit + "/" + exp.length + " mots — « " + SE.want + " »");
  }

  if(it.kind === "dictee"){
    const exp = dTok(SE.heard), got = dTok(v);
    let hit = 0;
    exp.forEach((w, n) => { if(got[n] && phon(got[n]) === phon(w)) hit++; });
    const perfect = hit === exp.length && got.length === exp.length;
    return seJudge(perfect ? "ok" : "no", "ok", null,
      perfect ? "" : hit + "/" + exp.length + " mots — « " + SE.heard + " »");
  }

  if(it.kind === "mot"){
    if(it.t === "g" || it.t === "r") return;
    const m = it.data, full = artOf(m) + m.fr, r = motCheck(v, m);
    return seJudge(r.ok ? "ok" : "no", "ok", null,
      r.ok ? (it.t === "p" && m.g && r.bare ? "Avec son article, la prochaine fois : « " + full + " »." : null)
      : r.artWrong ? "Le mot est juste, le genre non : « " + full + " »."
      : r.accent ? "Les accents comptent : « " + full + " »"
      : "La réponse était « " + full + " »");
  }
  const want = it.data.a;
  const ok = same(v, want);
  seJudge(ok ? "ok" : "no", "ok", null,
    ok ? null : (accentOnly(v, want) ? "Les accents comptent : « " + want + " »"
                                     : "La réponse était « " + want + " »"));
}

function seJudge(given, want, btn, msg, qForce){
  SE.answered = true;
  const ok = given === want;
  const ms = Date.now() - SE.t0;
  const dd = SE.cur.data || {};
  const expect = SE.cur.kind === "trad" ? SE.want : SE.cur.kind === "dictee" ? SE.heard
    : SE.cur.kind === "mot" ? dd.fr : SE.cur.kind === "ordre" ? (SE.ord && SE.ord.text) : (dd.a || "");
  const q = qForce || srsGrade(ok, ms, SE.helped, String(expect || "").length);
  const xp0 = (S.P.hero && S.P.hero.xp) || 0;
  const iv = srsUpdate(SE.curId, q);
  const gained = ((S.P.hero && S.P.hero.xp) || 0) - xp0;
  const leech = typeof isLeech === "function" && isLeech(SE.curId);
  noteLevel(SE.curId, ok);
  SE.done++;
  if(ok) SE.right++;
  if(!ok) SE.q.splice(Math.min(SE.i + SRS_RELEARN, SE.q.length), 0, SE.curId);

  const blank = $("seBlank");
  if(blank && SE.cur.data && SE.cur.data.a){
    blank.textContent = SE.cur.data.a;
    blank.classList.add("done", ok ? "ok" : "no");
  }
  if(btn) btn.classList.add(ok ? "right" : "wrong");
  if(SE.cur.kind === "genre" || (SE.cur.kind === "mot" && SE.cur.t === "g")){
    [...$("seCard").querySelectorAll(".artchoice .art")].forEach(b => {
      b.disabled = true;
      if((b.textContent === "le") === (SE.cur.data.g === "m")) b.classList.add("right");
    });
  }
  const inp = $("seIn");
  if(inp){ inp.readOnly = true; inp.classList.add(ok ? "ok" : "no"); }

  const vb = el("div", "verdict " + (ok ? "good" : "bad"));
  vb.append(el("span", "vmark", ok ? "\u2713" : "\u2715"),
    el("span", null, ok ? "Juste." : "Rat\u00e9."));
  if(gained > 0) vb.appendChild(el("span", "xpfloat", "+" + gained + " XP"));
  $("seCard").insertBefore(vb, $("seCard").firstChild);

  const tail = ok ? (iv === 1 ? "Revue demain." : "Revue dans " + iv + " jours.")
    : leech ? "Sangsue : rat\u00e9e six fois, elle s'endort. Refais-la autrement, ou r\u00e9veille-la dans Le Profil."
    : "Elle revient dans un instant.";
  $("seNote").innerHTML = (ok ? "Juste. " : "Raté. ") + (msg ? msg + " " : "") + "<i>" + tail + "</i>";

  const d = SE.cur.data;
  if(SE.cur.kind === "son"){
    const c = CONTRASTS.find(x => x.k === d.c);
    $("seCard").appendChild(el("p", "gloss", (c ? c.why : "") ));
  }else if(SE.cur.kind === "mot"){
    if(SE.cur.t !== "r"){
      if(d.pic) $("seCard").appendChild(picPlate(d.pic, d.fr, 108, d.img));
      const a = el("p", "fiche-ans");
      a.lang = "fr";
      a.textContent = artOf(d) + d.fr;
      $("seCard").appendChild(a);
      if(d.note && SE.cur.t !== "p"){
        const n = el("p", "gloss", d.note);
        n.dataset.keep = "1";
        $("seCard").appendChild(n);
      }
      if(d.g){
        const c = el("p", "gcue");
        genderCue(c, d.fr, d.g);
        $("seCard").appendChild(c);
      }
    }
  }else if(SE.cur.kind === "genre"){
    const g = el("p", "rule");
    g.innerHTML = "<b>" + (d.g === "m" ? "le " : "la ") + d.n + "</b> — " + d.r;
    $("seCard").appendChild(g);
    const c = el("p", "gcue");
    genderCue(c, d.n, d.g);
    $("seCard").appendChild(c);
  }else if(SE.cur.kind === "conj"){
    $("seCard").appendChild(el("p", "gloss",
      d.v + " · " + (d.p ? d.p + " · " : "") + d.t + " → " + d.a));
  }else if(SE.cur.kind === "decider"){
    deciderAfter(d);
  }else if(d.g && SE.cur.kind !== "ordre"){
    $("seCard").appendChild(el("p", "gloss", d.g));
  }

  if(!ok) $("seCard").appendChild(referBack(SE.cur, SE.curId));

  /* Le coup porte, ou il revient sur soi. */
  const bar = $("seBar");
  if(bar){ bar.classList.remove("hit"); void bar.offsetWidth; if(ok) bar.classList.add("hit"); }
  if(!ok){
    SE.misses = (SE.misses || 0) + 1;
    const card = $("seCard");
    card.classList.remove("shake"); void card.offsetWidth; card.classList.add("shake");
  }
  progress();

  paintMargin(); save();
  /* La phrase juste, dite par la vraie voix : on entend ce qu'on vient d'écrire. */
  const say = (SE.cur.kind === "trou" || SE.cur.kind === "trad") && dd.s && dd.a ? dd.s.replace("___", dd.a)
    : SE.cur.kind === "ordre" && SE.ord ? SE.ord.text : "";
  actions(say ? [["Suivante", "go", nextCard], ["▶ Écouter", "ghost", () => speakFr(say, .95)]]
    : [["Suivante", "go", nextCard]]);
  if(say && typeof speakFr === "function") speakFr(say, .95);
  if(!ok && SE.cur.kind !== "mot" && typeof missButton === "function"){
    const miss = SE.cur.kind === "mot" ? SE.cur.data.fr
      : SE.cur.kind === "son" ? SE.said
      : (SE.cur.data && SE.cur.data.a) || "";
    missButton($("seAfter"), miss);
  }
  const next = $("seAfter").firstChild;
  if(next) next.focus();
}

function nextCard(){
  SE.i++;
  if(SE.i >= SE.q.length) return finish(false);
  renderCard();
}

function finish(empty){
  const st = srsStats();
  $("seKind").textContent = "";
  $("seAfter").innerHTML = "";
  $("seNote").textContent = "";
  $("seCard").innerHTML = "";
  $("seFill").style.width = "0%";
  $("seFoe").textContent = typeof LANG !== "undefined" && LANG === "en" ? "Guardian of forgetting" : "Gardien de l’oubli";
  $("seCount").textContent = (typeof LANG !== "undefined" && LANG === "en" ? "HP " : "PV ") + "0";
  paintHearts();

  const mine = SE && SE.only === "mot";
  const h = el("p", "sedone", empty
    ? (mine ? "Ton paquet est à jour pour aujourd'hui." : "Rien à revoir aujourd'hui.")
    : (mine ? "Tes cartes sont faites." : "Victoire !"));
  $("seCard").appendChild(h);
  if(mine && empty && !(S.mots || []).length){
    $("seCard").appendChild(el("p", "lede",
      "Ton paquet est vide. Ajoute un thème du socle ou fabrique ta première carte dans Mes cartes."));
  }

  if(!empty){
    const pct = SE.done ? Math.round(SE.right / SE.done * 100) : 0;
    $("seCard").appendChild(el("p", "lede",
      SE.done + " rappels, " + pct + "% réussis du premier coup. "
      + SE.due + " en révision, " + SE.fresh + " nouvelle" + (SE.fresh > 1 ? "s" : "") + "."));

    /* Le bilan : ce que la séance a rapporté, et où en sont les quêtes et l'anneau. */
    const en = typeof LANG !== "undefined" && LANG === "en";
    const gained = ((S.P.hero && S.P.hero.xp) || 0) - (SE.xp0 || 0);
    const wrap = el("div", "sewrap");
    wrap.appendChild(el("span", "sexp", "+" + Math.max(0, gained) + " XP"));
    if(typeof todayQuests === "function" && typeof heroDay === "function"){
      const d = heroDay();
      todayQuests().forEach(qu => {
        const got = Math.min(qu.n, d[qu.k] || 0);
        const s = el("span", "seq");
        s.innerHTML = (got >= qu.n ? "<b>✓</b> " : "○ ") + (en ? qu.en : qu.fr) + " · " + got + "/" + qu.n;
        wrap.appendChild(s);
      });
    }
    if(typeof ringState === "function"){
      const r = ringState();
      wrap.appendChild(el("span", "seq", r.closed ? (en ? "Ring closed" : "Anneau fermé")
        : (en ? "Ring " : "Anneau ") + r.done + "/" + r.target));
    }
    $("seCard").appendChild(wrap);
  }
  if(SE.comeback && SE.left){
    $("seCard").appendChild(el("p", "lede dim", "Reprise douce après " + SE.comeback.away
      + " jours : " + SE.left + " autres cartes attendent demain. Rien n'est perdu."));
  }
  if(Array.isArray(S.intakeHeld) && S.intakeHeld.length){
    $("seCard").appendChild(el("p", "lede dim", "Pas de carte neuve aujourd'hui en "
      + S.intakeHeld.map(k => (KIND_LABEL[k] || k).toLowerCase()).join(", ")
      + " : la rétention est sous 70 % sur trente jours. Les cartes dues suffisent."));
  }

  const fc = srsForecast(7);
  const max = Math.max(1, ...fc);
  const chart = el("div", "forecast");
  const days = ["dem.", "+2", "+3", "+4", "+5", "+6", "+7"];
  fc.forEach((n, i) => {
    const col = el("div", "fcol");
    const bar = el("div", "fbar");
    bar.style.height = Math.round(n / max * 54) + "px";
    bar.title = n + " carte" + (n > 1 ? "s" : "");
    col.append(el("span", "fnum", n || ""), bar, el("span", "flab", days[i]));
    chart.appendChild(col);
  });
  $("seCard").appendChild(el("p", "fchead", "Ce qui revient"));
  $("seCard").appendChild(chart);

  $("seCard").appendChild(el("p", "lede dim",
    st.learned + " cartes sur " + st.total + " sont entrées dans le cycle"
    + (st.retention != null ? " · " + st.retention + "% de rappel depuis le début" : "")
    + (st.fresh ? " · " + st.fresh + " nouvelles encore disponibles aujourd'hui" : "")));

  if(S.P.promoted){
    const up = el("p", "promote", "Palier franchi — tu passes en " + S.P.promoted + ".");
    $("seCard").insertBefore(up, $("seCard").firstChild);
    S.P.promoted = null;
  }
  $("seCard").appendChild(el("p", "lede dim", gateText()));
  $("seRestart").hidden = false;
  paintMargin(); save();
}

/* Au clavier : 1 à 4 pour se noter, Entrée ou espace pour la carte suivante.
   Jamais quand on est en train d'écrire dans un champ. */
document.addEventListener("keydown", (e) => {
  if(S.mode !== "seance" || !SE || e.metaKey || e.ctrlKey || e.altKey) return;
  if(document.querySelector(".modal:not([hidden])")) return;
  const tag = (e.target && e.target.tagName) || "";
  if(tag === "INPUT" || tag === "TEXTAREA" || tag === "SELECT") return;
  const after = $("seAfter");
  const grades = after && after.querySelector(".grades");
  if(grades && /^[1-4]$/.test(e.key)){
    const b = grades.children[+e.key - 1];
    if(b){ e.preventDefault(); b.click(); }
    return;
  }
  if((e.key === "Enter" || e.key === " ") && SE.answered){
    const go = after && after.querySelector(".go");
    if(go){ e.preventDefault(); go.click(); }
  }
});
