/* Le Cahier — choisir sa voix.
   Le cahier prend la meilleure voix française qu'il trouve, mais c'est
   l'oreille qui tranche : on peut en essayer une autre et la garder. */

function voixPaint(){
  const en = typeof LANG !== "undefined" && LANG === "en";
  const sel = document.getElementById("vxPick");
  if(!sel) return;
  const vs = frVoices().slice().sort((a, b) => voiceScore(b) - voiceScore(a));
  const cur = dVoice();
  sel.innerHTML = "";
  if(!vs.length){
    const o = document.createElement("option");
    o.textContent = en ? "No French voice on this device" : "Aucune voix française sur cet appareil";
    sel.appendChild(o);
    sel.disabled = true;
    return;
  }
  sel.disabled = false;
  vs.forEach(v => {
    const o = document.createElement("option");
    o.value = v.voiceURI || v.name;
    o.textContent = v.name + (voiceScore(v) >= 6 ? (en ? "  · better" : "  · meilleure") : "");
    sel.appendChild(o);
  });
  if(cur) sel.value = cur.voiceURI || cur.name;
  const note = document.getElementById("vxNote");
  if(note) note.textContent = cur
    ? (en ? "Now using " : "Voix utilisée : ") + cur.name
    : "";
}

let VX_READY = false;
function voixInit(){
  if(VX_READY) return voixPaint();
  const host = document.getElementById("panel-sons");
  if(!host) return;
  VX_READY = true;
  const en = typeof LANG !== "undefined" && LANG === "en";

  const box = document.createElement("div");
  box.innerHTML =
    '<p class="fchead">' + (en ? "The voice" : "La voix") + "</p>"
    + '<p class="lede dim">' + (en
      ? "Most devices ship an old robotic French voice and a far better one. "
        + "The notebook picks the best it can find — try the others and keep what your ear prefers."
      : "La plupart des appareils ont une vieille voix française métallique et une bien "
        + "meilleure. Le cahier prend la meilleure qu’il trouve — essaie les autres et "
        + "garde celle que ton oreille préfère.") + "</p>"
    + '<div class="mkgrid"><label class="fld"><span>'
    + (en ? "French voice" : "Voix française")
    + '</span><select id="vxPick" class="seinput"></select></label>'
    + '<div class="after"><button class="ghost" id="vxTry">▶ '
    + (en ? "Hear it" : "L’essayer") + "</button></div></div>"
    + '<p class="note" id="vxNote"></p>';
  host.appendChild(box);

  document.getElementById("vxPick").addEventListener("change", () => {
    try{ localStorage.setItem(VOICE_KEY, document.getElementById("vxPick").value); }catch(e){}
    voixPaint();
    synthFr("Dépêche-toi, le train part dans deux minutes.", 1);
  });
  document.getElementById("vxTry").addEventListener("click", () =>
    synthFr("Dépêche-toi, le train part dans deux minutes. Il pleut : prends ton parapluie.", 1));

  voixPaint();
  if("speechSynthesis" in window)
    speechSynthesis.addEventListener("voiceschanged", voixPaint);
}

document.addEventListener("click", (e) => {
  const t = e.target && e.target.closest && e.target.closest('[data-mode="sons"]');
  if(t) setTimeout(voixInit, 140);
});
