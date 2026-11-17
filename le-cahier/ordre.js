/* Le Cahier — L'Ordre : remettre la phrase dans le bon ordre.

   Le trou teste un mot ; ici c'est la phrase entière qui se construit —
   place des mots, accord, pronoms. On ne reconnaît pas une réponse parmi
   quatre : on bâtit, et la structure ne pardonne pas.

   Le retour est immédiat mais avare : un mot posé au bon endroit verdit,
   un mot mal posé jaunit — sans dire où il allait. On peut donc se corriger
   sans que la phrase se résolve toute seule. */

let ORD = null;

const orTok = (s) => String(s || "").trim().split(/\s+/).filter(Boolean);

/* Des phrases ni trop courtes (rien à ordonner) ni trop longues (du bricolage). */
function orPool(){
  return ALL().filter(c => {
    if(!c.s || !c.a) return false;
    const n = orTok(c.s.replace("___", c.a)).length;
    if(n < 4 || n > 14) return false;
    const l = levelOf(c.id);
    return l <= S.P.level && l >= S.P.level - 2;
  });
}

function orShuffle(a){
  const r = a.slice();
  for(let i = r.length - 1; i > 0; i--){ const j = (Math.random() * (i + 1)) | 0; [r[i], r[j]] = [r[j], r[i]]; }
  return r;
}

function orNext(){
  const pool = orPool();
  if(!pool.length){
    $("orNote").textContent = "Aucune phrase à ce niveau pour l'instant.";
    return;
  }
  /* On privilégie ce que la répétition espacée réclame aujourd'hui. */
  const t = typeof srsDay === "function" ? srsDay() : 0;
  const due = pool.filter(c => { const s = S.P.srs["o" + c.id]; return s && s[0] <= t; });
  const fresh = pool.filter(c => !S.P.srs["o" + c.id]);
  const from = due.length ? due : (fresh.length ? fresh : pool);
  const pick = from[(Math.random() * from.length) | 0];

  const text = pick.s.replace("___", pick.a);
  ORD = {
    id:pick.id, srsId:"o" + pick.id, text, gloss:pick.g || "",
    want:orTok(text), placed:[], bank:[], slips:0, helped:false,
    done:false, t0:Date.now()
  };
  ORD.bank = orShuffle(ORD.want.map((w, i) => ({w, k:i})));

  $("orGloss").textContent = "";
  $("orGloss").hidden = true;
  $("orNote").textContent = "";
  $("orNote").className = "note";
  $("orNext").hidden = true;
  $("orCheck").hidden = false;
  $("orHint").hidden = false;
  $("orLv").textContent = LEVELS[Math.max(0, levelOf(pick.id) - 1)];
  orPaint();
}

/* Un mot est juste s'il est à la place qu'il occupe dans la phrase. */
const orRight = (i) => ORD.placed[i] && ORD.placed[i].w === ORD.want[i];

function orPaint(){
  const line = $("orLine");
  line.innerHTML = "";
  ORD.placed.forEach((tk, i) => {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "orchip " + (orRight(i) ? "ok" : "off");
    b.textContent = tk.w;
    b.setAttribute("aria-label", tk.w + (orRight(i) ? " — bien placé" : " — mal placé, clique pour reprendre"));
    if(!ORD.done) b.addEventListener("click", () => orPull(i));
    line.appendChild(b);
  });
  for(let i = ORD.placed.length; i < ORD.want.length; i++){
    const s = document.createElement("span");
    s.className = "orslot";
    line.appendChild(s);
  }

  const bank = $("orBank");
  bank.innerHTML = "";
  ORD.bank.forEach((tk, i) => {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "orchip";
    b.textContent = tk.w;
    if(!ORD.done) b.addEventListener("click", () => orPush(i));
    bank.appendChild(b);
  });

  const n = ORD.placed.filter((_, i) => orRight(i)).length;
  $("orGauge").textContent = n + " / " + ORD.want.length + " en place";
  $("orCheck").disabled = ORD.placed.length !== ORD.want.length;
}

function orPush(i){
  if(ORD.done || ORD.placed.length >= ORD.want.length) return;
  const tk = ORD.bank.splice(i, 1)[0];
  ORD.placed.push(tk);
  if(ORD.placed[ORD.placed.length - 1].w !== ORD.want[ORD.placed.length - 1]) ORD.slips++;
  orPaint();
  /* Phrase complète et entièrement juste : inutile de faire cliquer en plus. */
  if(ORD.placed.length === ORD.want.length && ORD.placed.every((_, k) => orRight(k)))
    setTimeout(() => { if(!ORD.done) orCheck(); }, 120);
}

function orPull(i){
  if(ORD.done) return;
  const tk = ORD.placed.splice(i, 1)[0];
  ORD.bank.push(tk);
  orPaint();
}

function orCheck(){
  if(!ORD || ORD.done) return;
  if(ORD.placed.length !== ORD.want.length){
    $("orNote").textContent = "Place tous les mots d'abord.";
    return;
  }
  ORD.done = true;
  const ok = ORD.placed.every((_, i) => orRight(i));
  const ms = Date.now() - ORD.t0;

  $("orNote").className = "note " + (ok ? "good" : "bad");
  if(ok){
    $("orNote").innerHTML = ORD.slips
      ? "Juste — après " + ORD.slips + " essai" + (ORD.slips > 1 ? "s" : "") + " de placement."
      : "Juste, du premier coup.";
  }else{
    $("orNote").innerHTML = "Pas encore. La phrase était :<br><b>" + ORD.text + "</b>";
  }
  $("orGloss").textContent = ORD.gloss;
  $("orGloss").hidden = !ORD.gloss;
  $("orCheck").hidden = true;
  $("orHint").hidden = true;
  $("orNext").hidden = false;
  $("orNext").focus();
  orPaint();

  /* On entend toujours la phrase juste à la fin : la prosodie fixe l'ordre. */
  if(typeof speakFr === "function") setTimeout(() => speakFr(ORD.text, .95), 220);

  const helped = ORD.helped || ORD.slips > 0;
  const q = typeof srsGrade === "function" ? srsGrade(ok, ms, helped) : (ok ? 4 : 1);
  if(typeof srsUpdate === "function") srsUpdate(ORD.srsId, q);
  if(typeof noteLevel === "function") noteLevel(ORD.id, ok);
  if(typeof scored === "function") scored(ok);
  if(typeof save === "function") save();
}

/* L'indice donne le premier mot manquant, jamais la phrase. */
function orHint(){
  if(!ORD || ORD.done) return;
  const i = ORD.placed.length;
  if(i >= ORD.want.length) return;
  const w = ORD.want[i];
  const j = ORD.bank.findIndex(tk => tk.w === w);
  if(j < 0) return;
  ORD.helped = true;
  const tk = ORD.bank.splice(j, 1)[0];
  ORD.placed.push(tk);
  $("orNote").textContent = "Un mot donné — le rappel compte moins.";
  orPaint();
}

let OR_READY = false;

function ordreInit(){
  if(OR_READY) return (ORD ? orPaint() : orNext());
  OR_READY = true;
  $("orCheck").addEventListener("click", orCheck);
  $("orNext").addEventListener("click", orNext);
  $("orHint").addEventListener("click", orHint);
  $("orHear").addEventListener("click", () => {
    if(!ORD) return;
    ORD.helped = true;
    if(typeof speakFr === "function") speakFr(ORD.text, .9);
    if(!ORD.done) $("orNote").textContent = "Tu l'as entendue — le rappel compte moins.";
  });
  orNext();
}
