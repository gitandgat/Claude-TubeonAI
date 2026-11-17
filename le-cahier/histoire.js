/* Le Cahier — l'histoire.
   Lire en continu, sans s'arrêter sur chaque mot : c'est le volume de
   lecture compréhensible qui fait le travail, pas le dictionnaire.
   Le glossaire est volontairement court — on apprend à tolérer le flou. */

const ST_WORDS = {1:130, 2:220, 3:340, 4:480, 5:620, 6:780};

let ST = null;

function storyKnown(){
  const out = [];
  (S.mots || []).slice(0, 40).forEach(m => out.push(m.fr));
  ALL().slice(0, 20).forEach(c => { if(c.a) out.push(c.a); });
  return out.slice(0, 50).join(", ");
}

function storyPrompt(){
  const lv = S.P.level, chapters = (S.P.story.chapters || []);
  const bible = typeof recitBible === "function" ? recitBible() : "";
  const last = chapters[chapters.length - 1];
  const doms = (typeof profilDomains === "function" ? profilDomains() : ["quotidien"])
    .map(d => (typeof domLabel === "function" ? domLabel(d) : d)).join(", ");

  return "Tu écris un feuilleton en français pour un apprenant de niveau " + LEVELS[lv - 1] + ".\n\n"
    + (last ? "Chapitre précédent, en une phrase : " + (last.resume || "") + "\n"
        + "Continue l'histoire au chapitre " + (chapters.length + 1) + ".\n"
      : (bible ? "C'est le premier chapitre des Chroniques : il prolonge l'histoire du Récit sans la répéter.\n"
        : "C'est le chapitre 1. Invente une intrigue avec un petit mystère ou une tension "
          + "qui donne envie de lire la suite.\n"))
    + (bible || "Univers possible, à puiser dans ce qui l'intéresse : " + doms + ".\n")
    + "Mots qu'il connaît déjà, à réutiliser : " + storyKnown() + "\n\n"
    + "Règles :\n"
    + "- Environ " + ST_WORDS[lv] + " mots, au niveau " + LEVELS[lv - 1] + " et pas au-dessus.\n"
    + "- Il doit comprendre l'essentiel sans dictionnaire : vise 90 à 95 % de mots qu'il a déjà.\n"
    + "- Glisse 6 à 10 mots nouveaux seulement, portés par le contexte.\n"
    + "- Du récit et du dialogue, pas une leçon. Une vraie histoire, avec une fin de chapitre "
    + "qui appelle la suite.\n\n"
    + "Réponds uniquement par ce JSON :\n"
    + '{"titre":"...","texte":"...","resume":"...","mots":[{"fr":"...","en":"..."}],'
    + '"questions":[{"q":"...","r":"..."}]}\n'
    + "- texte : le chapitre, paragraphes séparés par un saut de ligne.\n"
    + "- resume : une phrase en français qui résume ce chapitre (elle servira au suivant).\n"
    + "- mots : le glossaire, 6 à 10 mots du texte avec leur sens anglais, rien de plus.\n"
    + "- questions : 3 questions de compréhension en français, avec leur réponse.";
}

async function storyNew(){
  if(!S.sample){ $("stNote").textContent = PH_ERR.not_granted; return; }
  $("stGo").disabled = true;
  $("stNote").textContent = (typeof LANG !== "undefined" && LANG === "en")
    ? "Claude is writing the next chapter…" : "Claude écrit le chapitre…";
  let ch = null;
  try{
    ch = await S.sample.json(storyPrompt(), {modelTier:"default", cache:false});
  }catch(e){
    $("stNote").textContent = PH_ERR[(e && e.code)] || PH_ERR.upstream_error;
    $("stGo").disabled = false;
    return;
  }
  $("stGo").disabled = false;
  if(!ch || !ch.texte){ $("stNote").textContent = "Rien n'est revenu. Réessaie."; return; }

  const chapter = {
    n:(S.P.story.chapters || []).length + 1,
    titre:String(ch.titre || "").slice(0, 80),
    texte:String(ch.texte || ""),
    resume:String(ch.resume || "").slice(0, 200),
    mots:(Array.isArray(ch.mots) ? ch.mots : []).filter(m => m && m.fr).slice(0, 12),
    questions:(Array.isArray(ch.questions) ? ch.questions : []).slice(0, 4)
  };
  S.P.story.chapters = (S.P.story.chapters || []).concat([chapter]).slice(-12);
  S.P.story.at = chapter.n;
  save();
  storyShow(chapter);
}

function storyShow(ch){
  if("speechSynthesis" in window) speechSynthesis.cancel();
  ST = {ch, lookups:0, done:false, reading:false};
  const en = typeof LANG !== "undefined" && LANG === "en";
  $("stRead").textContent = en ? "▶ Listen" : "▶ Écouter";
  $("stTitle").textContent = "Chapitre " + ch.n + " · " + ch.titre;
  $("stNote").textContent = "";
  $("stEnd").innerHTML = "";
  $("stDone").hidden = false;
  $("stGo").textContent = en ? "Next chapter" : "Chapitre suivant";

  const gloss = {};
  (ch.mots || []).forEach(m => { gloss[m.fr.toLowerCase()] = m.en; });

  const body = $("stText");
  body.innerHTML = "";
  ch.texte.split(/\n+/).forEach(para => {
    if(!para.trim()) return;
    const p = document.createElement("p");
    para.split(/(\s+)/).forEach(tok => {
      const bare = tok.toLowerCase().replace(/[^a-zà-ÿœ'-]/g, "");
      if(bare && gloss[bare]){
        const s = document.createElement("span");
        s.className = "glossy";
        s.textContent = tok;
        s.title = en ? "Click for the meaning" : "Clique pour le sens";
        s.addEventListener("click", () => {
          if(s.classList.contains("shown")) return;
          s.classList.add("shown");
          const tip = document.createElement("span");
          tip.className = "glosstip";
          tip.textContent = gloss[bare];
          s.after(tip);
          ST.lookups++;
          $("stNote").textContent = ST.lookups < 4 ? ""
            : (en ? ST.lookups + " lookups — try reading to the end first, the sense usually arrives."
              : ST.lookups + " mots regardés — essaie d'aller au bout, le sens vient souvent tout seul.");
        });
        p.appendChild(s);
      }else p.appendChild(document.createTextNode(tok));
    });
    body.appendChild(p);
  });
}

function storyFinish(){
  if(!ST || ST.done) return;
  ST.done = true;
  const en = typeof LANG !== "undefined" && LANG === "en";
  const ch = ST.ch, box = $("stEnd");
  box.innerHTML = "";

  box.appendChild(Object.assign(document.createElement("p"),
    {className:"fchead", textContent:en ? "Comprehension" : "Compréhension"}));
  (ch.questions || []).forEach((q, i) => {
    const d = document.createElement("div");
    d.className = "exq";
    d.appendChild(Object.assign(document.createElement("p"), {className:"exqt", textContent:(i + 1) + ". " + q.q}));
    /* On répond avant de voir : une question dont on lit la réponse ne teste rien. */
    const ta = document.createElement("textarea");
    ta.className = "seinput";
    ta.rows = 2;
    ta.spellcheck = false;
    ta.placeholder = en ? "Answer in French, from memory" : "Réponds en français, de mémoire";
    d.appendChild(ta);
    const b = document.createElement("button");
    b.className = "ghost mkmini";
    b.textContent = en ? "Compare with the answer" : "Comparer à la réponse";
    b.addEventListener("click", () => {
      const model = Object.assign(document.createElement("p"),
        {className:"phline dimline", textContent:q.r || ""});
      b.replaceWith(model);
      ta.readOnly = true;
      /* Trois états, pas une comparaison de chaînes : une réponse libre peut être
         juste sans ressembler au modèle. C'est à toi de trancher, honnêtement. */
      const row = document.createElement("div");
      row.className = "after";
      [[en ? "I had it" : "Retrouvé", "ok", 1],
       [en ? "Valid variant" : "Variante juste", "vari", 1],
       [en ? "Missed it" : "Manqué", "miss", 0]].forEach(pair => {
        const lab = pair[0], key = pair[1], good = pair[2];
        const sb = document.createElement("button");
        sb.className = "ghost mkmini";
        sb.textContent = lab;
        sb.addEventListener("click", () => {
          const st = S.P.story.q = S.P.story.q || {ok:0, vari:0, miss:0};
          st[key] = (st[key] || 0) + 1;
          row.replaceWith(Object.assign(document.createElement("p"),
            {className:"phline", textContent:lab}));
          if(good && typeof xpGain === "function") xpGain(8, null);
          if(typeof scored === "function") scored(!!good);
          save();
        });
        row.appendChild(sb);
      });
      model.after(row);
    });
    d.appendChild(b);
    box.appendChild(d);
  });

  box.appendChild(Object.assign(document.createElement("p"),
    {className:"fchead", textContent:en ? "The chapter's words" : "Les mots du chapitre"}));
  const ul = document.createElement("ul");
  ul.className = "deckList";
  (ch.mots || []).forEach(m => {
    const li = document.createElement("li");
    li.append(Object.assign(document.createElement("b"), {textContent:m.fr}),
      document.createTextNode(" — " + (m.en || "")));
    ul.appendChild(li);
  });
  box.appendChild(ul);

  const row = document.createElement("div");
  row.className = "after";
  const mk = document.createElement("button");
  mk.className = "go";
  mk.textContent = en ? "Make cards from this chapter" : "Faire des cartes de ce chapitre";
  mk.addEventListener("click", () => {
    let n = 0;
    (ch.mots || []).forEach(m => {
      if(typeof motMake !== "function") return;
      if((S.mots || []).some(x => x.fr === m.fr)) return;
      if(motMake(m.fr, "", m.en || "", "", "", "histoire")) n++;
    });
    if(typeof drawMots === "function") drawMots();
    mk.replaceWith(Object.assign(document.createElement("p"),
      {className:"phline", textContent:n + (en ? " words added to the deck." : " mots ajoutés au paquet.")}));
  });
  const again = document.createElement("button");
  again.className = "ghost";
  again.textContent = en ? "Read it again" : "Relire";
  again.addEventListener("click", () => storyShow(ch));
  row.append(mk, again);
  box.appendChild(row);

  S.P.story.read = (S.P.story.read || 0) + 1;
  if(typeof xpGain === "function") xpGain(35, null);
  scored(true);
  save();
  $("stNote").textContent = ST.lookups === 0
    ? (en ? "Read end to end without one lookup. That is the whole point."
      : "Lu d'un bout à l'autre sans un seul mot cherché. C'est exactement ça.")
    : "";
}

function storyInit(){
  if(ST) return;
  $("stGo").addEventListener("click", storyNew);
  $("stDone").addEventListener("click", storyFinish);
  $("stRead").addEventListener("click", () => {
    if(!ST || !ST.ch) return;
    const en = typeof LANG !== "undefined" && LANG === "en";
    /* Un deuxième clic arrête. Et on lit le chapitre entier : la coupe à 1200
       signes n'en disait qu'un quart aux niveaux hauts, sans le dire. */
    if(ST.reading){
      ST.reading = false;
      $("stRead").textContent = en ? "▶ Listen" : "▶ Écouter";
      if("speechSynthesis" in window) speechSynthesis.cancel();
      return;
    }
    ST.reading = true;
    $("stRead").textContent = en ? "■ Stop" : "■ Arrêter";
    speakFr(ST.ch.texte, .92);
  });
  if(!S.sample) $("stWarn").hidden = false;
  const chapters = S.P.story.chapters || [];
  if(chapters.length) storyShow(chapters[chapters.length - 1]);
  else $("stDone").hidden = true;
}
