/* Le Cahier — Aujourd'hui : une seule question, « je fais quoi maintenant ? »

   Seize panneaux, c'est seize bonnes raisons de ne rien commencer. Cet écran
   ne rajoute aucun exercice : il regarde ce que la répétition espacée réclame
   aujourd'hui, ce que tu rates le plus souvent, et le temps que tu as — puis
   il tranche. Tu cliques sur la première ligne, tu n'y penses plus.

   Le temps choisi décide du plan, pas l'inverse : cinq minutes honnêtes
   valent mieux qu'une demi-heure qu'on ne fera pas. */

const JOUR_BUDGETS = [5, 15, 30];
const JOUR_PER_MIN = 6;          /* ~10 s par carte, mesuré large */

const KIND_FR = {
  trou:"Le Trou", dictee:"La Dictée", trad:"La Traduction", genre:"Le ou La",
  conj:"La Conjugaison", son:"Les Sons", mot:"Le Vocabulaire", ordre:"L'Ordre",
  decider:"Décider", imiter:"Imiter"
};
const KIND_EN = {
  trou:"sentence gaps", dictee:"dictation", trad:"translation", genre:"gender",
  conj:"conjugation", son:"minimal pairs", mot:"vocabulary", ordre:"word order",
  decider:"choosing the right form", imiter:"shadowing"
};
/* Vers quel panneau envoyer quand un type faiblit. */
const KIND_MODE = {
  trou:"trou", dictee:"dictee", genre:"genre", conj:"croise", son:"sons",
  mot:"cartes", trad:"seance", ordre:"ordre", decider:"decider", imiter:"imiter"
};

function jourBudget(){
  const b = S.P.budget;
  return JOUR_BUDGETS.indexOf(b) >= 0 ? b : 15;
}

/* Les types qui flanchent, du pire au moins pire — sans planter si la
   fonction n'existe pas dans cette version du cahier. */
function jourWeak(){
  if(typeof weakSpots !== "function") return [];
  let w = [];
  try{ w = weakSpots() || []; }catch(e){ return []; }
  /* weakSpots() rend {key, label, tries, hits, acc} — « kind:<type> » pour un
     exercice, « t:<temps> » pour un temps de conjugaison qui glisse. */
  return w.map(x => {
    if(!x || typeof x.key !== "string") return null;
    const pct = Math.round((x.acc || 0) * 100);
    if(x.key.indexOf("kind:") === 0){
      const kind = x.key.slice(5);
      if(!KIND_FR[kind]) return null;
      return {kind, mode:KIND_MODE[kind], label:KIND_FR[kind], en:KIND_EN[kind],
        pct, tries:x.tries || 0};
    }
    if(x.key.indexOf("t:") === 0){
      return {kind:"conj", mode:"croise", label:x.label || x.key.slice(2),
        en:"conjugation · " + x.key.slice(2), pct, tries:x.tries || 0};
    }
    return null;
  }).filter(Boolean);
}

/* Le plan : la séance d'abord — c'est elle qui tient le calendrier —
   puis de la production tant qu'il reste du temps. */
function jourPlan(){
  const b = jourBudget();
  const cap = b * JOUR_PER_MIN;
  const st = typeof srsStats === "function" ? srsStats() : {due:0, fresh:0, retention:null};
  const waiting = (st.due || 0) + (st.fresh || 0);
  const weak = jourWeak();

  const steps = [];
  const revise = Math.min(cap, waiting);
  if(revise > 0){
    steps.push({mode:"seance", title:"La Séance",
      detail:revise + " carte" + (revise > 1 ? "s" : "")
        + (st.due ? " · " + Math.min(st.due, revise) + " à revoir" : "")
        + (st.fresh ? " · " + st.fresh + " neuve" + (st.fresh > 1 ? "s" : "") : ""),
      min:Math.max(1, Math.round(revise / JOUR_PER_MIN)),
      why:"Ce que la mémoire réclame aujourd'hui. À faire en premier : "
        + "une carte revue en retard coûte plus cher qu'une carte neuve.",
      en:"Your due spaced-repetition cards. Always first — a card reviewed late costs more than a new one."});
  }

  /* Ce qui reste de temps après la révision — en minutes, pas en cartes :
     un bouton « 15 min » qui propose dix-sept minutes de travail est un
     bouton qui ment. */
  let left = Math.max(0, b - (steps.length ? steps[0].min : 0));

  /* Au-delà de la révision, on produit. Un type qui flanche passe devant. */
  const prod = [];
  const first = weak[0];
  if(first && first.mode && first.kind !== "trad"){
    prod.push({mode:first.mode, title:first.label, want:4,
      detail:"ton point faible · " + first.pct + "% de rappel sur " + first.tries + " essais",
      why:"C'est ce que tu rates le plus en ce moment. On y retourne pendant que c'est frais : "
        + "un point faible laissé de côté ne se répare pas tout seul.",
      en:"Your weakest spot right now (" + first.en + ") — " + first.pct + "% recall."});
  }
  /* La mission du jour passe devant l'écrit dès qu'on peut parler à un
     partenaire — c'est l'oral qui est le vrai but, le reste n'est qu'un détour. */
  const missionT = typeof dayNum === "function" ? dayNum() : -1;
  const missionDone = !!(S.P.parle && S.P.parle.day && S.P.parle.day.day === missionT && S.P.parle.day.done);
  if(S.sample && !missionDone){
    prod.push({mode:"parler", title:"Mission du jour", want:3, unit:"min", detail:"3 min · à l'oral",
      why:"Trois minutes à l'oral, micro en main : c'est ce qui compte vraiment, le reste est un détour.",
      en:"Three spoken minutes, mic in hand — the actual goal. Everything else is a detour."});
  }
  prod.push({mode:"ordre", title:"L'Ordre", want:5, unit:"phrase",
    why:"Construire la phrase entière, pas un mot : c'est là que l'ordre des mots et les accords se jouent.",
    en:"Build whole sentences from scrambled words — word order and agreement."});
  prod.push({mode:"decider", title:"Décider", want:5, unit:"choix",
    why:"Deux formes justes, une seule qui dit ce que tu veux dire. Le vrai mur du français.",
    en:"Two correct forms, one meaning. Choosing between valid options."});
  prod.push({mode:"imiter", title:"Imiter", want:4, unit:"phrase",
    why:"Écouter une vraie voix et la redire tout de suite, au même rythme : c'est la bouche qui apprend l'accent.",
    en:"Shadowing: hear a real voice and say it straight back. The mouth learns the accent, not the eyes."});

  /* Chaque bloc prend ce qu'il reste, jamais plus : le plan tient dans le temps annoncé. */
  prod.forEach(p => {
    if(left < 3) return;
    const m = Math.min(p.want, left);
    left -= m;
    steps.push({mode:p.mode, title:p.title, min:m, why:p.why, en:p.en,
      detail:p.detail || (m + " " + p.unit + (m > 1 && p.unit === "phrase" ? "s" : "")
        + (p.unit === "phrase" ? " à bâtir" : ""))});
  });

  if(!steps.length){
    steps.push({mode:"ordre", title:"L'Ordre", detail:"rien à revoir — on produit", min:b,
      why:"Aucune carte n'est due aujourd'hui. Autant bâtir des phrases plutôt que d'en revoir pour rien.",
      en:"Nothing is due today, so build sentences instead of reviewing for the sake of it."});
  }
  return {steps, budget:b, stats:st, weak};
}

function jourPaint(){
  const p = jourPlan();
  $("jLv").textContent = LEVELS[Math.max(0, S.P.level - 1)];

  const bb = $("jBudgets");
  bb.innerHTML = "";
  JOUR_BUDGETS.forEach(b => {
    const btn = document.createElement("button");
    btn.type = "button";
    btn.className = "jbud" + (b === p.budget ? " on" : "");
    btn.textContent = b + " min";
    btn.addEventListener("click", () => {
      S.P.budget = b;
      if(typeof save === "function") save();
      jourPaint();
    });
    bb.appendChild(btn);
  });

  const r = p.stats.retention;
  $("jStats").textContent =
    (p.stats.due || 0) + " à revoir · " + (p.stats.fresh || 0) + " neuve"
    + ((p.stats.fresh || 0) > 1 ? "s" : "") + " disponible"
    + ((p.stats.fresh || 0) > 1 ? "s" : "")
    + (r === null || r === undefined ? "" : " · " + r + "% de rappel")
    + (p.stats.comeback ? " · reprise douce, " + (p.stats.dueAll - p.stats.due) + " en attente" : "");

  /* Le soir, une série qui n'a pas encore été nourrie : une ligne, un bouton, cinq cartes. */
  const risk = $("jRisk");
  const en = typeof LANG !== "undefined" && LANG === "en";
  const atRisk = typeof streakAtRisk === "function" ? streakAtRisk()
    : new Date().getHours() >= 18 && S.P.last !== today() && S.P.streak > 0;
  risk.hidden = !atRisk;
  if(atRisk){
    risk.innerHTML = "";
    const t = document.createElement("span");
    t.textContent = en
      ? "Your " + S.P.streak + "-day streak ends at midnight. Five cards are enough."
      : "Ta série de " + S.P.streak + " jours se termine à minuit. Cinq cartes suffisent.";
    const b = document.createElement("button");
    b.type = "button"; b.className = "go";
    b.textContent = en ? "5 cards now" : "5 cartes maintenant";
    b.addEventListener("click", () => { S.P.budget = 5; save(); setMode("seance"); });
    risk.append(t, b);
  }

  const box = $("jSteps");
  box.innerHTML = "";
  p.steps.forEach((s, i) => {
    const row = document.createElement("button");
    row.type = "button";
    row.className = "jstep" + (i === 0 ? " lead" : "");
    const n = document.createElement("span");
    n.className = "jnum";
    n.textContent = String(i + 1);
    const mid = document.createElement("span");
    mid.className = "jmid";
    const kd = document.createElement("span");
    kd.className = "jkind";
    kd.textContent = i === 0 ? "Quête principale" : "Quête annexe";
    mid.appendChild(kd);
    const h = document.createElement("span");
    h.className = "jtitle";
    h.textContent = s.title;
    const d = document.createElement("span");
    d.className = "jdetail";
    d.textContent = s.detail;
    const w = document.createElement("span");
    w.className = "jwhy";
    w.textContent = s.why;
    const e = document.createElement("span");
    e.className = "jen";
    e.textContent = s.en;
    mid.append(h, d, w, e);
    const t = document.createElement("span");
    t.className = "jmin";
    t.textContent = "≈ " + s.min + " min";
    row.append(n, mid, t);
    row.addEventListener("click", () => setMode(s.mode));
    box.appendChild(row);
  });

  if(typeof paintQuestList === "function") paintQuestList($("jQuests"));
  if(typeof recitPaintCard === "function") recitPaintCard();
  if(typeof paintGuide === "function") paintGuide();

  const go = $("jGo");
  go.textContent = "Commencer — " + p.steps[0].title;
  go.onclick = () => setMode(p.steps[0].mode);

  const wl = $("jWeak");
  if(!p.weak.length){ wl.hidden = true; }
  else{
    wl.hidden = false;
    wl.innerHTML = "";
    const lab = document.createElement("span");
    lab.className = "jweaklab";
    lab.textContent = "Ce qui résiste : ";
    wl.appendChild(lab);
    p.weak.slice(0, 3).forEach(x => {
      const a = document.createElement("button");
      a.type = "button";
      a.className = "jchip";
      a.textContent = x.label + " · " + x.pct + "%";
      a.title = x.en + " — " + x.pct + "% recall over " + x.tries + " tries";
      a.addEventListener("click", () => setMode(x.mode || "seance"));
      wl.appendChild(a);
    });
  }
}

let J_READY = false;

function jourInit(){
  if(!J_READY){
    J_READY = true;
    if(typeof srsReset === "function") srsReset();
  }
  jourPaint();
}
