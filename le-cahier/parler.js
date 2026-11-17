/* Le Cahier — la conversation : partenaire d'entraînement, puis débriefing
   Les fautes de la conversation reviennent en cartes.

   La mission du jour (ci-dessous) est la même conversation, cadrée : trois
   minutes, un micro qui s'arme après chaque réplique, un débriefing qui
   arrive seul à la fin. L'oral, pas l'écrit — c'est le vrai but. */

let CV = null;
const CV_MISSION_SEC = 180;

const SCENES = {
  sante: [
    {q:"un patient inquiet", o:"dans ton cabinet", b:"il a mal au dos depuis deux semaines et veut savoir si c'est grave"},
    {q:"un pharmacien pressé", o:"à la pharmacie", b:"tu viens chercher une ordonnance qui n'est pas prête"}],
  travail: [
    {q:"un collègue", o:"en réunion d'équipe", b:"il veut repousser ton projet d'un mois"},
    {q:"un client mécontent", o:"au téléphone", b:"la livraison a trois jours de retard"}],
  quotidien: [
    {q:"ton voisin", o:"dans l'entrée de l'immeuble", b:"il se plaint du bruit de samedi soir"},
    {q:"un garagiste", o:"au garage", b:"ta voiture fait un bruit bizarre et il faut expliquer lequel"}],
  admin: [
    {q:"une agente de Service Canada", o:"au guichet", b:"il manque un document à ton dossier"},
    {q:"ton propriétaire", o:"au téléphone", b:"le chauffage ne marche plus depuis trois jours"}],
  actu: [
    {q:"un ami bavard", o:"au café", b:"il n'est pas d'accord avec toi sur une actualité récente"},
    {q:"une journaliste", o:"dans la rue", b:"elle te demande ton avis pour un micro-trottoir"}],
  voyage: [
    {q:"un agent SNCF", o:"au guichet de la gare", b:"ton train est annulé et tu dois arriver ce soir"},
    {q:"un réceptionniste", o:"à l'hôtel", b:"la chambre réservée n'est plus disponible"}],
  famille: [
    {q:"ta belle-sœur", o:"à un repas de famille", b:"elle te demande des nouvelles de ton travail"},
    {q:"un parent d'élève", o:"devant l'école", b:"il organise une sortie et cherche des volontaires"}],
  cuisine: [
    {q:"un poissonnier", o:"au marché", b:"tu veux préparer un plat mais tu ne sais pas quoi prendre"},
    {q:"un serveur", o:"au restaurant", b:"tu as une allergie et le plat du jour pose problème"}],
  sport: [
    {q:"un coach de salle", o:"à la salle de sport", b:"tu reprends après une blessure et il faut l'expliquer"},
    {q:"un partenaire de course", o:"avant un dix kilomètres", b:"il veut connaître ton plan d'entraînement"}],
  culture: [
    {q:"une libraire", o:"dans une librairie", b:"tu cherches un roman mais tu ne te souviens plus du titre"},
    {q:"un ami cinéphile", o:"après une séance", b:"il a détesté le film que tu as aimé"}]
};

/* Chaque interlocuteur a un nom et un visage : on parle à quelqu'un, pas à « un client ». */
const NPCS = {
  "un patient inquiet":["M. Roy", "🧓"], "un pharmacien pressé":["M. Lavoie", "👨‍⚕️"],
  "un collègue":["Étienne", "🧑‍💼"], "un client mécontent":["Mme Tremblay", "😤"],
  "ton voisin":["M. Bélanger", "🧔"], "un garagiste":["Gilles", "👨‍🔧"],
  "une agente de Service Canada":["Mme Pelletier", "👩‍💼"], "ton propriétaire":["M. Gauthier", "🧐"],
  "un ami bavard":["Mathieu", "🗣️"], "une journaliste":["Camille", "🎙️"],
  "un agent SNCF":["M. Perrin", "🧑‍✈️"], "un réceptionniste":["Antoine", "🛎️"],
  "ta belle-sœur":["Isabelle", "👩‍🦰"], "un parent d'élève":["M. Leclerc", "👨‍👧"],
  "un poissonnier":["Yvon", "🧑‍🍳"], "un serveur":["Julien", "🍽️"],
  "un coach de salle":["Marc", "🏋️"], "un partenaire de course":["Sophie", "🏃"],
  "une libraire":["Mme Dubois", "📚"], "un ami cinéphile":["Léa", "🎬"]
};
const npcOf = (sc) => {
  const n = NPCS[sc && sc.q];
  return n ? {name:n[0], face:n[1]} : {name:"", face:"🎭"};
};

/* La scène du jour ne change pas à chaque clic : elle est tirée de la date, pour
   que la mission annoncée soit celle qu'on rencontre. */
function missionScene(){
  const doms = profilDomains(), t = dayNum();
  const d = doms[t % doms.length];
  const list = SCENES[d] || SCENES.quotidien;
  return {...list[(t >> 1) % list.length], dom:d};
}

/* L'encadré de l'interlocuteur : visage, nom, rôle, lieu, situation. */
function showNpc(sc){
  const en = typeof LANG !== "undefined" && LANG === "en";
  const npc = npcOf(sc);
  const cap = (x) => x.charAt(0).toUpperCase() + x.slice(1);
  $("cvNpP").textContent = npc.face;
  $("cvNpN").textContent = sc.free ? (en ? "At your request" : "À ta demande") : npc.name;
  $("cvNpN").dataset.keep = "1";
  $("cvNpR").textContent = sc.free ? "" : cap(tr(sc.q)) + " · " + tr(sc.o);
  $("cvNpT").textContent = cap(tr(sc.b)) + ".";
  const log = $("cvLog");
  log.style.setProperty("--npc", JSON.stringify(npc.face));
  log.style.setProperty("--hero", JSON.stringify((S.P.hero && S.P.hero.avatar) || "🦊"));
}

function pickScene(){
  const doms = profilDomains();
  const d = doms[(Math.random() * doms.length) | 0];
  const list = SCENES[d] || SCENES.quotidien;
  return {...list[(Math.random() * list.length) | 0], dom:d};
}

/* Un partenaire, pas un inconnu : il se souvient des fois d'avant
   et des fautes qui reviennent. */
function cvMemory(){
  const list = S.P.convos || [];
  if(!list.length) return "";
  const last = list[list.length - 1];
  const tally = {};
  list.slice(-4).forEach(c => (c.f || []).forEach(f => { tally[f] = (tally[f] || 0) + 1; }));
  const often = Object.keys(tally).filter(k => tally[k] >= 2).slice(0, 4);
  return "\n\nCe que tu sais de lui :\n"
    + "- Vous vous êtes déjà parlé " + list.length + " fois.\n"
    + (last.r ? "- La dernière fois : " + last.r + "\n" : "")
    + (often.length ? "- Fautes qui reviennent chez lui : " + often.join(" ; ")
      + ". Amène-le naturellement sur ce terrain pour qu'il doive réessayer.\n" : "");
}

function cvRules(sc, lv){
  const nm = npcOf(sc).name;
  return "Nous faisons un jeu de rôle en français. Tu joues " + sc.q
    + (sc.o ? ", " + sc.o : "") + (nm ? " — tu t'appelles " + nm : "") + ". Situation : " + sc.b + ".\n\n"
    + "Règles strictes :\n"
    + "- Tu réponds UNIQUEMENT en français, jamais un mot d'anglais, quoi qu'il arrive.\n"
    + "- Tu restes dans ton rôle du début à la fin.\n"
    + "- Tu ne le corriges JAMAIS ouvertement. Mais quand sa phrase est fautive, reprends l'idée "
    + "correctement dans ta propre réponse, l'air de rien : s'il dit « j'ai allé chez le médecin », "
    + "tu enchaînes « ah, vous êtes allé chez le médecin… ». Sans jamais signaler que tu corriges.\n"
    + "- Niveau " + LEVELS[lv - 1] + " au départ : un français naturel mais à sa portée.\n"
    + "- S'il répond vite, juste et long, monte d'un cran : phrases plus riches, questions plus "
    + "ouvertes, un mot de vocabulaire qu'il devra deviner. S'il bloque ou répond en deux mots, "
    + "simplifie — sans le dire.\n"
    + "- Une à trois phrases par réponse, pas plus.\n"
    + "- Tu finis presque toujours par une question ou une demande, pour qu'il doive répondre.\n"
    + "- S'il écrit en anglais, tu réponds en français et tu reposes la question plus simplement."
    + cvMemory() + "\n\n"
    + "Commence maintenant : dis la première réplique, dans ton rôle.";
}

function cvBubble(who, text){
  const b = document.createElement("div");
  b.className = "bub " + who;
  b.textContent = text;
  $("cvLog").appendChild(b);
  $("cvLog").scrollTop = $("cvLog").scrollHeight;
  return b;
}

async function cvStart(){
  if(!S.sample){ $("cvNote").textContent = PH_ERR.not_granted; return; }
  const wish = $("cvTopic").value.trim();
  const sc = wish
    ? {q:"un interlocuteur crédible pour cette situation", o:"", b:wish, dom:"libre", free:true}
    : pickScene();
  const lv = S.P.level;
  CV = {sc, lv, turns:[{role:"user", content:cvRules(sc, lv)}], busy:false, done:false, n:0};

  showNpc(sc);
  $("cvLog").innerHTML = "";
  $("cvOut").innerHTML = "";
  $("cvNote").textContent = "";
  $("cvStart").textContent = "Autre situation";
  $("cvEnd").hidden = false;
  $("cvRow").hidden = false;
  await cvReply();
}

async function cvReply(){
  if(CV.busy) return;
  CV.busy = true;
  const bub = cvBubble("them", "…");
  try{
    const {text} = await S.sample(CV.turns, {
      modelTier:"quick", cache:false,
      onText:({text}) => { bub.textContent = text; $("cvLog").scrollTop = $("cvLog").scrollHeight; }
    });
    CV.turns.push({role:"assistant", content:text});
    CV.lastReplyText = text;
    if($("cvSpeak").checked) speakFr(text, .95);
  }catch(e){
    bub.remove();
    const code = (e && e.code) || "upstream_error";
    $("cvNote").textContent = PH_ERR[code] || PH_ERR.upstream_error;
    if(["not_granted", "sampling_disabled", "not_declared", "capability_disabled"].includes(code)) S.sample = null;
  }
  CV.busy = false;
}

async function cvSend(){
  if(!CV || CV.busy || CV.done) return;
  const v = $("cvIn").value.trim();
  if(!v){ $("cvNote").textContent = "Réponds-lui. En français, même approximatif."; return; }
  /* Le micro se coupe à l'envoi : sinon il transcrirait la réponse lue à voix haute. */
  if(CV_LISTEN && CV_LISTEN.isOn()) CV_LISTEN.stop();
  clearTimeout(CV.sendTimer);
  $("cvIn").value = "";
  cvBubble("me", v);
  CV.turns.push({role:"user", content:v});
  CV.n++;
  // on garde les instructions et les derniers échanges
  if(CV.turns.length > 17) CV.turns = [CV.turns[0]].concat(CV.turns.slice(-16));
  $("cvNote").textContent = CV.mission ? ""
    : CV.n < 4 ? "Continue — il faut au moins quatre répliques pour un débriefing utile." : "";
  await cvReply();
  if(CV.mission) missionArmAfterReply();
}

/* ---------- la mission du jour : trois minutes, micro en main ----------
   Même moteur que la conversation libre, mais cadré dans le temps et pensé
   pour ne jamais faire taper : le micro se réarme tout seul après chaque
   réplique, quand l'appareil le permet, et le débriefing arrive seul à la
   fin. Taper reste le filet de sécurité, jamais le chemin par défaut. */

/* Une fois la réplique dite, on laisse le temps de la parole s'écouler
   avant de tendre le micro — sinon on enregistre la fin de sa propre voix. */
function missionArmAfterReply(){
  if(!CV || !CV.mission || CV.done) return;
  const spoke = $("cvSpeak").checked && CV.lastReplyText;
  const delay = spoke
    ? (typeof imModelSec === "function" ? imModelSec(CV.lastReplyText, .95) : 2.2) * 1000 + 450
    : 150;
  CV.armTimer = setTimeout(cvArmTurn, delay);
}

function cvArmTurn(){
  if(!CV || !CV.mission || CV.done) return;
  const btn = $("cvMic");
  if(!CV_LISTEN){ setTimeout(() => $("cvIn").focus(), 30); return; }
  if(CV_LISTEN.kind === "sr"){
    if(!CV_LISTEN.start()) btn.classList.add("ready");
  }else btn.classList.add("ready");         /* le dictaphone demande toujours un vrai tap */
}

function missionClockTick(){
  if(!CV || !CV.mission) return;
  CV.secLeft--;
  const m = Math.floor(Math.max(0, CV.secLeft) / 60), s = Math.max(0, CV.secLeft) % 60;
  $("cvClock").textContent = m + ":" + String(s).padStart(2, "0");
  $("cvClock").classList.toggle("urgent", CV.secLeft <= 20);
  if(CV.secLeft <= 0 || CV.wantEnd) cvMissionEnd();
}

async function cvMissionStart(){
  if(!S.sample){ $("cvNote").textContent = PH_ERR.not_granted; return; }
  if(CV){ clearInterval(CV.timer); clearTimeout(CV.armTimer); clearTimeout(CV.sendTimer); }
  const sc = missionScene();
  const lv = S.P.level;
  CV = {sc, lv, turns:[{role:"user", content:cvRules(sc, lv)}], busy:false, done:false, n:0,
    mission:true, secLeft:CV_MISSION_SEC, lastReplyText:""};

  showNpc(sc);
  $("cvLog").innerHTML = ""; $("cvOut").innerHTML = ""; $("cvNote").textContent = "";
  $("cvMissionGo").hidden = true; $("cvMissionStop").hidden = false;
  $("cvClock").hidden = false; $("cvClock").textContent = "3:00"; $("cvClock").classList.remove("urgent");
  $("cvStart").hidden = true; $("cvTopic").closest("label").hidden = true; $("cvEnd").hidden = true;
  $("cvRow").hidden = false;
  clearInterval(CV.timer);
  CV.timer = setInterval(missionClockTick, 1000);

  await cvReply();
  missionArmAfterReply();
}

function cvMissionEnd(){
  if(!CV || !CV.mission) return;
  /* Une réplique est en route : on note la demande, la prochaine seconde la fera. */
  if(CV.busy){ CV.wantEnd = true; return; }
  clearTimeout(CV.armTimer);
  clearInterval(CV.timer);
  $("cvClock").hidden = true;
  $("cvMissionStop").hidden = true;
  $("cvMissionGo").hidden = false;
  $("cvStart").hidden = false;
  $("cvTopic").closest("label").hidden = false;
  if(CV_LISTEN && CV_LISTEN.isOn()) CV_LISTEN.stop();
  $("cvMic").classList.remove("ready");
  if(CV.n >= 2){
    CV.missionEnding = true;
    cvEnd();
  }else{
    CV.mission = false;
    $("cvRow").hidden = true;
    $("cvNote").textContent = tr("Trop court pour un débriefing — retente demain, trois minutes complètes.");
  }
}

function cvDebriefPrompt(){
  const dialogue = CV.turns.slice(1)
    .map(t => (t.role === "assistant" ? CV.sc.q + " : " : "Toi : ") + t.content).join("\n");
  return "Un apprenant de français de niveau " + LEVELS[CV.lv - 1]
    + " vient de faire ce jeu de rôle. Tu jouais " + CV.sc.q + ".\n\n" + dialogue + "\n\n"
    + "Corrige SES répliques à lui (les lignes « Toi : »), sans complaisance : accords, temps, "
    + "genres, prépositions, tournures que personne ne dirait. « Presque juste » n'existe pas. "
    + "Ne relève pas deux fois la même faute.\n\n"
    + "Réponds uniquement par un objet JSON :\n"
    + '{"verdict":"...","note":12,"fautes":[{"tu":"...","juste":"...","pourquoi":"..."}],'
    + '"evite":"...","resume":"...","recurrents":["..."],"ampleur":"juste",'
    + '"cartes":[{"s":"... ___ ...","a":"...","d":["x","y","z"],"g":"..."}]}\n'
    + "- verdict : deux phrases, en français, sur ce qui tient et ce qui ne tient pas.\n"
    + "- note : sur 20, sévère.\n"
    + "- fautes : au plus 6, les plus importantes. \"tu\" = ce qu'il a écrit, \"juste\" = la forme "
    + "correcte, \"pourquoi\" = la règle en une phrase simple.\n"
    + "- evite : ce qu'il a contourné faute de savoir le dire, ou \"\".\n"
    + "- resume : une phrase, à la troisième personne, sur ce dont vous avez parlé et comment "
    + "il s'en est sorti. Elle servira de mémoire la prochaine fois.\n"
    + "- recurrents : 1 à 3 étiquettes courtes de ses faiblesses de fond "
    + "(ex. « passé composé avec être », « genre des noms »).\n"
    + "- ampleur : « facile » si le niveau était trop bas, « juste » si c'était le bon, "
    + "« dur » s'il a été dépassé.\n"
    + "- cartes : 3 à 5 phrases à trous construites sur SES fautes à lui, niveau "
    + LEVELS[CV.lv - 1] + ", avec 3 distracteurs plausibles et une traduction anglaise.";
}

async function cvEnd(){
  if(!CV || CV.busy || CV.done) return;
  if(CV.n < 2){ $("cvNote").textContent = "Dis-lui au moins deux choses avant de demander la correction."; return; }
  CV.busy = true;
  $("cvNote").textContent = "Débriefing en cours…";
  let r = null;
  try{
    r = await S.sample.json(cvDebriefPrompt(), {modelTier:"default", cache:false});
  }catch(e){
    CV.busy = false;
    $("cvNote").textContent = PH_ERR[(e && e.code)] || PH_ERR.upstream_error;
    /* Mission finie mais débriefing raté : on laisse un bouton pour le redemander. */
    if(CV.mission){ $("cvEnd").hidden = false; $("cvRow").hidden = true; }
    return;
  }
  CV.busy = false;
  CV.done = true;
  clearTimeout(CV.sendTimer);
  if(CV_LISTEN && CV_LISTEN.isOn()) CV_LISTEN.stop();
  $("cvRow").hidden = true;
  $("cvEnd").hidden = true;

  const out = $("cvOut");
  out.innerHTML = "";
  const note = Math.max(0, Math.min(20, Math.round((r && r.note) || 0)));
  const head = document.createElement("p");
  head.className = "phverdict " + (note >= 14 ? "good" : "bad");
  head.textContent = note + "/20";
  out.appendChild(head);
  if(r && r.verdict){
    const v = document.createElement("p");
    v.className = "phline"; v.textContent = r.verdict;
    out.appendChild(v);
  }
  (r && Array.isArray(r.fautes) ? r.fautes : []).slice(0, 6).forEach(f => {
    if(!f || !f.tu) return;
    const row = document.createElement("p");
    row.className = "phfix";
    row.append(Object.assign(document.createElement("del"), {textContent:f.tu}),
      document.createTextNode(" → "),
      Object.assign(document.createElement("ins"), {textContent:f.juste || ""}));
    out.appendChild(row);
    if(f.pourquoi){
      const w = document.createElement("p");
      w.className = "phline dimline"; w.textContent = f.pourquoi;
      out.appendChild(w);
    }
  });
  if(r && r.evite){
    const e = document.createElement("p");
    e.className = "phline dimline";
    e.textContent = "Contourné faute de savoir le dire : " + r.evite;
    out.appendChild(e);
  }

  const cards = cleanCards((r && r.cartes) || [], "conversation");
  if(cards.length){
    const stamp = Date.now().toString(36);
    cards.forEach((c, i) => { c.id = "c" + stamp + i; c.lv = CV.lv; });
    S.cards = cards.concat(S.cards).slice(0, 150);
    saveCards();
    srsReset();
    const p = document.createElement("p");
    p.className = "phline";
    p.textContent = cards.length + " cartes tirées de tes fautes rejoignent la séance.";
    out.appendChild(p);
  }

  const amp = (r && r.ampleur) || "";
  if(amp){
    const a = document.createElement("p");
    a.className = "phline dimline";
    a.textContent = amp === "facile" ? "Ce niveau est devenu trop facile pour toi à l'oral."
      : amp === "dur" ? "Tu as été dépassé : ce niveau n'est pas encore acquis à l'oral."
      : "Le niveau était le bon.";
    out.appendChild(a);
  }

  S.P.convos = (S.P.convos || []).concat([{
    d:today(), s:CV.sc.free ? CV.sc.b.slice(0, 48) : CV.sc.q, n:note,
    r:((r && r.resume) || "").slice(0, 220),
    f:(r && Array.isArray(r.recurrents) ? r.recurrents : []).slice(0, 3).map(x => String(x).slice(0, 48))
  }]).slice(-8);
  drawConvos();

  if(typeof xpGain === "function") xpGain(note * 3, "convo");
  S.P.parle.n++;
  S.P.parle.points += note;
  if(CV.mission){
    /* La mission compte pour la journée, quelle que soit la note : on récompense
       d'avoir parlé trois minutes, la note dit seulement comment. */
    S.P.parle.day = {day:dayNum(), done:true, note};
    S.P.parle.missions = (S.P.parle.missions || 0) + 1;
    if(typeof xpGain === "function") xpGain(25, null);
  }
  noteLevelRaw(note >= 14);
  scored(note >= 14);
  paintMargin();
  save();
  $("cvNote").textContent = (CV.mission ? tr("Mission faite. Demain, une autre situation.") + " " : "")
    + "Moyenne : " + Math.round(S.P.parle.points / S.P.parle.n) + "/20 sur " + S.P.parle.n + " conversations.";
  if(CV.mission){ CV.mission = false; paintMissionBox(); }
}

/* ---------- le micro ----------
   Un seul « écouteur », deux moteurs possibles derrière la même interface :
   - « dict » : la dictée de la plateforme (meilleure transcription, mais
     chaque démarrage doit venir d'un vrai tap — jamais d'un minuteur) ;
   - « sr »   : la reconnaissance vocale du navigateur, qui peut se réarmer
     toute seule entre deux répliques.
   Sans l'un ni l'autre, le bouton disparaît et on tape : le filet reste. */
let CV_LISTEN = null;
let CV_MIC_WIRED = false;

function cvSetMicState(state){
  const b = $("cvMic");
  b.classList.toggle("rec", state === "on");
  b.classList.toggle("wait", state === "starting");
  if(state === "on" || state === "starting") b.classList.remove("ready");
}

/* Ce qui est reconnu s'écrit dans le champ ; en mission, un silence après
   une phrase finie l'envoie tout seul — on parle, on ne clique pas. */
function cvHeardFinal(text){
  const inp = $("cvIn");
  const piece = String(text || "");
  inp.value = inp.value.trim() ? inp.value + piece : piece.replace(/^\s+/, "");
  if(CV && CV.mission && !CV.done){
    clearTimeout(CV.sendTimer);
    CV.sendTimer = setTimeout(() => {
      if(!CV || CV.done || CV.busy || !$("cvIn").value.trim()) return;
      if(CV_LISTEN && CV_LISTEN.isOn()) CV_LISTEN.stop();
      cvSend();
    }, 1300);
  }
}

function cvListenerDict(d){
  /* La dictée est partagée avec Imiter : on n'écoute que les séances
     lancées d'ici, sinon une prise d'Imiter s'écrirait dans la conversation. */
  let on = false, mine = false;
  const offs = [];
  offs.push(d.onPartial(({text}) => { if(mine && text) $("cvNote").textContent = "… " + text; }));
  offs.push(d.onFinal(({text}) => { if(!mine) return; $("cvNote").textContent = ""; cvHeardFinal(text); }));
  offs.push(d.onState(({state, reason}) => {
    if(!mine) return;
    on = state !== "idle";
    cvSetMicState(state === "listening" ? "on" : state === "starting" ? "starting" : "off");
    if(state !== "idle") return;
    mine = false;
    if(reason === "unavailable" || reason === "not_granted"){
      /* La dictée est refusée ou absente : on retombe sur le navigateur, une fois. */
      offs.forEach(f => f());
      CV_LISTEN = cvListenerSR() || null;
      if(!CV_LISTEN) $("cvMic").hidden = true;
      $("cvNote").textContent = reason === "not_granted"
        ? tr("Micro refusé — tu peux toujours taper.") : "";
    }else if(reason === "rate_limited") $("cvNote").textContent = tr("Le micro est occupé ailleurs — réessaie dans un instant.");
    else if(reason === "upstream_error") $("cvNote").textContent = tr("Le micro a lâché — tape, ou retente.");
  }));
  return {
    kind:"dict",
    isOn:() => on,
    detach:() => offs.forEach(f => f()),
    /* toujours depuis le clic : start() doit partir avant tout await */
    start:() => {
      mine = true;
      d.start({language:"fr"}).catch((e) => {
        const code = e && e.code;
        if(code === "no_gesture"){ $("cvMic").classList.add("ready"); return; }
        if(code === "not_granted" || code === "unavailable") return;   /* onState gère le repli */
        if(code !== "stopped" && code !== "dismissed") $("cvNote").textContent = tr("Le micro n'a pas démarré.");
      });
      return true;
    },
    stop:() => { d.stop().catch(() => {}); }
  };
}

function cvListenerSR(){
  const SR = window.SpeechRecognition || window.webkitSpeechRecognition;
  if(!SR) return null;
  let rec = null, on = false;
  try{ rec = new SR(); }catch(e){ return null; }
  rec.lang = "fr-FR"; rec.interimResults = true; rec.continuous = false;
  rec.addEventListener("result", (e) => {
    let interim = "";
    for(let i = e.resultIndex; i < e.results.length; i++){
      const t = e.results[i][0].transcript.trim();
      /* Une espace devant chaque morceau ; cvHeardFinal la retire si le champ est vide. */
      if(e.results[i].isFinal){ if(t) cvHeardFinal(" " + t); }
      else interim += e.results[i][0].transcript;
    }
    $("cvNote").textContent = interim ? "… " + interim : "";
  });
  rec.addEventListener("end", () => { on = false; cvSetMicState("off"); });
  rec.addEventListener("error", (e) => {
    on = false; cvSetMicState("off");
    if(e && (e.error === "not-allowed" || e.error === "service-not-allowed")){
      CV_LISTEN = null; $("cvMic").hidden = true;
      $("cvNote").textContent = tr("Micro refusé — tu peux toujours taper.");
    }
  });
  return {
    kind:"sr",
    isOn:() => on,
    start:() => {
      if(on) return true;
      try{ rec.start(); on = true; cvSetMicState("on"); return true; }
      catch(e){ return false; }
    },
    stop:() => { try{ rec.stop(); }catch(e){} }
  };
}

/* Appelé à l'ouverture du panneau, puis une seconde fois si la dictée de la
   plateforme répond après coup (voir connect() dans cahier.js). */
function cvMic(){
  if(CV_LISTEN){
    if(CV_LISTEN.isOn()) CV_LISTEN.stop();
    if(CV_LISTEN.detach) CV_LISTEN.detach();
  }
  CV_LISTEN = (S.dictation && cvListenerDict(S.dictation)) || cvListenerSR();
  $("cvMic").hidden = !CV_LISTEN;
  if(CV_MIC_WIRED) return;
  CV_MIC_WIRED = true;
  $("cvMic").addEventListener("click", () => {
    if(!CV_LISTEN) return;
    if(CV_LISTEN.isOn()){ CV_LISTEN.stop(); return; }
    CV_LISTEN.start();
  });
}

function drawConvos(){
  const list = (S.P.convos || []).slice().reverse();
  const ul = $("cvHist");
  ul.innerHTML = "";
  ul.hidden = !list.length;
  $("cvHistHead").hidden = !list.length;
  list.forEach(c => {
    const li = document.createElement("li");
    li.appendChild(Object.assign(document.createElement("b"), {textContent:c.n + "/20 · " + c.s}));
    if(c.r) li.append(document.createTextNode(" — " + c.r));
    ul.appendChild(li);
  });
}

/* L'encart de la mission : fait ou à faire aujourd'hui, et combien en tout. */
function paintMissionBox(){
  const en = typeof LANG !== "undefined" && LANG === "en";
  const d = S.P.parle.day;
  const done = !!(d && d.day === dayNum() && d.done);
  const n = S.P.parle.missions || 0;
  $("cvMissionState").textContent = done
    ? (en ? "Done today · " + d.note + "/20" : "Faite aujourd'hui · " + d.note + "/20")
    : (en ? "Not done yet today" : "Pas encore faite aujourd'hui");
  $("cvMissionState").classList.toggle("done", done);
  $("cvMissionCount").textContent = n ? n + (en ? " missions so far" : " missions jusqu'ici") : "";
  const sc = missionScene(), npc = npcOf(sc);
  const cap = (x) => x.charAt(0).toUpperCase() + x.slice(1);
  const who = $("cvMissionWho");
  if(who){
    who.dataset.keep = "1";
    who.textContent = (en ? "Today you meet " : "Aujourd'hui, tu rencontres ") + npc.face + " " + npc.name
      + " — " + tr(sc.q) + ", " + tr(sc.o) + ".";
  }
  $("cvMissionGo").textContent = done ? (en ? "One more, for the pleasure" : "Une de plus, pour le plaisir")
    : (en ? "Start the mission · 3 min" : "Lancer la mission · 3 min");
  if(!S.sample) $("cvMissionGo").disabled = true;
}

let CV_READY = false;

function parlerInit(){
  if(CV_READY){ paintMissionBox(); return; }
  CV_READY = true;
  $("cvStart").addEventListener("click", cvStart);
  $("cvEnd").addEventListener("click", cvEnd);
  $("cvSend").addEventListener("click", cvSend);
  $("cvMissionGo").addEventListener("click", cvMissionStart);
  $("cvMissionStop").addEventListener("click", cvMissionEnd);
  $("cvIn").addEventListener("keydown", (e) => {
    if(e.key === "Enter" && !e.shiftKey){ e.preventDefault(); cvSend(); }
  });
  /* Taper au clavier pendant la mission désarme l'envoi automatique. */
  $("cvIn").addEventListener("input", () => { if(CV && CV.sendTimer) clearTimeout(CV.sendTimer); });
  cvMic();
  drawConvos();
  paintMissionBox();
  if(!S.sample) $("cvWarn").hidden = false;
}
