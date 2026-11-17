/* Le Cahier — Imiter : l'ombre de la voix (shadowing).

   On écoute une phrase dite par une vraie voix, et on la redit tout de
   suite, au même rythme, avec les mêmes liaisons. Pas « comprendre » :
   reproduire. C'est le seul exercice du cahier où la bouche travaille
   avant la tête, et c'est là que l'accent et la prosodie se prennent.

   Deux façons de s'y mettre :
   - « après »  : la voix dit la phrase, puis c'est toi — propre, sans écho,
                  et la reconnaissance vocale peut compter tes mots ;
   - « avec »   : tu parles en même temps que la voix, comme une ombre —
                  le vrai shadowing, au casque de préférence.

   Le micro enregistre ta prise ; tu l'écoutes à côté du modèle, puis tu te
   notes. Personne d'autre ne peut juger un accent à ta place : la note est
   la tienne, et elle décide quand la phrase revient. Sans micro, on fait
   la même chose à voix haute, sans la réécoute. */

let IM = null;
let IM_MEDIA = null;      /* null : pas encore su ; false : pas de micro ici */
let IM_STREAM = null;

const IM_RATES = {lent:.75, normal:1};

function imRecorded(text){
  return typeof VOIX_REC === "object" && !!VOIX_REC[dStrip(String(text || ""))];
}

/* Combien de temps dure le modèle : on le sait pour les phrases enregistrées,
   on l'estime pour la synthèse. Large plutôt que court : couper la fin
   d'une prise est pire qu'une seconde de silence. */
function imModelSec(text, rate){
  const r = Math.max(.5, Math.min(1.25, rate || 1));
  const seg = typeof VOIX_REC === "object" ? VOIX_REC[dStrip(String(text || ""))] : null;
  if(seg) return seg[1] / r;
  return (String(text || "").length * .072) / Math.min(1.15, r) + .5;
}

function imPrefs(){
  if(!S.P.imiter || typeof S.P.imiter !== "object")
    S.P.imiter = {n:0, takes:0, mode:"apres", rate:1, hide:false};
  const p = S.P.imiter;
  if(p.mode !== "avec") p.mode = "apres";
  if(!(p.rate > 0)) p.rate = 1;
  return p;
}

function imPool(){
  return ALL().filter(c => c.s && c.a && levelOf(c.id) <= S.P.level + 1);
}

/* ---------- le micro ----------
   On ne demande le micro qu'au premier clic sur « Imiter », jamais au
   chargement. Un refus est définitif pour la page : on n'insiste pas. */
async function imStream(){
  if(IM_MEDIA === false) return null;
  if(IM_STREAM && IM_STREAM.active) return IM_STREAM;
  if(!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia
    || typeof MediaRecorder === "undefined"){ IM_MEDIA = false; return null; }
  try{
    IM_STREAM = await navigator.mediaDevices.getUserMedia({audio:true});
    IM_MEDIA = true;
    return IM_STREAM;
  }catch(e){ IM_MEDIA = false; return null; }
}

/* Une prise : le modèle, puis (ou pendant) l'enregistrement.
   Rend {url, heard, blob} — ou null si le micro n'est pas là.
   opts : {rate, mode:"apres"|"avec", onPhase(fn), ctl:{stop:false}} */
async function imTake(text, opts){
  opts = opts || {};
  const rate = opts.rate || 1, mode = opts.mode === "avec" ? "avec" : "apres";
  const ctl = opts.ctl || {stop:false};
  const phase = (p) => { if(opts.onPhase) opts.onPhase(p); };
  const wait = (ms) => new Promise(r => setTimeout(r, ms));

  const stream = await imStream();
  if(!stream){ phase("nomic"); return null; }

  let rec = null;
  try{ rec = new MediaRecorder(stream); }catch(e){ IM_MEDIA = false; phase("nomic"); return null; }
  const chunks = [];
  rec.addEventListener("dataavailable", (e) => { if(e.data && e.data.size) chunks.push(e.data); });

  /* La reconnaissance vocale écoute en même temps que le micro enregistre :
     elle n'entend pas la prise, elle entend la pièce. Une indication, pas une note.
     Si la dictée de la plateforme a été lancée par le clic (opts.dict), c'est
     elle qui transcrit — meilleure — et la reconnaissance du navigateur se tait. */
  const heard = opts.dict ? opts.dict.heard : [];
  const SR = opts.dict ? null : (window.SpeechRecognition || window.webkitSpeechRecognition);
  let sr = null;
  if(SR){
    try{
      sr = new SR();
      sr.lang = "fr-FR"; sr.continuous = true; sr.interimResults = false;
      sr.addEventListener("result", (e) => {
        for(let i = e.resultIndex; i < e.results.length; i++)
          if(e.results[i].isFinal) heard.push(e.results[i][0].transcript);
      });
    }catch(e){ sr = null; }
  }

  const sec = imModelSec(text, rate);
  phase("ecoute");
  speakFr(text, rate);
  if(mode === "apres"){
    const until = Date.now() + sec * 1000 + 280;
    while(Date.now() < until && !ctl.stop) await wait(60);
    if(ctl.stop){ phase("fini"); return null; }
  }

  phase("parle");
  const t0 = Date.now();
  try{ rec.start(); }catch(e){ IM_MEDIA = false; phase("nomic"); return null; }
  if(sr){ try{ sr.start(); }catch(e){ sr = null; } }
  const span = mode === "apres" ? sec * 1500 + 1300 : sec * 1000 + 1200;
  while(Date.now() - t0 < span && !ctl.stop) await wait(60);

  const stopped = new Promise(r => rec.addEventListener("stop", r, {once:true}));
  try{ rec.stop(); }catch(e){}
  if(sr){ try{ sr.stop(); }catch(e){} }
  /* stop() de la dictée attend les derniers mots : rien à deviner. */
  const dictDone = opts.dict ? opts.dict.stop() : Promise.resolve();
  await stopped;
  await dictDone;
  if(!opts.dict) await wait(260);         /* le dernier mot reconnu arrive après l'arrêt */
  phase("fini");
  const blob = new Blob(chunks, {type:rec.mimeType || "audio/webm"});
  if(!blob.size) return null;
  return {url:URL.createObjectURL(blob), heard:heard.join(" ").trim(), blob, ms:Date.now() - t0};
}

/* La dictée de la plateforme pour une prise : lancée de façon synchrone depuis
   le clic, elle collecte les morceaux settled dans heard[]. null si elle n'est
   pas disponible ici — on retombe alors sur la reconnaissance du navigateur.
   La Conversation peut tenir la dictée au même moment : on ne la vole pas. */
function imDictStart(){
  const d = (typeof S !== "undefined") && S.dictation;
  if(!d || (typeof d.active === "function" && d.active())) return null;
  const heard = [];
  const offs = [];
  const box = {heard, gateUntil:0};
  try{
    /* gateUntil : la phrase du modèle peut se « poser » un instant après que
       c'est ton tour — on l'écarte, elle gonflerait le compte de mots. */
    offs.push(d.onFinal(({text}) => { if(text && Date.now() >= box.gateUntil) heard.push(text.trim()); }));
    d.start({language:"fr"}).catch(() => {});      /* un refus laisse heard vide : la note reste la tienne */
  }catch(e){ offs.forEach(f => f()); return null; }
  box.stop = () => d.stop().catch(() => {}).then(() => offs.forEach(f => f()));
  return box;
}

/* Les mots reconnus, face aux mots attendus — même diff que la dictée. */
function imHeardInto(host, want, heard){
  host.innerHTML = "";
  if(!heard) return 0;
  const exp = dTok(want), got = dTok(heard);
  const ops = dLcs(exp.map(dStrip), got.map(dStrip));
  const out = document.createElement("p");
  out.className = "dcorr";
  out.style.margin = "6px 0 0";
  let hit = 0;
  const add = (tag, cls, txt) => {
    const e = document.createElement(tag);
    if(cls) e.className = cls;
    e.textContent = txt;
    out.appendChild(e);
    out.appendChild(document.createTextNode(" "));
  };
  ops.forEach(([k, i, j]) => {
    if(k === "eq"){ hit++; add("span", "w ok", exp[i]); }
    else if(k === "sub"){ add("del", "", got[j]); add("ins", "", exp[i]); }
    else if(k === "del") add("ins", "miss", exp[i]);
    else add("del", "", got[j]);
  });
  const en = typeof LANG !== "undefined" && LANG === "en";
  const head = document.createElement("p");
  head.className = "imsrc";
  head.textContent = hit + " / " + exp.length + (en ? " words recognised" : " mots reconnus");
  host.append(head, out);
  return hit;
}

/* ---------- la rangée commune : Modèle · Imiter · Toi ----------
   Sert au panneau et à la carte de la séance. */
function imRecorderRow(host, text, getRate, getMode, onTake){
  const en = typeof LANG !== "undefined" && LANG === "en";
  const row = document.createElement("div");
  row.className = "dplay";
  const take = document.createElement("button");
  take.className = "dbig imtake";
  take.textContent = "● Imiter";
  const mine = document.createElement("button");
  mine.className = "ghost";
  mine.textContent = "▶ Toi";
  mine.disabled = true;
  const both = document.createElement("button");
  both.className = "ghost";
  both.textContent = "Modèle, puis toi";
  both.disabled = true;
  row.append(take, mine, both);
  host.appendChild(row);

  const state = {url:null, audio:null, ctl:null, busy:false};
  const labels = {
    ecoute:[en ? "Listen…" : "Écoute…", "wait"],
    parle:[en ? "● Speak!" : "● Parle !", "rec"],
    fini:["● Imiter", ""]
  };
  const playMine = () => {
    if(!state.url) return;
    if(state.audio){ try{ state.audio.pause(); }catch(e){} }
    if("speechSynthesis" in window) speechSynthesis.cancel();
    if(typeof vrHalt === "function") vrHalt();
    state.audio = new Audio(state.url);
    state.audio.play().catch(() => {});
  };

  take.addEventListener("click", async () => {
    if(state.busy){ if(state.ctl) state.ctl.stop = true; return; }
    state.busy = true;
    state.ctl = {stop:false};
    const rate = getRate(), mode = getMode();
    /* La dictée doit partir dans le clic même, avant tout await.
       On jette ce qu'elle entend pendant que le modèle parle (mode « après »),
       pour ne transcrire que ta prise. */
    const dict = imDictStart();
    const r = await imTake(text, {rate, mode, ctl:state.ctl, dict, onPhase:(p) => {
      if(dict && p === "parle"){ dict.heard.length = 0; dict.gateUntil = Date.now() + 900; }
      if(p === "nomic"){
        take.hidden = true; mine.hidden = true; both.hidden = true;
        host.appendChild(Object.assign(document.createElement("p"), {className:"note",
          textContent:en ? "No microphone here — say it aloud anyway, then grade yourself."
            : "Pas de micro ici — dis-la quand même à voix haute, puis note-toi."}));
        return;
      }
      const l = labels[p]; if(!l) return;
      take.textContent = l[0];
      take.classList.toggle("wait", l[1] === "wait");
      take.classList.toggle("rec", l[1] === "rec");
    }});
    /* imTake rend la main tôt quand le micro manque ou qu'on arrête pendant
       l'écoute : la dictée ne doit pas rester ouverte derrière. stop() est
       sans effet si elle est déjà fermée. */
    if(dict) await dict.stop();
    state.busy = false;
    take.textContent = "● Imiter";
    take.classList.remove("wait", "rec");
    if(!r) return;
    if(state.url) URL.revokeObjectURL(state.url);
    state.url = r.url;
    mine.disabled = false; both.disabled = false;
    if(onTake) onTake(r);
  });
  mine.addEventListener("click", playMine);
  both.addEventListener("click", () => {
    const rate = getRate();
    speakFr(text, rate);
    setTimeout(playMine, imModelSec(text, rate) * 1000 + 380);
  });
  return state;
}

/* ---------- le panneau ---------- */
function imNext(){
  const pool = imPool();
  if(!pool.length){ $("imNote").textContent = "Aucune phrase à ce niveau pour l'instant."; return; }
  const t = srsDay();
  const due = pool.filter(c => { const s = S.P.srs["i" + c.id]; return s && s[0] <= t; });
  const fresh = pool.filter(c => !S.P.srs["i" + c.id]);
  /* Les phrases enregistrées d'abord : on imite une vraie voix avant une voix de synthèse. */
  const freshReal = fresh.filter(c => imRecorded(c.s.replace("___", c.a)));
  const from = due.length ? due : freshReal.length ? freshReal : fresh.length ? fresh : pool;
  const pick = from[(Math.random() * from.length) | 0];
  const text = pick.s.replace("___", pick.a);
  IM = {id:pick.id, srsId:"i" + pick.id, text, gloss:pick.g || "", real:imRecorded(text),
    take:null, hit:null, done:false, t0:Date.now()};
  imPaint();
}

function imPaint(){
  const en = typeof LANG !== "undefined" && LANG === "en";
  const p = imPrefs();
  $("imLv").textContent = LEVELS[Math.max(0, levelOf(IM.id) - 1)];
  const src = $("imSrc");
  src.textContent = IM.real ? (en ? "recorded · real voice" : "enregistrée · vraie voix")
    : (en ? "synthetic voice" : "voix de synthèse");
  src.classList.toggle("real", !!IM.real);

  const tx = $("imText");
  tx.textContent = IM.text;
  tx.lang = "fr";
  tx.classList.toggle("veil", !!p.hide);
  $("imHide").textContent = p.hide ? "Montrer le texte" : "Cacher le texte";
  $("imGloss").textContent = IM.gloss;
  $("imGloss").hidden = !IM.gloss || !!p.hide;

  [...$("imModes").children].forEach(b => {
    const on = b.dataset.mode === p.mode;
    b.classList.toggle("on", on); b.setAttribute("aria-pressed", on ? "true" : "false");
  });
  [...$("imRates").children].forEach(b => {
    const on = +b.dataset.rate === +p.rate;
    b.classList.toggle("on", on); b.setAttribute("aria-pressed", on ? "true" : "false");
  });

  const row = $("imRow");
  row.innerHTML = "";
  imRecorderRow(row, IM.text, () => imPrefs().rate, () => imPrefs().mode, (r) => {
    IM.take = r;
    S.P.imiter.takes = (S.P.imiter.takes || 0) + 1;
    IM.hit = r.heard ? imHeardInto($("imHeard"), IM.text, r.heard) : null;
    IM.n = dTok(IM.text).length;
    if(!r.heard) $("imHeard").innerHTML = "";
    $("imNote").textContent = en ? "Listen to yourself next to the model, then grade yourself."
      : "Écoute-toi à côté du modèle, puis note-toi.";
  });

  $("imHeard").innerHTML = "";
  $("imNote").textContent = "";
  $("imNext").hidden = true;
  imGradesPaint();
}

function imGradesPaint(){
  const box = $("imGrades");
  box.innerHTML = "";
  if(IM.done) return;
  const en = typeof LANG !== "undefined" && LANG === "en";
  const grades = document.createElement("div");
  grades.className = "grades";
  [["Raté", 1, "g1"], ["Difficile", 3, "g3"], ["Bien", 4, "g4"], ["Facile", 5, "g5"]].forEach(([lab, q, cls]) => {
    const b = document.createElement("button");
    b.className = "grade " + cls; b.type = "button";
    b.appendChild(Object.assign(document.createElement("span"), {className:"grade-lab", textContent:lab}));
    b.appendChild(Object.assign(document.createElement("span"), {className:"grade-iv",
      textContent:q < 3 ? (en ? "again soon" : "dans un instant") : ivText(srsPreview(IM.srsId, q))}));
    b.addEventListener("click", () => imGrade(q));
    grades.appendChild(b);
  });
  box.appendChild(grades);
}

function imGrade(q){
  if(!IM || IM.done) return;
  IM.done = true;
  const en = typeof LANG !== "undefined" && LANG === "en";
  /* Moins de six mots sur dix reconnus : l'auto-évaluation plafonne à « Difficile ». */
  let capped = false;
  if(IM.hit != null && IM.n && IM.hit / IM.n < .6 && q > 3){ q = 3; capped = true; }
  const ok = q >= 3;
  const iv = srsUpdate(IM.srsId, q);
  noteLevel(IM.id, ok);
  const p = imPrefs();
  p.n = (p.n || 0) + 1;
  $("imGrades").innerHTML = "";
  $("imNote").className = "note " + (ok ? "good" : "bad");
  $("imNote").textContent = (capped
    ? (en ? "Only " + IM.hit + "/" + IM.n + " words recognised — capped at Hard. "
      : "Reconnu " + IM.hit + "/" + IM.n + " mots — plafonné à Difficile. ") : "") + (ok
    ? (iv === 1 ? (en ? "Back tomorrow." : "Revue demain.")
      : (en ? "Back in " + iv + " days." : "Revue dans " + iv + " jours."))
    : (en ? "It comes back soon — say it once more now." : "Elle revient bientôt — redis-la une fois maintenant."))
    + "  " + p.n + (en ? " sentences shadowed" : " phrases imitées")
    + (p.takes ? " · " + p.takes + (en ? " takes" : " prises") : "") + ".";
  $("imNext").hidden = false;
  $("imNext").focus();
  if(typeof scored === "function") scored(ok);
  save();
}

let IM_READY = false;
function imiterInit(){
  if(IM_READY) return (IM ? imPaint() : imNext());
  IM_READY = true;
  const en = typeof LANG !== "undefined" && LANG === "en";
  const p = imPrefs();

  const modes = $("imModes");
  [["apres", "Après la voix"], ["avec", "En même temps"]].forEach(([k, lab]) => {
    const b = document.createElement("button");
    b.type = "button"; b.className = "chip"; b.dataset.mode = k; b.textContent = lab;
    b.addEventListener("click", () => { imPrefs().mode = k; save(); imPaint(); });
    modes.appendChild(b);
  });
  const rates = $("imRates");
  [[IM_RATES.lent, "Lentement"], [IM_RATES.normal, "Vitesse normale"]].forEach(([r, lab]) => {
    const b = document.createElement("button");
    b.type = "button"; b.className = "chip"; b.dataset.rate = r; b.textContent = lab;
    b.addEventListener("click", () => { imPrefs().rate = r; save(); imPaint(); });
    rates.appendChild(b);
  });

  $("imPlay").addEventListener("click", () => IM && speakFr(IM.text, imPrefs().rate));
  $("imLoop").addEventListener("click", () => {
    if(!IM) return;
    const r = imPrefs().rate, gap = imModelSec(IM.text, r) * 1000 + 700;
    speakFr(IM.text, r);
    setTimeout(() => speakFr(IM.text, r), gap);
    setTimeout(() => speakFr(IM.text, r), gap * 2);
  });
  $("imHide").addEventListener("click", () => { const q = imPrefs(); q.hide = !q.hide; save(); imPaint(); });
  $("imText").addEventListener("click", () => {
    if(!imPrefs().hide) return;
    $("imText").classList.remove("veil");            /* un coup d'œil, sans changer le réglage */
    $("imGloss").hidden = !IM.gloss;
  });
  $("imNext").addEventListener("click", imNext);

  if(!("speechSynthesis" in window) && !(typeof VOIX_REC === "object")){
    $("imWarn").textContent = en ? "This browser has no voice at all — shadowing needs one."
      : "Ce navigateur n'a aucune voix : imiter demande une voix.";
    $("imWarn").hidden = false;
  }
  imNext();
}
