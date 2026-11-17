/* Le Cahier — examen blanc DELF / DALF
   Quatre épreuves sur 25, total sur 100. Admis à 50/100, mais éliminé
   sous 5/25 à n'importe quelle épreuve : c'est la règle officielle. */

const EX_PARTS = [
  {k:"co", l:"Compréhension de l'oral", s:"CO"},
  {k:"ce", l:"Compréhension des écrits", s:"CE"},
  {k:"pe", l:"Production écrite", s:"PE"},
  {k:"po", l:"Production orale", s:"PO"}
];

/* Durées officielles, en minutes */
const EX_MIN = {
  1:{co:20, ce:30, pe:30, po:7},   2:{co:25, ce:30, pe:45, po:8},
  3:{co:25, ce:45, pe:45, po:15},  4:{co:30, ce:60, pe:60, po:20},
  5:{co:40, ce:50, pe:150, po:30}, 6:{co:45, ce:90, pe:120, po:30}
};
const EX_WORDS = {1:40, 2:80, 3:160, 4:250, 5:250, 6:400};
const EX_DIPLOMA = (lv) => (lv <= 4 ? "DELF " : "DALF ") + LEVELS[lv - 1];

let EX = null;

/* ---------- génération des sujets ---------- */
function exPrompt(kind, lv){
  const L = LEVELS[lv - 1], head = "Tu rédiges un sujet d'examen blanc " + EX_DIPLOMA(lv)
    + ", niveau " + L + ", fidèle au format officiel. Tout en français.\n\n";

  if(kind === "co") return head
    + "Épreuve : compréhension de l'oral. Écris UN document sonore (il sera lu à voix haute) : "
    + (lv <= 2 ? "une annonce, un message sur répondeur ou une conversation courte"
      : lv <= 4 ? "un extrait de radio, une interview ou un reportage court"
      : "un extrait d'émission, un débat ou une conférence") + ", "
    + (lv <= 2 ? "60 à 90" : lv <= 4 ? "120 à 180" : "200 à 260") + " mots, "
    + "à l'oral naturel. Puis 5 questions de compréhension.\n\n"
    + 'Réponds uniquement par ce JSON : {"contexte":"...","script":"...","questions":'
    + '[{"q":"...","type":"qcm","options":["a","b","c"],"reponse":"a","points":5}]}\n'
    + "- contexte : la phrase de mise en situation que le candidat lit avant d'écouter.\n"
    + "- script : le texte qui sera lu, sans didascalies ni noms de locuteurs entre crochets.\n"
    + "- questions : 5 au total, dont 3 de type \"qcm\" (3 options, une seule juste, "
    + "\"reponse\" = le texte exact de la bonne option) et 2 de type \"court\" "
    + "(\"reponse\" = la réponse attendue en quelques mots). Les points font 25 en tout.";

  if(kind === "ce") return head
    + "Épreuve : compréhension des écrits. Écris UN document écrit : "
    + (lv <= 2 ? "un courriel, une petite annonce ou un prospectus"
      : lv <= 4 ? "un article de presse ou un courrier des lecteurs"
      : "un article de fond, une tribune ou un texte argumentatif") + ", "
    + (lv <= 2 ? "80 à 120" : lv <= 4 ? "200 à 320" : "350 à 450") + " mots. "
    + "Puis 5 questions de compréhension, dont une au moins sur l'intention de l'auteur.\n\n"
    + 'Réponds uniquement par ce JSON : {"titre":"...","texte":"...","questions":'
    + '[{"q":"...","type":"qcm","options":["a","b","c"],"reponse":"a","points":5}]}\n'
    + "- questions : 5, dont 3 \"qcm\" (3 options, \"reponse\" = le texte exact de la bonne) "
    + "et 2 \"court\". Les points font 25 en tout.";

  if(kind === "pe") return head
    + "Épreuve : production écrite. Donne UNE consigne conforme au niveau : "
    + (lv === 1 ? "un message simple (carte postale, mot à un voisin)"
      : lv === 2 ? "décrire un événement vécu ou écrire une lettre d'invitation, de remerciement ou d'excuse"
      : lv === 3 ? "un essai, une lettre ou un article exprimant une prise de position personnelle"
      : lv === 4 ? "un texte argumenté : contribution à un débat, lettre formelle ou article critique"
      : lv === 5 ? "un essai argumenté à partir d'une problématique de société"
      : "un texte de réflexion nuancé sur une question abstraite")
    + ", environ " + EX_WORDS[lv] + " mots.\n\n"
    + 'Réponds uniquement par ce JSON : {"consigne":"...","mots":' + EX_WORDS[lv] + '}\n'
    + "- consigne : la consigne complète telle qu'elle figurerait sur le sujet, avec la situation.";

  return head
    + "Épreuve : production orale, partie « expression d'un point de vue ». "
    + "Donne un court document déclencheur (3 à 5 lignes : un titre de presse et son chapô, "
    + "ou une brève) et la consigne qui va avec.\n\n"
    + 'Réponds uniquement par ce JSON : {"document":"...","consigne":"..."}\n'
    + "- consigne : ce que le candidat doit faire (dégager le thème, présenter et défendre "
    + "son point de vue, puis débattre avec l'examinateur).";
}

/* ---------- barème ---------- */
function gradePrompt(kind, lv, payload){
  const L = LEVELS[lv - 1];
  const grids = {
    pe:"Respect de la consigne · Correction sociolinguistique · Capacité à présenter des faits · "
      + "Capacité à exprimer sa pensée · Cohérence et cohésion · Étendue du vocabulaire · "
      + "Maîtrise du vocabulaire · Choix des formes grammaticales · Degré d'élaboration des phrases",
    po:"Respect de la consigne · Capacité à présenter et défendre un point de vue · "
      + "Capacité à interagir · Lexique · Morphosyntaxe · Maîtrise du système phonologique"
  };
  return "Tu es correcteur " + EX_DIPLOMA(lv) + ". Note cette copie sur 25 selon la grille "
    + "officielle du niveau " + L + " : " + (grids[kind] || "compréhension") + ".\n\n"
    + payload + "\n\n"
    + "Note comme un vrai correcteur : exigeant mais juste pour le niveau " + L + ". "
    + "Un candidat de ce niveau n'a pas à écrire comme un natif, mais la consigne doit être "
    + "respectée et la langue tenir debout.\n\n"
    + 'Réponds uniquement par ce JSON : {"note":16.5,"details":[{"critere":"...","note":3,"sur":4}],'
    + '"commentaire":"...","conseil":"..."}\n'
    + "- note : sur 25, un demi-point près.\n"
    + "- details : 4 à 6 critères de la grille, avec la note obtenue et le maximum.\n"
    + "- commentaire : deux phrases en français, franches.\n"
    + "- conseil : la seule chose à travailler en priorité, en une phrase.";
}

/* ---------- minuterie ---------- */
function exTick(){
  if(!EX || !EX.until) return;
  const left = Math.max(0, Math.round((EX.until - Date.now()) / 1000));
  const m = String((left / 60) | 0).padStart(2, "0"), s = String(left % 60).padStart(2, "0");
  $("exClock").textContent = m + ":" + s;
  $("exClock").classList.toggle("urgent", left <= 60);
  if(left <= 0){
    clearInterval(EX.timer); EX.timer = null; EX.until = 0;
    $("exNote").textContent = "Temps écoulé — la copie part telle quelle.";
    exSubmit();
  }
}

function exStartClock(min){
  EX.until = Date.now() + min * 60000;
  clearInterval(EX.timer);
  EX.timer = setInterval(exTick, 1000);
  exTick();
}

function exStopClock(){
  if(EX && EX.timer){ clearInterval(EX.timer); EX.timer = null; }
  EX && (EX.until = 0);
}

/* ---------- déroulé d'une épreuve ---------- */
async function exRun(kind){
  if(!S.sample){ $("exNote").textContent = PH_ERR.not_granted; return; }
  const lv = EX.lv;
  EX.kind = kind; EX.sujet = null; EX.answers = {}; EX.plays = 0; EX.turns = null;
  $("exBoard").hidden = true;
  $("exRoom").hidden = false;
  $("exTitle").textContent = EX_DIPLOMA(lv) + " · " + EX_PARTS.find(p => p.k === kind).l;
  $("exBody").innerHTML = "";
  $("exOut").innerHTML = "";
  $("exNote").textContent = "Préparation du sujet…";
  $("exClock").textContent = "--:--";
  $("exSubmit").hidden = true;

  try{
    EX.sujet = await S.sample.json(exPrompt(kind, lv), {modelTier:"default", cache:false});
  }catch(e){
    $("exNote").textContent = PH_ERR[(e && e.code)] || PH_ERR.upstream_error;
    $("exRoom").hidden = true; $("exBoard").hidden = false;
    return;
  }
  $("exNote").textContent = "";
  $("exSubmit").hidden = false;
  ({co:exRenderCO, ce:exRenderCE, pe:exRenderPE, po:exRenderPO})[kind]();
  exStartClock(EX_MIN[lv][kind]);
}

function exQuestions(list){
  const box = document.createElement("div");
  (list || []).forEach((q, i) => {
    const wrap = document.createElement("div");
    wrap.className = "exq";
    wrap.appendChild(Object.assign(document.createElement("p"),
      {className:"exqt", textContent:(i + 1) + ". " + (q.q || "")}));
    if(q.type === "qcm" && Array.isArray(q.options)){
      q.options.forEach(o => {
        const lab = document.createElement("label");
        lab.className = "exopt";
        const r = document.createElement("input");
        r.type = "radio"; r.name = "exq" + i; r.value = o;
        r.addEventListener("change", () => { EX.answers[i] = o; });
        lab.append(r, document.createTextNode(" " + o));
        wrap.appendChild(lab);
      });
    }else{
      const inp = document.createElement("input");
      inp.className = "seinput"; inp.autocomplete = "off";
      inp.addEventListener("input", () => { EX.answers[i] = inp.value; });
      wrap.appendChild(inp);
    }
    box.appendChild(wrap);
  });
  $("exBody").appendChild(box);
}

function exRenderCO(){
  const s = EX.sujet;
  $("exBody").appendChild(Object.assign(document.createElement("p"),
    {className:"scene", textContent:s.contexte || "Écoutez le document."}));
  const row = document.createElement("div");
  row.className = "dplay";
  const play = document.createElement("button");
  play.className = "dbig"; play.textContent = "▶ Écouter (2 fois maximum)";
  play.addEventListener("click", () => {
    if(EX.plays >= 2){ $("exNote").textContent = "Deux écoutes, comme à l'examen. C'est fini."; return; }
    EX.plays++;
    speakFr(s.script || "", .95);
    play.textContent = EX.plays >= 2 ? "Écoutes épuisées" : "▶ Deuxième écoute";
    if(EX.plays >= 2) play.disabled = true;
  });
  row.appendChild(play);
  $("exBody").appendChild(row);
  exQuestions(s.questions);
}

function exRenderCE(){
  const s = EX.sujet;
  const art = document.createElement("div");
  art.className = "extext";
  if(s.titre) art.appendChild(Object.assign(document.createElement("h3"), {textContent:s.titre}));
  (s.texte || "").split(/\n+/).forEach(p => {
    if(p.trim()) art.appendChild(Object.assign(document.createElement("p"), {textContent:p.trim()}));
  });
  $("exBody").appendChild(art);
  exQuestions(s.questions);
}

function exRenderPE(){
  const s = EX.sujet;
  $("exBody").appendChild(Object.assign(document.createElement("p"),
    {className:"phtask", textContent:s.consigne || ""}));
  const lab = document.createElement("label");
  lab.className = "fld";
  lab.appendChild(Object.assign(document.createElement("span"),
    {textContent:"Ta copie — environ " + (s.mots || EX_WORDS[EX.lv]) + " mots"}));
  const ta = document.createElement("textarea");
  ta.id = "exIn"; ta.className = "seinput"; ta.rows = 10; ta.spellcheck = false;
  ta.addEventListener("input", () => {
    const n = ta.value.trim().split(/\s+/).filter(Boolean).length;
    $("exCount").textContent = n + " mots";
  });
  lab.appendChild(ta);
  $("exBody").appendChild(lab);
  $("exCount").textContent = "0 mots";
  setTimeout(() => ta.focus(), 40);
}

function exRenderPO(){
  const s = EX.sujet;
  const d = document.createElement("div");
  d.className = "extext";
  d.appendChild(Object.assign(document.createElement("p"), {textContent:s.document || ""}));
  $("exBody").appendChild(d);
  $("exBody").appendChild(Object.assign(document.createElement("p"),
    {className:"phtask", textContent:s.consigne || ""}));
  const log = document.createElement("div");
  log.className = "chatlog"; log.id = "exLog";
  $("exBody").appendChild(log);
  const row = document.createElement("div");
  row.className = "cvrow";
  const ta = document.createElement("textarea");
  ta.id = "exIn"; ta.className = "seinput"; ta.rows = 2; ta.spellcheck = false;
  ta.placeholder = "Présente ton point de vue, puis réponds à l'examinateur…";
  ta.addEventListener("keydown", (e) => {
    if(e.key === "Enter" && !e.shiftKey){ e.preventDefault(); exSay(); }
  });
  const send = document.createElement("button");
  send.className = "go"; send.textContent = "Dire";
  send.addEventListener("click", exSay);
  row.append(ta, send);
  $("exBody").appendChild(row);

  EX.turns = [{role:"user", content:
    "Tu es l'examinateur d'une épreuve de production orale " + EX_DIPLOMA(EX.lv)
    + ". Le candidat va présenter un point de vue à partir de ce document :\n\n"
    + (s.document || "") + "\n\nConsigne : " + (s.consigne || "") + "\n\n"
    + "Règles : tu parles UNIQUEMENT en français, tu restes l'examinateur, tu ne corriges rien, "
    + "tu ne notes rien à voix haute. Après sa présentation, tu le fais réagir avec des questions "
    + "précises et des objections, une à deux phrases à la fois. Attends sa première prise de "
    + "parole : dis seulement une phrase d'accueil et invite-le à commencer."}];
  exJury();
}

async function exJury(){
  const bub = document.createElement("div");
  bub.className = "bub them"; bub.textContent = "…";
  $("exLog").appendChild(bub);
  try{
    const {text} = await S.sample(EX.turns, {modelTier:"quick", cache:false,
      onText:({text}) => { bub.textContent = text; $("exLog").scrollTop = $("exLog").scrollHeight; }});
    EX.turns.push({role:"assistant", content:text});
    speakFr(text, .95);
  }catch(e){ bub.remove(); $("exNote").textContent = PH_ERR[(e && e.code)] || PH_ERR.upstream_error; }
}

async function exSay(){
  const ta = $("exIn");
  const v = (ta.value || "").trim();
  if(!v) return;
  ta.value = "";
  const b = document.createElement("div");
  b.className = "bub me"; b.textContent = v;
  $("exLog").appendChild(b);
  $("exLog").scrollTop = $("exLog").scrollHeight;
  EX.turns.push({role:"user", content:v});
  if(EX.turns.length > 15) EX.turns = [EX.turns[0]].concat(EX.turns.slice(-14));
  await exJury();
}

/* ---------- correction ---------- */
async function exSubmit(){
  if(!EX || EX.grading) return;
  EX.grading = true;
  exStopClock();
  $("exSubmit").hidden = true;
  $("exNote").textContent = "Correction en cours…";

  const kind = EX.kind, lv = EX.lv, s = EX.sujet;
  let note = 0, details = [], comm = "", conseil = "";

  if(kind === "co" || kind === "ce"){
    const qs = (s.questions || []);
    let auto = 0, autoMax = 0, shorts = [];
    qs.forEach((q, i) => {
      const pts = Number(q.points) || (25 / Math.max(1, qs.length));
      const mine = EX.answers[i] || "";
      if(q.type === "qcm"){
        autoMax += pts;
        const ok = String(mine).trim() === String(q.reponse || "").trim();
        if(ok) auto += pts;
        details.push({critere:"Q" + (i + 1), note:ok ? pts : 0, sur:pts});
      }else{
        shorts.push("Q" + (i + 1) + " — attendu : " + (q.reponse || "") + " | réponse : " + (mine || "(rien)")
          + " | barème : " + pts);
      }
    });
    let shortNote = 0, shortMax = qs.filter(q => q.type !== "qcm")
      .reduce((a, q) => a + (Number(q.points) || 5), 0);
    if(shorts.length && S.sample){
      try{
        const r = await S.sample.json(gradePrompt(kind, lv,
          "Réponses courtes à corriger :\n" + shorts.join("\n")
          + "\n\nAccepte toute formulation qui montre que le candidat a compris. "
          + "Mets la note totale de ces réponses courtes dans \"note\" (sur " + shortMax + ")."),
          {modelTier:"quick", cache:false});
        shortNote = Math.max(0, Math.min(shortMax, Number(r && r.note) || 0));
        comm = (r && r.commentaire) || ""; conseil = (r && r.conseil) || "";
      }catch(e){ shortNote = 0; comm = "Les réponses courtes n'ont pas pu être corrigées."; }
    }
    note = Math.round((auto + shortNote) * 2) / 2;
    if(!comm) comm = auto === autoMax ? "Tous les QCM sont justes." : "Des QCM sont tombés à côté.";
  }else{
    const body = kind === "pe"
      ? "Consigne : " + (s.consigne || "") + "\n\nCopie du candidat :\n" + (($("exIn") || {}).value || "(copie blanche)")
      : "Document : " + (s.document || "") + "\nConsigne : " + (s.consigne || "")
        + "\n\nTranscription de l'épreuve :\n"
        + (EX.turns || []).slice(1).map(t => (t.role === "assistant" ? "Examinateur : " : "Candidat : ") + t.content).join("\n");
    try{
      const r = await S.sample.json(gradePrompt(kind, lv, body), {modelTier:"default", cache:false});
      note = Math.max(0, Math.min(25, Number(r && r.note) || 0));
      details = (r && Array.isArray(r.details) ? r.details : []).slice(0, 6);
      comm = (r && r.commentaire) || ""; conseil = (r && r.conseil) || "";
    }catch(e){
      EX.grading = false;
      $("exNote").textContent = PH_ERR[(e && e.code)] || PH_ERR.upstream_error;
      $("exSubmit").hidden = false;
      return;
    }
  }

  EX.grading = false;
  if(typeof xpGain === "function") xpGain(Math.round(note * 2), "exam");
  S.P.exam.parts[kind] = note;
  S.P.exam.lv = lv;
  save();
  exShowResult(kind, note, details, comm, conseil);
}

function exShowResult(kind, note, details, comm, conseil){
  const out = $("exOut");
  out.innerHTML = "";
  const pass = note >= 5;
  out.appendChild(Object.assign(document.createElement("p"),
    {className:"phverdict " + (note >= 12.5 ? "good" : pass ? "" : "bad"),
     textContent:(Math.round(note * 2) / 2) + " / 25"}));
  if(!pass) out.appendChild(Object.assign(document.createElement("p"),
    {className:"phline", textContent:"Sous 5/25, cette épreuve est éliminatoire, quel que soit le total."}));
  details.forEach(d => {
    const row = document.createElement("div");
    row.className = "lvrow";
    row.appendChild(Object.assign(document.createElement("span"),
      {className:"weakname", textContent:d.critere || ""}));
    const track = document.createElement("div");
    track.className = "lvtrack";
    const fill = document.createElement("div");
    fill.className = "lvfill";
    const sur = Number(d.sur) || 1;
    fill.style.width = Math.round(Math.max(0, Math.min(1, (Number(d.note) || 0) / sur)) * 100) + "%";
    track.appendChild(fill);
    row.appendChild(track);
    row.appendChild(Object.assign(document.createElement("span"),
      {className:"lvnum", textContent:(Number(d.note) || 0) + "/" + sur}));
    out.appendChild(row);
  });
  if(comm) out.appendChild(Object.assign(document.createElement("p"), {className:"phline", textContent:comm}));
  if(conseil) out.appendChild(Object.assign(document.createElement("p"),
    {className:"phline dimline", textContent:"À travailler : " + conseil}));

  $("exNote").textContent = "";
  const back = document.createElement("button");
  back.className = "go"; back.textContent = "Retour au tableau";
  back.addEventListener("click", exBoard);
  out.appendChild(back);
  scored(note >= 12.5);
  paintMargin();
}

/* ---------- tableau des épreuves ---------- */
function exBoard(){
  exStopClock();
  $("exRoom").hidden = true;
  $("exBoard").hidden = false;
  const lv = EX ? EX.lv : S.P.level;
  const p = S.P.exam.parts || {};
  const box = $("exGrid");
  box.innerHTML = "";
  let total = 0, done = 0, floored = false;
  EX_PARTS.forEach(part => {
    const n = (S.P.exam.lv === lv) ? p[part.k] : null;
    if(n != null){ total += n; done++; if(n < 5) floored = true; }
    const row = document.createElement("div");
    row.className = "exrow";
    row.appendChild(Object.assign(document.createElement("span"),
      {className:"exname", textContent:part.l}));
    row.appendChild(Object.assign(document.createElement("span"),
      {className:"exdur", textContent:EX_MIN[lv][part.k] + " min"}));
    row.appendChild(Object.assign(document.createElement("span"),
      {className:"exscore" + (n != null && n < 5 ? " bad" : ""),
       textContent:n == null ? "—" : (Math.round(n * 2) / 2) + "/25"}));
    const go = document.createElement("button");
    go.className = "ghost";
    go.textContent = n == null ? "Passer l'épreuve" : "Repasser";
    go.addEventListener("click", () => exRun(part.k));
    row.appendChild(go);
    box.appendChild(row);
  });

  const v = $("exVerdict");
  if(done === 4){
    const admis = total >= 50 && !floored;
    v.className = "phverdict " + (admis ? "good" : "bad");
    v.textContent = (Math.round(total * 2) / 2) + " / 100 — " + (admis ? "admis" : "ajourné");
    $("exRule").textContent = floored
      ? "Une épreuve est sous 5/25 : éliminatoire, même avec la moyenne."
      : admis ? "Tu aurais le diplôme " + EX_DIPLOMA(lv) + "." : "Il faut 50/100 pour être admis.";
  }else{
    v.className = "phverdict";
    v.textContent = done ? (Math.round(total * 2) / 2) + " / " + (done * 25) : "";
    $("exRule").textContent = "Admis à 50/100, éliminé sous 5/25 à une épreuve. "
      + (4 - done) + " épreuve" + (4 - done > 1 ? "s" : "") + " à passer.";
  }
}

function exSetLevel(lv){
  EX = EX || {};
  EX.lv = lv;
  if(S.P.exam.lv !== lv) S.P.exam = {lv, parts:{}};
  [...$("exLevels").children].forEach(b =>
    b.classList.toggle("on", +b.dataset.lv === lv));
  $("exDiploma").textContent = EX_DIPLOMA(lv);
  exBoard();
}

let EX_READY = false;

function examenInit(){
  if(EX_READY) return exBoard();
  EX_READY = true;
  const box = $("exLevels");
  box.innerHTML = "";
  LEVELS.forEach((L, i) => {
    const b = document.createElement("button");
    b.className = "chip"; b.type = "button"; b.dataset.lv = i + 1; b.textContent = L;
    b.addEventListener("click", () => exSetLevel(i + 1));
    box.appendChild(b);
  });
  $("exSubmit").addEventListener("click", exSubmit);
  $("exQuit").addEventListener("click", exBoard);
  if(!S.sample) $("exWarn").hidden = false;
  exSetLevel(S.P.exam.lv || S.P.level);
}
