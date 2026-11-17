/* Le Cahier — niveau : test de placement adaptatif et palier de maîtrise */

const LEVELS = ["A1", "A2", "B1", "B2", "C1", "C2"];
const TENSE_LV = {"présent":1, "participe passé":2, "imparfait":2, "futur":3,
  "conditionnel":4, "subjonctif":5, "passé simple":5, "subjonctif imparfait":6};

const TROU_LV = {t1:1, t2:1, t3:1, t4:2, t5:2, t6:1, t7:2, t8:2, t9:1, t10:1,
  t11:2, t12:2, t13:4, t14:2, t15:5, t16:2, t17:3, t18:2, t19:3, t20:3,
  t21:2, t22:1, t23:3, t24:2, t25:3, t26:4, t27:4, t28:3,
  t29:4, t30:5, t31:4, t32:5, t33:4, t34:5, t35:5, t36:6, t37:5, t38:5, t39:6, t40:6};

const GENRE_LV = [2,2,2,3,1,2,3,2,3,2,1,1,2,3,2,3,3,3,1,1,1,2,1,2,1,2,2,3,1,1,2,1];

function levelOf(id){
  if(id[0] === "m") return 1;
  if(id[0] === "w"){ const m = motById(id); return (m && m.lv) || 2; }
  if(id[0] === "k"){ const f = POOL[+id.slice(1)]; return f ? (TENSE_LV[f.t] || 3) : 3; }
  if(id[0] === "g"){ const v = GENRE_LV[+id.slice(1)]; return v || 2; }
  if(id[0] === "s") return Math.min(6, levelOf(id.slice(1)) + 1);
  if(id[0] === "x") return Math.min(6, levelOf(id.slice(1)) + 1);
  if(id[0] === "o" || id[0] === "i") return levelOf(id.slice(1));
  if(id[0] === "y"){ const d = (typeof DECIDE !== "undefined") ? DECIDE[+id.slice(1)] : null; return (d && d.lv) || 3; }
  if(TROU_LV[id]) return TROU_LV[id];
  const c = ALL().find(i => i.id === id);
  return (c && c.lv) || 3;
}

/* Le palier ne s'ouvre pas sur une bonne journée : il faut un taux de rappel
   tenu sur la durée ET des cartes qui ont survécu à une semaine d'oubli. */
const GATE_N = 20, GATE_ACC = .85, GATE_HELD = 12, GATE_DAYS = 7;

function gate(){
  const lv = S.P.level, h = S.P.lvHist || [];
  const n = h.length, ok = h.filter(Boolean).length;
  let held = 0;
  registry().forEach(it => {
    const s = S.P.srs[it.id];
    if(s && s[1] >= GATE_DAYS && levelOf(it.id) === lv) held++;
  });
  const acc = n ? ok / n : 0;
  return {n, acc, held, lv,
    open: n >= GATE_N && acc >= GATE_ACC && held >= GATE_HELD && lv < LEVELS.length};
}

function noteLevelRaw(ok){
  S.P.lvHist.push(ok ? 1 : 0);
  while(S.P.lvHist.length > 25) S.P.lvHist.shift();
  const g = gate();
  if(g.open){
    S.P.level++;
    S.P.lvHist = [];
    S.P.promoted = LEVELS[S.P.level - 1];
  }
}

function noteLevel(id, ok){
  if(levelOf(id) === S.P.level) noteLevelRaw(ok);
}

function gateText(){
  const g = gate();
  if(g.lv >= LEVELS.length) return "Niveau C2 — le dernier. Les cartes continuent, "
    + "le palier s'arrête ici.";
  return "Pour passer en " + LEVELS[g.lv] + " : " + g.n + "/" + GATE_N + " rappels à ce niveau · "
    + Math.round(g.acc * 100) + "% (il en faut " + Math.round(GATE_ACC * 100) + ") · "
    + g.held + "/" + GATE_HELD + " cartes tenues une semaine.";
}

/* ---------- test de placement ---------- */
let NT = null;

function hasVoice(){ return typeof dVoice === "function" && !!dVoice(); }

function testPool(lv){
  const voice = hasVoice();
  return registry().filter(it =>
    (it.kind === "trou" || it.kind === "conj" || (it.kind === "dictee" && voice))
    && levelOf(it.id) === lv);
}

function startTest(){
  NT = {i:0, lv:2, seen:[], path:[], answered:false, n:12, phase:null, probing:false, lastKind:null};
  $("nvCheck").textContent = "Valider";
  $("nvIntro").hidden = true;
  $("nvResult").hidden = true;
  $("nvTest").hidden = false;
  testCard();
}

function testCard(){
  let pool = testPool(NT.lv).filter(it => !NT.seen.includes(it.id));
  for(let d = 1; !pool.length && d <= 4; d++){
    pool = testPool(Math.min(5, NT.lv + d)).concat(testPool(Math.max(1, NT.lv - d)))
      .filter(it => !NT.seen.includes(it.id));
  }
  if(!pool.length) return endTest();

  const varied = pool.filter(it => it.kind !== NT.lastKind);
  const use = varied.length ? varied : pool;
  const pick = use[(Math.random() * use.length) | 0];
  NT.lastKind = pick.kind;
  NT.seen.push(pick.id);
  NT.path.push(NT.lv);
  NT.cur = srsItem(pick.id);
  NT.curId = pick.id;
  NT.answered = false;

  $("nvCount").textContent = (NT.i + 1) + " / " + NT.n;
  $("nvLv").textContent = LEVELS[NT.lv - 1];
  $("nvNote").textContent = "";
  const card = $("nvCard");
  card.innerHTML = "";

  if(NT.cur.kind === "conj"){
    const p = document.createElement("p");
    p.className = "xclue";
    const f = NT.cur.data;
    p.innerHTML = "<b>" + f.v + "</b> · " + (f.p ? f.p + " · " + f.t : f.t);
    card.appendChild(p);
  }else if(NT.cur.kind === "dictee"){
    const c = NT.cur.data;
    NT.heard = c.s.replace("___", c.a);
    const row = document.createElement("div");
    row.className = "dplay";
    const play = document.createElement("button");
    play.className = "dbig"; play.textContent = "▶ Écouter";
    play.addEventListener("click", () => speakFr(NT.heard, .95));
    const slow = document.createElement("button");
    slow.className = "ghost"; slow.textContent = "Lentement";
    slow.addEventListener("click", () => speakFr(NT.heard, .6));
    row.append(play, slow);
    card.appendChild(row);
    setTimeout(() => speakFr(NT.heard, .95), 150);
  }else{
    const c = NT.cur.data;
    const [a, b] = c.s.split("___");
    const p = document.createElement("p");
    p.className = "sentence";
    const blank = document.createElement("span");
    blank.className = "blank"; blank.textContent = "?";
    p.append(a, blank, b);
    card.appendChild(p);
  }

  const lab = document.createElement("label");
  lab.className = "fld";
  const sp = document.createElement("span");
  sp.textContent = NT.cur.kind === "dictee" ? "Ce que tu entends — accents compris"
    : "De mémoire — accents compris";
  const inp = document.createElement("input");
  inp.id = "nvIn"; inp.className = "seinput"; inp.autocomplete = "off"; inp.spellcheck = false;
  inp.addEventListener("keydown", (e) => {
    if(e.key === "Enter"){ e.preventDefault(); NT.answered ? testCard() : testAnswer(); }
  });
  lab.append(sp, inp);
  card.appendChild(lab);
  setTimeout(() => inp.focus(), 30);
}

function testAnswer(){
  if(NT.answered) return;
  const v = $("nvIn").value;
  if(!v.trim()){ $("nvNote").textContent = "Écris ta réponse. Une tentative vaut mieux qu'un blanc."; return; }
  NT.answered = true;
  NT.i++;

  let ok, msg;
  if(NT.cur.kind === "dictee"){
    const exp = dTok(NT.heard), got = dTok(v);
    let hit = 0;
    exp.forEach((w, n) => { if(got[n] && phon(got[n]) === phon(w)) hit++; });
    ok = hit === exp.length && got.length === exp.length;
    msg = ok ? "Juste, mot pour mot." : hit + "/" + exp.length + " mots — <b>" + NT.heard + "</b>";
  }else{
    const want = NT.cur.data.a;
    ok = same(v, want);
    msg = ok ? "Juste."
      : (accentOnly(v, want) ? "Les accents comptent : <b>" + want + "</b>."
                             : "C'était <b>" + want + "</b>.");
  }
  $("nvIn").readOnly = true;
  $("nvIn").classList.add(ok ? "ok" : "no");
  $("nvNote").innerHTML = msg;

  NT.lv = Math.max(1, Math.min(6, NT.lv + (ok ? 1 : -1)));
  if(NT.i >= NT.n) return setTimeout(afterStaircase, 900);
  setTimeout(testCard, ok ? 700 : 1600);
}

function staircaseLevel(){
  const tail = NT.path.slice(-6);
  return Math.max(1, Math.min(6, Math.round(tail.reduce((a, b) => a + b, 0) / tail.length)));
}

/* Reconnaître et se souvenir, ce n'est pas encore savoir écrire :
   une dernière phrase, produite seule, décide du plafond. */
function afterStaircase(){
  NT.stair = staircaseLevel();
  if(!S.sample) return endTest(0, "");
  NT.phase = "probe";
  const frames = PH_FRAMES[NT.stair] || PH_FRAMES[3];
  NT.task = frames[(Math.random() * frames.length) | 0]
    .replace("{v}", PH_VERBS[(Math.random() * PH_VERBS.length) | 0]);

  $("nvCount").textContent = "épreuve";
  $("nvLv").textContent = LEVELS[NT.stair - 1];
  const card = $("nvCard");
  card.innerHTML = "";
  const p = document.createElement("p");
  p.className = "phtask";
  p.textContent = NT.task;
  card.appendChild(p);
  const lab = document.createElement("label");
  lab.className = "fld";
  const sp = document.createElement("span");
  sp.textContent = "Ta phrase — accents compris";
  const ta = document.createElement("textarea");
  ta.id = "nvIn"; ta.className = "seinput"; ta.rows = 3; ta.spellcheck = false;
  lab.append(sp, ta);
  card.appendChild(lab);
  $("nvNote").textContent = "Dernière épreuve : la phrase, tu l'écris toi-même.";
  $("nvCheck").textContent = "Soumettre";
  setTimeout(() => ta.focus(), 30);
}

async function probeSubmit(){
  if(NT.probing) return;
  const text = $("nvIn").value.trim();
  if(text.split(/\s+/).filter(Boolean).length < 4){
    $("nvNote").textContent = "Une phrase complète, pas trois mots.";
    return;
  }
  NT.probing = true;
  $("nvNote").textContent = "Correction en cours…";
  let r = null;
  try{
    r = await S.sample.json(phrasePrompt(NT.task, text, NT.stair), {modelTier:"default", cache:false});
  }catch(e){
    return endTest(0, "La phrase n'a pas pu être corrigée — le niveau vient des douze questions seules.");
  }
  const ok = r && r.ok === true && r.consigne !== false;
  endTest(ok ? 0 : -1, ok
    ? "Phrase juste : le niveau des douze questions tient à l'écrit."
    : "Phrase fausse" + (r && r.faute ? " — " + r.faute : "")
      + " Tu reconnais à ce niveau sans l'écrire encore : on démarre un cran plus bas.");
}

function endTest(delta, note){
  const est = Math.max(1, Math.min(6, (NT.stair || staircaseLevel()) + (delta || 0)));
  S.P.level = est;
  S.P.tested = true;
  S.P.lvHist = [];
  srsReset();
  save();

  $("nvTest").hidden = true;
  $("nvResult").hidden = false;
  $("nvCheck").textContent = "Valider";
  $("nvBadge").textContent = LEVELS[est - 1];
  $("nvVerdict").textContent = (note ? note + " " : "")
    + "Les cartes neuves viendront de ce niveau et du précédent. "
    + "Rien au-dessus tant que le palier n'est pas franchi.";
  NT.phase = null; NT.probing = false;
  paintLevel();
}

function paintLevel(){
  $("nvNow").textContent = LEVELS[S.P.level - 1];
  $("nvGate").textContent = gateText();
  $("nvIntro").hidden = !!S.P.tested;
  $("nvResult").hidden = !S.P.tested;
  if(S.P.tested) $("nvBadge").textContent = LEVELS[S.P.level - 1];
  const counts = LEVELS.map(() => 0);
  registry().forEach(it => { const l = levelOf(it.id); if(l >= 1 && l <= LEVELS.length) counts[l - 1]++; });
  const done = LEVELS.map(() => 0);
  registry().forEach(it => { if(S.P.srs[it.id]) done[levelOf(it.id) - 1]++; });
  const box = $("nvBars");
  box.innerHTML = "";
  LEVELS.forEach((L, i) => {
    const row = document.createElement("div");
    row.className = "lvrow" + (i + 1 === S.P.level ? " now" : "") + (i + 1 > S.P.level ? " locked" : "");
    const name = document.createElement("span");
    name.className = "lvname"; name.textContent = L;
    const track = document.createElement("div");
    track.className = "lvtrack";
    const fill = document.createElement("div");
    fill.className = "lvfill";
    fill.style.width = counts[i] ? Math.round(done[i] / counts[i] * 100) + "%" : "0%";
    track.appendChild(fill);
    const num = document.createElement("span");
    num.className = "lvnum"; num.textContent = done[i] + "/" + counts[i];
    row.append(name, track, num);
    box.appendChild(row);
  });
  paintMargin();
}

let NV_READY = false;

function niveauInit(){
  if(NV_READY) return paintLevel();
  NV_READY = true;
  $("nvStart").addEventListener("click", startTest);
  $("nvAgain").addEventListener("click", startTest);
  $("nvCheck").addEventListener("click", () => {
    if(!NT) return;
    if(NT.phase === "probe") return probeSubmit();
    NT.answered ? testCard() : testAnswer();
  });
  paintLevel();
}
