/* Le Cahier — le profil : ce que cet apprenant-là doit savoir dire */

const DOMAINS = [
  {k:"sante", l:"Santé et soins"}, {k:"travail", l:"Travail et réunions"},
  {k:"quotidien", l:"Vie quotidienne"}, {k:"admin", l:"Démarches et administration"},
  {k:"actu", l:"Actualité et débat"}, {k:"voyage", l:"Voyage et transports"},
  {k:"famille", l:"Famille et amis"}, {k:"cuisine", l:"Cuisine et marché"},
  {k:"sport", l:"Sport et santé physique"}, {k:"culture", l:"Films, livres, musique"}
];
const domLabel = (k) => (DOMAINS.find(d => d.k === k) || {l:k}).l;

/* Le profil sert à trois choses : ce qu'on fabrique, ce qu'on demande d'écrire,
   et combien de cartes neuves tiennent dans la journée. */
function profilDomains(){
  const d = (S.P.profil && S.P.profil.domains) || [];
  return d.length ? d : ["quotidien"];
}

function newPerDay(){
  const m = (S.P.profil && S.P.profil.minutes) || 10;
  return Math.max(4, Math.min(30, Math.round(m)));
}

/* ---------- diagnostic : la faute qui revient, pas la carte ratée ---------- */
/* Par type : les trente derniers jours (le journal), dès qu'il y a assez de
   rappels récents ; avant cela, tout l'historique. Par temps de conjugaison :
   tout l'historique, le journal ne descend pas à ce grain. */
function weakSpots(){
  const b = {};
  const add = (key, label, tries, hits) => {
    const x = b[key] = b[key] || {key, label, tries:0, hits:0};
    x.tries += tries; x.hits += hits;
  };
  const recent = typeof retention30 === "function" && retention30().rev >= 20;
  registry().forEach(it => {
    const s = S.P.srs[it.id];
    if(!s) return;
    const tries = s[5] || 0, hits = s[6] || 0;
    if(!tries) return;
    if(!recent) add("kind:" + it.kind, (KIND_LABEL[it.kind] || it.kind).toLowerCase(), tries, hits);
    if(it.kind === "conj"){
      const f = POOL[+it.id.slice(1)];
      if(f) add("t:" + f.t, (/^[aeiouéè]/i.test(f.t) ? "l'" : "le ") + f.t, tries, hits);
    }
  });
  if(recent){
    Object.keys(KIND_LABEL).forEach(k => {
      const r = retention30(k);
      if(r.rev) add("kind:" + k, KIND_LABEL[k].toLowerCase(), r.rev, r.ok);
    });
  }
  return Object.values(b)
    .filter(x => x.tries >= 6)
    .map(x => ({...x, acc:x.hits / x.tries}))
    .filter(x => x.acc < .85)
    .sort((x, y) => x.acc - y.acc)
    .slice(0, 3);
}

/* Les sangsues : ce qui dort, avec de quoi le réveiller. */
function paintLeech(){
  const box = $("prLeech");
  if(!box || typeof leechList !== "function") return;
  const en = typeof LANG !== "undefined" && LANG === "en";
  box.innerHTML = "";
  const ids = leechList();
  if(!ids.length){
    box.appendChild(Object.assign(document.createElement("p"),
      {className:"lede dim", textContent:en ? "No leech. Every card still comes back." : "Aucune sangsue. Toutes les cartes reviennent."}));
    return;
  }
  ids.forEach(id => {
    const it = srsItem(id);
    if(!it) return;
    const d = it.data;
    const text = it.kind === "mot" ? (typeof artOf === "function" ? artOf(d) : "") + d.fr
      : it.kind === "genre" ? d.n : it.kind === "conj" ? d.v + " · " + d.t
      : it.kind === "son" ? d.a + " / " + d.b : it.kind === "decider" ? d.stem.replace(/<[^>]+>/g, "")
      : d.s ? d.s.replace("___", d.a) : id;
    const row = document.createElement("div");
    row.className = "leechrow";
    const lt = document.createElement("span");
    lt.className = "lt"; lt.lang = "fr";
    lt.textContent = (KIND_LABEL[it.kind] || it.kind) + " · " + text;
    const b = document.createElement("button");
    b.className = "ghost mkmini"; b.type = "button";
    b.textContent = en ? "Wake it" : "Réveiller";
    b.addEventListener("click", () => { leechResume(id); save(); paintMargin(); paintLeech(); });
    row.append(lt, b);
    box.appendChild(row);
  });
}

function weakText(){
  const w = weakSpots();
  if(!w.length) return "";
  return w.map(x => x.label + " (" + Math.round(x.acc * 100) + "%)").join(", ");
}

/* ---------- fabrication de cartes sur son monde ---------- */
function profilPrompt(n){
  const p = S.P.profil, lv = S.P.level, w = weakText();
  return "Tu fabriques des cartes de français pour un apprenant précis. "
    + "Écris " + n + " phrases à trous.\n\n"
    + "Niveau visé : " + LEVELS[lv - 1] + " (rien au-dessus)\n"
    + (p.why ? "Pourquoi il apprend : " + p.why + "\n" : "")
    + "Ce dont il a besoin de parler : " + profilDomains().map(domLabel).join(", ") + "\n"
    + (p.l1 ? "Sa langue la plus forte : " + p.l1 + " — évite les pièges qu'elle lui tend.\n" : "")
    + (w ? "Ce qu'il rate en ce moment : " + w + " — vise ça en priorité.\n" : "")
    + "\nRègles :\n"
    + "- Des phrases qu'il pourrait vraiment entendre ou dire dans ces domaines. "
    + "Rien qui sente le manuel.\n"
    + "- Un seul mot ou une seule expression remplacée par ___ , jamais un mot grammatical banal.\n"
    + "- 3 distracteurs de même nature grammaticale, plausibles ailleurs mais faux ici.\n"
    + "- Une traduction anglaise naturelle de la phrase complète.\n"
    + "- Entre 7 et 16 mots par phrase.\n\n"
    + "Réponds uniquement par un tableau JSON d'objets {\"s\",\"a\",\"d\",\"g\"} :\n"
    + "[{\"s\":\"Le patient se plaint d'une douleur ___ depuis trois jours.\",\"a\":\"persistante\","
    + "\"d\":[\"bruyante\",\"gratuite\",\"salée\"],\"g\":\"The patient has had a persistent pain for three days.\"}]";
}

async function makeMyCards(){
  if(!S.sample){ $("prNote").textContent = PH_ERR.not_granted; return; }
  const go = $("prMake");
  go.disabled = true;
  $("prNote").textContent = "Claude écrit tes cartes…";
  let cards = [];
  try{
    const raw = await S.sample.json(profilPrompt(10), {modelTier:"default", cache:false});
    cards = cleanCards(raw, "profil");
  }catch(e){
    const code = (e && e.code) || "upstream_error";
    $("prNote").textContent = PH_ERR[code] || PH_ERR.upstream_error;
    if(["not_granted", "sampling_disabled", "not_declared", "capability_disabled"].includes(code)) S.sample = null;
    go.disabled = false;
    return;
  }
  go.disabled = false;
  if(!cards.length){ $("prNote").textContent = "Rien d'utilisable n'est revenu. Réessaie."; return; }

  const stamp = Date.now().toString(36);
  cards.forEach((c, i) => { c.id = "p" + stamp + i; c.lv = S.P.level; });
  S.cards = cards.concat(S.cards).slice(0, 150);
  saveCards();
  srsReset();
  S.queue = cards.map(c => c.id).concat(S.queue);
  $("prNote").textContent = cards.length + " cartes ajoutées, à ton niveau et sur tes sujets. "
    + "Elles entrent dans la séance — et deviennent aussi des dictées.";
  drawMine();
  paintMargin();
}

function drawMine(){
  const mine = S.cards.filter(c => c.src === "profil");
  const ul = $("prList");
  ul.innerHTML = "";
  ul.hidden = !mine.length;
  mine.slice(0, 6).forEach(c => {
    const li = document.createElement("li");
    li.textContent = c.s.replace("___", "……");
    ul.appendChild(li);
  });
  if(mine.length > 6){
    const li = document.createElement("li");
    li.className = "more";
    li.textContent = "et " + (mine.length - 6) + " autres dans la séance.";
    ul.appendChild(li);
  }
}

/* ---------- panneau ---------- */
function paintWeak(){
  const w = weakSpots();
  const box = $("prWeak");
  box.innerHTML = "";
  const ret = $("prRet");
  if(ret && typeof retention30 === "function"){
    const r = retention30();
    const en = typeof LANG !== "undefined" && LANG === "en";
    ret.textContent = r.rev
      ? (en ? "30-day recall: " : "Rappel 30 j : ") + Math.round(r.acc * 100) + " % " + (en ? "over " : "sur ")
        + r.rev + (en ? " recalls · target 85–90 %" : " rappels · cible 85–90 %")
      : (en ? "30-day recall: not enough data yet" : "Rappel 30 j : pas encore assez de données");
  }
  paintLeech();
  if(!w.length){
    box.appendChild(Object.assign(document.createElement("p"), {className:"lede dim",
      textContent:"Pas encore assez de rappels pour dire ce qui cloche. Reviens après quelques séances."}));
    return;
  }
  w.forEach(x => {
    const row = document.createElement("div");
    row.className = "lvrow";
    const name = document.createElement("span");
    name.className = "weakname"; name.textContent = x.label;
    const track = document.createElement("div");
    track.className = "lvtrack";
    const fill = document.createElement("div");
    fill.className = "lvfill weak";
    fill.style.width = Math.round(x.acc * 100) + "%";
    track.appendChild(fill);
    const num = document.createElement("span");
    num.className = "lvnum"; num.textContent = Math.round(x.acc * 100) + "% · " + x.tries;
    row.append(name, track, num);
    box.appendChild(row);
  });
}

function readProfil(){
  const p = S.P.profil;
  $("prWhy").value = p.why || "";
  $("prL1").value = p.l1 || "";
  $("prMin").value = p.minutes || 10;
  $("prMinOut").textContent = (p.minutes || 10) + " min";
  const box = $("prChips");
  box.innerHTML = "";
  DOMAINS.forEach(d => {
    const b = document.createElement("button");
    b.className = "chip" + ((p.domains || []).includes(d.k) ? " on" : "");
    b.type = "button";
    b.textContent = d.l;
    b.setAttribute("aria-pressed", (p.domains || []).includes(d.k) ? "true" : "false");
    b.addEventListener("click", () => {
      const on = b.classList.toggle("on");
      b.setAttribute("aria-pressed", on ? "true" : "false");
    });
    box.appendChild(b);
  });
}

function saveProfil(){
  const chosen = [...$("prChips").children]
    .filter(b => b.classList.contains("on"))
    .map(b => (DOMAINS.find(d => d.l === b.textContent) || {}).k)
    .filter(Boolean);
  S.P.profil = {
    why:$("prWhy").value.trim().slice(0, 300),
    l1:$("prL1").value.trim().slice(0, 40),
    minutes:Math.max(5, Math.min(40, +$("prMin").value || 10)),
    domains:chosen
  };
  save();
  paintMargin();
  $("prNote").textContent = "Profil enregistré. " + newPerDay()
    + " cartes neuves par jour, et les consignes d'écriture viendront de tes sujets.";
}

let PR_READY = false;

function profilInit(){
  if(PR_READY){ paintWeak(); drawMine(); return; }
  PR_READY = true;
  readProfil();
  $("prSave").addEventListener("click", saveProfil);
  $("prMake").addEventListener("click", makeMyCards);
  $("prMin").addEventListener("input", () => { $("prMinOut").textContent = $("prMin").value + " min"; });
  if(!S.sample) $("prWarn").hidden = false;
  paintWeak();
  drawMine();
}
