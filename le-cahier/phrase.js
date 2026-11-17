/* Le Cahier — la phrase : production libre, corrigée sans complaisance */

let PH = null;

const PH_VERBS = ["parler", "oublier", "venir", "prendre", "choisir", "ouvrir", "vivre",
  "attendre", "rendre", "suivre", "devenir", "perdre", "écrire", "répondre", "sortir", "tenir"];

const PH_FRAMES = {
  1: ["Écris une phrase au présent avec « {v} » et un lieu (à, chez, dans…).",
      "Écris une phrase au présent avec « {v} » et le mot « parce que »."],
  2: ["Écris une phrase au passé composé avec « {v} » et un complément de temps (hier, la semaine dernière…).",
      "Écris une phrase à l'imparfait avec « {v} » qui décrit une habitude passée."],
  3: ["Écris une phrase au futur avec « {v} » et une condition en « si ».",
      "Écris une phrase avec « {v} » et un pronom complément (le, la, lui, y, en).",
      "Écris deux propositions liées par « pendant que », avec « {v} »."],
  4: ["Écris une phrase avec « dont » et le verbe « {v} ».",
      "Écris une phrase au conditionnel avec « {v} » pour donner un conseil poli.",
      "Écris une phrase au plus-que-parfait avec « {v} » qui explique une conséquence."],
  5: ["Écris une phrase au subjonctif après « il faut que » avec « {v} ».",
      "Écris une phrase avec « bien que » + subjonctif et le verbe « {v} ».",
      "Écris une phrase avec « {v} » au subjonctif passé après « je regrette que »."],
  6: ["Écris une phrase au passé simple avec « {v} », comme dans un récit écrit.",
      "Écris une phrase avec « {v} » et une concordance des temps complète : "
        + "principale au passé, subordonnée au plus-que-parfait.",
      "Écris une phrase avec « {v} » et une inversion du sujet après « peut-être » ou « à peine ».",
      "Écris une phrase soutenue avec « {v} » et « quoi que » ou « pour peu que » + subjonctif."]
};

const PH_ERR = {
  not_granted:"Tu n'as pas autorisé cette page à utiliser Claude — c'est lui qui corrige ici.",
  rate_limited:"Trop de corrections d'affilée. Reprends dans quelques minutes.",
  session_expired:"Session Claude expirée : reconnecte-toi, puis réessaie.",
  invalid_json:"La correction est revenue de travers. Resoumets ta phrase.",
  refused:"Claude n'a pas voulu corriger ça. Reformule.",
  empty_completion:"Pas de correction. Réessaie avec une phrase complète.",
  upstream_error:"Connexion interrompue pendant la correction."
};

function newPhrase(){
  const lv = S.P.level;
  const frames = PH_FRAMES[lv] || PH_FRAMES[3];
  const doms = profilDomains();
  const dom = domLabel(doms[(Math.random() * doms.length) | 0]).toLowerCase();
  const task = frames[(Math.random() * frames.length) | 0]
    .replace("{v}", PH_VERBS[(Math.random() * PH_VERBS.length) | 0])
    + " Parle de " + dom + ".";
  PH = {task, lv, done:false};
  $("phTask").textContent = task;
  $("phLevel").textContent = LEVELS[lv - 1];
  $("phIn").value = "";
  $("phIn").readOnly = false;
  $("phIn").className = "seinput";
  $("phOut").innerHTML = "";
  $("phNote").textContent = "";
  $("phGo").hidden = false;
  $("phNew").textContent = "Autre consigne";
  setTimeout(() => $("phIn").focus(), 30);
}

function phrasePrompt(task, text, lv){
  return "Tu es un correcteur de français exigeant. Un apprenant de niveau " + LEVELS[lv - 1]
    + " a reçu cette consigne et a écrit cette phrase.\n\n"
    + "Consigne : " + task + "\n"
    + "Phrase de l'apprenant : " + text + "\n\n"
    + "Sois strict, sans complaisance : une faute d'accord, de temps, de genre, de préposition "
    + "ou une tournure que personne ne dirait en français = la phrase est fausse. "
    + "« Presque juste » n'existe pas. Ne félicite pas une phrase qui ne respecte pas la consigne.\n\n"
    + "Réponds uniquement par un objet JSON :\n"
    + '{"ok":true,"consigne":true,"corrige":"...","faute":"","mieux":""}\n'
    + "- ok : true seulement si la phrase est correcte ET naturelle ET respecte la consigne.\n"
    + "- consigne : true si la consigne est respectée.\n"
    + "- corrige : la phrase corrigée (la même si elle est juste).\n"
    + "- faute : en une phrase courte et en français simple, la faute principale ; \"\" si aucune.\n"
    + "- mieux : une façon plus naturelle de dire la même chose, ou \"\".";
}

async function submitPhrase(){
  if(!PH || PH.done) return;
  const text = $("phIn").value.trim();
  if(text.split(/\s+/).filter(Boolean).length < 4){
    $("phNote").textContent = "Une phrase complète, pas trois mots.";
    return;
  }
  if(!S.sample){
    $("phNote").textContent = PH_ERR.not_granted;
    return;
  }

  $("phGo").hidden = true;
  $("phNote").textContent = "Correction en cours…";
  PH.ctl = new AbortController();

  let r = null;
  try{
    r = await S.sample.json(phrasePrompt(PH.task, text, PH.lv),
      {modelTier:"default", cache:false, signal:PH.ctl.signal});
  }catch(e){
    const code = (e && e.code) || "upstream_error";
    if(code !== "cancelled") $("phNote").textContent = PH_ERR[code] || PH_ERR.upstream_error;
    if(["not_granted", "sampling_disabled", "not_declared", "capability_disabled"].includes(code)) S.sample = null;
    $("phGo").hidden = false;
    return;
  }

  PH.done = true;
  const ok = r && r.ok === true && r.consigne !== false;
  $("phIn").readOnly = true;
  $("phIn").classList.add(ok ? "ok" : "no");

  const out = $("phOut");
  out.innerHTML = "";
  const verdict = document.createElement("p");
  verdict.className = "phverdict " + (ok ? "good" : "bad");
  verdict.textContent = ok ? "Juste." : (r && r.consigne === false ? "Consigne non respectée." : "Faux.");
  out.appendChild(verdict);

  if(r && r.faute){
    const f = document.createElement("p");
    f.className = "phline";
    f.textContent = r.faute;
    out.appendChild(f);
  }
  if(r && r.corrige && r.corrige.trim() !== text){
    const c = document.createElement("p");
    c.className = "phfix";
    c.append(document.createTextNode("→ "), Object.assign(document.createElement("ins"), {textContent:r.corrige}));
    out.appendChild(c);
  }
  if(r && r.mieux){
    const m = document.createElement("p");
    m.className = "phline dimline";
    m.textContent = "Plus naturel : " + r.mieux;
    out.appendChild(m);
  }

  if(typeof xpGain === "function") xpGain(ok ? 15 : 4, ok ? "phrase" : null);
  S.P.phrase.n++;
  if(ok) S.P.phrase.ok++;
  noteLevelRaw(ok);
  $("phNote").textContent = S.P.phrase.ok + " phrases justes sur " + S.P.phrase.n + ".";
  $("phNew").textContent = "Phrase suivante";
  scored(ok);
  paintMargin();
  if(typeof paintLevel === "function") paintLevel();
  save();
}

function phraseInit(){
  $("phGo").addEventListener("click", submitPhrase);
  $("phNew").addEventListener("click", newPhrase);
  $("phIn").addEventListener("keydown", (e) => {
    if(e.key === "Enter" && (e.metaKey || e.ctrlKey)){ e.preventDefault(); submitPhrase(); }
  });
  if(!S.sample) $("phWarn").hidden = false;
  newPhrase();
}
