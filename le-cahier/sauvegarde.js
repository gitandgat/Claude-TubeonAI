/* Le Cahier — la sauvegarde : tout le cahier dans un fichier, et retour.

   Le planning, le profil, tes cartes de vidéo, ton paquet de mots : un seul
   fichier JSON, lisible, que tu gardes où tu veux. Le compte synchronise
   déjà entre appareils ; le fichier est ce qui reste si le compte, le
   navigateur ou l'artefact disparaissent.

   Trois sorties, de la meilleure à la plus rustique : le téléchargement
   de la plateforme, un lien de téléchargement ordinaire, le presse-papiers.
   Deux entrées : un fichier, ou du texte collé.

   Remplacer efface ce qui est sur cet appareil. Fusionner garde le profil
   d'ici et rapporte les cartes et le planning du fichier — carte par carte,
   c'est l'état le plus travaillé qui gagne. */

const SV_VERSION = 1;
let SV_DL = null;        /* la capacité « downloads », ou false */
let SV_PENDING = null;   /* un cahier lu, en attente de Remplacer / Fusionner */

const svEn = () => typeof LANG !== "undefined" && LANG === "en";

function svPayload(){
  let theme = null, voice = null;
  try{ theme = localStorage.getItem("le-cahier-theme"); voice = localStorage.getItem(VOICE_KEY); }catch(e){}
  return {app:"le-cahier", v:SV_VERSION, at:new Date().toISOString(),
    P:S.P, cards:S.cards || [], mots:S.mots || [],
    motDel:(typeof motDel === "function") ? motDel() : [],
    prefs:{lang:(typeof LANG !== "undefined") ? LANG : "fr", theme, voice}};
}

const svFilename = () => "le-cahier-" + today() + ".json";

function svMark(n){
  S.P.backupAt = Date.now();
  S.P.backupBytes = n;
  save();
  svPaint();
}

async function svDownloads(){
  if(SV_DL !== null) return SV_DL;
  try{
    SV_DL = (window.claude && typeof window.claude.use === "function")
      ? ((await window.claude.use("downloads")) || false) : false;
  }catch(e){ SV_DL = false; }
  return SV_DL;
}

function svReveal(text){
  const en = svEn();
  const ta = $("svRaw");
  ta.value = text;
  $("svRawBox").hidden = false;
  $("svCopy").onclick = async () => {
    try{
      await navigator.clipboard.writeText(text);
      $("svNote").textContent = en ? "Copied. Paste it into a file you keep." : "Copié. Colle-le dans un fichier que tu gardes.";
      svMark(text.length);
    }catch(e){
      ta.focus(); ta.select();
      $("svNote").textContent = en ? "Select the text and copy it yourself." : "Sélectionne le texte et copie-le toi-même.";
    }
  };
}

async function svExport(){
  const en = svEn();
  const note = $("svNote");
  const text = JSON.stringify(svPayload());
  const name = svFilename();
  $("svRawBox").hidden = true;
  note.textContent = en ? "Preparing the file…" : "Préparation du fichier…";

  const dl = await svDownloads();
  if(dl){
    try{
      await dl.save({filename:name, data:text});
      svMark(text.length);
      note.textContent = (en ? "Saved as " : "Enregistré sous ") + name + " · " + Math.round(text.length / 1024) + " Ko.";
      return;
    }catch(e){
      const code = e && e.code;
      if(code === "declined"){ note.textContent = en ? "Export cancelled." : "Export annulé."; return; }
      if(code === "rate_limited"){ note.textContent = en ? "One moment, then try again." : "Un instant, puis réessaie."; return; }
      /* tout autre refus : on passe aux sorties rustiques */
    }
  }

  let linked = false;
  try{
    const url = URL.createObjectURL(new Blob([text], {type:"application/json"}));
    const a = document.createElement("a");
    a.href = url; a.download = name;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(url), 5000);
    linked = true;
  }catch(e){}
  svReveal(text);
  note.textContent = linked
    ? (en ? "A download was offered. If no file appeared, copy the text below instead."
      : "Un téléchargement a été proposé. Si aucun fichier n'apparaît, copie le texte ci-dessous.")
    : (en ? "Copy the text below into a file you keep." : "Copie le texte ci-dessous dans un fichier que tu gardes.");
}

/* ---------- lecture d'un cahier ---------- */
function svRead(text){
  const en = svEn();
  let o = null;
  try{ o = JSON.parse(text); }catch(e){}
  if(!o || o.app !== "le-cahier" || !o.P || typeof o.P !== "object"){
    $("svNote").textContent = en ? "That is not a notebook file." : "Ce n'est pas un fichier du cahier.";
    return;
  }
  const P = hydrate(o.P);
  const cards = asCards(o.cards);
  const mots = Array.isArray(o.mots) ? o.mots.filter(m => m && m.fr && m.id).slice(0, MOT_CAP) : [];
  const del = Array.isArray(o.motDel) ? o.motDel.map(String).slice(-500) : [];
  SV_PENDING = {P, cards, mots, del, at:o.at || "", prefs:o.prefs || {}};

  const srsN = Object.keys(P.srs || {}).length;
  const when = o.at ? String(o.at).slice(0, 10) : (en ? "unknown date" : "date inconnue");
  $("svSummary").textContent = (en
    ? "Notebook from " + when + " · " + srsN + " cards in the schedule · " + mots.length + " words · "
      + cards.length + " of your own sentences · level " + LEVELS[P.level - 1] + " · streak " + P.streak + "."
    : "Cahier du " + when + " · " + srsN + " cartes dans le planning · " + mots.length + " mots · "
      + cards.length + " phrases à toi · niveau " + LEVELS[P.level - 1] + " · série " + P.streak + ".");
  $("svConfirm").hidden = false;
  $("svNote").textContent = en
    ? "Replace wipes this device's notebook. Merge keeps this profile and brings in the file's cards and schedule."
    : "Remplacer efface le cahier de cet appareil. Fusionner garde ce profil et rapporte les cartes et le planning du fichier.";
}

/* Carte par carte : l'état le plus travaillé gagne (plus d'essais, puis l'échéance la plus lointaine). */
function svMergeSrs(a, b){
  const out = {...a};
  Object.keys(b || {}).forEach(id => {
    const x = out[id], y = b[id];
    if(!Array.isArray(y)) return;
    if(!x){ out[id] = y; return; }
    const tx = x[5] || 0, ty = y[5] || 0;
    if(ty > tx || (ty === tx && (y[0] || 0) > (x[0] || 0))) out[id] = y;
  });
  return out;
}

function svApply(mode){
  if(!SV_PENDING) return;
  const en = svEn();
  const f = SV_PENDING;
  if(mode === "replace"){
    S.P = f.P;
    S.cards = f.cards;
    S.mots = f.mots;
    S.motDel = f.del;
  }else{
    const del = new Set((typeof motDel === "function" ? motDel() : []).concat(f.del));
    S.P.srs = svMergeSrs(S.P.srs || {}, f.P.srs || {});
    S.P.hero.xp = Math.max(S.P.hero.xp || 0, (f.P.hero && f.P.hero.xp) || 0);
    S.P.streak = Math.max(S.P.streak || 0, f.P.streak || 0);
    S.P.days = Math.max(S.P.days || 0, f.P.days || 0);
    /* Les pages lues s'additionnent : sinon les cartes du récit deviendraient orphelines. */
    S.P.recit.read = {...((f.P.recit && f.P.recit.read) || {}), ...S.P.recit.read};
    S.P.recall = {rev:(S.P.recall.rev || 0) + (f.P.recall.rev || 0), ok:(S.P.recall.ok || 0) + (f.P.recall.ok || 0)};
    const have = new Set((S.cards || []).map(c => c.id));
    S.cards = (S.cards || []).concat(f.cards.filter(c => !have.has(c.id))).slice(0, 150);
    const byId = {};
    (S.mots || []).forEach(m => { byId[m.id] = m; });
    f.mots.forEach(m => { if(!byId[m.id] || (m.at || 0) > (byId[m.id].at || 0)) byId[m.id] = m; });
    S.mots = Object.values(byId).filter(m => !del.has(m.id))
      .sort((x, y) => (y.at || 0) - (x.at || 0)).slice(0, MOT_CAP);
    S.motDel = [...del].slice(-500);
  }
  SV_PENDING = null;
  $("svConfirm").hidden = true;

  /* tout ce qui dérive du planning repart de zéro */
  srsReset();
  saveCards();
  if(typeof saveMots === "function") saveMots();
  save();
  refillQueue();
  if(typeof drawCards === "function") drawCards();
  if(typeof drawMots === "function") drawMots();
  paintMargin();
  SE = null;                       /* la prochaine séance se reconstruit sur le nouveau planning */
  if(typeof readProfil === "function") readProfil();
  if(typeof paintWeak === "function") paintWeak();
  $("svNote").textContent = mode === "replace"
    ? (en ? "Notebook replaced. Everything now comes from the file." : "Cahier remplacé. Tout vient maintenant du fichier.")
    : (en ? "Merged. The schedule, cards and words are combined." : "Fusionné. Planning, cartes et mots sont réunis.");
  svPaint();
}

function svPaint(){
  const en = svEn();
  const at = S.P.backupAt || 0;
  const srsN = Object.keys(S.P.srs || {}).length;
  const size = Math.round(JSON.stringify(svPayload()).length / 1024);
  let last;
  if(!at) last = en ? "never exported" : "jamais exporté";
  else{
    const d = Math.floor((Date.now() - at) / 864e5);
    last = d === 0 ? (en ? "exported today" : "exporté aujourd'hui")
      : d === 1 ? (en ? "exported yesterday" : "exporté hier")
      : (en ? "exported " + d + " days ago" : "exporté il y a " + d + " jours");
  }
  $("svMeta").textContent = srsN + (en ? " cards in the schedule · " : " cartes dans le planning · ")
    + (S.mots || []).length + (en ? " words · " : " mots · ") + size + " Ko · " + last;
  const stale = srsN > 20 && (!at || Date.now() - at > 14 * 864e5);
  $("svMeta").classList.toggle("stale", stale);
}

let SV_READY = false;
function sauvegardeInit(){
  if(SV_READY) return svPaint();
  SV_READY = true;
  $("svExport").addEventListener("click", svExport);
  $("svFile").addEventListener("change", () => {
    const f = $("svFile").files && $("svFile").files[0];
    if(!f) return;
    const r = new FileReader();
    r.onload = () => { svRead(String(r.result || "")); $("svFile").value = ""; };
    r.readAsText(f);
  });
  $("svPaste").addEventListener("click", () => {
    const t = $("svRaw").value.trim();
    if(!t){ $("svRawBox").hidden = false; $("svRaw").focus();
      $("svNote").textContent = svEn() ? "Paste an exported notebook here first." : "Colle d'abord un cahier exporté ici."; return; }
    svRead(t);
  });
  $("svReplace").addEventListener("click", () => svApply("replace"));
  $("svMerge").addEventListener("click", () => svApply("merge"));
  $("svCancel").addEventListener("click", () => { SV_PENDING = null; $("svConfirm").hidden = true; $("svNote").textContent = ""; });
  svPaint();
}
