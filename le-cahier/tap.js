/* Le Cahier — toucher un mot pour en avoir le sens.
   On cherche d'abord dans ce que le cahier sait déjà, et on ne dérange
   Claude que pour les mots vraiment inconnus. Chaque réponse est gardée. */

const TAP_IN = ".sentence, .story, .bub, .extext, .noun, .clue, .phtask, .scene, .xclue,"
  + " .fiche-mot, .fiche-note, .motpic, .exqt, .sfr, .ckword, .rule, .gloss, .dcorr, .seinput, .nt";

function lexLocal(w){
  const k = w.toLowerCase();
  const m = (S.mots || []).find(x => x.fr.toLowerCase() === k);
  if(m && (m.note || m.en)) return m.note || m.en;
  const g = (typeof GENRE !== "undefined" ? GENRE : []).find(x => x.n.toLowerCase() === k);
  if(g) return g.t;
  const mo = (typeof MOTUS !== "undefined" ? MOTUS : []).find(x => x.w.toLowerCase() === k);
  if(mo) return mo.c;
  const c = (typeof ALL === "function" ? ALL() : []).find(x => x.a && x.a.toLowerCase() === k);
  if(c && c.g) return c.g;
  return null;
}

function tapTip(x, y, text, pending){
  let t = document.getElementById("tapTip");
  if(!t){
    t = document.createElement("div");
    t.id = "tapTip"; t.className = "taptip";
    t.addEventListener("click", (e) => { e.stopPropagation(); t.remove(); });
    document.body.appendChild(t);
  }
  t.textContent = text;
  t.classList.toggle("wait", !!pending);
  const w = Math.min(260, Math.max(120, text.length * 8));
  t.style.width = w + "px";
  t.style.left = Math.max(8, Math.min(window.innerWidth - w - 8, x - w / 2)) + "px";
  t.style.top = (y + window.scrollY + 14) + "px";
  return t;
}

async function tapLook(word, context, x, y){
  const k = word.toLowerCase();
  S.P.lex = S.P.lex || {};
  const known = S.P.lex[k] || lexLocal(word);
  if(known){ tapTip(x, y, word + " — " + known); return; }
  if(!S.sample){ tapTip(x, y, word + " — ?"); return; }
  tapTip(x, y, "…", true);
  try{
    const r = await S.sample.json(
      "Donne le sens anglais de « " + word + " » tel qu'il est employé ici :\n« "
      + String(context || "").slice(0, 300) + " »\n\n"
      + "Réponds uniquement par {\"en\":\"...\"} : deux à six mots d'anglais, pas de phrase, "
      + "pas de guillemets, la forme du dictionnaire.",
      {modelTier:"quick", cache:{gcTime:86400000}});
    const en = String(r && r.en || "").trim().slice(0, 70);
    if(en){
      S.P.lex[k] = en;
      if(Object.keys(S.P.lex).length > 600) delete S.P.lex[Object.keys(S.P.lex)[0]];
      save();
      tapTip(x, y, word + " — " + en);
    }else tapTip(x, y, word + " — ?");
  }catch(e){
    tapTip(x, y, word + " — " + ((e && e.code === "not_granted") ? "?" : "…"));
  }
}

function tapInit(){
  document.addEventListener("click", (ev) => {
    const tip = document.getElementById("tapTip");
    const host = ev.target && ev.target.closest && ev.target.closest(TAP_IN);
    if(!host){ if(tip) tip.remove(); return; }
    if(ev.target.tagName === "INPUT" || ev.target.tagName === "TEXTAREA"
      || ev.target.tagName === "BUTTON") return;

    const pos = document.caretPositionFromPoint
      ? document.caretPositionFromPoint(ev.clientX, ev.clientY)
      : (document.caretRangeFromPoint
        ? (() => { const r = document.caretRangeFromPoint(ev.clientX, ev.clientY);
            return r && {offsetNode:r.startContainer, offset:r.startOffset}; })()
        : null);
    if(!pos || !pos.offsetNode || pos.offsetNode.nodeType !== 3) return;

    const s = pos.offsetNode.nodeValue || "";
    const ok = (ch) => /[a-zà-ÿœ'’-]/i.test(ch);
    let a = pos.offset, b = pos.offset;
    while(a > 0 && ok(s[a - 1])) a--;
    while(b < s.length && ok(s[b])) b++;
    const word = s.slice(a, b).replace(/^[''’-]+|[''’-]+$/g, "");
    if(word.length < 2) return;
    if(tip) tip.remove();
    tapLook(word, host.textContent, ev.clientX, ev.clientY);
  });
}
