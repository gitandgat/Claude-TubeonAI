/* Le Cahier — tes captures.
   Le dictionnaire pop-up exporte « Word,Sentence » : le mot en français, la
   phrase dite à voix haute, le plus souvent en anglais. On traduit la phrase
   fidèlement, on ne cache QUE le mot nu, l'article reste dans la phrase et le
   genre devient une étiquette. */

let CP = null;

function csvRows(text){
  const rows = [];
  let f = "", row = [], q = false;
  for(let i = 0; i < text.length; i++){
    const c = text[i];
    if(q){
      if(c === '"' && text[i + 1] === '"'){ f += '"'; i++; }
      else if(c === '"') q = false;
      else f += c;
    }else if(c === '"') q = true;
    else if(c === ","){ row.push(f); f = ""; }
    else if(c === "\n" || c === "\r"){
      if(c === "\r" && text[i + 1] === "\n") i++;
      row.push(f); f = "";
      if(row.some(x => x.trim())) rows.push(row);
      row = [];
    }else f += c;
  }
  row.push(f);
  if(row.some(x => x.trim())) rows.push(row);
  if(rows.length && /^\s*word\s*$/i.test(rows[0][0] || "")) rows.shift();
  return rows.filter(r => (r[0] || "").trim())
    .map(r => ({w:(r[0] || "").trim(), s:(r[1] || "").trim()}));
}

function capPrompt(batch){
  return "Un apprenant lit en français avec un dictionnaire pop-up. À chaque mot "
    + "capturé il dit une phrase de contexte, le plus souvent EN ANGLAIS.\n\n"
    + "Pour chaque capture, fabrique une carte à trou en français.\n\n"
    + "Règles, dans l'ordre d'importance :\n"
    + "1. Traduis fidèlement SA phrase en français — mêmes détails, mêmes noms, "
    + "même idée. N'invente jamais une phrase générique à la place.\n"
    + "2. Dans cette traduction, remplace UNIQUEMENT le mot nu par ___ . "
    + "L'article, le possessif, la préposition et la contraction restent dans la "
    + "phrase, juste à côté du trou : « Mes ___ préférés… », « prendre l'___ », "
    + "« ont un ___ ». Jamais « un le », jamais « l'l' ».\n"
    + "3. La réponse est le mot SEUL, en forme de dictionnaire, sans article.\n"
    + "4. Le genre est une étiquette à part : \"m\", \"f\" ou \"\" si ce n'est pas un nom.\n"
    + "5. Vérifie en insérant la réponse dans le trou : la phrase entière doit être "
    + "grammaticale, accords compris.\n"
    + "6. Si la phrase est déjà en français, ne la traduis pas : creuse-la telle quelle.\n"
    + "7. Si la phrase est vide ou sans rapport, écris une phrase courte et naturelle "
    + "qui emploie le mot.\n\n"
    + "Captures :\n"
    + batch.map((c, i) => (i + 1) + ". " + c.w + " | " + (c.s || "(rien)")).join("\n") + "\n\n"
    + "Réponds uniquement par un tableau JSON, un objet par capture, dans l'ordre :\n"
    + '[{"s":"Mes ___ préférés sont mes Apple Pro Max.","a":"écouteurs","g":"m",'
    + '"pl":true,"d":["casseroles","ceintures","cahiers"],"en":"My favourite headphones are my Apple Pro Max."}]\n'
    + "- s : la phrase française avec ___ .\n"
    + "- a : le mot nu, forme de dictionnaire.\n"
    + "- g : \"m\", \"f\" ou \"\".\n"
    + "- pl : true si la phrase l'emploie au pluriel.\n"
    + "- d : 3 distracteurs de même nature, plausibles ailleurs mais faux ici.\n"
    + "- en : la phrase anglaise de départ, telle qu'il l'a dite.";
}

async function capRun(){
  if(!S.sample){ $("cpNote").textContent = PH_ERR.not_granted; return; }
  const rows = csvRows($("cpText").value);
  if(!rows.length){ $("cpNote").textContent = tr("Rien à lire dans ce CSV."); return; }
  CP = {rows, done:0, made:[]};
  $("cpGo").disabled = true;
  await capBatch();
  $("cpGo").disabled = false;
}

async function capBatch(){
  const en = typeof LANG !== "undefined" && LANG === "en";
  const batch = CP.rows.slice(CP.done, CP.done + 10);
  if(!batch.length){
    $("cpNote").textContent = en ? "Every capture has been turned into a card."
      : "Toutes les captures sont devenues des cartes.";
    return;
  }
  $("cpNote").textContent = (en ? "Claude is building cards " : "Claude fabrique les cartes ")
    + (CP.done + 1) + "–" + (CP.done + batch.length) + "…";
  let raw = null;
  try{
    raw = await S.sample.json(capPrompt(batch), {modelTier:"default", cache:false});
  }catch(e){
    $("cpNote").textContent = PH_ERR[(e && e.code)] || PH_ERR.upstream_error;
    return;
  }
  const list = Array.isArray(raw) ? raw : [];
  CP.batch = list.map((c, i) => ({
    s:String(c && c.s || ""), a:String(c && c.a || ""),
    g:(c && c.g === "m") || (c && c.g === "f") ? c.g : "",
    pl:!!(c && c.pl),
    d:(Array.isArray(c && c.d) ? c.d : []).filter(x => typeof x === "string").slice(0, 3),
    en:String(c && c.en || ""), src:batch[i] ? batch[i].w : "", keep:true
  })).filter(c => c.s.includes("___") && c.a);
  CP.done += batch.length;
  capDraw();
}

function capDraw(){
  const en = typeof LANG !== "undefined" && LANG === "en";
  const ul = $("cpList");
  ul.innerHTML = "";
  ul.hidden = !CP.batch.length;
  CP.batch.forEach((c, i) => {
    const li = document.createElement("li");
    const b = document.createElement("button");
    b.className = "sug";
    b.type = "button";
    b.setAttribute("aria-pressed", c.keep ? "true" : "false");
    const chk = document.createElement("span");
    chk.className = "schk"; chk.textContent = "✓";
    const w = document.createElement("span");
    w.className = "sw";
    const fr = document.createElement("span");
    fr.className = "sfr"; fr.textContent = c.s.replace("___", "……");
    const bk = document.createElement("span");
    bk.className = "sen";
    bk.textContent = c.a + (c.g ? " (" + c.g + "." + (c.pl ? " pl." : "") + ")" : "");
    w.append(fr, bk);
    b.append(Object.assign(document.createElement("span"), {className:"spic", textContent:"✎"}), w, chk);
    b.addEventListener("click", () => {
      c.keep = !c.keep;
      b.setAttribute("aria-pressed", c.keep ? "true" : "false");
    });
    li.appendChild(b);
    ul.appendChild(li);
  });
  $("cpAct").hidden = !CP.batch.length;
  $("cpNote").textContent = (en ? "Check each one, then keep what's right. "
    : "Relis, puis garde ce qui est juste. ")
    + CP.done + "/" + CP.rows.length + (en ? " captures read." : " captures lues.");
}

function capKeep(){
  const en = typeof LANG !== "undefined" && LANG === "en";
  const stamp = Date.now().toString(36);
  let n = 0, g = 0;
  CP.batch.filter(c => c.keep).forEach((c, i) => {
    const d = c.d.length === 3 ? c.d : [c.a + "s", "chose", "autre"];
    S.cards = [{id:"q" + stamp + i, s:c.s.replace("___", "___"), a:c.a, d:d,
      g:c.en, src:"capture", lv:S.P.level}].concat(S.cards).slice(0, 150);
    n++;
    if(c.g && typeof motMake === "function"
      && !(S.mots || []).some(m => m.fr === c.a)){
      motMake(c.a, "", c.en.slice(0, 110), c.g, "nom", "capture");
      g++;
    }
  });
  saveCards();
  srsReset();
  if(typeof drawCards === "function") drawCards();
  if(typeof drawMots === "function") drawMots();
  paintMargin();
  CP.batch = [];
  capDraw();
  $("cpNote").textContent = n + (en ? " cards added" : " cartes ajoutées")
    + (g ? (en ? ", " + g + " of them also as word cards." : ", dont " + g + " aussi en cartes de mot.") : ".")
    + (CP.done < CP.rows.length ? (en ? " Build the next ten." : " Enchaîne avec les dix suivantes.") : "");
}

let CP_READY = false;
function capturesInit(){
  if(CP_READY) return;
  CP_READY = true;
  $("cpGo").addEventListener("click", capRun);
  $("cpNext").addEventListener("click", async () => {
    $("cpNext").disabled = true;
    await capBatch();
    $("cpNext").disabled = false;
  });
  $("cpKeep").addEventListener("click", capKeep);
  $("cpFile").addEventListener("change", () => {
    const f = $("cpFile").files && $("cpFile").files[0];
    if(!f) return;
    const r = new FileReader();
    r.onload = () => {
      $("cpText").value = String(r.result || "").slice(0, 60000);
      $("cpNote").textContent = csvRows($("cpText").value).length
        + ((typeof LANG !== "undefined" && LANG === "en") ? " captures read from the file."
          : " captures lues dans le fichier.");
    };
    r.readAsText(f);
  });
  if(!S.sample) $("cpWarn").hidden = false;
}
