/* Le Cahier — données */

const TROU = [
  {id:"t1", s:"Dépêche-toi, le train ___ dans deux minutes.", a:"part", d:["dort","mange","ouvre"], g:"Hurry up, the train leaves in two minutes."},
  {id:"t2", s:"Je n'arrive pas à ___ cette bouteille.", a:"ouvrir", d:["boire","casser","choisir"], g:"I can't manage to open this bottle."},
  {id:"t3", s:"Il pleut depuis ce matin, n'oublie pas ton ___.", a:"parapluie", d:["portefeuille","tabouret","oreiller"], g:"It's been raining since this morning — don't forget your umbrella."},
  {id:"t4", s:"Elle travaille comme ___ à l'hôpital Saint-Louis.", a:"infirmière", d:["boulangère","serveuse","couturière"], g:"She works as a nurse at Saint-Louis hospital."},
  {id:"t5", s:"Ce quartier est très ___ la nuit : on entend les oiseaux.", a:"calme", d:["bruyant","cher","humide"], g:"This neighbourhood is very quiet at night — you can hear the birds."},
  {id:"t6", s:"Tu peux me ___ ton stylo une seconde ?", a:"prêter", d:["vendre","jeter","perdre"], g:"Can you lend me your pen for a second?"},
  {id:"t7", s:"Le boulanger sort les baguettes du ___.", a:"four", d:["frigo","tiroir","évier"], g:"The baker takes the baguettes out of the oven."},
  {id:"t8", s:"Je me suis ___ en cherchant la gare.", a:"perdu", d:["assis","levé","couché"], g:"I got lost looking for the station."},
  {id:"t9", s:"Elle a ___ son téléphone dans le taxi.", a:"oublié", d:["chanté","écrit","traduit"], g:"She left her phone in the taxi."},
  {id:"t10", s:"Il fait tellement ___ que la fontaine a gelé.", a:"froid", d:["chaud","lourd","sombre"], g:"It's so cold that the fountain froze."},
  {id:"t11", s:"Le médecin m'a conseillé de ___ une heure par jour.", a:"marcher", d:["fumer","conduire","crier"], g:"The doctor advised me to walk an hour a day."},
  {id:"t12", s:"Cette rue est interdite aux ___ depuis janvier.", a:"voitures", d:["oiseaux","nuages","chansons"], g:"This street has been closed to cars since January."},
  {id:"t13", s:"J'ai ___ rater mon avion ce matin.", a:"failli", d:["réussi","décidé","promis"], g:"I nearly missed my plane this morning. (faillir + infinitive = to nearly do)"},
  {id:"t14", s:"Ne t'inquiète pas, ce n'est pas ___.", a:"grave", d:["lourd","sale","tard"], g:"Don't worry, it's not serious."},
  {id:"t15", s:"Il a ___ insister, je ne changerai pas d'avis.", a:"beau", d:["bien","trop","très"], g:"However much he insists, I won't change my mind. (avoir beau + inf.)"},
  {id:"t16", s:"Tu as l'air ___, tu devrais te reposer.", a:"fatigué", d:["rapide","poli","gourmand"], g:"You look tired, you should rest."},
  {id:"t17", s:"Les charges sont ___ dans le loyer.", a:"comprises", d:["ouvertes","parties","assises"], g:"Utilities are included in the rent."},
  {id:"t18", s:"Je passe te ___ vers huit heures.", a:"chercher", d:["vendre","cuisiner","traduire"], g:"I'll come pick you up around eight."},
  {id:"t19", s:"N'hésite pas à me ___ si tu as besoin.", a:"rappeler", d:["raccrocher","refuser","ranger"], g:"Don't hesitate to call me back if you need anything."},
  {id:"t20", s:"Il a ___ son café sur le clavier.", a:"renversé", d:["rempli","rangé","réchauffé"], g:"He spilled his coffee on the keyboard."},
  {id:"t21", s:"On se retrouve ___ la mairie à midi.", a:"devant", d:["pendant","sans","malgré"], g:"Let's meet in front of the town hall at noon."},
  {id:"t22", s:"Cette recette demande trois ___ et du beurre.", a:"œufs", d:["clous","ciseaux","timbres"], g:"This recipe needs three eggs and butter."},
  {id:"t23", s:"Je ne supporte plus ce ___ : les voisins refont leur cuisine.", a:"bruit", d:["goût","parfum","silence"], g:"I can't stand this noise any more — the neighbours are redoing their kitchen."},
  {id:"t24", s:"Il est arrivé ___ parce que le métro était bloqué.", a:"en retard", d:["en avance","en maillot","en vacances"], g:"He arrived late because the métro was stuck."},
  {id:"t25", s:"Il faut que tu ___ à l'heure, c'est un entretien.", a:"sois", d:["es","seras","étais"], g:"You have to be on time — it's an interview. (subjunctive after il faut que)"},
  {id:"t26", s:"Si j'avais su, je ne ___ pas venu.", a:"serais", d:["serai","suis","étais"], g:"If I had known, I wouldn't have come. (third conditional)"},
  {id:"t27", s:"Le livre ___ je t'ai parlé vient de sortir.", a:"dont", d:["que","où","qui"], g:"The book I told you about has just come out. (parler DE → dont)"},
  {id:"t28", s:"C'est la ville ___ je suis né.", a:"où", d:["que","dont","qui"], g:"That's the town where I was born."},

  {id:"t29", s:"Il s'est fait ___ par la police à la sortie du métro.", a:"arrêter", d:["arrêté","arrêtant","arrête"], g:"He got stopped by the police coming out of the métro. (se faire + infinitive)"},
  {id:"t30", s:"Quoi qu'il ___, nous partirons à l'aube.", a:"arrive", d:["arrivera","arrivait","arriver"], g:"Whatever happens, we'll leave at dawn. (quoi que + subjunctive)"},
  {id:"t31", s:"Elle n'est pas venue, ___ m'a beaucoup surpris.", a:"ce qui", d:["qui","que","ce que"], g:"She didn't come, which surprised me a lot."},
  {id:"t32", s:"À peine ___-il entré que le téléphone a sonné.", a:"était", d:["avait","fut","est"], g:"He had barely come in when the phone rang. (inversion after à peine)"},
  {id:"t33", s:"Je m'attendais à ce qu'il ___ plus prudent.", a:"soit", d:["est","sera","était"], g:"I expected him to be more careful. (s'attendre à ce que + subjunctive)"},
  {id:"t34", s:"Il parle de ce poste comme s'il l'___ déjà obtenu.", a:"avait", d:["a","aurait","aura"], g:"He talks about that job as if he'd already got it. (comme si + pluperfect)"},
  {id:"t35", s:"Ce n'est pas tant le prix ___ le principe qui me gêne.", a:"que", d:["comme","mais","dont"], g:"It isn't so much the price as the principle that bothers me."},
  {id:"t36", s:"Pour peu qu'on ___ attention, la faute saute aux yeux.", a:"fasse", d:["fait","fera","faisait"], g:"If one pays even a little attention, the mistake is glaring. (pour peu que + subjunctive)"},
  {id:"t37", s:"Elle a eu beau insister, il n'en ___ pas démordu.", a:"a", d:["est","avait","aura"], g:"However much she insisted, he wouldn't budge. (ne pas démordre de)"},
  {id:"t38", s:"Le rapport, ___ les conclusions sont contestées, sort demain.", a:"dont", d:["que","où","duquel"], g:"The report, whose conclusions are disputed, comes out tomorrow."},
  {id:"t39", s:"Il fut décidé que l'affaire ___ classée sans suite.", a:"serait", d:["sera","soit","était"], g:"It was decided that the case would be dropped. (concordance des temps)"},
  {id:"t40", s:"Encore ___-il que tout le monde soit d'accord.", a:"faut", d:["faudrait","fallait","falloir"], g:"That still assumes everyone agrees. (encore faut-il que)"}
];

/* Une image dit le mot sans passer par l'anglais. Là où rien ne s'image,
   le mot anglais reste. */
const PIC = {
  "maison":"\u{1F3E0}", "jardin":"\u{1F333}", "parler":"\u{1F4AC}", "soleil":"\u2600\uFE0F",
  "marche":"\u{1F6B6}", "bouche":"\u{1F444}", "voisin":"\u{1F3D8}\uFE0F", "cheval":"\u{1F40E}",
  "orange":"\u{1F34A}", "dormir":"\u{1F634}", "sortir":"\u{1F6AA}", "fermer":"\u{1F512}",
  "miroir":"\u{1FA9E}", "balcon":"\u{1FA9F}", "citron":"\u{1F34B}", "cerise":"\u{1F352}",
  "renard":"\u{1F98A}", "souris":"\u{1F42D}",
  "mus\u00e9e":"\u{1F3DB}\uFE0F", "dent":"\u{1F9B7}", "for\u00eat":"\u{1F332}", "voyage":"\u{1F9F3}",
  "plage":"\u{1F3D6}\uFE0F", "chaleur":"\u{1F525}", "main":"\u270B", "beurre":"\u{1F9C8}",
  "cuill\u00e8re":"\u{1F944}", "eau":"\u{1F4A7}", "nuit":"\u{1F319}", "page":"\u{1F4C4}",
  "fromage":"\u{1F9C0}", "\u00e9toile":"\u2B50", "travail":"\u{1F4BC}", "groupe":"\u{1F465}",
  "pays":"\u{1F5FA}\uFE0F", "vitesse":"\u{1F3CE}\uFE0F", "bruit":"\u{1F50A}", "silence":"\u{1F92B}",
  "sant\u00e9":"\u{1FA7A}", "bonheur":"\u{1F60A}", "peau":"\u{1F91A}", "fin":"\u{1F3C1}",
  "manger":"\u{1F37D}\uFE0F", "boire":"\u{1F964}", "lire":"\u{1F4D6}", "\u00e9crire":"\u270D\uFE0F",
  "voir":"\u{1F441}\uFE0F", "acheter":"\u{1F6D2}", "appeler":"\u{1F4DE}", "ouvrir":"\u{1F513}",
  "finir":"\u{1F3C1}", "aller":"\u27A1\uFE0F", "venir":"\u2B05\uFE0F", "dire":"\u{1F4AC}",
  "recevoir":"\u{1F4E9}", "partir":"\u{1F6EB}", "prendre":"\u{1F91D}", "vivre":"\u{1F331}"
};
const picOf = (w) => PIC[String(w || "").toLowerCase()] || "";

/* Place l'indice : l'image d'abord, le mot anglais seulement s'il n'y a pas d'image */
function cueInto(el, word, english){
  el.innerHTML = "";
  const p = picOf(word);
  if(p){
    const s = document.createElement("span");
    s.className = "pic"; s.textContent = p;
    s.title = english || "";
    el.appendChild(s);
  }
  if(english) el.appendChild(Object.assign(document.createElement("span"),
    {className:p ? "cueword dim" : "cueword", textContent:english}));
}

const MOTUS = [
  {w:"MAISON", c:"a house"}, {w:"JARDIN", c:"a garden"}, {w:"PARLER", c:"to speak"},
  {w:"SOLEIL", c:"the sun"}, {w:"MARCHE", c:"a step — or walking"}, {w:"BOUCHE", c:"a mouth"},
  {w:"VOISIN", c:"a neighbour"}, {w:"CHEVAL", c:"a horse"}, {w:"ORANGE", c:"an orange"},
  {w:"DORMIR", c:"to sleep"}, {w:"SORTIR", c:"to go out"}, {w:"FERMER", c:"to close"},
  {w:"MIROIR", c:"a mirror"}, {w:"BALCON", c:"a balcony"}, {w:"CITRON", c:"a lemon"},
  {w:"CERISE", c:"a cherry"}, {w:"RENARD", c:"a fox"}, {w:"SOURIS", c:"a mouse"}];

const GENRE = [
  {n:"problème", g:"m", t:"problem", r:"Presque tous les noms en <b>-ème</b> sont masculins : le problème, le système, le thème."},
  {n:"musée", g:"m", t:"museum", r:"Les noms en <b>-ée</b> sont féminins, sauf le musée, le lycée et le trophée."},
  {n:"peau", g:"f", t:"skin", r:"La peau, l'eau — les noms en <b>-eau</b> sont masculins sauf ces deux-là."},
  {n:"silence", g:"m", t:"silence", r:"Les noms en <b>-ence</b> sont féminins (la patience), mais le silence est masculin."},
  {n:"dent", g:"f", t:"tooth", r:"La dent, la jument — mais le vent, le client."},
  {n:"fin", g:"f", t:"end", r:"La fin, la main — beaucoup de noms courts en <b>-in</b> restent féminins."},
  {n:"moitié", g:"f", t:"half", r:"Les noms en <b>-té</b> sont féminins : la moitié, la liberté, la santé."},
  {n:"chaleur", g:"f", t:"heat", r:"Les noms en <b>-eur</b> abstraits sont féminins : la chaleur, la peur, la douleur."},
  {n:"bonheur", g:"m", t:"happiness", r:"Exception : le bonheur, le malheur et l'honneur sont masculins."},
  {n:"forêt", g:"f", t:"forest", r:"La forêt, la fôret… l'accent circonflexe marque un <b>s</b> disparu : forest."},
  {n:"voyage", g:"m", t:"journey", r:"Les noms en <b>-age</b> sont masculins : le voyage, le fromage, le garage."},
  {n:"plage", g:"f", t:"beach", r:"Exception au <b>-age</b> : la plage, la page, la cage, l'image, la nage."},
  {n:"groupe", g:"m", t:"group", r:"Le groupe, le doute, le monde — masculins malgré le <b>-e</b> final."},
  {n:"façon", g:"f", t:"way, manner", r:"Les noms en <b>-on</b> sont masculins, sauf la façon, la leçon, la maison, la raison."},
  {n:"vitesse", g:"f", t:"speed", r:"Les noms en <b>-esse</b> sont féminins : la vitesse, la jeunesse, la richesse."},
  {n:"rôle", g:"m", t:"role", r:"Le rôle, le pôle, le contrôle."},
  {n:"vérité", g:"f", t:"truth", r:"Encore un <b>-té</b> : la vérité, la beauté, la société."},
  {n:"système", g:"m", t:"system", r:"En <b>-ème</b>, donc masculin : le système, le poème, le thème."},
  {n:"pays", g:"m", t:"country", r:"Le pays, le corps, le bras — le <b>-s</b> final ne change rien."},
  {n:"main", g:"f", t:"hand", r:"La main, la fin — deux féminins en <b>-in</b> à retenir ensemble."},
  {n:"beurre", g:"m", t:"butter", r:"Le beurre, le sucre, le sel — mais la farine, la crème."},
  {n:"cuillère", g:"f", t:"spoon", r:"La cuillère, la fourchette, l'assiette — mais le couteau, le verre."},
  {n:"eau", g:"f", t:"water", r:"L'eau est féminine : <i>de l'eau fraîche</i>. L'article élidé cache le genre."},
  {n:"choix", g:"m", t:"choice", r:"Le choix, le prix, le poids — les noms en <b>-x</b> sont presque tous masculins."},
  {n:"nuit", g:"f", t:"night", r:"La nuit, la pluie, la vie — mais le bruit, le fruit."},
  {n:"bruit", g:"m", t:"noise", r:"Le bruit et le fruit sont masculins ; la nuit est féminine. Une rime, trois genres."},
  {n:"santé", g:"f", t:"health", r:"En <b>-té</b> : la santé, la qualité, la difficulté."},
  {n:"doute", g:"m", t:"doubt", r:"Le doute, le groupe, le monde, le silence."},
  {n:"page", g:"f", t:"page", r:"La page comme la plage : exception au <b>-age</b> masculin."},
  {n:"fromage", g:"m", t:"cheese", r:"Le fromage suit la règle du <b>-age</b> : masculin."},
  {n:"étoile", g:"f", t:"star", r:"L'étoile, l'école, l'idée — féminins cachés par l'élision."},
  {n:"travail", g:"m", t:"work", r:"Les noms en <b>-ail</b> sont masculins : le travail, le détail, le portail."}
];

/* ---------- état ---------- */
const $ = (id) => document.getElementById(id);
const today = () => new Date().toLocaleDateString("sv");
const blank = () => ({streak:0, last:"", days:0, trou:{seen:0, right:0}, genre:{seen:0, right:0},
  motus:{played:0, won:0, idx:0}, croise:{done:0}, dictee:{done:0, words:0, right:0},
  lex:{}, srs:{}, recall:{rev:0, ok:0}, day:{n:0, fresh:0},
  level:2, tested:false, lvHist:[], promoted:null, phrase:{n:0, ok:0},
  profil:{why:"", l1:"", minutes:10, domains:[]}, parle:{n:0, points:0}, convos:[],
  exam:{lv:0, parts:{}},
  story:{chapters:[], read:0, at:0},
  recit:{read:{}, acc:{}, tr:true},
  imiter:{n:0, takes:0, mode:"apres", rate:1, hide:false}, backupAt:0, backupBytes:0,
  hist:{}, ring:{day:0, target:0, closed:false}, joker:"", comebackDay:0, comebackAway:0,
  hero:{xp:0, name:"", avatar:"\u{1F98A}", cls:"", created:0, ach:{}, day:{n:0, xp:0, recalls:0, clean:0, convo:0, phrase:0, grid:0, exam:0},
    quests:[], claimed:[], questDay:0, justLevelled:null},
  missed:[], mastered:{}});

const S = {mode:"trou", P:blank(), db:null, uid:null, sample:null, queue:[], cards:[], mots:[],
  gIdx:-1, timer:null, cTimer:null, ctl:null, busy:false};
let T = null, M = null, G = null;

function hydrate(raw){
  const p = blank();
  if(!raw || typeof raw !== "object") return p;
  return {...p, ...raw,
    trou:{...p.trou, ...(raw.trou||{})},
    genre:{...p.genre, ...(raw.genre||{})},
    motus:{...p.motus, ...(raw.motus||{})},
    croise:{...p.croise, ...(raw.croise||{})},
    dictee:{...p.dictee, ...(raw.dictee||{})},
    lex:(raw.lex && typeof raw.lex === "object" && !Array.isArray(raw.lex)) ? raw.lex : {},
    recall:{...p.recall, ...(raw.recall||{})},
    phrase:{...p.phrase, ...(raw.phrase||{})},
    parle:{...p.parle, ...(raw.parle||{})},
    convos:Array.isArray(raw.convos) ? raw.convos.slice(-8) : [],
    hero:{...p.hero, ...(raw.hero||{}),
      day:{...p.hero.day, ...((raw.hero && raw.hero.day) || {})},
      quests:Array.isArray(raw.hero && raw.hero.quests) ? raw.hero.quests : [],
      claimed:Array.isArray(raw.hero && raw.hero.claimed) ? raw.hero.claimed : []},
    story:{...p.story, ...(raw.story||{}),
      chapters:Array.isArray(raw.story && raw.story.chapters) ? raw.story.chapters.slice(-12) : []},
    imiter:{...p.imiter, ...((raw.imiter && typeof raw.imiter === "object") ? raw.imiter : {})},
    recit:{...p.recit, ...((raw.recit && typeof raw.recit === "object") ? raw.recit : {}),
      read:(raw.recit && raw.recit.read && typeof raw.recit.read === "object" && !Array.isArray(raw.recit.read)) ? raw.recit.read : {},
      acc:(raw.recit && raw.recit.acc && typeof raw.recit.acc === "object" && !Array.isArray(raw.recit.acc)) ? raw.recit.acc : {}},
    hist:(raw.hist && typeof raw.hist === "object" && !Array.isArray(raw.hist)) ? raw.hist : {},
    ring:{...p.ring, ...((raw.ring && typeof raw.ring === "object") ? raw.ring : {})},
    joker:typeof raw.joker === "string" ? raw.joker : "",
    exam:{lv:+((raw.exam && raw.exam.lv) || 0),
      parts:(raw.exam && raw.exam.parts && typeof raw.exam.parts === "object") ? raw.exam.parts : {}},
    profil:{...p.profil, ...(raw.profil||{}),
      domains:Array.isArray(raw.profil && raw.profil.domains) ? raw.profil.domains : []},
    level:Math.min(6, Math.max(1, +raw.level || 2)),
    lvHist:Array.isArray(raw.lvHist) ? raw.lvHist.slice(-25) : [],
    day:{...p.day, ...(raw.day||{})},
    srs:(raw.srs && typeof raw.srs === "object" && !Array.isArray(raw.srs)) ? raw.srs : {},
    missed:Array.isArray(raw.missed) ? raw.missed.slice(0,60) : [],
    mastered:(raw.mastered && typeof raw.mastered === "object") ? raw.mastered : {}};
}

function readLocal(){
  try{
    const p = hydrate(JSON.parse(localStorage.getItem("le-cahier-v1")));
    const s = JSON.parse(localStorage.getItem("le-cahier-srs-v1"));
    if(s && typeof s === "object" && !Array.isArray(s)) p.srs = s;
    return p;
  }catch(e){ return blank(); }
}
/* Un document a droit à 256 Kio. Le planning est la seule chose irremplaçable :
   il vit à part, et le reste est élagué avant d'approcher la limite. */
const DOC_MAX = 240000;

/* Une sauvegarde qui échoue ne doit jamais passer inaperçue. */
function docTrouble(which){
  S.warnDoc = which;
  const en = typeof LANG !== "undefined" && LANG === "en";
  const el = document.getElementById("syncNote");
  if(el) el.textContent = en
    ? "Saving failed (" + which + "). Your work is still on this device — tell Claude."
    : "La sauvegarde a échoué (" + which + "). Tout reste sur cet appareil — préviens Claude.";
}
const bytes = (o) => { try{ return new Blob([JSON.stringify(o)]).size; }catch(e){ return 0; } };

function trimProfile(){
  const p = S.P;
  let cut = [];
  const over = () => bytes(rest()) > DOC_MAX;
  if(!over()) return cut;
  const histKeys = Object.keys(p.hist || {}).map(Number).sort((a, b) => a - b);
  while(histKeys.length > 400){ delete p.hist[histKeys.shift()]; }
  while(over() && histKeys.length > 60){ delete p.hist[histKeys.shift()]; cut.push("hist"); }
  const lexKeys = Object.keys(p.lex || {});
  while(over() && lexKeys.length){ delete p.lex[lexKeys.shift()]; cut.push("lex"); }
  while(over() && (p.story.chapters || []).length > 2){ p.story.chapters.shift(); cut.push("story"); }
  while(over() && (p.convos || []).length > 2){ p.convos.shift(); cut.push("convos"); }
  while(over() && (p.lvHist || []).length > 5){ p.lvHist.shift(); }
  return cut;
}

/* Le profil sans le planning : c'est ce qui part dans le document « progress ». */
function rest(){
  const o = {};
  Object.keys(S.P).forEach(k => { if(k !== "srs") o[k] = S.P[k]; });
  return o;
}

function writeLocal(){
  try{
    localStorage.setItem("le-cahier-v1", JSON.stringify(rest()));
    localStorage.setItem("le-cahier-srs-v1", JSON.stringify(S.P.srs || {}));
  }catch(e){}
}

function saveSrs(){
  if(!S.db || !S.uid) return;
  clearTimeout(S.sTimer);
  S.sTimer = setTimeout(async () => {
    try{ await S.db.doc("data/users/" + S.uid + "/srs").set({srs:S.P.srs, at:Date.now()}); }
    catch(e){
      if(e && e.code === "revoked") S.db = null;
      else if(e && e.code === "invalid_argument") docTrouble("srs");
    }
  }, 1400);
}

function save(){
  const cut = trimProfile();
  if(cut.length) S.trimmed = cut.length;
  writeLocal();
  saveSrs();
  if(!S.db || !S.uid) return;
  clearTimeout(S.timer);
  S.timer = setTimeout(async () => {
    if(S.busy){ S.timer = setTimeout(save, 600); return; }
    S.busy = true;
    try{ await S.db.doc("data/users/" + S.uid + "/progress").set(rest()); }
    catch(e){
      if(e && e.code === "revoked") S.db = null;
      else if(e && e.code === "invalid_argument") docTrouble("progress");
    }
    S.busy = false;
  }, 1200);
}

/* Semaine ISO, « 2026-W46 » : un joker par semaine, pas un par sept jours glissants. */
function isoWeek(d){
  d = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
  const day = d.getUTCDay() || 7;
  d.setUTCDate(d.getUTCDate() + 4 - day);
  const y0 = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
  return d.getUTCFullYear() + "-W" + String(Math.ceil(((d - y0) / 864e5 + 1) / 7)).padStart(2, "0");
}

/* La série : un jour où l'on a répondu à une seule carte compte. Un jour
   sauté par semaine est pardonné — le joker se pose tout seul, une fois. */
function scored(correct){
  const d = today();
  if(S.P.last !== d){
    const y = new Date(Date.now() - 864e5).toLocaleDateString("sv");
    const y2 = new Date(Date.now() - 2 * 864e5).toLocaleDateString("sv");
    const wk = isoWeek(new Date());
    if(S.P.last === y) S.P.streak++;
    else if(S.P.last === y2 && S.P.streak > 0 && S.P.joker !== wk){
      S.P.streak++;
      S.P.joker = wk;
      S.jokerUsed = true;
    }else S.P.streak = 1;
    S.P.last = d; S.P.days++;
  }
  paintMargin(); save();
  return correct;
}

/* L'anneau du jour : des rappels, pas des minutes. La cible se fixe au premier
   regard de la journée — ce qui est dû, borné par le temps choisi — et ne bouge plus. */
function ringState(){
  const t = dayNum();
  const r = S.P.ring;
  if(r.day !== t){
    const st = srsStats();
    const perMin = typeof JOUR_PER_MIN === "number" ? JOUR_PER_MIN : 6;
    const mins = typeof jourBudget === "function" ? jourBudget() : 15;
    r.day = t; r.closed = false;
    r.target = Math.max(5, Math.min(mins * perMin, st.due + st.fresh || 5));
  }
  const done = (typeof heroDay === "function") ? (heroDay().recalls || 0) : 0;
  if(!r.closed && done >= r.target){
    r.closed = true;
    S.P.rings = (S.P.rings || 0) + 1;
    S.ringJustClosed = true;
    if(typeof xpGain === "function") xpGain(30, null);
  }
  return {done, target:r.target, closed:r.closed, pct:Math.min(1, done / r.target)};
}

/* ---------- marge ---------- */
function paintMargin(){
  const p = S.P, tot = p.trou.seen + p.genre.seen, right = p.trou.right + p.genre.right;
  $("mStreak").textContent = p.streak;
  const en = typeof LANG !== "undefined" && LANG === "en";
  $("mStreakN").textContent = p.streak === 1 ? (en ? "day" : "jour")
    : (en ? "days running" : "jours de suite");
  $("streakPill").innerHTML = '<svg class="fl" viewBox="0 0 24 24" aria-hidden="true"><use href="#i-flamme"/></svg><b>'
    + p.streak + "</b><span>" + (p.streak === 1 ? (en ? "day" : "jour") : (en ? "days" : "jours")) + "</span>";
  $("streakPill").title = en ? "Day streak" : "Série de jours";

  const st = srsStats();
  $("mDue").textContent = st.due + st.fresh;
  $("mDueN").textContent = en ? st.due + " due, " + st.fresh + " new"
    : st.due + " \u00e0 revoir, " + st.fresh + " neuve" + (st.fresh > 1 ? "s" : "");
  document.title = "Le Cahier" + (st.due + st.fresh ? " \u00b7 " + (st.due + st.fresh) : "");

  const ring = ringState();
  const arc = $("ringArc");
  if(arc){
    const C = 2 * Math.PI * 17;
    arc.style.strokeDasharray = C.toFixed(1);
    arc.style.strokeDashoffset = (C * (1 - ring.pct)).toFixed(1);
    arc.classList.toggle("closed", ring.closed);
    $("ringN").textContent = ring.done + "/" + ring.target;
    $("mRingN").textContent = ring.closed ? (en ? "ring closed" : "anneau ferm\u00e9")
      : (en ? "recalls today" : "rappels aujourd'hui");
  }
  $("mRecall").textContent = st.retention == null ? "\u2014" : st.retention + "%";
  $("mRecallN").textContent = p.recall.rev
    ? (en ? "over " + p.recall.rev + " recalls" : "sur " + p.recall.rev + " rappels")
    : (en ? "from memory" : "de m\u00e9moire");
  $("mLevel").textContent = LEVELS[p.level - 1];
  $("mLevelN").textContent = p.tested ? (en ? "level tested" : "niveau test\u00e9")
    : (en ? "not tested \u2014 take the test" : "non test\u00e9 \u2014 fais le test");
  $("mScore").textContent = right;
  $("mScoreN").textContent = (en ? "of " : "sur ") + tot
    + (tot ? " \u00b7 " + Math.round(right / tot * 100) + "%" : "");

  const bits = [st.learned + "/" + st.total + (en ? " cards started" : " cartes lanc\u00e9es")];
  if(p.motus.won) bits.push("Motus " + p.motus.won);
  if(p.croise.done) bits.push("Crois\u00e9s " + p.croise.done);
  if(p.dictee.done) bits.push("Dict\u00e9es " + p.dictee.done);
  if(p.missed.length) bits.push((en ? "Error book " : "Carnet ") + p.missed.length);
  $("carnet").textContent = bits.join(" \u00b7 ");

  const notes = ["Commence par une s\u00e9ance.", "Bien. Continue.",
    "Le genre s'apprend avec le mot, jamais apr\u00e8s.", "Relis \u00e0 voix haute.",
    "Une carte rat\u00e9e revient plus vite : c'est voulu.", "Encore dix minutes."];
  $("annot").textContent = S.jokerUsed ? (en ? "Joker used \u2014 the streak holds." : "Joker utilis\u00e9 \u2014 la s\u00e9rie tient.")
    : ring.closed ? (en ? "Ring closed. Anything more is a gift." : "Anneau ferm\u00e9. Le reste est cadeau.")
    : st.comeback ? (en ? "Gentle return: twenty today, the rest follows." : "Reprise douce : vingt aujourd'hui, le reste suit.")
    : notes[Math.min(p.days, notes.length - 1)];
  paintHud();
  if(typeof recitRefresh === "function") recitRefresh();
  heroCelebrate();
}

/* ---------- Le Trou ---------- */
/* TROU_PLUS (phrases.js) : les phrases de la semaine, voix enregistrée. */
/* Les phrases du récit n'entrent qu'une fois la page lue (recit.js). */
const ALL = () => TROU.concat(typeof TROU_PLUS !== "undefined" ? TROU_PLUS : [],
  typeof recitCards === "function" ? recitCards() : [], S.cards);

function refillQueue(){
  const all = ALL();
  const pool = all.filter(i => (S.P.mastered[i.id] || 0) < 2);
  const deck = (pool.length ? pool : all).map(i => i.id);
  for(let i = deck.length - 1; i > 0; i--){ const j = (Math.random() * (i + 1)) | 0; [deck[i], deck[j]] = [deck[j], deck[i]]; }
  const first = S.P.missed.filter(id => all.some(i => i.id === id)).slice(0, 3);
  S.queue = [...first, ...deck.filter(id => !first.includes(id))];
}

function nextTrou(){
  if(typeof vrHalt === "function") vrHalt();
  if("speechSynthesis" in window) speechSynthesis.cancel();
  if(!S.queue.length) refillQueue();
  const id = S.queue.shift();
  const item = ALL().find(i => i.id === id) || TROU[0];
  T = {item, answered:false};
  const opts = [item.a, ...item.d];
  for(let i = opts.length - 1; i > 0; i--){ const j = (Math.random() * (i + 1)) | 0; [opts[i], opts[j]] = [opts[j], opts[i]]; }

  const [before, after] = item.s.split("___");
  $("sentence").innerHTML = "";
  const tb = document.createElement("span");
  tb.className = "blank"; tb.id = "theBlank";
  tb.textContent = (typeof wordShape === "function") ? wordShape(item.a, 0) : "?";
  tb.style.letterSpacing = ".2em";
  tb.style.fontFamily = '"IBM Plex Mono", monospace';
  tb.style.fontSize = ".88em";
  $("sentence").append(before, tb, after);
  /* Le sens d'abord : retrouver le mot qu'on veut dire, ce n'est pas deviner. */
  $("gloss").textContent = item.g || "";
  T.hint = 0;
  $("trouAfter").innerHTML = "";
  const tag = item.id[0] === "p" ? "sur mesure" : item.id[0] === "v" ? "d'après ta vidéo"
    : item.id[0] === "c" ? "d'après ta conversation" : item.id[0] === "n" ? "phrase de la semaine" : "";
  const link = /^https?:\/\//i.test(item.src || "");
  $("trouEyebrow").innerHTML = "Exercice I · Complétez la phrase — " + S.P.trou.right + " justes"
    + (tag ? " · " + (link ? "<a href=\"" + encodeURI(item.src) + "\" target=\"_blank\" rel=\"noopener\">"
      + tag + " ↗</a>" : tag) : "");

  const box = $("options"); box.innerHTML = ""; box.hidden = true;
  opts.forEach(w => {
    const b = document.createElement("button");
    b.className = "opt"; b.textContent = w;
    b.addEventListener("click", () => answerTrou(w, b));
    box.appendChild(b);
  });

  const inp = $("trouIn");
  inp.value = ""; inp.readOnly = false; inp.className = "seinput";
  inp.onkeydown = (e) => { if(e.key === "Enter"){ e.preventDefault(); checkTyped(); } };
  const verify = document.createElement("button");
  verify.className = "go"; verify.textContent = "V\u00e9rifier";
  verify.addEventListener("click", checkTyped);
  const hintNote = document.createElement("span");
  hintNote.className = "exdur";
  const help = document.createElement("button");
  help.className = "ghost"; help.textContent = "Un indice";
  help.addEventListener("click", () => {
    if(T.answered) return;
    T.hint = (T.hint || 0) + 1;
    T.helped = true;
    const en = typeof LANG !== "undefined" && LANG === "en";
    if(T.hint >= 3){
      box.hidden = false;
      help.disabled = true;
      hintNote.textContent = en ? "Options shown \u2014 this card comes back sooner."
        : "Propositions affich\u00e9es \u2014 cette carte reviendra plus t\u00f4t.";
      return;
    }
    if(typeof wordShape === "function") $("theBlank").textContent = wordShape(item.a, T.hint);
    hintNote.textContent = en ? "A hint costs you: this card comes back sooner."
      : "Un indice se paie : cette carte reviendra plus t\u00f4t.";
  });
  $("trouAfter").append(verify, help, hintNote);
  setTimeout(() => inp.focus(), 20);
}

function checkTyped(){
  if(!T || T.answered) return;
  const v = $("trouIn").value.trim();
  if(!v){ $("gloss").textContent = "\u00c9cris le mot \u2014 m\u00eame une tentative compte."; return; }
  answerTrou(same(v, T.item.a) ? T.item.a : v, null);
}

function answerTrou(word, btn){
  if(T.answered) return;
  T.answered = true;
  const item = T.item, ok = word === item.a;
  S.P.trou.seen++;
  const bl = $("theBlank");
  bl.textContent = item.a;
  bl.classList.add("done", ok ? "ok" : "no");

  $("options").hidden = false;
  [...$("options").children].forEach(b => {
    b.disabled = true;
    if(b.textContent === item.a) b.classList.add("right");
    else if(b === btn) b.classList.add("wrong");
  });
  const inp = $("trouIn");
  inp.readOnly = true;
  inp.classList.add(ok ? "ok" : "no");
  srsUpdate(item.id, srsGrade(ok, 0, T.helped));
  noteLevel(item.id, ok);

  if(ok){
    S.P.trou.right++;
    S.P.mastered[item.id] = (S.P.mastered[item.id] || 0) + 1;
    S.P.missed = S.P.missed.filter(id => id !== item.id);
  }else{
    S.P.mastered[item.id] = 0;
    if(!S.P.missed.includes(item.id)) S.P.missed.unshift(item.id);
    S.P.missed = S.P.missed.slice(0, 40);
    S.queue.splice(3, 0, item.id);
  }
  $("gloss").textContent = item.g;

  const after = $("trouAfter");
  if(!ok && typeof missButton === "function") missButton(after, item.a);
  const go = document.createElement("button");
  go.className = "go"; go.textContent = "Phrase suivante";
  go.addEventListener("click", nextTrou);
  after.appendChild(go);

  /* La phrase entière, dite par la vraie voix française (la même qu'en Séance et en
     Dictée) dès la réponse, et à redemander. Avant, ce bouton appelait la synthèse
     du navigateur sans choisir de voix : une voix anglaise lisait parfois le français. */
  const full = item.s.replace("___", item.a);
  const sp = document.createElement("button");
  sp.className = "ghost"; sp.textContent = "▶ Écouter";
  sp.addEventListener("click", () => speakFr(full, .95));
  after.appendChild(sp);
  speakFr(full, .95);
  go.focus();
  scored(ok);
}

/* ---------- Motus ---------- */
const KEYS = [["A","Z","E","R","T","Y","U","I","O","P"], ["Q","S","D","F","G","H","J","K","L","M"],
  ["ENTRÉE","W","X","C","V","B","N","EFF"]];

function newMotus(){
  const entry = MOTUS[S.P.motus.idx % MOTUS.length], w = entry.w;
  M = {word:w, clue:entry.c, rows:[], cur:w[0], done:false, states:{}};
  cueInto($("motusClue"), entry.w, entry.c);
  $("motusNote").textContent = "Tapez un mot de six lettres, puis Entrée. La première lettre est donnée.";
  drawMotus(); drawKeys();
}

function judge(guess, word){
  const marks = Array(6).fill("no"), left = {};
  for(let i = 0; i < 6; i++){ if(guess[i] === word[i]) marks[i] = "ok"; else left[word[i]] = (left[word[i]] || 0) + 1; }
  for(let i = 0; i < 6; i++){ if(marks[i] === "no" && left[guess[i]] > 0){ marks[i] = "mis"; left[guess[i]]--; } }
  return marks;
}

function drawMotus(){
  const g = $("motusGrid"); g.innerHTML = "";
  for(let r = 0; r < 6; r++){
    const row = document.createElement("div"); row.className = "row";
    for(let c = 0; c < 6; c++){
      const cell = document.createElement("div"); cell.className = "cell";
      if(r < M.rows.length){
        cell.textContent = M.rows[r].guess[c];
        cell.classList.add("c-" + M.rows[r].marks[c]);
      }else if(r === M.rows.length && !M.done){
        if(c < M.cur.length) cell.textContent = M.cur[c];
        else { cell.textContent = "·"; cell.classList.add("dot"); }
      }
      row.appendChild(cell);
    }
    g.appendChild(row);
  }
}

function drawKeys(){
  const kb = $("kb"); kb.innerHTML = "";
  KEYS.forEach(row => {
    const r = document.createElement("div"); r.className = "kb-row";
    row.forEach(k => {
      const b = document.createElement("button");
      b.className = "key" + (k.length > 1 ? " wide" : "");
      b.textContent = k;
      if(M.states[k]) b.classList.add("c-" + M.states[k]);
      b.addEventListener("click", () => press(k === "ENTRÉE" ? "ENTER" : k === "EFF" ? "BACK" : k));
      r.appendChild(b);
    });
    kb.appendChild(r);
  });
}

function press(k){
  if(!M || M.done) return;
  if(k === "BACK"){ if(M.cur.length > 1) M.cur = M.cur.slice(0, -1); }
  else if(k === "ENTER"){ if(M.cur.length === 6) return submitMotus(); }
  else if(/^[A-Z]$/.test(k) && M.cur.length < 6){ M.cur += k; }
  drawMotus();
}

function submitMotus(){
  const guess = M.cur, marks = judge(guess, M.word);
  M.rows.push({guess, marks});
  const rank = {no:0, mis:1, ok:2};
  guess.split("").forEach((ch, i) => {
    if(!M.states[ch] || rank[marks[i]] > rank[M.states[ch]]) M.states[ch] = marks[i];
  });

  if(guess === M.word){
    M.done = true; S.P.motus.played++; S.P.motus.won++; S.P.motus.idx++;
    $("motusNote").textContent = "Trouvé en " + M.rows.length + " essai" + (M.rows.length > 1 ? "s" : "") + ". " + M.word + ".";
    endMotus(); scored(true);
  }else if(M.rows.length >= 6){
    M.done = true; S.P.motus.played++; S.P.motus.idx++;
    $("motusNote").textContent = "Le mot était « " + M.word + " ».";
    endMotus(); scored(false);
  }else{
    M.cur = M.word[0];
  }
  drawMotus(); drawKeys();
}

function endMotus(){
  const b = document.createElement("button");
  b.className = "go"; b.textContent = "Nouvelle grille";
  b.style.marginTop = "12px";
  b.addEventListener("click", newMotus);
  $("motusNote").appendChild(document.createElement("br"));
  $("motusNote").appendChild(b);
}

document.addEventListener("keydown", (e) => {
  if(S.mode !== "motus" || !M || M.done) return;
  if(e.metaKey || e.ctrlKey || e.altKey) return;
  const k = e.key.toUpperCase();
  if(k === "ENTER" || k === "BACKSPACE"){ e.preventDefault(); press(k === "ENTER" ? "ENTER" : "BACK"); }
  else if(/^[A-Z]$/.test(k)) press(k);
});

/* ---------- Le ou La ---------- */
function nextGenre(){
  let i = (Math.random() * GENRE.length) | 0;
  if(i === S.gIdx) i = (i + 1) % GENRE.length;
  S.gIdx = i;
  G = {item:GENRE[i], answered:false};
  $("noun").textContent = GENRE[i].n;
  cueInto($("nounGloss"), GENRE[i].n, GENRE[i].t);
  $("genreRule").innerHTML = "";
  ["artLe", "artLa"].forEach(id => { const b = $(id); b.disabled = false; b.className = "art"; });
}

function answerGenre(choice){
  if(!G || G.answered) return;
  G.answered = true;
  const ok = choice === G.item.g;
  S.P.genre.seen++; if(ok) S.P.genre.right++;
  srsUpdate("g" + S.gIdx, srsGrade(ok, 0, false));
  noteLevel("g" + S.gIdx, ok);
  const right = G.item.g === "m" ? "artLe" : "artLa";
  const picked = choice === "m" ? "artLe" : "artLa";
  $(right).classList.add("right");
  if(!ok) $(picked).classList.add("wrong");
  ["artLe", "artLa"].forEach(id => $(id).disabled = true);
  $("genreRule").innerHTML = "<b>" + (G.item.g === "m" ? "le " : "la ") + G.item.n + "</b> — " + G.item.r;
  scored(ok);
  setTimeout(() => { if(S.mode === "genre") nextGenre(); }, ok ? 1100 : 2600);
}
$("artLe").addEventListener("click", () => answerGenre("m"));
$("artLa").addEventListener("click", () => answerGenre("f"));

/* ---------- La Vidéo ---------- */
const STOP_FR = new Set(["alors","aussi","avec","avoir","beaucoup","c'est","cette","comme","comment",
  "dans","déjà","donc","elle","elles","encore","est-ce","être","faire","faut","ici","juste","leur",
  "mais","même","moins","nous","parce","plus","pour","quand","que","quel","quelque","sans","sont",
  "surtout","toujours","tous","tout","toute","très","vais","vous","voilà","vraiment","était","étais"]);

function localCards(txt, src){
  const words = [...new Set((txt.toLowerCase().match(/[a-zà-ÿœ']{5,}/g) || []).filter(w => !STOP_FR.has(w)))];
  const out = [];
  const sentences = txt.replace(/\s+/g, " ").split(/(?<=[.!?…])\s+/)
    .map(s => s.trim()).filter(s => { const n = s.split(" ").length; return n >= 6 && n <= 18; });
  for(const s of sentences){
    if(out.length >= 10) break;
    const cands = s.split(" ").filter(w => /^[a-zA-ZÀ-ÿœ']{5,}$/.test(w) && !STOP_FR.has(w.toLowerCase()));
    if(!cands.length) continue;
    const a = cands[(Math.random() * cands.length) | 0];
    const pool = words.filter(w => w !== a.toLowerCase() && Math.abs(w.length - a.length) <= 3);
    if(pool.length < 3) continue;
    const d = [];
    while(d.length < 3 && pool.length){ d.push(pool.splice((Math.random() * pool.length) | 0, 1)[0]); }
    out.push({s:s.replace(a, "___"), a, d, g:"", src});
  }
  return out;
}

function cardPrompt(txt){
  return "Voici la transcription d'une vidéo en français. Fabrique des exercices à trous "
    + "pour un apprenant de niveau intermédiaire (B1-B2).\n\n"
    + "Règles :\n"
    + "- Chaque phrase vient de la transcription, nettoyée : ponctuation correcte, fautes de "
    + "transcription corrigées, entre 6 et 16 mots.\n"
    + "- Remplace UN mot ou une expression utile (verbe, nom, adjectif, locution) par ___ . "
    + "Jamais un mot grammatical banal comme « le », « de », « et ».\n"
    + "- Donne 3 distracteurs de la même catégorie grammaticale : plausibles, mais clairement "
    + "faux dans ce contexte.\n"
    + "- Donne une traduction anglaise naturelle de la phrase complète, trou rempli.\n"
    + "- N'invente aucune phrase qui ne soit pas dans la transcription.\n\n"
    + "Réponds uniquement par un tableau JSON de 6 à 12 objets {\"s\",\"a\",\"d\",\"g\"}, par exemple :\n"
    + "[{\"s\":\"Je passe te ___ vers huit heures.\",\"a\":\"chercher\","
    + "\"d\":[\"vendre\",\"cuisiner\",\"traduire\"],\"g\":\"I'll come pick you up around eight.\"}]\n\n"
    + "Transcription :\n" + txt;
}

function cleanCards(raw, src){
  if(!Array.isArray(raw)) return [];
  return raw.map(c => {
    if(!c || typeof c.s !== "string" || typeof c.a !== "string") return null;
    if(!c.s.includes("___") || !c.a.trim()) return null;
    const d = Array.isArray(c.d) ? c.d.filter(x => typeof x === "string" && x.trim()).slice(0, 3) : [];
    if(d.length < 3) return null;
    return {s:c.s.trim(), a:c.a.trim(), d, g:typeof c.g === "string" ? c.g.trim() : "", src,
      lv:(c.lv >= 1 && c.lv <= 5) ? c.lv : undefined};
  }).filter(Boolean);
}

const VID_ERR = {
  not_granted:"Tu n'as pas autorisé cette page à utiliser Claude. Les exercices seront fabriqués sans traduction.",
  rate_limited:"Trop de demandes d'un coup. Réessaie dans quelques minutes.",
  session_expired:"Ta session Claude a expiré — reconnecte-toi, puis réessaie.",
  prompt_too_large:"Transcription trop longue. Colle une partie plus courte.",
  invalid_json:"Claude a répondu de travers. Réessaie.",
  refused:"Claude n'a pas voulu traiter ce texte. Essaie une autre vidéo.",
  empty_completion:"Aucun exercice n'est sorti de ce texte. Essaie un passage plus dense.",
  upstream_error:"Connexion interrompue. Réessaie."
};

async function buildFromVideo(){
  const txt = $("vidText").value.trim();
  const src = $("vidUrl").value.trim();
  if(txt.length < 120){ $("vidNote").textContent = "Il faut un peu plus de texte — deux ou trois minutes de transcription."; return; }

  const go = $("vidGo"), stop = $("vidStop");
  go.disabled = true; stop.hidden = false;
  $("vidNote").textContent = "Claude lit la transcription…";
  let cards = [];

  if(S.sample){
    S.ctl = new AbortController();
    try{
      const raw = await S.sample.json(cardPrompt(txt.slice(0, 7000)),
        {signal:S.ctl.signal, modelTier:"default"});
      cards = cleanCards(raw, src);
    }catch(e){
      const code = (e && e.code) || "upstream_error";
      if(code === "cancelled"){ $("vidNote").textContent = "Arrêté."; go.disabled = false; stop.hidden = true; return; }
      $("vidNote").textContent = VID_ERR[code] || VID_ERR.upstream_error;
      if(["not_granted","sampling_disabled","not_declared","capability_disabled","capability_removed"].includes(code)) S.sample = null;
    }
  }
  if(!cards.length){
    cards = localCards(txt, src);
    if(cards.length && !S.sample) $("vidNote").textContent = "Exercices fabriqués sur l'appareil, sans traduction.";
  }

  go.disabled = false; stop.hidden = true;
  if(!cards.length){ if(!$("vidNote").textContent) $("vidNote").textContent = "Rien à en tirer. Essaie un autre passage."; return; }

  const stamp = Date.now().toString(36);
  cards.forEach((c, i) => { c.id = "v" + stamp + i; c.lv = S.P.level; });
  S.cards = cards.concat(S.cards).slice(0, 150);
  saveCards();
  S.queue = cards.map(c => c.id).concat(S.queue);
  $("vidNote").textContent = cards.length + " exercice" + (cards.length > 1 ? "s" : "") + " ajouté"
    + (cards.length > 1 ? "s" : "") + " au Trou.";
  drawCards();
  nextTrou(); setMode("trou");
}

function drawCards(){
  const ul = $("vidList"); ul.innerHTML = "";
  if(!S.cards.length){ ul.hidden = true; $("vidClear").hidden = true; return; }
  ul.hidden = false; $("vidClear").hidden = false;
  S.cards.slice(0, 8).forEach(c => {
    const li = document.createElement("li");
    li.textContent = c.s.replace("___", "……");
    ul.appendChild(li);
  });
  if(S.cards.length > 8){
    const li = document.createElement("li");
    li.className = "more";
    li.textContent = "et " + (S.cards.length - 8) + " autres dans le Trou.";
    ul.appendChild(li);
  }
}

function saveCards(){
  srsReset();
  try{ localStorage.setItem("le-cahier-cards-v1", JSON.stringify(S.cards)); }catch(e){}
  if(!S.db || !S.uid) return;
  clearTimeout(S.cTimer);
  S.cTimer = setTimeout(async () => {
    try{ await S.db.doc("data/users/" + S.uid + "/video").set({cards:S.cards, at:Date.now()}); }
    catch(e){ if(e && e.code === "revoked") S.db = null; }
  }, 900);
}

$("vidGo").addEventListener("click", buildFromVideo);
$("vidStop").addEventListener("click", () => S.ctl && S.ctl.abort());
let VID_ARM = false;
$("vidClear").addEventListener("click", () => {
  const en = typeof LANG !== "undefined" && LANG === "en";
  if(!VID_ARM){
    VID_ARM = true;
    $("vidClear").classList.add("danger", "arm");
    $("vidNote").textContent = en
      ? "Tap again to delete the " + S.cards.length + " exercises built from your videos."
      : "Touche encore pour effacer les " + S.cards.length + " exercices tirés de tes vidéos.";
    setTimeout(() => { VID_ARM = false; $("vidClear").classList.remove("danger", "arm"); }, 5000);
    return;
  }
  VID_ARM = false;
  $("vidClear").classList.remove("danger", "arm");
  S.cards = []; saveCards(); srsReset(); refillQueue(); drawCards(); paintMargin();
  $("vidNote").textContent = en ? "Cards deleted." : "Cartes effacées.";
});

/* ---------- onglets & thème ---------- */
function setMode(m){
  /* Quitter La Conversation en pleine mission la termine : le micro ne doit
     pas rester armé pendant qu'on fait autre chose ailleurs. */
  if(S.mode === "parler" && m !== "parler" && typeof CV !== "undefined" && CV && CV.mission
    && !CV.done && typeof cvMissionEnd === "function") cvMissionEnd();
  S.mode = m;
  document.querySelectorAll(".tab").forEach(t => {
    const on = t.dataset.mode === m;
    t.setAttribute("aria-selected", on ? "true" : "false");
  });
  ["seance", "cartes", "phrase", "parler", "perso", "examen", "sons", "histoire", "trou", "motus",
   "genre", "video", "croise", "dictee", "niveau", "profil",
   "ordre", "decider", "imiter", "jour", "ref"].forEach(k => { const p = $("panel-" + k); if(p) p.hidden = (k !== m); });
  if(m === "motus" && (!M || M.done && !M.rows.length)) newMotus();
  if(m === "genre" && !G) nextGenre();
  if(m === "croise" && !X) croiseInit();
  if(m === "dictee" && !D) dicteeInit();
  if(m === "jour") jourInit();
  if(m === "ordre") ordreInit();
  if(m === "decider") deciderInit();
  if(m === "imiter") imiterInit();
  if(m === "seance" && !SE) seanceInit();
  if(m === "phrase" && !PH) phraseInit();
  if(m === "niveau") niveauInit();
  if(m === "profil"){ profilInit(); sauvegardeInit(); }
  if(m === "cartes"){ cartesInit(); capturesInit(); ff625Init(); }
  if(m === "examen") examenInit();
  if(m === "perso") persoInit();
  if(m === "sons") sonsInit();
  if(m === "histoire"){ storyInit(); if(typeof recitPaintBook === "function") recitPaintBook(); }
  if(m === "parler"){ parlerInit(); $("cvLevel").textContent = LEVELS[S.P.level - 1]; }
}
document.querySelectorAll(".tab").forEach(t => t.addEventListener("click", () => setMode(t.dataset.mode)));

$("themeBtn").addEventListener("click", () => {
  const cur = document.documentElement.getAttribute("data-theme");
  const dark = cur ? cur === "dark" : matchMedia("(prefers-color-scheme: dark)").matches;
  document.documentElement.setAttribute("data-theme", dark ? "light" : "dark");
  try{ localStorage.setItem("le-cahier-theme", dark ? "light" : "dark"); }catch(e){}
});
try{
  const th = localStorage.getItem("le-cahier-theme");
  if(th) document.documentElement.setAttribute("data-theme", th);
}catch(e){}

/* ---------- démarrage ---------- */
function asCards(v){
  if(!Array.isArray(v)) return [];
  return v.map(c => {
    const ok = cleanCards([c], (c && c.src) || "")[0];
    return (ok && c.id) ? {...ok, id:String(c.id)} : null;
  }).filter(Boolean).slice(0, 150);
}
function readCards(){
  try{ return asCards(JSON.parse(localStorage.getItem("le-cahier-cards-v1"))); }catch(e){ return []; }
}

function start(hot){
  rpgInit();
  langInit();
  tapInit();
  if(typeof recitInit === "function") recitInit();
  if(typeof guideInit === "function") guideInit();
  if(typeof skyInit === "function") skyInit();
  if(typeof tailleInit === "function") tailleInit();
  S.P = hot && hot.P ? hydrate(hot.P) : readLocal();
  S.cards = hot && hot.cards ? hot.cards : readCards();
  S.mots = hot && hot.mots ? hot.mots : readMots();
  srsReset();   // le registre a pu se construire avant que le paquet soit chargé
  drawCards();
  refillQueue();
  nextTrou(); newMotus(); nextGenre();
  paintMargin();
  setMode(hot && hot.mode ? hot.mode : "jour");
  connect();
  /* Les pistes enregistrées se chargent pendant qu'on lit l'écran : la première phrase
     demandée part tout de suite, dans le geste même du clic. */
  setTimeout(() => { if(typeof vrWarm === "function") vrWarm(); }, 1500);
}

/* La création du personnage attend que le compte ait répondu : sinon on la
   proposerait à quelqu'un qui l'a déjà faite sur un autre appareil. */
async function connect(){
  try{ await connectAccount(); }
  finally{ maybeCreate(); }
}

async function connectAccount(){
  const c = window.claude;
  if(!c || typeof c.use !== "function") return;
  let db = null, user = null;
  try{
    const [d, u, s, dict] = await Promise.all(
      [c.use("db"), c.use("user"), c.use("sample"), c.use("dictation")]);
    db = d; user = u; S.sample = s;
    S.dictation = dict || null;
    /* La Conversation a pu s'initialiser avant que le micro réponde : on la
       reconstruit une fois qu'on sait vraiment ce qui est disponible. */
    if(S.dictation && typeof CV_READY !== "undefined" && CV_READY && typeof cvMic === "function") cvMic();
  }catch(e){ return; }
  if(S.sample) $("vidHow").hidden = false;
  if(!db || !user) return;
  let uid = null;
  try{ uid = await user.id(); }catch(e){}
  if(!uid) return;
  S.db = db; S.uid = uid;
  try{
    const snap = await db.doc("data/users/" + uid + "/progress").get();
    if(snap.exists){
      const cloud = hydrate(snap.data());
      if(cloud.days >= S.P.days){ S.P = cloud; refillQueue(); paintMargin(); }
      else save();
    }else if(S.P.days){ save(); }
    $("syncNote").textContent = "Progrès enregistrés sur ton compte.";
  }catch(e){ S.db = null; return; }

  try{
    const ss = await db.doc("data/users/" + uid + "/srs").get();
    const cloud = ss.exists && ss.data() && ss.data().srs;
    if(cloud && typeof cloud === "object"){
      if(Object.keys(cloud).length >= Object.keys(S.P.srs || {}).length){
        S.P.srs = cloud; refillQueue(); paintMargin();
      }else saveSrs();
    }else if(Object.keys(S.P.srs || {}).length) saveSrs();
  }catch(e){}

  try{
    const vs = await db.doc("data/users/" + uid + "/video").get();
    if(vs.exists){
      const cloud = asCards(vs.data().cards);
      if(cloud.length >= S.cards.length){ S.cards = cloud; srsReset(); refillQueue(); drawCards(); }
      else saveCards();
    }else if(S.cards.length){ saveCards(); }
  }catch(e){}

  if(typeof syncMots === "function") await syncMots();
}

if(window.claude && window.claude.hot){
  window.claude.hot.snapshot(() => ({P:S.P, mode:S.mode, cards:S.cards, mots:S.mots}));
  window.claude.hot.ready ? window.claude.hot.ready(start) : start(window.claude.hot.data || {});
}else{
  start(null);
}
if(!window.claude || typeof window.claude.use !== "function") setTimeout(maybeCreate, 700);
