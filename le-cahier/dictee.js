/* Le Cahier — la dictée */

let D = null;

const dStrip = (s) => s.normalize("NFD").replace(/[̀-ͯ]/g, "")
  .toLowerCase().replace(/[^a-z0-9]/g, "");
const dBare = (s) => s.toLowerCase().replace(/[^a-zà-ÿœ0-9]/gi, "");
const dTok = (s) => s.trim().split(/\s+/).filter(Boolean);

/* ---------- les phrases enregistrées ----------
   Les quarante phrases du cahier sont lues par une vraie voix française, pas
   par la synthèse. Tout tient dans une seule piste : on s'y déplace au
   décalage voulu, on joue, on s'arrête. Le reste — le vocabulaire, les phrases
   importées d'une vidéo — passe par la synthèse comme avant. */
const VOIX_SRC = "voix.mp3";
/* La carte (VOIX_REC) vit dans voix-map.js. Une entrée à deux nombres pointe
   dans voix.mp3 ; une troisième valeur nomme la piste de la semaine où elle
   se trouve. Une piste par semaine : aucune ne grossit, aucune n'est réencodée. */
const vrEls = {}, vrDead = {}, vrPrep = {};
let vrCur = null, vrTimer = null, vrToken = 0;

/* Chaque lecture a son numéro : une lecture remplacée ne peut plus rien arrêter ni relancer. */
function vrHalt(){
  vrToken++;
  if(vrTimer){ clearTimeout(vrTimer); vrTimer = null; }
  if(vrCur){ try{ vrCur.pause(); }catch(e){} }
}

/* Un élément audio dont la durée est connue, ou un échec. */
function vrLoad(url){
  return new Promise((res, rej) => {
    const a = new Audio();
    a.preload = "auto";
    const off = () => { a.removeEventListener("loadedmetadata", yes); a.removeEventListener("error", no); };
    const yes = () => { off(); res(a); };
    const no = () => { off(); rej(new Error("audio")); };
    a.addEventListener("loadedmetadata", yes);
    a.addEventListener("error", no);
    a.src = url;
    a.load();
  });
}

/* Une piste se charge entière en mémoire (quelques centaines de Ko) : on peut alors s'y
   déplacer n'importe où, même quand le serveur ne sait pas envoyer un morceau de fichier.
   Sans cela, Chrome revient au début de la piste et lit la mauvaise phrase. Si ce
   chargement est refusé, on lit le fichier lui-même ; s'il manque, la synthèse prend le relais. */
function vrPrepare(src){
  if(!vrPrep[src]){
    const direct = () => vrLoad(src);
    /* fetch ne lit pas un fichier local (file://) : là, on lit la piste directement */
    const whole = location.protocol !== "file:" && typeof fetch === "function"
      && typeof URL !== "undefined" && typeof URL.createObjectURL === "function";
    vrPrep[src] = (whole
        ? fetch(src)
          .then(r => { if(!r.ok) throw new Error(String(r.status)); return r.blob(); })
          .then(b => vrLoad(URL.createObjectURL(b)))
          .catch(direct)
        : direct())
      .then(a => (vrEls[src] = a))
      .catch(() => { vrDead[src] = true; return null; });
  }
  return vrPrep[src];
}
const vrAudio = vrPrepare;   /* ancien nom */

/* Rend true si l'enregistrement est pris en charge ; s'il échoue, la synthèse prend le relais
   (fallback). Quand la piste est prête, play() part dans le geste même du clic (certains
   navigateurs refusent un play() qui arrive plus tard), et l'on s'arrête sur la position
   réelle de la lecture, pas sur une minuterie lancée avant la fin du saut dans la piste. */
function vrPlay(seg, rate, fallback){
  const src = (seg && typeof seg[2] === "string" && seg[2]) || VOIX_SRC;
  if(vrDead[src]) return false;
  vrHalt();
  const tok = vrToken;
  if("speechSynthesis" in window) speechSynthesis.cancel();
  const r = Math.max(.5, Math.min(1.25, typeof rate === "number" ? rate : 1));
  const end = seg[0] + seg[1];
  const live = () => tok === vrToken;
  const fail = () => { if(!live()) return; vrHalt(); if(fallback) fallback(); };
  const run = (el) => {
    if(!live()) return;
    vrCur = el;
    const stopAtEnd = () => {
      if(!live()) return;
      if(el.currentTime >= end){ vrHalt(); return; }
      if(!el.paused) requestAnimationFrame(stopAtEnd);
    };
    const onTime = () => {
      if(!live()){ el.removeEventListener("timeupdate", onTime); return; }
      if(el.currentTime >= end){ el.removeEventListener("timeupdate", onTime); vrHalt(); }
    };
    try{
      el.playbackRate = r;
      el.currentTime = seg[0];
      el.addEventListener("playing", () => {
        if(!live()) return;
        requestAnimationFrame(stopAtEnd);
        /* filet : même si l'onglet passe en arrière-plan, la phrase ne déborde pas */
        vrTimer = setTimeout(() => { if(live()) vrHalt(); }, (seg[1] / r) * 1000 + 700);
      }, {once:true});
      el.addEventListener("timeupdate", onTime);
      const p = el.play();
      if(p && p.catch) p.catch(fail);
    }catch(e){ fail(); }
  };
  const ready = vrEls[src];
  if(ready && ready.readyState >= 1) run(ready);
  else vrPrepare(src).then(el => { if(!live()) return; if(el) run(el); else fail(); });
  return true;
}

/* Charger les pistes avant qu'on les demande : la première phrase part sans attendre. */
function vrWarm(){
  if(typeof VOIX_REC === "undefined") return;
  const srcs = new Set([VOIX_SRC]);
  Object.values(VOIX_REC).forEach(seg => {
    const s = seg && typeof seg[2] === "string" ? seg[2] : null;
    if(s && !/^voix-r\d/.test(s)) srcs.add(s);       /* les pistes du récit : à l'ouverture d'une page */
  });
  srcs.forEach(s => vrPrepare(s));
}

/* ---------- la voix de synthèse ----------
   La plupart des appareils ont deux voix françaises : une vieille, métallique,
   et une bien meilleure qu'il faut aller chercher. On classe, on prend la
   meilleure, et on laisse choisir. */
const VOICE_KEY = "le-cahier-voix";

function frVoices(){
  if(!("speechSynthesis" in window)) return [];
  return (speechSynthesis.getVoices() || []).filter(v => /^fr\b|^fr[-_]/i.test(v.lang));
}

/* Plus le score est haut, plus la voix est naturelle. */
function voiceScore(v){
  const n = (v.name || "") + " " + (v.voiceURI || "");
  let k = 0;
  if(/premium|enhanced|neural|natural|siri|google|wavenet|studio/i.test(n)) k += 6;
  if(/eloquence|compact|basic|espeak|pico/i.test(n)) k -= 6;
  if(!v.localService) k += 2;            /* les voix serveur sont souvent meilleures */
  if(/fr[-_]FR/i.test(v.lang)) k += 1;   /* français de France par défaut */
  return k;
}

function dVoice(){
  const vs = frVoices();
  if(!vs.length) return null;
  let want = null;
  try{ want = localStorage.getItem(VOICE_KEY); }catch(e){}
  if(want){
    const hit = vs.find(v => v.voiceURI === want || v.name === want);
    if(hit) return hit;
  }
  return vs.slice().sort((a, b) => voiceScore(b) - voiceScore(a))[0];
}

/* Découper par phrase : l'intonation retombe à chaque point, et les moteurs
   tronquent moins. Une voix qui respire s'entend tout de suite. */
/* Le seul point d'entrée : une phrase enregistrée se joue, le reste se synthétise.
   Tous les panneaux passent par ici, donc tous en profitent. */
function speakFr(text, rate){
  const seg = VOIX_REC[dStrip(String(text || ""))];
  if(seg && vrPlay(seg, rate, () => synthFr(text, rate))) return;
  synthFr(text, rate);
}

/* La liste des voix arrive en retard dans Chrome : avant elle, aucune voix n'est choisie et
   le navigateur lit le français avec sa voix par défaut, souvent anglaise. On attend la
   liste une fois (1,5 s au plus). */
let VOICES_WAIT = null;
function voicesReady(){
  if(!("speechSynthesis" in window)) return Promise.resolve(false);
  if((speechSynthesis.getVoices() || []).length) return Promise.resolve(true);
  if(!VOICES_WAIT){
    VOICES_WAIT = new Promise(res => {
      const done = () => res((speechSynthesis.getVoices() || []).length > 0);
      speechSynthesis.addEventListener("voiceschanged", done, {once:true});
      setTimeout(done, 1500);
    });
  }
  return VOICES_WAIT;
}

let NO_FR_SAID = false;
function noFrenchVoice(){
  if(NO_FR_SAID) return;
  NO_FR_SAID = true;
  const en = typeof LANG !== "undefined" && LANG === "en";
  const t = en ? "No French voice for unrecorded words" : "Pas de voix française pour les mots non enregistrés";
  const s = en ? "Sentences use the recorded voice. For single words, add a French voice in your system settings (Spoken content)."
    : "Les phrases ont la voix enregistrée. Pour les mots seuls, ajoute une voix française dans les réglages du système (Contenu énoncé).";
  if(typeof toast === "function") toast(t, s, "i-sons");
}

function synthFr(text, rate){
  vrHalt();
  if(!("speechSynthesis" in window)) return;
  speechSynthesis.cancel();
  if(!(speechSynthesis.getVoices() || []).length){
    const tok = vrToken;
    voicesReady().then(() => { if(tok === vrToken) synthSpeak(text, rate); });
    return;
  }
  synthSpeak(text, rate);
}

function synthSpeak(text, rate){
  const v = dVoice();
  /* Jamais une voix d'une autre langue pour du français : une prononciation fausse
     apprend une faute. Si l'appareil n'en a aucune, on le dit et on se tait. */
  if(!v && (speechSynthesis.getVoices() || []).length){ noFrenchVoice(); return; }
  const r = typeof rate === "number" ? rate : 1;
  String(text || "")
    .split(/(?<=[.!?…:;])\s+/)
    .flatMap(p => p.length > 180 ? p.split(/(?<=,)\s+/) : [p])
    .map(p => p.trim())
    .filter(Boolean)
    .forEach((part, i) => {
      const u = new SpeechSynthesisUtterance(part);
      if(v) u.voice = v;
      u.lang = (v && v.lang) || "fr-FR";
      /* Un rien plus lent que la vitesse neutre, jamais traînant. */
      u.rate = Math.max(.5, Math.min(1.15, r));
      u.pitch = 1;
      if(i) u.volume = 1;
      speechSynthesis.speak(u);
    });
}

function dSpeak(rate){
  if(!D) return;
  speakFr(D.text, rate);
  D.heard = true;
  $("dNote").textContent = rate < .8 ? "Lecture lente." : "Écoute, puis écris.";
}

/* diff mot à mot */
function dLcs(a, b){
  const n = a.length, m = b.length;
  const dp = Array.from({length:n + 1}, () => new Uint16Array(m + 1));
  for(let i = n - 1; i >= 0; i--) for(let j = m - 1; j >= 0; j--)
    dp[i][j] = a[i] === b[j] ? dp[i + 1][j + 1] + 1 : Math.max(dp[i + 1][j], dp[i][j + 1]);
  const ops = [];
  let i = 0, j = 0;
  while(i < n && j < m){
    if(a[i] === b[j]){ ops.push(["eq", i, j]); i++; j++; }
    else if(dp[i + 1][j] >= dp[i][j + 1]){ ops.push(["del", i, -1]); i++; }
    else { ops.push(["ins", -1, j]); j++; }
  }
  while(i < n){ ops.push(["del", i, -1]); i++; }
  while(j < m){ ops.push(["ins", -1, j]); j++; }

  const out = [];
  for(let k = 0; k < ops.length; k++){
    if(ops[k][0] === "del" && ops[k + 1] && ops[k + 1][0] === "ins"){
      out.push(["sub", ops[k][1], ops[k + 1][2]]); k++;
    }else out.push(ops[k]);
  }
  return out;
}

function dCorrect(){
  if(!D || D.marked) return;
  const exp = dTok(D.text), got = dTok($("dInput").value);
  if(!got.length){ $("dNote").textContent = "Écris d'abord ce que tu entends."; return; }
  D.marked = true;

  const ops = dLcs(exp.map(dStrip), got.map(dStrip));
  const out = $("dCorr");
  out.innerHTML = "";
  let right = 0, accents = 0;

  const add = (tag, cls, txt, title) => {
    const el = document.createElement(tag);
    if(cls) el.className = cls;
    if(title) el.title = title;
    el.textContent = txt;
    out.appendChild(el);
    out.appendChild(document.createTextNode(" "));
  };

  ops.forEach(([kind, i, j]) => {
    if(kind === "eq"){
      const want = exp[i], typed = got[j];
      if(dBare(want) === dBare(typed)){ right++; add("span", "w ok", want); }
      else { accents++; add("span", "w acc", want, "Tu as écrit « " + typed + " » — accent ou majuscule."); }
    }else if(kind === "sub"){
      add("del", "", got[j]);
      add("ins", "", exp[i]);
    }else if(kind === "del"){
      add("ins", "miss", exp[i], "Mot oublié.");
    }else{
      add("del", "", got[j]);
    }
  });

  S.P.dictee.done++;
  S.P.dictee.words += exp.length;
  S.P.dictee.right += right;
  const pct = Math.round(right / exp.length * 100);
  $("dNote").innerHTML = right + " mot" + (right > 1 ? "s" : "") + " sur " + exp.length
    + " — <b>" + pct + "%</b>"
    + (accents ? ". " + accents + " faute" + (accents > 1 ? "s" : "") + " d'accent." : "")
    + (pct === 100 ? " Sans faute." : "");
  $("dGloss").textContent = D.g || "";
  $("dNext").hidden = false;
  $("dCheck").hidden = true;
  $("dNext").focus();
  scored(pct >= 80);
}

function dNext(){
  const pool = ALL().filter(i => i.s && i.a);
  const pick = pool[(Math.random() * pool.length) | 0];
  D = {text:pick.s.replace("___", pick.a), g:pick.g || "", marked:false, heard:false};
  $("dInput").value = "";
  $("dCorr").innerHTML = "";
  $("dGloss").textContent = "";
  $("dNote").textContent = "Appuie sur Écouter quand tu es prêt.";
  $("dNext").hidden = true;
  $("dCheck").hidden = false;
  $("dReveal").hidden = false;
  dWarnCheck();
}

function dicteeInit(){
  $("dPlay").addEventListener("click", () => dSpeak(1));
  $("dSlow").addEventListener("click", () => dSpeak(.7));
  $("dCheck").addEventListener("click", dCorrect);
  $("dNext").addEventListener("click", dNext);
  $("dReveal").addEventListener("click", () => {
    if(D) $("dGloss").textContent = D.g || "Pas de traduction pour cette phrase.";
    $("dReveal").hidden = true;
  });
  $("dInput").addEventListener("keydown", (e) => {
    if(e.key === "Enter" && !e.shiftKey){ e.preventDefault(); D && D.marked ? dNext() : dCorrect(); }
  });

  dNext();
  dWarnCheck();
  if("speechSynthesis" in window) speechSynthesis.addEventListener("voiceschanged", dWarnCheck);
}

function dWarnCheck(){
  {
    /* Les phrases du cahier sont enregistrées : rien à signaler pour celles-là. */
    const rec = D && VOIX_REC[dStrip(String(D.text || ""))];
    if(rec) $("dWarn").hidden = true;
    else if(!("speechSynthesis" in window)){
      $("dWarn").textContent = "Ce navigateur ne lit pas le texte à voix haute. La dictée a besoin d'une voix.";
      $("dWarn").hidden = false;
    }else if(!dVoice()){
      $("dWarn").textContent = "Cette phrase-là n'est pas enregistrée et aucune voix française n'est "
        + "installée — elle sera lue avec l'accent du système. Ajoute une voix française dans les réglages.";
      $("dWarn").hidden = false;
    }else $("dWarn").hidden = true;
  }
}
