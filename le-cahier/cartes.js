/* Le Cahier — mes cartes : le paquet façon Fluent Forever.
   L'ordre de la méthode : l'oreille, le socle, tes mots, puis les phrases.
   Des images à la place des traductions, un souvenir à toi sur la carte,
   une image de genre pour chaque nom, et chaque mot vu de quatre côtés. */

/* ---------- le genre en images ----------
   L'astuce de Gabriel Wyner : une image forte par genre, et chaque nom
   s'imagine avec elle. Le chien en feu, la pomme prise dans la glace. */
const GIMG = [
  {k:"feu", pic:"\u{1F525}", m:"en feu", f:"en feu", en:"on fire"},
  {k:"glace", pic:"\u{1F9CA}", m:"pris dans la glace", f:"prise dans la glace", en:"frozen in ice"},
  {k:"boom", pic:"\u{1F4A5}", m:"qui explose", f:"qui explose", en:"exploding"},
  {k:"fleurs", pic:"\u{1F338}", m:"couvert de fleurs", f:"couverte de fleurs", en:"covered in flowers"},
  {k:"foudre", pic:"⚡", m:"frappé par la foudre", f:"frappée par la foudre", en:"struck by lightning"},
  {k:"eau", pic:"\u{1F4A7}", m:"trempé", f:"trempée", en:"soaking wet"},
  {k:"miel", pic:"\u{1F36F}", m:"couvert de miel", f:"couverte de miel", en:"dripping with honey"},
  {k:"pierre", pic:"\u{1FAA8}", m:"changé en pierre", f:"changée en pierre", en:"turned to stone"}
];
const GIMG_DEF = {m:"feu", f:"glace"};
const ckEn = () => typeof LANG !== "undefined" && LANG === "en";

function gImg(g){
  const k = (S.P.gimg && S.P.gimg[g]) || GIMG_DEF[g];
  return GIMG.find(x => x.k === k) || GIMG[g === "m" ? 0 : 1];
}

/* Les mots toujours au pluriel gardent « les ». */
const PLURALS = {lunettes:1, ciseaux:1, gens:1, vacances:1, toilettes:1};

/* L'article qui montre le genre : le, la — et un, une là où l'élision
   cacherait tout (un arbre, une étoile, un hôpital). */
function artOf(m){
  if(!m || (m.g !== "m" && m.g !== "f")) return "";
  const w = String(m.fr || "").toLowerCase();
  if(m.pl || PLURALS[w]) return "les ";
  const v = /^[aeiouyhàâäéèêëîïôöûùüœæ]/i.test(w);
  return m.g === "m" ? (v ? "un " : "le ") : (v ? "une " : "la ");
}

function genderCue(host, word, g, making){
  host.innerHTML = "";
  if(g !== "m" && g !== "f"){ host.hidden = true; return; }
  host.hidden = false;
  const im = gImg(g), en = ckEn();
  const act = en ? im.en : im[g];
  host.appendChild(el("span", "gpic", im.pic));
  const t = el("span", "gtxt");
  const b = el("b", null, artOf({fr:word, g}) + word);
  b.lang = "fr";
  if(making){
    t.append(en ? "Imagine " : "Imagine ", b, " " + act
      + (en ? " — for one real second, in colour. That picture is what will hold the gender."
            : " — une vraie seconde, en couleur. C’est cette image qui retiendra le genre."));
  }else{
    t.append(en ? "Picture " : "Vois ", b, " " + act + ".");
  }
  host.appendChild(t);
}

/* ---------- état du panneau ---------- */
const CK = {q:"", f:"all", n:40, open:null, arm:null};
let CK_READY = false;

function motState(id, t){
  const s = S.P.srs[id];
  if(!s) return "new";
  if(s[0] <= t) return "due";
  if(s[1] >= 21) return "held";
  return "on";
}

function motDue(m, t){
  let best = null;
  motCards(m).forEach(id => {
    const s = S.P.srs[id];
    if(s && (best === null || s[0] < best)) best = s[0];
  });
  return best === null ? null : best - t;
}

function dueText(d){
  const en = ckEn();
  if(d === null) return en ? "new" : "neuf";
  if(d <= 0) return en ? "today" : "aujourd’hui";
  if(d === 1) return en ? "tomorrow" : "demain";
  return en ? "in " + d + " d" : "dans " + d + " j";
}

/* ---------- les quatre étapes ---------- */
function paintSteps(){
  const en = ckEn();
  const sonsOn = PAIRS.filter((p, n) => S.P.srs["m" + n]).length;
  let baseTot = 0, baseHave = 0;
  BASE.forEach(th => th.w.forEach(w => { baseTot++; if(baseAdded(w[0])) baseHave++; }));
  const own = (S.mots || []).filter(m => m.from !== "socle").length;
  const cloze = ALL();
  const clozeOn = cloze.filter(c => S.P.srs[c.id]).length;

  const steps = [
    {t:en ? "Your ear" : "L’oreille", c:sonsOn + " / " + PAIRS.length + (en ? " pairs started" : " paires lancées"),
     a:en ? "Sounds →" : "Les Sons →", go:() => setMode("sons")},
    {t:en ? "Base deck" : "Le socle", c:baseHave + " / " + baseTot + (en ? " words" : " mots"),
     a:en ? "Below ↓" : "Plus bas ↓", go:() => $("ckSocle").scrollIntoView({behavior:"smooth", block:"start"})},
    {t:en ? "Your words" : "Tes mots", c:own + (en ? (own === 1 ? " word of your own" : " words of your own")
      : (own > 1 ? " mots à toi" : " mot à toi")),
     a:en ? "Make one ↓" : "Fabriquer ↓", go:() => {
       $("mkForm").scrollIntoView({behavior:"smooth", block:"center"});
       const i = $("mkForm").querySelector("input");
       if(i) setTimeout(() => i.focus({preventScroll:true}), 350);
     }},
    {t:en ? "Sentences" : "Les phrases", c:clozeOn + " / " + cloze.length + (en ? " started" : " lancées"),
     a:en ? "From Video →" : "La Vidéo →", go:() => setMode("video")}
  ];
  const box = $("ckSteps");
  box.innerHTML = "";
  steps.forEach((s, i) => {
    const b = el("button", "step");
    b.type = "button";
    b.append(el("span", "sn", String(i + 1)), el("span", "st", s.t), el("span", "sc", s.c), el("span", "sa", s.a));
    b.addEventListener("click", s.go);
    box.appendChild(b);
  });
}

/* ---------- la révision du paquet ---------- */
function paintReview(){
  const en = ckEn();
  const {due, fresh} = srsQueue("mot");
  const n = due + fresh;
  $("ckRevN").textContent = n
    ? n + (en ? (n > 1 ? " cards today" : " card today") : (n > 1 ? " cartes aujourd’hui" : " carte aujourd’hui"))
    : (en ? "All caught up" : "À jour");
  $("ckRevSub").textContent = !(S.mots || []).length
    ? (en ? "Your deck is empty — add a theme from the base deck or make a card."
          : "Ton paquet est vide — ajoute un thème du socle ou fabrique une carte.")
    : n
    ? (en ? due + " due, " + fresh + " new" : due + " à revoir, " + fresh + " neuve" + (fresh > 1 ? "s" : ""))
    : (en ? "Nothing due in your deck. New cards come back tomorrow."
          : "Rien à revoir dans ton paquet. Les neuves reviennent demain.");
  $("ckGo").disabled = !n;
}

/* ---------- le genre en images : le choix ---------- */
function paintGimg(){
  const en = ckEn();
  const box = $("ckGimg");
  const wasOpen = box.open;
  box.innerHTML = "";
  const sum = document.createElement("summary");
  sum.append(el("span", null, en ? "Gender in pictures" : "Le genre en images"),
    el("span", "gimg-now", gImg("m").pic + " le · " + gImg("f").pic + " la"));
  box.appendChild(sum);
  const body = el("div", "gimg-body");
  body.appendChild(el("p", "lede dim", en
    ? "Wyner’s trick: give each gender one vivid picture, and see every noun inside it. Choose yours once and keep them — they only work if they stay the same."
    : "L’astuce de Wyner : une image forte par genre, et chaque nom se voit dedans. Choisis les tiennes une fois pour toutes — elles ne marchent que si elles ne changent pas."));
  ["m", "f"].forEach(g => {
    const row = el("div", "gimg-row");
    const art = el("span", "gimg-art", g === "m" ? "le" : "la");
    art.lang = "fr";
    const chips = el("div", "chips");
    GIMG.forEach(x => {
      const on = gImg(g).k === x.k;
      const b = el("button", "chip" + (on ? " on" : ""), x.pic + " " + (en ? x.en : x[g]));
      b.type = "button";
      b.setAttribute("aria-pressed", on ? "true" : "false");
      b.addEventListener("click", () => {
        const other = g === "m" ? "f" : "m";
        const next = {m:gImg("m").k, f:gImg("f").k};
        if(next[other] === x.k) next[other] = next[g];
        next[g] = x.k;
        S.P.gimg = next;
        save();
        paintGimg();
        const cue = $("mkForm").querySelector(".gcue");
        const w = $("mkForm").querySelector("input");
        if(cue && w) w.dispatchEvent(new Event("input"));
      });
      chips.appendChild(b);
    });
    row.append(art, chips);
    body.appendChild(row);
  });
  const ex = el("p", "gcue");
  genderCue(ex, "chien", "m");
  const ex2 = el("p", "gcue");
  genderCue(ex2, "pomme", "f");
  body.append(ex, ex2);
  box.appendChild(body);
  box.open = wasOpen;
}

/* ---------- ton paquet ---------- */
const CK_FILTERS = [
  ["all", "Tous", "All"], ["due", "À revoir", "Due"], ["new", "Neufs", "New"],
  ["own", "Faits main", "Your own"], ["socle", "Socle", "Base deck"]
];

function deckList(){
  const t = srsDay();
  const q = motNorm(CK.q);
  return (S.mots || []).map((m, i) => ({m, i, d:motDue(m, t)}))
    .filter(({m, d}) => {
      if(q && !motNorm(m.fr).includes(q) && !String(m.note || "").toLowerCase().includes(q)) return false;
      if(CK.f === "due") return d !== null && d <= 0;
      if(CK.f === "new") return d === null;
      if(CK.f === "own") return m.from !== "socle";
      if(CK.f === "socle") return m.from === "socle";
      return true;
    })
    .sort((a, b) => (b.m.at || 0) - (a.m.at || 0) || a.i - b.i);
}

function paintFilters(){
  const en = ckEn();
  const box = $("ckFilters");
  box.innerHTML = "";
  CK_FILTERS.forEach(([k, fr, eng]) => {
    const b = el("button", "chip" + (CK.f === k ? " on" : ""), en ? eng : fr);
    b.type = "button";
    b.setAttribute("aria-pressed", CK.f === k ? "true" : "false");
    b.addEventListener("click", () => { CK.f = k; CK.n = 40; CK.open = null; paintDeck(); });
    box.appendChild(b);
  });
}

const RARITY = {
  fr:["Commun", "Peu commun", "Rare", "Épique", "Légendaire"],
  en:["Common", "Uncommon", "Rare", "Epic", "Legendary"]
};

function paintDeck(){
  const en = ckEn();
  paintFilters();
  const t = srsDay();
  const all = S.mots || [];
  const list = deckList();
  let cards = 0, due = 0;
  all.forEach(m => motCards(m).forEach(id => { cards++; if(motState(id, t) === "due") due++; }));
  $("ckCount").textContent = all.length
    ? all.length + (en ? " words · " : " mots · ") + cards + (en ? " cards · " : " cartes · ")
      + due + (en ? " due today" : " à revoir aujourd’hui")
      + (list.length !== all.length ? (en ? " · showing " : " · affichés : ") + list.length : "")
    : (en ? "No words yet." : "Pas encore de mots.");

  const ul = $("ckList");
  ul.innerHTML = "";
  list.slice(0, CK.n).forEach(({m, d}) => {
    const open = CK.open === m.id;
    const li = el("li", "ckitem" + (open ? " open" : ""));
    const row = el("button", "ckrow");
    row.type = "button";
    row.setAttribute("aria-expanded", open ? "true" : "false");
    const pic = el("span", "ckpic", m.pic || "·");
    const main = el("span", "ckmain");
    const w = el("span", "ckword", artOf(m) + m.fr);
    w.lang = "fr";
    const line = el("span", "ckline");
    line.appendChild(w);
    main.appendChild(line);
    if(m.note){
      const n = el("span", "cknote", m.note);
      n.dataset.keep = "1";
      main.appendChild(n);
    }
    const dots = el("span", "ckdots");
    let held = 0;
    motCards(m).forEach(id => {
      const st = motState(id, t);
      if(st === "held") held++;
      const dot = el("span", "dot " + st);
      dot.title = MOT_LABEL[id[1]];
      dots.appendChild(dot);
    });
    /* La rareté : combien des cartes du mot tiennent depuis trois semaines et plus. */
    const tier = Math.min(4, held);
    li.className += " r" + tier;
    const rar = el("span", "rar r" + tier, (en ? RARITY.en : RARITY.fr)[tier]);
    const dt = el("span", "ckdue" + (d !== null && d <= 0 ? " now" : ""), dueText(d));
    line.appendChild(rar);
    row.append(pic, main, dots, dt);
    row.addEventListener("click", () => {
      CK.open = open ? null : m.id;
      CK.arm = null;
      paintDeck();
    });
    li.appendChild(row);
    if(open) li.appendChild(deckEditor(m, t));
    ul.appendChild(li);
  });
  const more = list.length - CK.n;
  $("ckMore").hidden = more <= 0;
  if(more > 0) $("ckMore").textContent = en ? "Show " + Math.min(40, more) + " more" : "Afficher " + Math.min(40, more) + " de plus";
  $("ckEmpty").hidden = !!all.length;
}

function deckEditor(m, t){
  const en = ckEn();
  const box = el("div", "ckedit");

  const st = el("div", "ckcards");
  motCards(m).forEach(id => {
    const s = S.P.srs[id], k = motState(id, t);
    const line = el("div");
    line.append(el("span", "dot " + k), el("span", "ckclab", MOT_LABEL[id[1]]),
      el("span", "ckcst", !s ? (en ? "not seen yet" : "pas encore vue")
        : k === "due" ? (en ? "due today" : "à revoir aujourd’hui")
        : (en ? "back " : "revient ") + dueText(s[0] - t)
          + (s[1] >= 1 ? (en ? " · gap " + s[1] + " d" : " · écart " + s[1] + " j") : "")));
    st.appendChild(line);
  });
  box.appendChild(st);

  const mk = (id, label, val) => {
    const l = el("label", "fld");
    l.appendChild(el("span", null, label));
    const i = el("input");
    i.className = "seinput"; i.id = id; i.value = val || ""; i.autocomplete = "off"; i.spellcheck = false;
    l.appendChild(i);
    return [l, i];
  };
  const [lw, iw] = mk("ckEdWord", en ? "The French word" : "Le mot français", m.fr);
  iw.lang = "fr";
  const [lp, ip] = mk("ckEdPic", en ? "A picture" : "Une image", m.pic);
  const [ln, inn] = mk("ckEdNote", en ? "Your own memory of it" : "Ton souvenir à toi", m.note);
  inn.dataset.keep = "1";
  const grid = el("div", "mkgrid");
  grid.append(lw, lp);
  box.append(grid, ln);

  let g = m.g || "";
  const gl = el("div", "fld");
  gl.appendChild(el("span", null, en ? "Gender" : "Genre"));
  const chips = el("div", "chips");
  [["", en ? "none" : "aucun"], ["m", "le"], ["f", "la"]].forEach(([v, lab]) => {
    const b = el("button", "chip" + (g === v ? " on" : ""), lab);
    b.type = "button";
    if(v) b.lang = "fr";
    b.addEventListener("click", () => {
      g = v;
      [...chips.children].forEach(c => c.classList.toggle("on", c === b));
    });
    chips.appendChild(b);
  });
  gl.appendChild(chips);
  box.appendChild(gl);

  const note = el("p", "note");
  const row = el("div", "after");
  const saveB = el("button", "go", en ? "Save" : "Enregistrer");
  saveB.addEventListener("click", () => {
    const w = splitArt(iw.value).word;
    if(!w){ note.textContent = en ? "The word can't be empty." : "Le mot ne peut pas être vide."; return; }
    const dup = motFind(w);
    if(dup && dup.id !== m.id){
      note.textContent = en ? "That word is already in your deck." : "Ce mot est déjà dans ton paquet.";
      return;
    }
    motEdit(m.id, {fr:iw.value, pic:ip.value, note:inn.value, g});
    CK.open = null;
    paintCartes();
  });
  const say = el("button", "ghost", en ? "Hear it" : "Écouter");
  say.addEventListener("click", () => speakFr(artOf({fr:splitArt(iw.value).word, g}) + splitArt(iw.value).word, .9));
  const armed = CK.arm === m.id;
  const del = el("button", "ghost danger" + (armed ? " arm" : ""),
    armed ? (en ? "Delete for good" : "Supprimer pour de bon") : (en ? "Delete" : "Supprimer"));
  del.addEventListener("click", () => {
    if(CK.arm !== m.id){ CK.arm = m.id; paintDeck(); return; }
    CK.arm = null; CK.open = null;
    motDelete(m.id);
    paintCartes();
  });
  row.append(saveB, say, del);
  box.append(row, note);
  if(armed) note.textContent = en ? "Its " + motCards(m).length + " cards and their history go with it."
    : "Ses " + motCards(m).length + " cartes et leur historique partent avec lui.";
  return box;
}

/* ---------- les mots de ton monde ----------
   Après le socle, Fluent Forever passe aux mots qui comptent pour toi.
   Claude propose, tu choisis : la traduction anglaise sert seulement à
   choisir, elle n'entre jamais sur la carte. */
const SG = {list:[], seen:[], busy:false, ctl:null};

function sgDoms(){
  const d = Array.isArray(S.P.ckDoms) ? S.P.ckDoms : (S.P.profil && S.P.profil.domains) || [];
  return d.filter(k => DOMAINS.some(x => x.k === k));
}
const sgVar = () => S.P.ckVar === "fr" ? "fr" : "ca";

function sgPrompt(){
  const p = S.P.profil || {}, lv = S.P.level;
  const doms = sgDoms().length ? sgDoms() : profilDomains();
  const topic = $("ckTopic").value.trim().slice(0, 200);
  const have = (S.mots || []).map(m => m.fr).slice(0, 400);
  const usage = sgVar() === "ca"
    ? "le français du Canada tel qu'on le parle en Ontario et au Québec : prends le mot qu'on y emploie "
      + "vraiment (courriel, fin de semaine, cellulaire, rendez-vous à la clinique), sans joual ni anglicisme familier"
    : "le français de France, registre courant";
  return "Tu proposes du vocabulaire à un apprenant de français qui suit la méthode Fluent Forever "
    + "de Gabriel Wyner : pas de traduction sur les cartes, une image pour chaque mot.\n\n"
    + "Niveau : " + LEVELS[lv - 1] + " — des mots courants dans ces situations ; un mot un peu plus "
    + "rare seulement si la situation l'exige vraiment.\n"
    + (p.why ? "Pourquoi il apprend : " + p.why + "\n" : "")
    + "Ses terrains : " + doms.map(domLabel).join(", ") + "\n"
    + (topic ? "Situation précise à préparer : " + topic + "\n" : "")
    + "Usage : " + usage + ".\n"
    + (have.length ? "Mots déjà dans son paquet — n'en propose aucun : " + have.join(", ") + "\n" : "")
    + (SG.seen.length ? "Déjà proposés à l'instant — n'en propose aucun : " + SG.seen.join(", ") + "\n" : "")
    + "\nRègles :\n"
    + "- 12 mots, du plus utile au moins utile pour ces situations.\n"
    + "- D'abord des noms concrets qu'on peut montrer du doigt, puis quelques verbes d'action. "
    + "Rien d'abstrait qu'aucune image ne peut montrer.\n"
    + "- Un mot ou une expression figée courte (trois mots au plus), sans article.\n"
    + "- g : \"m\" ou \"f\" pour un nom, \"\" pour le reste. Pour un nom toujours au pluriel, "
    + "donne son genre et ajoute \"pl\":true.\n"
    + "- pic : un seul emoji qui montre vraiment la chose, pas un emoji décoratif.\n"
    + "- en : la traduction anglaise en un à trois mots. Elle sert seulement à choisir.\n\n"
    + "Réponds uniquement par un tableau JSON :\n"
    + '[{"fr":"tapis de course","g":"m","pic":"\u{1F3C3}","en":"treadmill"}]';
}

function sgClean(raw){
  const arr = Array.isArray(raw) ? raw : (raw && Array.isArray(raw.mots) ? raw.mots : []);
  const out = [], taken = {};
  arr.forEach(x => {
    if(!x || typeof x.fr !== "string") return;
    const sp = splitArt(x.fr);
    const fr = sp.word.replace(/\s+/g, " ").trim();
    if(!fr || fr.length > 40 || fr.split(" ").length > 3) return;
    const key = fr.toLowerCase();
    if(taken[key] || motFind(fr) || SG.seen.includes(key)) return;
    taken[key] = 1;
    const g = x.g === "m" || x.g === "f" ? x.g : sp.g;
    out.push({
      fr, g, pl:x.pl === true && !!g,
      pic:typeof x.pic === "string" ? x.pic.trim().slice(0, 12) : "",
      en:typeof x.en === "string" ? x.en.trim().slice(0, 40) : "",
      on:true
    });
  });
  return out.slice(0, 12);
}

async function sgAsk(){
  const en = ckEn();
  if(SG.busy) return;
  if(!S.sample){ $("ckSugNote").textContent = tr(PH_ERR.not_granted); return; }
  SG.busy = true;
  SG.ctl = new AbortController();
  $("ckSuggest").disabled = true;
  $("ckSugMore").disabled = true;
  $("ckStop").hidden = false;
  $("ckSugNote").textContent = en ? "Claude is choosing words…" : "Claude choisit des mots…";
  let raw = null;
  try{
    raw = await S.sample.json(sgPrompt(), {modelTier:"default", cache:false, signal:SG.ctl.signal});
  }catch(e){
    const code = (e && e.code) || "upstream_error";
    $("ckSugNote").textContent = code === "cancelled" ? (en ? "Stopped." : "Arrêté.")
      : tr(PH_ERR[code] || PH_ERR.upstream_error);
    if(["not_granted", "sampling_disabled", "not_declared", "capability_disabled"].includes(code)){
      S.sample = null;
      $("ckWarn").hidden = false;
    }
  }
  SG.busy = false;
  $("ckSuggest").disabled = false;
  $("ckSugMore").disabled = false;
  $("ckStop").hidden = true;
  if(!raw) return;
  const got = sgClean(raw);
  if(!got.length){
    $("ckSugNote").textContent = en ? "Nothing new came back. Try another topic or a precise situation."
      : "Rien de neuf. Essaie un autre terrain ou une situation précise.";
    return;
  }
  SG.seen = SG.seen.concat(got.map(x => x.fr.toLowerCase())).slice(-120);
  SG.list = got;
  $("ckSugNote").textContent = en
    ? "Keep the ones that matter to you — tap a word to drop it."
    : "Garde ceux qui comptent pour toi — touche un mot pour l’écarter.";
  paintSugg();
}

function paintSugg(){
  const en = ckEn();
  const ul = $("ckSugList");
  ul.innerHTML = "";
  ul.hidden = !SG.list.length;
  $("ckSugAct").hidden = !SG.list.length;
  SG.list.forEach(x => {
    const li = el("li");
    const b = el("button", "sug");
    b.type = "button";
    b.setAttribute("aria-pressed", x.on ? "true" : "false");
    const w = el("span", "sfr", artOf(x) + x.fr);
    w.lang = "fr";
    const words = el("span", "sw");
    words.appendChild(w);
    if(x.en){
      const g = el("span", "sen", x.en);
      g.dataset.keep = "1";
      words.appendChild(g);
    }
    b.append(el("span", "spic", x.pic || "·"), words, el("span", "schk", "✓"));
    b.addEventListener("click", () => { x.on = !x.on; paintSugg(); });
    li.appendChild(b);
    ul.appendChild(li);
  });
  const n = SG.list.filter(x => x.on).length;
  $("ckSugAdd").disabled = !n;
  $("ckSugAdd").textContent = en
    ? (n ? "Add " + n + (n > 1 ? " words" : " word") : "Pick at least one word")
    : (n ? "Ajouter " + (n > 1 ? "ces " + n + " mots" : "ce mot") : "Choisis au moins un mot");
}

function sgAdd(){
  const en = ckEn();
  const keep = SG.list.filter(x => x.on);
  let n = 0;
  keep.slice().reverse().forEach(x => {
    if(motFind(x.fr)) return;
    const m = motMake(x.fr, x.pic, "", x.g, "", "claude");
    if(!m) return;
    if(x.pl){ m.pl = true; }
    n++;
  });
  if(n) saveMots();
  SG.list = SG.list.filter(x => !x.on);
  paintSugg();
  paintCartes();
  $("ckSugNote").textContent = n
    ? (en ? n + " words added. They go before the base deck in your new cards. Open one in your deck and add a memory of your own — that is what makes it stick."
          : n + " mots ajoutés. Ils passent avant le socle dans tes cartes neuves. Ouvre-les dans ton paquet et ajoute un souvenir à toi : c’est ce qui les fera tenir.")
    : (en ? "Already in your deck." : "Déjà dans ton paquet.");
}

function paintSgControls(){
  const en = ckEn();
  const box = $("ckDoms");
  box.innerHTML = "";
  const on = sgDoms();
  DOMAINS.forEach(d => {
    const sel = on.includes(d.k);
    const b = el("button", "chip" + (sel ? " on" : ""), d.l);
    b.type = "button";
    b.setAttribute("aria-pressed", sel ? "true" : "false");
    b.addEventListener("click", () => {
      const cur = sgDoms();
      S.P.ckDoms = cur.includes(d.k) ? cur.filter(k => k !== d.k) : cur.concat([d.k]);
      save();
      paintSgControls();
    });
    box.appendChild(b);
  });
  const vbox = $("ckVar");
  vbox.innerHTML = "";
  [["ca", en ? "Canada" : "Canada"], ["fr", en ? "France" : "France"]].forEach(([k, lab]) => {
    const b = el("button", "chip" + (sgVar() === k ? " on" : ""), lab);
    b.type = "button";
    b.setAttribute("aria-pressed", sgVar() === k ? "true" : "false");
    b.addEventListener("click", () => { S.P.ckVar = k; save(); paintSgControls(); });
    vbox.appendChild(b);
  });
  $("ckWarn").hidden = !!S.sample;
}

let SG_READY = false;
function sgInit(){
  if(SG_READY) return paintSgControls();
  SG_READY = true;
  $("ckSuggest").addEventListener("click", () => { SG.seen = []; sgAsk(); });
  $("ckSugMore").addEventListener("click", sgAsk);
  $("ckStop").addEventListener("click", () => SG.ctl && SG.ctl.abort());
  $("ckSugAdd").addEventListener("click", sgAdd);
  $("ckTopic").addEventListener("keydown", (e) => { if(e.key === "Enter"){ e.preventDefault(); SG.seen = []; sgAsk(); } });
  paintSgControls();
}

/* ---------- le panneau ---------- */
function paintCartes(full){
  if(!CK_READY) return;
  paintSteps();
  paintReview();
  paintDeck();
  sgInit();
  if(full){
    paintSugg();
    paintGimg();
    cardForm($("mkForm"), "", null);
    if(typeof paintBase === "function") paintBase();
  }
}

function cartesInit(){
  if(!CK_READY){
    CK_READY = true;
    baseInit();
    cardForm($("mkForm"), "", null);
    paintGimg();
    $("ckGo").addEventListener("click", () => {
      setMode("seance");
      startSeance("mot");
      const top = document.querySelector(".tabs");
      if(top && top.getBoundingClientRect().top < 0) top.scrollIntoView({block:"start"});
    });
    $("ckSearch").addEventListener("input", () => { CK.q = $("ckSearch").value; CK.n = 40; CK.open = null; paintDeck(); });
    $("ckMore").addEventListener("click", () => { CK.n += 40; paintDeck(); });
  }
  paintCartes();
}

/* L'interface change de langue : on redessine ce qui est composé ici. */
(function(){
  const base = setLang;
  setLang = function(l){ base(l); if(CK_READY) paintCartes(true); };
})();

/* Sur la fiche : espace pour retourner, 1 à 4 pour se noter. */
document.addEventListener("keydown", (e) => {
  if(S.mode !== "seance" || !SE || !SE.cur || SE.cur.kind !== "mot" || SE.cur.t !== "r" || SE.answered) return;
  const tag = (e.target && e.target.tagName) || "";
  if(tag === "INPUT" || tag === "TEXTAREA") return;
  if(!SE.flipped && e.key === " "){ e.preventDefault(); ficheFlip(); return; }
  if(SE.flipped && /^[1-4]$/.test(e.key)){
    const b = $("seAfter").querySelectorAll(".grade")[+e.key - 1];
    if(b){ e.preventDefault(); b.click(); }
  }
});

/* ---------- l'interface en anglais ---------- */
Object.assign(EN, {
  "Mes cartes":"My cards",
  "Mes cartes · méthode Fluent Forever":"My cards · the Fluent Forever method",
  "Des images à la place des traductions, un souvenir à toi sur chaque carte, et chaque mot vu de quatre côtés. Dans cet ordre : l’oreille, le socle, tes mots, puis les phrases.":
    "Pictures instead of translations, a memory of your own on every card, and every word seen from four sides. In this order: your ear, the base deck, your own words, then sentences.",
  "Réviser mes cartes":"Review my cards",
  "Fabriquer une carte":"Make a card",
  "Une image plutôt qu’une traduction, et un souvenir à toi : c’est fabriquer la carte qui la fait tenir. Un mot donne quatre cartes : mot → image, image → mot, son → orthographe, et le genre.":
    "A picture rather than a translation, and a memory of your own: it is making the card that makes it stick. One word makes four cards: word → picture, picture → word, sound → spelling, and gender.",
  "Des mots concrets, qu’on peut montrer du doigt — c’est par là que commence la méthode. Chaque mot entre avec son image et son genre, sans traduction, et donne quatre cartes.":
    "Concrete words you can point at — that is where the method starts. Each word arrives with its picture and its gender, no translation, and makes four cards.",
  "Ton paquet":"Your deck",
  "Les mots de ton monde":"Words for your world",
  "Après le socle, la méthode passe aux mots dont toi tu as besoin. Choisis tes terrains : Claude propose des mots concrets avec leur image et leur genre, et tu gardes ceux qui te parlent.":
    "After the base deck, the method moves on to the words you need. Pick your areas: Claude suggests concrete words with their picture and gender, and you keep the ones that speak to you.",
  "Les propositions viennent de Claude, et il faut ton accord. Le reste de tes cartes fonctionne sans lui.":
    "The suggestions come from Claude, and that needs your permission. The rest of your cards work without it.",
  "Une situation précise — facultatif":"A precise situation — optional",
  "Le français de":"French as spoken in",
  "Proposer 12 mots":"Suggest 12 words", "12 autres":"12 more",
  "Ajouter les mots choisis":"Add the chosen words",
  "pas encore vue":"not seen yet", "prévue":"scheduled", "à revoir aujourd’hui":"due today",
  "tenue trois semaines et plus":"held three weeks or more",
  "Ton paquet est vide. Ajoute un thème du socle, ou fabrique ta première carte plus haut.":
    "Your deck is empty. Add a theme from the base deck, or make your first card above.",
  "Retourner la fiche":"Turn the card over",
  "Qu’est-ce que c’est ? Vois l’image dans ta tête, puis retourne la fiche.":
    "What is it? See the picture in your head, then turn the card over.",
  "Pas d’image sur cette carte — ajoute-en une dans Mes cartes.":
    "No picture on this card — add one in My cards.",
  "Raté":"Again", "Difficile":"Hard", "Bien":"Good", "Facile":"Easy",
  "dans un instant":"in a moment",
  "Mot → image":"Word → picture", "Image → mot":"Picture → word",
  "Son → orthographe":"Sound → spelling", "Le ou la":"Le or la",
  "Ton paquet est à jour pour aujourd'hui.":"Your deck is done for today.",
  "Tes cartes sont faites.":"Your cards are done.",
  "Ton paquet est vide. Ajoute un thème du socle ou fabrique ta première carte dans Mes cartes.":
    "Your deck is empty. Add a theme from the base deck or make your first card in My cards."
});
Object.assign(EN_PH, {
  "le mot, avec son article":"the word, with its article",
  "le mot":"the word",
  "chercher un mot ou un souvenir…":"search a word or a memory…",
  "expliquer un exercice à un client, prendre rendez-vous à la clinique…":
    "explaining an exercise to a client, booking at the clinic…"
});

/* Les verdicts de la séance, traduits jusqu'au bout. */
const CK_TAIL = [
  [/La réponse était « (.+?) »/, "The answer was “$1”."],
  [/Les accents comptent : « (.+?) »/, "Accents count: “$1”."],
  [/Le mot est juste, le genre non : « (.+?) »\./, "Right word, wrong gender: “$1”."],
  [/Avec son article, la prochaine fois : « (.+?) »\./, "Next time, say it with its article: “$1”."],
  [/Revue demain\./, "Due again tomorrow."],
  [/Revue dans (\d+) jours\./, "Due again in $1 days."],
  [/Elle revient dans un instant\./, "It comes back in a moment."]
];
EN_PAT.unshift(
  [/^(Juste|Raté)\. (.+)$/, (all, v, rest) => {
    let out = rest;
    CK_TAIL.forEach(([re, to]) => { out = out.replace(re, to); });
    return (v === "Juste" ? "Correct. " : "Missed. ") + out;
  }],
  [/^(Mot → image|Image → mot|Son → orthographe|Le ou la) · (?:nouvelle|new)$/,
    (all, k) => (EN[k] || k) + " · new"]
);
