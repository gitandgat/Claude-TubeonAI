/* Le Cahier — Décider : choisir entre deux formes justes.

   Le vrai mur du français n'est pas la règle, c'est le choix : deux formes
   sont grammaticales, une seule dit ce que tu veux dire. Deux sortes
   d'épreuves ici :

   « sens » — on annonce d'abord ce qu'on veut dire, et c'est ce sens-là qui
   impose le mode. Les deux phrases sont correctes ; se tromper, ce n'est pas
   faire une faute de grammaire, c'est dire autre chose que prévu.

   « choix » — une seule forme passe, et on explique pourquoi l'autre tombe. */

const DECIDE = [
  /* ---------- le sens commande ---------- */
  {k:"sens", lv:4, tag:"subjonctif ou indicatif",
   stem:"Je cherche un appartement qui ___ un balcon.",
   means:["L'appartement existe — je l'ai visité", "Je n'en connais aucun : c'est ce que je cherche"],
   forms:["a", "ait"],
   why:["L'appartement est réel et identifié : l'indicatif l'affirme — « qui <b>a</b> un balcon ».",
     "Son existence n'est pas affirmée, elle est seulement souhaitée : le subjonctif — « qui <b>ait</b> un balcon »."]},

  {k:"sens", lv:2, tag:"imparfait ou passé composé",
   stem:"Hier soir, je ___ la télévision.",
   means:["Je plante le décor : j'étais en train de la regarder", "Je raconte un fait terminé, borné dans le temps"],
   forms:["regardais", "ai regardé"],
   why:["L'imparfait étale l'action sans la boucler : c'est le fond sur lequel autre chose arrive.",
     "Le passé composé la donne finie et comptable — « je l'ai regardée, puis j'ai éteint »."]},

  {k:"sens", lv:3, tag:"antériorité",
   stem:"Quand je suis arrivé, il ___.",
   means:["Il est parti après mon arrivée", "Il était déjà parti avant que j'arrive"],
   forms:["est parti", "était déjà parti"],
   why:["Deux faits qui se suivent : le passé composé les met l'un après l'autre.",
     "Le plus-que-parfait recule d'un cran : son départ précède mon arrivée."]},

  {k:"sens", lv:5, tag:"doute ou quasi-certitude",
   stem:"Je ne pense pas qu'il ___ venir.",
   means:["Je doute franchement", "Je penche pour oui, je nuance à peine"],
   forms:["puisse", "peut"],
   why:["Après un verbe d'opinion nié, le subjonctif est la forme attendue : il suspend l'affirmation.",
     "L'indicatif après « je ne pense pas que » existe, et il trahit que tu y crois quand même — nuance d'oral, assumée."]},

  {k:"sens", lv:4, tag:"réel ou irréel",
   stem:"Quelle phrase dit une hypothèse <i>irréelle</i> ?",
   means:["Une vraie possibilité, pour aujourd'hui", "Une hypothèse que je sais fausse"],
   forms:["Si j'ai le temps, je viendrai.", "Si j'avais le temps, je viendrais."],
   why:["Si + présent → futur : la condition peut encore se réaliser.",
     "Si + imparfait → conditionnel : l'hypothèse est écartée d'avance. Jamais « si j'aurais »."]},

  /* ---------- une seule forme passe ---------- */
  {k:"choix", lv:2, tag:"depuis · pendant · il y a",
   stem:"Je travaille ici ___ trois ans.",
   opts:["depuis", "pendant", "il y a"], ok:0,
   why:"« Depuis » part d'un point du passé et court jusqu'à maintenant — et le verbe reste au présent. "
     + "« Pendant » enferme une durée finie, « il y a » situe un moment révolu."},

  {k:"choix", lv:2, tag:"depuis · pendant · il y a",
   stem:"J'ai quitté Paris ___ trois ans.",
   opts:["depuis", "pendant", "il y a"], ok:2,
   why:"Un départ est ponctuel et fini : « il y a trois ans » le situe. « Depuis trois ans » "
     + "demanderait une action qui dure encore."},

  {k:"choix", lv:3, tag:"qui · que · dont",
   stem:"La femme ___ je t'ai parlé est médecin.",
   opts:["qui", "que", "dont"], ok:2,
   why:"On dit « parler <b>de</b> quelqu'un » : ce « de » devient « dont ». « Qui » serait sujet, « que » complément direct."},

  {k:"choix", lv:2, tag:"qui · que · dont",
   stem:"Le livre ___ tu m'as prêté est passionnant.",
   opts:["qui", "que", "dont"], ok:1,
   why:"« Prêter quelque chose » : complément direct, donc « que ». « Qui » ferait du livre le sujet de « prêter »."},

  {k:"choix", lv:1, tag:"c'est ou il est",
   stem:"___ une très bonne avocate.",
   opts:["C'est", "Elle est"], ok:0,
   why:"Devant un groupe nominal avec déterminant (« une avocate »), c'est « c'est ». "
     + "« Elle est » appelle le nom nu : « elle est avocate »."},

  {k:"choix", lv:1, tag:"c'est ou il est",
   stem:"___ avocate depuis dix ans.",
   opts:["C'est", "Elle est"], ok:1,
   why:"Un métier sans article se comporte comme un adjectif : « elle est avocate ». "
     + "« C'est avocate » ne se dit pas."},

  {k:"choix", lv:2, tag:"savoir ou connaître",
   stem:"Tu ___ où il habite ?",
   opts:["sais", "connais"], ok:0,
   why:"« Savoir » porte une information — souvent suivi de que, si, où, comment. "
     + "« Connaître » prend un objet : on connaît un quartier, une personne."},

  {k:"choix", lv:2, tag:"savoir ou connaître",
   stem:"Je ___ bien ce quartier.",
   opts:["sais", "connais"], ok:1,
   why:"Un lieu est un objet de familiarité, pas une information : « connaître »."},

  {k:"choix", lv:2, tag:"venir de ou aller",
   stem:"Il ___ de sortir, tu l'as manqué de peu.",
   opts:["vient", "va"], ok:0,
   why:"« Venir de + infinitif » = le passé immédiat. « Aller + infinitif » regarde devant."},

  {k:"choix", lv:2, tag:"pronom direct ou indirect",
   stem:"Je ___ ai téléphoné hier soir.",
   opts:["l'", "lui"], ok:1,
   why:"On téléphone <b>à</b> quelqu'un : complément indirect, donc « lui ». "
     + "« Je l'ai appelé » marcherait, parce qu'« appeler » est direct — le pronom suit le verbe, pas le sens."},

  {k:"choix", lv:4, tag:"avant que ou après que",
   stem:"Je partirai avant qu'il ___ là.",
   opts:["soit", "est"], ok:0,
   why:"« Avant que » ouvre sur du non encore réalisé : subjonctif. « Après que » décrit du fait accompli "
     + "et prend l'indicatif — c'est la dissymétrie que presque tout le monde rate."},

  {k:"choix", lv:4, tag:"avant que ou après que",
   stem:"Je suis parti après qu'il ___ arrivé.",
   opts:["soit", "est"], ok:1,
   why:"Son arrivée a bien eu lieu : « après que » + indicatif. Le subjonctif ici est une sur-correction fréquente."},

  {k:"choix", lv:3, tag:"espérer ou souhaiter",
   stem:"J'espère qu'il ___ demain.",
   opts:["vienne", "viendra"], ok:1,
   why:"« Espérer » se construit avec l'indicatif, contre toute attente — « j'espère qu'il viendra ». "
     + "« Souhaiter que », lui, prend le subjonctif : « je souhaite qu'il vienne »."},

  {k:"choix", lv:3, tag:"ce qui ou ce que",
   stem:"Je ne sais pas ___ se passe.",
   opts:["ce qui", "ce que"], ok:0,
   why:"« Se passer » a besoin d'un sujet, et « ce qui » en est un. « Ce que » viendrait devant un verbe "
     + "qui a déjà son sujet : « ce que tu dis »."},

  {k:"choix", lv:2, tag:"bon ou bien",
   stem:"Elle chante ___ que moi.",
   opts:["meilleur", "mieux"], ok:1,
   why:"« Chanter » est un verbe : il prend un adverbe, donc « mieux ». « Meilleur » qualifie un nom — "
     + "« une meilleure chanteuse »."},

  {k:"choix", lv:1, tag:"en ou y",
   stem:"Des pommes ? J'___ ai trois.",
   opts:["en", "y"], ok:0,
   why:"« En » reprend une quantité ou un groupe introduit par de/des. « Y » remplace un lieu "
     + "ou un complément en à."},

  {k:"choix", lv:3, tag:"pour ou pendant",
   stem:"Je suis à Lyon ___ deux semaines — je rentre le 15.",
   opts:["pour", "pendant"], ok:0,
   why:"« Pour » annonce une durée prévue, vue depuis son début. « Pendant » raconte une durée "
     + "qu'on traverse ou qu'on a traversée."}
];

/* La règle en une ligne, en anglais : les explications ci-dessus sont en
   français, et ce n'est pas la peine de deviner deux fois. */
const DEC_EN = {
  "subjonctif ou indicatif":"A real, identified thing takes the indicative; something only wished for or "
    + "searched for takes the subjunctive.",
  "imparfait ou passé composé":"Imparfait = ongoing background, no end point. Passé composé = one finished, "
    + "bounded event.",
  "antériorité":"Plus-que-parfait steps one layer further back: it happened BEFORE the other past event.",
  "doute ou quasi-certitude":"After a negated opinion verb, the subjunctive is standard; the indicative leaks "
    + "that you actually believe it.",
  "réel ou irréel":"si + present → future (still possible). si + imparfait → conditional (ruled out). "
    + "Never « si j'aurais ».",
  "depuis · pendant · il y a":"depuis = started in the past, still true now (verb stays present). "
    + "pendant = a closed stretch. il y a = a finished point in time, \"ago\".",
  "qui · que · dont":"qui = subject. que = direct object. dont = replaces a « de » complement.",
  "c'est ou il est":"c'est + noun with an article. il/elle est + bare noun (a job) or an adjective.",
  "savoir ou connaître":"savoir carries information (that/if/where/how). connaître takes an object you are "
    + "familiar with — a place, a person.",
  "venir de ou aller":"venir de + infinitive = just happened. aller + infinitive = about to happen.",
  "pronom direct ou indirect":"The verb decides, not the meaning: téléphoner à → lui; appeler (direct) → le/l'.",
  "avant que ou après que":"avant que + subjunctive (not yet real). après que + indicative (already happened) "
    + "— the asymmetry almost everyone gets wrong.",
  "espérer ou souhaiter":"espérer que + indicative. souhaiter que + subjunctive. Yes, really.",
  "ce qui ou ce que":"ce qui is the subject of the following verb; ce que is its object.",
  "bon ou bien":"Verbs take adverbs (mieux); nouns take adjectives (meilleur).",
  "en ou y":"en replaces a de/des quantity or group; y replaces a place or an à complement.",
  "pour ou pendant":"pour = a planned duration seen from its start. pendant = a duration you live through."
};

let DEC = null;

function ydPool(){
  return DECIDE.map((d, i) => ({d, i}))
    .filter(x => x.d.lv <= S.P.level + 1);
}

function ydNext(){
  const pool = ydPool();
  if(!pool.length){ $("ydStem").textContent = "Rien à ce niveau."; return; }
  const t = typeof srsDay === "function" ? srsDay() : 0;
  const due = pool.filter(x => { const s = S.P.srs["y" + x.i]; return s && s[0] <= t; });
  const fresh = pool.filter(x => !S.P.srs["y" + x.i]);
  const from = due.length ? due : (fresh.length ? fresh : pool);
  const pick = from[(Math.random() * from.length) | 0];

  DEC = {d:pick.d, i:pick.i, srsId:"y" + pick.i, step:pick.d.k === "sens" ? 1 : 2,
    mean:-1, done:false, slip:false, t0:Date.now()};
  ydPaint();
}

function ydPaint(){
  const d = DEC.d;
  $("ydTag").textContent = d.tag;
  $("ydLv").textContent = LEVELS[Math.max(0, d.lv - 1)];
  $("ydStem").innerHTML = d.stem;
  $("ydNote").textContent = "";
  $("ydNote").className = "note";
  $("ydWhy").hidden = true;
  $("ydWhy").innerHTML = "";
  $("ydNext").hidden = true;

  const q = $("ydQ"), box = $("ydOpts");
  box.innerHTML = "";

  if(DEC.step === 1){
    q.textContent = "Qu'est-ce que tu veux dire ?";
    d.means.forEach((m, n) => box.appendChild(ydBtn(m, () => ydMean(n))));
  }else{
    const opts = d.k === "sens" ? d.forms : d.opts;
    q.innerHTML = d.k === "sens"
      ? "Tu veux dire : <i>" + d.means[DEC.mean] + "</i>. Quelle forme ?"
      : "Quelle forme passe ?";
    opts.forEach((o, n) => box.appendChild(ydBtn(o, () => ydPick(n), true)));
  }
}

function ydBtn(label, fn, code){
  const b = document.createElement("button");
  b.type = "button";
  b.className = "ydopt" + (code ? " code" : "");
  b.innerHTML = label;
  b.addEventListener("click", fn);
  return b;
}

function ydMean(n){
  if(DEC.done) return;
  DEC.mean = n;
  DEC.step = 2;
  ydPaint();
}

function ydPick(n){
  if(DEC.done) return;
  const d = DEC.d;
  const want = d.k === "sens" ? DEC.mean : d.ok;
  const ok = n === want;
  DEC.done = true;

  Array.from($("ydOpts").children).forEach((b, i) => {
    b.disabled = true;
    if(i === want) b.classList.add("ok");
    else if(i === n) b.classList.add("no");
  });

  $("ydNote").className = "note " + (ok ? "good" : "bad");
  $("ydNote").textContent = ok
    ? (d.k === "sens" ? "Juste — la forme suit bien ton intention." : "Juste.")
    : (d.k === "sens" ? "Cette forme est correcte, mais elle dit l'autre chose." : "Non.");
  const en = DEC_EN[d.tag];
  $("ydWhy").innerHTML = (d.k === "sens" ? d.why[want] : d.why)
    + (en ? '<span class="ydwhyen">' + en + "</span>" : "");
  $("ydWhy").hidden = false;
  $("ydNext").hidden = false;
  $("ydNext").focus();

  if(d.k === "sens" && typeof speakFr === "function" && /^[A-ZÀ-Ý]/.test(d.forms[want]))
    setTimeout(() => speakFr(d.forms[want], .95), 200);

  const ms = Date.now() - DEC.t0;
  const q = typeof srsGrade === "function" ? srsGrade(ok, ms, false) : (ok ? 4 : 1);
  if(typeof srsUpdate === "function") srsUpdate(DEC.srsId, q);
  if(typeof noteLevelRaw === "function" && d.lv === S.P.level) noteLevelRaw(ok);
  if(typeof scored === "function") scored(ok);
  if(typeof save === "function") save();
}

let YD_READY = false;

function deciderInit(){
  if(YD_READY) return (DEC ? ydPaint() : ydNext());
  YD_READY = true;
  $("ydNext").addEventListener("click", ydNext);
  ydNext();
}
