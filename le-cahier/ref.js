/* Le Cahier — les références : les tableaux qu'on vient consulter,
   construits à partir des formes que le cahier fait déjà réviser.
   Et les images de phrases, fabriquées une fois pour toutes. */

const REF_TENSES = ["présent", "imparfait", "passé simple", "futur", "conditionnel",
  "subjonctif", "subjonctif imparfait", "participe passé"];
const REF_PEOPLE = ["je", "j'", "tu", "il", "elle", "nous", "vous", "ils"];

function refTable(){
  const by = {};
  (typeof FORMS !== "undefined" ? FORMS : []).forEach(f => {
    const v = by[f.v] = by[f.v] || {};
    const t = v[f.t] = v[f.t] || {};
    t[f.p || "—"] = f.a;
  });
  return by;
}

function refPaint(verb){
  const en = typeof LANG !== "undefined" && LANG === "en";
  const by = refTable();
  const verbs = Object.keys(by).sort((a, b) => a.localeCompare(b, "fr"));
  const sel = document.getElementById("refVerb");
  if(sel && !sel.children.length){
    verbs.forEach(v => {
      const o = document.createElement("option");
      o.value = v; o.textContent = v;
      sel.appendChild(o);
    });
  }
  const v = verb || (sel && sel.value) || verbs[0];
  if(sel) sel.value = v;
  const data = by[v] || {};
  const host = document.getElementById("refBody");
  host.innerHTML = "";

  const tenses = REF_TENSES.filter(t => data[t]);
  if(!tenses.length){
    host.appendChild(Object.assign(document.createElement("p"),
      {className:"lede dim", textContent:en ? "Nothing recorded for this verb yet."
        : "Rien d'enregistré pour ce verbe."}));
    return;
  }

  tenses.forEach(t => {
    const block = document.createElement("div");
    block.style.cssText = "margin:0 0 22px;max-width:460px";
    block.appendChild(Object.assign(document.createElement("p"),
      {className:"fchead", textContent:t, style:"margin:0 0 8px;padding-top:0;border-top:none"}));
    const people = REF_PEOPLE.filter(p => data[t][p]);
    const keys = people.length ? people : Object.keys(data[t]);
    keys.forEach(p => {
      const row = document.createElement("div");
      row.style.cssText = "display:grid;grid-template-columns:4.5em 1fr;gap:12px;"
        + "padding:5px 0;border-bottom:1px dashed var(--border)";
      row.appendChild(Object.assign(document.createElement("span"),
        {textContent:p === "—" ? "" : p,
         style:"font-family:'IBM Plex Mono',monospace;font-size:.72rem;color:var(--ink-faint)"}));
      const f = document.createElement("span");
      f.lang = "fr";
      f.textContent = data[t][p];
      f.style.cssText = "font-size:1.04rem";
      row.appendChild(f);
      block.appendChild(row);
    });
    host.appendChild(block);
  });

  const say = document.getElementById("refSay");
  if(say) say.onclick = () => {
    const first = (data["présent"] && (data["présent"]["je"] || data["présent"]["j'"])) || v;
    if(typeof speakFr === "function") speakFr(first, .9);
  };
}

/* ---------- une image pour chaque phrase ---------- */
async function refScenes(){
  const en = typeof LANG !== "undefined" && LANG === "en";
  const note = document.getElementById("refPicNote");
  if(!S.sample){ note.textContent = (typeof PH_ERR === "object" ? PH_ERR.not_granted : "") ; return; }

  const todo = ALL().filter(c => c.s && c.a && !c.pic).slice(0, 24);
  if(!todo.length){
    note.textContent = en ? "Every sentence already has its picture."
      : "Chaque phrase a déjà son image.";
    return;
  }
  document.getElementById("refPicGo").disabled = true;
  note.textContent = (en ? "Claude is picturing " : "Claude met en image ") + todo.length
    + (en ? " sentences…" : " phrases…");

  let raw = null;
  try{
    raw = await S.sample.json(
      "Pour chaque phrase française, choisis 1 à 3 emoji qui montrent la SCÈNE — "
      + "ce qui se passe, pas chaque mot. Rien d'abstrait : si la phrase ne se montre pas, "
      + "renvoie \"\".\n\n"
      + todo.map((c, i) => (i + 1) + ". " + c.s.replace("___", c.a)).join("\n")
      + "\n\nRéponds uniquement par un tableau JSON de chaînes, dans l'ordre, "
      + 'une par phrase : ["🚆⏱️","🥖🔥",""]',
      {modelTier:"quick", cache:false});
  }catch(e){
    note.textContent = (typeof PH_ERR === "object" && PH_ERR[e && e.code]) || "…";
    document.getElementById("refPicGo").disabled = false;
    return;
  }
  document.getElementById("refPicGo").disabled = false;

  let n = 0;
  (Array.isArray(raw) ? raw : []).forEach((p, i) => {
    const pic = String(p || "").trim().slice(0, 8);
    if(!pic || !todo[i]) return;
    todo[i].pic = pic;
    n++;
  });
  if(typeof saveCards === "function") saveCards();
  const left = ALL().filter(c => c.s && c.a && !c.pic).length;
  note.textContent = n + (en ? " sentences pictured." : " phrases mises en image.")
    + (left ? (en ? " " + left + " left — run it again." : " Il en reste " + left + " — relance.") : "");
}

let REF_READY = false;
function refInit(){
  if(REF_READY) return refPaint();
  REF_READY = true;
  document.getElementById("refVerb").addEventListener("change", () => refPaint());
  document.getElementById("refPicGo").addEventListener("click", refScenes);
  refPaint();
}

/* Comme photo.js, le module se branche seul. */
document.addEventListener("click", (e) => {
  const t = e.target && e.target.closest && e.target.closest('[data-mode="ref"]');
  if(!t) return;
  const p = document.getElementById("panel-ref");
  if(p) p.hidden = false;
  document.querySelectorAll('[id^="panel-"]').forEach(x => {
    if(x.id !== "panel-ref") x.hidden = true;
  });
  document.querySelectorAll(".tab").forEach(x =>
    x.setAttribute("aria-selected", x === t ? "true" : "false"));
  setTimeout(refInit, 60);
});
