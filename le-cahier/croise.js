/* Le Cahier — mots croisés de conjugaison */

const V = (v, rows) => rows.map(([a, p, t]) => ({a, v, p, t}));

const FORMS = [].concat(
  V("être", [["suis","je","présent"],["sommes","nous","présent"],["êtes","vous","présent"],
    ["sont","ils","présent"],["étais","j'","imparfait"],["était","il","imparfait"],
    ["étions","nous","imparfait"],["étaient","ils","imparfait"],["serai","je","futur"],
    ["serons","nous","futur"],["seront","ils","futur"],["serait","il","conditionnel"],
    ["soyons","nous","subjonctif"],["soient","ils","subjonctif"]]),
  V("avoir", [["avons","nous","présent"],["avez","vous","présent"],["avais","j'","imparfait"],
    ["avait","il","imparfait"],["avions","nous","imparfait"],["avaient","ils","imparfait"],
    ["aurai","j'","futur"],["aurons","nous","futur"],["auront","ils","futur"],
    ["aurait","il","conditionnel"],["aurais","j'","conditionnel"],["ayons","nous","subjonctif"],
    ["aient","ils","subjonctif"]]),
  V("aller", [["vais","je","présent"],["allons","nous","présent"],["allez","vous","présent"],
    ["vont","ils","présent"],["allais","j'","imparfait"],["allait","il","imparfait"],
    ["allions","nous","imparfait"],["irai","j'","futur"],["irons","nous","futur"],
    ["iront","ils","futur"],["irait","il","conditionnel"],["irais","j'","conditionnel"],
    ["aille","il","subjonctif"]]),
  V("faire", [["fais","je","présent"],["fait","il","présent"],["faisons","nous","présent"],
    ["faites","vous","présent"],["font","ils","présent"],["faisais","je","imparfait"],
    ["faisait","il","imparfait"],["faisions","nous","imparfait"],["ferai","je","futur"],
    ["ferons","nous","futur"],["feront","ils","futur"],["ferait","il","conditionnel"],
    ["ferais","je","conditionnel"],["fasse","il","subjonctif"],["fassions","nous","subjonctif"]]),
  V("pouvoir", [["peux","je","présent"],["peut","il","présent"],["pouvons","nous","présent"],
    ["pouvez","vous","présent"],["peuvent","ils","présent"],["pouvais","je","imparfait"],
    ["pouvait","il","imparfait"],["pourrai","je","futur"],["pourra","il","futur"],
    ["pourrons","nous","futur"],["pourront","ils","futur"],["pourrait","il","conditionnel"],
    ["pourrais","je","conditionnel"],["puisse","il","subjonctif"]]),
  V("vouloir", [["veux","je","présent"],["veut","il","présent"],["voulons","nous","présent"],
    ["voulez","vous","présent"],["veulent","ils","présent"],["voulais","je","imparfait"],
    ["voulait","il","imparfait"],["voudrai","je","futur"],["voudra","il","futur"],
    ["voudrons","nous","futur"],["voudront","ils","futur"],["voudrait","il","conditionnel"],
    ["voulu","","participe passé"],["veuille","il","subjonctif"]]),
  V("devoir", [["dois","je","présent"],["doit","il","présent"],["devons","nous","présent"],
    ["devez","vous","présent"],["doivent","ils","présent"],["devais","je","imparfait"],
    ["devait","il","imparfait"],["devrai","je","futur"],["devra","il","futur"],
    ["devrait","il","conditionnel"],["devrais","je","conditionnel"],["doive","il","subjonctif"]]),
  V("savoir", [["sais","je","présent"],["sait","il","présent"],["savons","nous","présent"],
    ["savez","vous","présent"],["savent","ils","présent"],["savais","je","imparfait"],
    ["savait","il","imparfait"],["saurai","je","futur"],["saura","il","futur"],
    ["saurait","il","conditionnel"],["saurais","je","conditionnel"],["sache","il","subjonctif"],
    ["sachions","nous","subjonctif"]]),
  V("voir", [["vois","je","présent"],["voit","il","présent"],["voyons","nous","présent"],
    ["voyez","vous","présent"],["voient","ils","présent"],["voyais","je","imparfait"],
    ["voyait","il","imparfait"],["verrai","je","futur"],["verra","il","futur"],
    ["verrons","nous","futur"],["verront","ils","futur"],["verrait","il","conditionnel"],
    ["verrais","je","conditionnel"],["voie","il","subjonctif"]]),
  V("venir", [["viens","je","présent"],["vient","il","présent"],["venons","nous","présent"],
    ["venez","vous","présent"],["viennent","ils","présent"],["venais","je","imparfait"],
    ["venait","il","imparfait"],["viendrai","je","futur"],["viendra","il","futur"],
    ["viendront","ils","futur"],["viendrait","il","conditionnel"],["venu","","participe passé"],
    ["vienne","il","subjonctif"]]),
  V("prendre", [["prends","je","présent"],["prend","il","présent"],["prenons","nous","présent"],
    ["prenez","vous","présent"],["prennent","ils","présent"],["prenais","je","imparfait"],
    ["prenait","il","imparfait"],["prenions","nous","imparfait"],["prendrai","je","futur"],
    ["prendra","il","futur"],["prendrait","il","conditionnel"],["pris","","participe passé"],
    ["prenne","il","subjonctif"]]),
  V("mettre", [["mets","je","présent"],["mettons","nous","présent"],["mettez","vous","présent"],
    ["mettent","ils","présent"],["mettais","je","imparfait"],["mettait","il","imparfait"],
    ["mettrai","je","futur"],["mettra","il","futur"],["mettrait","il","conditionnel"],
    ["mette","il","subjonctif"]]),
  V("dire", [["disons","nous","présent"],["dites","vous","présent"],["disent","ils","présent"],
    ["disais","je","imparfait"],["disait","il","imparfait"],["disions","nous","imparfait"],
    ["dirai","je","futur"],["dira","il","futur"],["diront","ils","futur"],
    ["dirait","il","conditionnel"],["dise","il","subjonctif"]]),
  V("partir", [["pars","je","présent"],["part","il","présent"],["partons","nous","présent"],
    ["partez","vous","présent"],["partent","ils","présent"],["partais","je","imparfait"],
    ["partait","il","imparfait"],["partirai","je","futur"],["partira","il","futur"],
    ["parti","","participe passé"],["parte","il","subjonctif"]]),
  V("sortir", [["sors","je","présent"],["sort","il","présent"],["sortons","nous","présent"],
    ["sortez","vous","présent"],["sortent","ils","présent"],["sortais","je","imparfait"],
    ["sortait","il","imparfait"],["sortions","nous","imparfait"],["sortirai","je","futur"],
    ["sortira","il","futur"],["sorti","","participe passé"],["sorte","il","subjonctif"]]),
  V("dormir", [["dors","je","présent"],["dort","il","présent"],["dormons","nous","présent"],
    ["dormez","vous","présent"],["dorment","ils","présent"],["dormais","je","imparfait"],
    ["dormait","il","imparfait"],["dormirai","je","futur"],["dormi","","participe passé"]]),
  V("finir", [["finis","je","présent"],["finit","il","présent"],["finissons","nous","présent"],
    ["finissez","vous","présent"],["finissent","ils","présent"],["finissais","je","imparfait"],
    ["finissait","il","imparfait"],["finirai","je","futur"],["finira","il","futur"],
    ["fini","","participe passé"],["finisse","il","subjonctif"]]),
  V("parler", [["parle","je","présent"],["parles","tu","présent"],["parlons","nous","présent"],
    ["parlez","vous","présent"],["parlent","ils","présent"],["parlais","je","imparfait"],
    ["parlait","il","imparfait"],["parlions","nous","imparfait"],["parlaient","ils","imparfait"],
    ["parlerai","je","futur"],["parlera","il","futur"],["parleront","ils","futur"],
    ["parlerait","il","conditionnel"],["parlé","","participe passé"]]),
  V("manger", [["mange","je","présent"],["manges","tu","présent"],["mangeons","nous","présent"],
    ["mangez","vous","présent"],["mangent","ils","présent"],["mangeais","je","imparfait"],
    ["mangeait","il","imparfait"],["mangerai","je","futur"],["mangera","il","futur"],
    ["mangé","","participe passé"]]),
  V("acheter", [["achète","j'","présent"],["achetons","nous","présent"],["achetez","vous","présent"],
    ["achètent","ils","présent"],["achetais","j'","imparfait"],["achèterai","j'","futur"],
    ["acheté","","participe passé"]]),
  V("écrire", [["écris","j'","présent"],["écrit","il","présent"],["écrivons","nous","présent"],
    ["écrivez","vous","présent"],["écrivent","ils","présent"],["écrivais","j'","imparfait"],
    ["écrivait","il","imparfait"],["écrirai","j'","futur"],["écrira","il","futur"]]),
  V("lire", [["lisons","nous","présent"],["lisez","vous","présent"],["lisent","ils","présent"],
    ["lisais","je","imparfait"],["lisait","il","imparfait"],["lisions","nous","imparfait"],
    ["lirai","je","futur"],["lirons","nous","futur"],["lise","il","subjonctif"]]),
  V("boire", [["bois","je","présent"],["boit","il","présent"],["buvons","nous","présent"],
    ["buvez","vous","présent"],["boivent","ils","présent"],["buvais","je","imparfait"],
    ["buvait","il","imparfait"],["boirai","je","futur"],["boira","il","futur"],
    ["boive","il","subjonctif"]]),
  V("croire", [["crois","je","présent"],["croit","il","présent"],["croyons","nous","présent"],
    ["croyez","vous","présent"],["croient","ils","présent"],["croyais","je","imparfait"],
    ["croyait","il","imparfait"],["croirai","je","futur"],["croie","il","subjonctif"]]),
  V("vivre", [["vivons","nous","présent"],["vivez","vous","présent"],["vivent","ils","présent"],
    ["vivais","je","imparfait"],["vivait","il","imparfait"],["vivrai","je","futur"],
    ["vivra","il","futur"],["vécu","","participe passé"]]),
  V("suivre", [["suit","il","présent"],["suivons","nous","présent"],["suivez","vous","présent"],
    ["suivent","ils","présent"],["suivais","je","imparfait"],["suivait","il","imparfait"],
    ["suivrai","je","futur"],["suivi","","participe passé"]]),
  V("ouvrir", [["ouvre","j'","présent"],["ouvres","tu","présent"],["ouvrons","nous","présent"],
    ["ouvrez","vous","présent"],["ouvrent","ils","présent"],["ouvrais","j'","imparfait"],
    ["ouvrait","il","imparfait"],["ouvrirai","j'","futur"],["ouvert","","participe passé"]]),
  V("tenir", [["tiens","je","présent"],["tient","il","présent"],["tenons","nous","présent"],
    ["tenez","vous","présent"],["tiennent","ils","présent"],["tiendrai","je","futur"],
    ["tiendra","il","futur"],["tenu","","participe passé"]]),
  V("recevoir", [["reçois","je","présent"],["reçoit","il","présent"],["recevons","nous","présent"],
    ["recevez","vous","présent"],["reçoivent","ils","présent"],["recevrai","je","futur"],
    ["reçu","","participe passé"]]),
  V("connaître", [["connais","je","présent"],["connaît","il","présent"],["connu","","participe passé"]]),

  /* C1 — le passé simple : on ne le parle pas, on le lit partout */
  V("être", [["fus","je","passé simple"],["fut","il","passé simple"],["furent","ils","passé simple"]]),
  V("avoir", [["eus","j'","passé simple"],["eut","il","passé simple"],["eurent","ils","passé simple"]]),
  V("faire", [["fis","je","passé simple"],["fit","il","passé simple"],["firent","ils","passé simple"]]),
  V("aller", [["allai","j'","passé simple"],["alla","il","passé simple"],["allèrent","ils","passé simple"]]),
  V("venir", [["vins","je","passé simple"],["vint","il","passé simple"],["vinrent","ils","passé simple"]]),
  V("prendre", [["pris","je","passé simple"],["prit","il","passé simple"],["prirent","ils","passé simple"]]),
  V("voir", [["vis","je","passé simple"],["vit","il","passé simple"],["virent","ils","passé simple"]]),
  V("dire", [["dis","je","passé simple"],["dit","il","passé simple"],["dirent","ils","passé simple"]]),
  V("pouvoir", [["pus","je","passé simple"],["put","il","passé simple"],["purent","ils","passé simple"]]),
  V("vouloir", [["voulus","je","passé simple"],["voulut","il","passé simple"],["voulurent","ils","passé simple"]]),
  V("savoir", [["sus","je","passé simple"],["sut","il","passé simple"],["surent","ils","passé simple"]]),
  V("écrire", [["écrivis","j'","passé simple"],["écrivit","il","passé simple"],["écrivirent","ils","passé simple"]]),
  V("parler", [["parlai","je","passé simple"],["parla","il","passé simple"],["parlèrent","ils","passé simple"]]),
  V("finir", [["finis","je","passé simple"],["finit","il","passé simple"],["finirent","ils","passé simple"]]),

  /* C2 — le subjonctif imparfait : littéraire, mais c'est là que la langue finit */
  V("être", [["fusse","je","subjonctif imparfait"],["fût","il","subjonctif imparfait"],
    ["fussent","ils","subjonctif imparfait"]]),
  V("avoir", [["eusse","j'","subjonctif imparfait"],["eût","il","subjonctif imparfait"],
    ["eussent","ils","subjonctif imparfait"]]),
  V("faire", [["fisse","je","subjonctif imparfait"],["fît","il","subjonctif imparfait"],
    ["fissent","ils","subjonctif imparfait"]]),
  V("venir", [["vinsse","je","subjonctif imparfait"],["vînt","il","subjonctif imparfait"],
    ["vinssent","ils","subjonctif imparfait"]]),
  V("savoir", [["susse","je","subjonctif imparfait"],["sût","il","subjonctif imparfait"],
    ["sussent","ils","subjonctif imparfait"]]),
  V("pouvoir", [["pusse","je","subjonctif imparfait"],["pût","il","subjonctif imparfait"],
    ["pussent","ils","subjonctif imparfait"]]),
  V("prendre", [["prisse","je","subjonctif imparfait"],["prît","il","subjonctif imparfait"],
    ["prissent","ils","subjonctif imparfait"]]),
  V("parler", [["parlasse","je","subjonctif imparfait"],["parlât","il","subjonctif imparfait"],
    ["parlassent","ils","subjonctif imparfait"]])
);

const noAcc = (s) => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toUpperCase();
const POOL = FORMS.map(f => ({...f, w:noAcc(f.a)}))
  .filter(f => /^[A-Z]{4,10}$/.test(f.w))
  .map((f, n) => ({...f, n}));

let X = null;

/* ---------- génération ---------- */
function shuffled(a){
  const r = a.slice();
  for(let i = r.length - 1; i > 0; i--){ const j = (Math.random() * (i + 1)) | 0; [r[i], r[j]] = [r[j], r[i]]; }
  return r;
}

function canPlace(g, w, r, c, dir){
  const H = g.length, W = g[0].length;
  const dr = dir === "v" ? 1 : 0, dc = dir === "h" ? 1 : 0;
  const er = r + dr * (w.length - 1), ec = c + dc * (w.length - 1);
  if(r < 0 || c < 0 || er >= H || ec >= W) return -1;
  if(r - dr >= 0 && c - dc >= 0 && g[r - dr][c - dc]) return -1;
  if(er + dr < H && ec + dc < W && g[er + dr][ec + dc]) return -1;
  let cross = 0;
  for(let i = 0; i < w.length; i++){
    const rr = r + dr * i, cc = c + dc * i, cur = g[rr][cc];
    if(cur){ if(cur !== w[i]) return -1; cross++; continue; }
    if(dir === "h"){
      if(rr > 0 && g[rr - 1][cc]) return -1;
      if(rr < H - 1 && g[rr + 1][cc]) return -1;
    }else{
      if(cc > 0 && g[rr][cc - 1]) return -1;
      if(cc < W - 1 && g[rr][cc + 1]) return -1;
    }
  }
  return cross;
}

function put(g, w, r, c, dir){
  for(let i = 0; i < w.length; i++) g[r + (dir === "v" ? i : 0)][c + (dir === "h" ? i : 0)] = w[i];
}

/* ---------- la grille de vocabulaire ----------
   Les mots viennent de ton paquet, pas d'une liste à part : ce que tu as
   mis dans tes cartes, tu le retrouves ici, avec son image pour définition. */
function vocabPool(){
  const out = [], seen = new Set();
  const add = (a, clue, pic, sid) => {
    const w = noAcc(a);
    if(!/^[A-Z]{3,11}$/.test(w) || seen.has(w)) return;
    seen.add(w);
    out.push({w, a, clue:clue || "", pic:pic || "", sid:sid || null, vocab:true});
  };
  (S.mots || []).forEach(m => add(m.fr, m.note || "", m.pic || "", "wp_" + m.id));
  (typeof GENRE !== "undefined" ? GENRE : []).forEach((g, n) =>
    add(g.n, g.t, typeof picOf === "function" ? picOf(g.n) : "", "g" + n));
  (typeof MOTUS !== "undefined" ? MOTUS : []).forEach(m =>
    add(m.w.toLowerCase(), m.c, typeof picOf === "function" ? picOf(m.w) : "", null));
  return out;
}

const gridPool = () => (X && X.mode === "vocab") ? vocabPool() : POOL;

function makeGrid(pool){
  pool = pool && pool.length ? pool : POOL;
  const N = 15;
  let best = null;
  for(let attempt = 0; attempt < 30; attempt++){
    const seen = new Set(), words = [];
    for(const f of shuffled(pool)){
      if(seen.has(f.w)) continue;
      seen.add(f.w); words.push(f);
      if(words.length >= 44) break;
    }
    words.sort((a, b) => b.w.length - a.w.length);
    const g = Array.from({length:N}, () => Array(N).fill(""));
    const first = words.shift();
    const r0 = N >> 1, c0 = (N - first.w.length) >> 1;
    put(g, first.w, r0, c0, "h");
    const placed = [{...first, r:r0, c:c0, dir:"h"}];

    for(const f of words){
      if(placed.length >= 11) break;
      let spot = null;
      for(const p of placed){
        for(let i = 0; i < p.w.length; i++){
          for(let j = 0; j < f.w.length; j++){
            if(p.w[i] !== f.w[j]) continue;
            const dir = p.dir === "h" ? "v" : "h";
            const r = p.dir === "h" ? p.r - j : p.r + i;
            const c = p.dir === "h" ? p.c + i : p.c - j;
            const sc = canPlace(g, f.w, r, c, dir);
            if(sc > 0 && (!spot || sc > spot.sc)) spot = {r, c, dir, sc};
          }
        }
      }
      if(spot){ put(g, f.w, spot.r, spot.c, spot.dir); placed.push({...f, r:spot.r, c:spot.c, dir:spot.dir}); }
    }
    if(!best || placed.length > best.placed.length) best = {g, placed};
    if(best.placed.length >= 9) break;
  }
  return trim(best);
}

function trim({g, placed}){
  let r0 = 99, c0 = 99, r1 = -1, c1 = -1;
  g.forEach((row, r) => row.forEach((v, c) => {
    if(!v) return;
    r0 = Math.min(r0, r); c0 = Math.min(c0, c); r1 = Math.max(r1, r); c1 = Math.max(c1, c);
  }));
  return {
    g:g.slice(r0, r1 + 1).map(row => row.slice(c0, c1 + 1)),
    placed:placed.map(p => ({...p, r:p.r - r0, c:p.c - c0}))
  };
}

function numberGrid(g, placed){
  const H = g.length, W = g[0].length, nums = {}, entries = [];
  let n = 0;
  for(let r = 0; r < H; r++) for(let c = 0; c < W; c++){
    if(!g[r][c]) continue;
    const sh = (c === 0 || !g[r][c - 1]) && c + 1 < W && g[r][c + 1];
    const sv = (r === 0 || !g[r - 1][c]) && r + 1 < H && g[r + 1][c];
    if(sh || sv) nums[r + "," + c] = ++n;
    for(const dir of ["h", "v"]){
      if(dir === "h" ? !sh : !sv) continue;
      const src = placed.find(p => p.r === r && p.c === c && p.dir === dir);
      if(src) entries.push({n, r, c, dir, w:src.w, a:src.a, v:src.v, p:src.p, t:src.t, k:src.n,
        vocab:src.vocab, clue:src.clue, pic:src.pic, sid:src.sid});
    }
  }
  return {nums, entries};
}

/* ---------- rendu ---------- */
function cellsOf(e){
  const out = [];
  for(let i = 0; i < e.w.length; i++) out.push([e.r + (e.dir === "v" ? i : 0), e.c + (e.dir === "h" ? i : 0)]);
  return out;
}

function drawCroise(){
  const host = $("xGrid");
  host.innerHTML = "";
  host.style.gridTemplateColumns = "repeat(" + X.g[0].length + ", var(--xc))";
  X.inputs = {};
  X.g.forEach((row, r) => row.forEach((v, c) => {
    if(!v){ host.appendChild(Object.assign(document.createElement("div"), {className:"xblock"})); return; }
    const box = document.createElement("div");
    box.className = "xcell";
    const num = X.nums[r + "," + c];
    if(num){
      const s = document.createElement("span");
      s.className = "xnum"; s.textContent = num;
      box.appendChild(s);
    }
    const inp = document.createElement("input");
    inp.id = "x-" + r + "-" + c;
    inp.maxLength = 1; inp.autocomplete = "off"; inp.autocapitalize = "characters";
    inp.setAttribute("aria-label", "ligne " + (r + 1) + ", colonne " + (c + 1));
    inp.addEventListener("focus", () => select(r, c, false));
    inp.addEventListener("pointerdown", () => { if(document.activeElement === inp) select(r, c, true); });
    inp.addEventListener("input", () => onType(r, c, inp));
    inp.addEventListener("keydown", (ev) => onKey(ev, r, c, inp));
    box.appendChild(inp);
    X.inputs[r + "," + c] = inp;
    host.appendChild(box);
  }));
  drawClues();
  highlight();
}

function clueText(e){
  if(e.vocab){
    const pic = e.pic ? '<span class="picsm">' + e.pic + "</span> " : "";
    return pic + (e.clue ? e.clue : "<i>" + (e.a || "").length + " lettres</i>");
  }
  const p = typeof picOf === "function" ? picOf(e.v) : "";
  return (p ? '<span class="picsm">' + p + "</span> " : "")
    + "<b>" + e.v + "</b> · " + (e.p ? e.p + " · " + e.t : e.t);
}

function drawClues(){
  [["h", "xAcross"], ["v", "xDown"]].forEach(([dir, id]) => {
    const ul = $(id);
    ul.innerHTML = "";
    X.entries.filter(e => e.dir === dir).sort((a, b) => a.n - b.n).forEach(e => {
      const li = document.createElement("li");
      li.dataset.key = e.n + e.dir;
      li.innerHTML = "<span class=\"xn\">" + e.n + "</span> " + clueText(e);
      li.addEventListener("click", () => {
        X.dir = dir;
        const inp = X.inputs[e.r + "," + e.c];
        if(inp) inp.focus();
      });
      ul.appendChild(li);
    });
  });
}

function entryAt(r, c, dir){
  return X.entries.find(e => e.dir === dir && cellsOf(e).some(([a, b]) => a === r && b === c));
}

function select(r, c, toggle){
  if(toggle){
    const other = X.dir === "h" ? "v" : "h";
    if(entryAt(r, c, other)) X.dir = other;
  }
  if(!entryAt(r, c, X.dir)) X.dir = X.dir === "h" ? "v" : "h";
  X.at = [r, c];
  highlight();
}

function highlight(){
  Object.values(X.inputs).forEach(i => i.classList.remove("act", "cur"));
  document.querySelectorAll("#xAcross li, #xDown li").forEach(li => li.classList.remove("act"));
  if(!X.at) return;
  const e = entryAt(X.at[0], X.at[1], X.dir);
  if(!e) return;
  cellsOf(e).forEach(([r, c]) => X.inputs[r + "," + c].classList.add("act"));
  X.inputs[X.at[0] + "," + X.at[1]].classList.add("cur");
  const li = document.querySelector("[data-key=\"" + e.n + e.dir + "\"]");
  if(li) li.classList.add("act");
  $("xClue").innerHTML = e.n + " " + (e.dir === "h" ? "horizontal" : "vertical") + " — " + clueText(e);
}

function step(r, c, d){
  const e = entryAt(r, c, X.dir);
  if(!e) return null;
  const cells = cellsOf(e);
  const i = cells.findIndex(([a, b]) => a === r && b === c) + d;
  return (i >= 0 && i < cells.length) ? cells[i] : null;
}

function onType(r, c, inp){
  const ch = noAcc(inp.value).replace(/[^A-Z]/g, "").slice(-1);
  inp.value = ch;
  inp.classList.remove("err", "ok");
  if(!ch) return;

  if(X.live){
    const good = ch === X.g[r][c];
    inp.classList.add(good ? "ok" : "err");
    if(!good){
      X.bad[r + "," + c] = 1;
      $("xNote").textContent = "Cette lettre-là ne va pas.";
      return;
    }
    $("xNote").textContent = "";
  }
  const nx = step(r, c, 1);
  if(nx) X.inputs[nx[0] + "," + nx[1]].focus();
  if(Object.values(X.inputs).every(i => i.value)) verify(true);
}

function onKey(ev, r, c, inp){
  const moves = {ArrowRight:["h", 1], ArrowLeft:["h", -1], ArrowDown:["v", 1], ArrowUp:["v", -1]};
  if(ev.key === "Backspace" && !inp.value){
    const pv = step(r, c, -1);
    if(pv){ ev.preventDefault(); const p = X.inputs[pv[0] + "," + pv[1]]; p.value = ""; p.classList.remove("err", "ok"); p.focus(); }
    return;
  }
  if(moves[ev.key]){
    ev.preventDefault();
    const [dir, d] = moves[ev.key];
    if(X.dir !== dir && entryAt(r, c, dir)){ X.dir = dir; highlight(); return; }
    const nx = step(r, c, d);
    if(nx) X.inputs[nx[0] + "," + nx[1]].focus();
  }
}

/* ---------- vérification ---------- */
function verify(auto){
  let wrong = 0, filled = 0;
  Object.entries(X.inputs).forEach(([key, inp]) => {
    const [r, c] = key.split(",").map(Number);
    if(!inp.value){ inp.classList.remove("err", "ok"); return; }
    filled++;
    const ok = inp.value === X.g[r][c];
    inp.classList.toggle("err", !ok);
    inp.classList.toggle("ok", ok);
    if(!ok) wrong++;
  });
  const total = Object.keys(X.inputs).length;
  if(filled === total && !wrong){
    if(!X.done){
      X.done = true;
      const slips = Object.keys(X.bad).length;
      S.P.croise.done++;
      X.entries.forEach(e => {
        const id = e.vocab ? e.sid : (e.k == null ? null : "k" + e.k);
        if(!id) return;
        const fumbled = cellsOf(e).some(([r, c]) => X.bad[r + "," + c]);
        srsUpdate(id, srsGrade(!fumbled, 0, X.live));
        noteLevel(id, !fumbled);
      });
      if(typeof xpGain === "function") xpGain(slips ? 25 : 45, "grid");
      paintMargin();
      scored(!slips);
      $("xNote").textContent = slips
        ? "Grille finie — " + slips + " lettre" + (slips > 1 ? "s" : "") + " reprise"
          + (slips > 1 ? "s" : "") + " en route. Ces formes-là reviendront plus tôt."
        : "Grille finie, sans une reprise.";
    }
    return;
  }
  if(auto) $("xNote").textContent = wrong + " lettre" + (wrong > 1 ? "s" : "") + " à revoir.";
  else $("xNote").textContent = filled === 0 ? "Rien à vérifier pour l'instant."
    : wrong ? wrong + " lettre" + (wrong > 1 ? "s" : "") + " en rouge." : "Juste jusqu'ici. Continue.";
}

function revealLetter(){
  if(!X.at) return;
  const e = entryAt(X.at[0], X.at[1], X.dir);
  if(!e) return;
  const miss = cellsOf(e).find(([r, c]) => X.inputs[r + "," + c].value !== X.g[r][c]);
  if(!miss){ $("xNote").textContent = "Cette forme est déjà juste."; return; }
  const inp = X.inputs[miss[0] + "," + miss[1]];
  inp.value = X.g[miss[0]][miss[1]];
  inp.classList.remove("err"); inp.classList.add("ok");
  $("xNote").textContent = "Une lettre donnée — " + e.v + " à l'" + e.t + ".";
  if(Object.values(X.inputs).every(i => i.value)) verify(true);
}

function newCroise(mode){
  const m = typeof mode === "string" ? mode : (X && X.mode) || "conj";
  const pool = m === "vocab" ? vocabPool() : POOL;
  const en = typeof LANG !== "undefined" && LANG === "en";
  if(m === "vocab" && pool.length < 8){
    $("xNote").textContent = en
      ? "Not enough words in your deck yet — add a theme from the base deck first."
      : "Pas encore assez de mots dans ton paquet — ajoute un thème du socle d'abord.";
    return;
  }
  const built = makeGrid(pool);
  const {nums, entries} = numberGrid(built.g, built.placed);
  X = {g:built.g, nums, entries, inputs:{}, dir:"h", at:null, done:false,
    bad:{}, live:$("xLive").checked, mode:m};
  $("xNote").textContent = "";
  drawCroise();
  const first = X.entries.find(e => e.dir === "h");
  if(first) select(first.r, first.c, false);
}

function croiseInit(){
  /* Le choix de grille : conjugaison ou vocabulaire. */
  const bar = document.createElement("div");
  bar.className = "chips";
  bar.style.margin = "0 0 14px";
  [["conj", "Conjugaison", "Conjugation"], ["vocab", "Vocabulaire", "Vocabulary"]].forEach(([k, fr, en]) => {
    const b = document.createElement("button");
    b.type = "button";
    b.className = "chip" + (k === "conj" ? " on" : "");
    b.textContent = (typeof LANG !== "undefined" && LANG === "en") ? en : fr;
    b.addEventListener("click", () => {
      [...bar.children].forEach(c => c.classList.toggle("on", c === b));
      newCroise(k);
    });
    bar.appendChild(b);
  });
  const board = document.querySelector("#panel-croise .xboard");
  if(board && board.parentNode) board.parentNode.insertBefore(bar, board);

  $("xNew").addEventListener("click", () => newCroise());
  $("xLive").addEventListener("change", () => {
    if(X) X.live = $("xLive").checked;
    $("xNote").textContent = $("xLive").checked
      ? "Chaque lettre est jugée en direct."
      : "Plus de correction en direct : il faudra vérifier toi-même.";
  });
  $("xCheck").addEventListener("click", () => verify(false));
  $("xHint").addEventListener("click", revealLetter);
  newCroise();
}
