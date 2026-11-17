/* Le Cahier — de vraies photos sur les cartes.
   L'image part dans le magasin de l'artefact ; la carte ne garde que son
   identifiant, et le paquet reste léger. */

let PHO = null;

const photoUrl = (id) => "/_blob/" + id;

const PHO_ERR = {
  too_large:["Photo trop lourde (20 Mo maximum).", "Photo too large (20 MB max)."],
  unsupported_type:["Ce format ne passe pas — JPEG, PNG, WebP ou GIF.",
    "That format isn't accepted — JPEG, PNG, WebP or GIF."],
  quota_or_state:["Le magasin de photos est plein.", "The photo store is full."],
  rate_limited:["Trop d'envois d'affilée. Attends un instant.", "Too many uploads. Wait a moment."],
  not_granted:["Tu n'as pas autorisé l'envoi de photos ici.", "Photo upload isn't allowed here."],
  store_unavailable:["Le magasin n'a pas répondu. Réessaie.", "The store didn't answer. Try again."]
};

async function photoStore(){
  if(PHO !== null) return PHO;
  const c = window.claude;
  if(!c || typeof c.use !== "function"){ PHO = false; return false; }
  try{ PHO = (await c.use("assets")) || false; }catch(e){ PHO = false; }
  return PHO;
}

/* Une carte, mot ou phrase : toutes deux peuvent porter une vraie photo. */
function photoCards(){
  const out = [];
  (S.mots || []).forEach(m => out.push({kind:"mot", id:m.id, o:m,
    label:(m.pic ? m.pic + " " : "") + m.fr}));
  (typeof ALL === "function" ? ALL() : []).forEach(c => {
    if(!c.s || !c.a) return;
    out.push({kind:"phrase", id:c.id, o:c, label:c.s.replace("___", "……").slice(0, 58)});
  });
  return out;
}

const photoFind = (id) => photoCards().find(x => x.id === id) || null;

function photoSave(kind){
  if(kind === "mot"){ if(typeof saveMots === "function") saveMots(); }
  else if(typeof saveCards === "function") saveCards();
}

function photoPaint(){
  const en = typeof LANG !== "undefined" && LANG === "en";
  const sel = document.getElementById("phoPick");
  if(!sel) return;
  const keep = sel.value;
  sel.innerHTML = "";
  const cards = photoCards();
  [["mot", en ? "Words" : "Mots"], ["phrase", en ? "Sentences" : "Phrases"]].forEach(([k, lab]) => {
    const list = cards.filter(c => c.kind === k);
    if(!list.length) return;
    const g = document.createElement("optgroup");
    g.label = lab + " · " + list.filter(c => c.o.img).length + "/" + list.length;
    list.forEach(c => {
      const o = document.createElement("option");
      o.value = c.id;
      o.textContent = (c.o.img ? "◉ " : "○ ") + c.label;
      g.appendChild(o);
    });
    sel.appendChild(g);
  });
  if(keep) sel.value = keep;
  const found = photoFind(sel.value);
  const m = found && found.o;
  const prev = document.getElementById("phoPrev");
  prev.innerHTML = "";
  if(m && m.img){
    const img = document.createElement("img");
    img.src = photoUrl(m.img);
    img.alt = m.fr || m.a || "";
    img.style.cssText = "width:150px;height:150px;object-fit:cover;border-radius:22px;"
      + "box-shadow:0 1px 2px rgba(20,16,40,.16),0 14px 28px -16px rgba(20,16,40,.5)";
    prev.appendChild(img);
    const rm = document.createElement("button");
    rm.className = "ghost mkmini";
    rm.textContent = en ? "Remove this photo" : "Retirer cette photo";
    rm.style.marginLeft = "12px";
    rm.addEventListener("click", async () => {
      const store = await photoStore();
      const old = m.img;
      m.img = null;
      photoSave(found.kind);
      photoPaint();
      if(store){ try{ await store.delete(old); }catch(e){} }
    });
    prev.appendChild(rm);
  }else if(m){
    prev.appendChild(Object.assign(document.createElement("p"),
      {className:"lede dim", textContent:en
        ? "No photo yet — this card falls back to its picture."
        : "Pas encore de photo — cette carte garde son image."}));
    if(found && found.kind === "phrase")
      prev.appendChild(Object.assign(document.createElement("p"),
        {className:"lede dim", lang:"fr", textContent:found.o.s.replace("___", found.o.a)}));
  }
}

async function photoUpload(){
  const en = typeof LANG !== "undefined" && LANG === "en";
  const note = document.getElementById("phoNote");
  const f = document.getElementById("phoFile").files[0];
  const found = photoFind(document.getElementById("phoPick").value);
  const m = found && found.o;
  if(!f || !m){ note.textContent = en ? "Pick a card and a photo." : "Choisis une carte et une photo."; return; }

  const store = await photoStore();
  if(!store){
    note.textContent = en ? "Photo storage isn't available in this view."
      : "Le magasin de photos n'est pas disponible ici.";
    return;
  }
  note.textContent = en ? "Sending…" : "Envoi…";
  try{
    const r = await store.upload(f, f.type ? undefined : {type:"image/jpeg"});
    m.img = r.id;
    photoSave(found.kind);
    photoPaint();
    note.textContent = (en ? "Photo saved — " : "Photo enregistrée — ")
      + Math.round(r.sizeBytes / 1024) + " Ko.";
    document.getElementById("phoFile").value = "";
  }catch(e){
    const msg = PHO_ERR[(e && e.code)] || ["L'envoi a échoué.", "The upload failed."];
    note.textContent = msg[en ? 1 : 0];
  }
}

let PHO_READY = false;
async function photoInit(){
  if(PHO_READY) return photoPaint();
  const host = document.getElementById("panel-cartes");
  if(!host) return;
  PHO_READY = true;
  const en = typeof LANG !== "undefined" && LANG === "en";

  const wrap = document.createElement("div");
  wrap.innerHTML =
    '<p class="fchead">' + (en ? "Real photos" : "De vraies photos") + "</p>"
    + '<p class="lede dim">' + (en
      ? "A photograph you chose yourself beats any emoji — it is your picture, so it sticks. "
        + "Pick a card, pick an image, and it replaces the emoji on that card everywhere."
      : "Une photo que tu as choisie toi-même vaut mieux que n’importe quel emoji — "
        + "c’est ton image, donc elle tient. Choisis une carte, choisis une photo, "
        + "et elle remplace l’emoji partout sur cette carte.") + "</p>"
    + '<div class="mkgrid">'
    + '<label class="fld"><span>' + (en ? "The card" : "La carte")
    + '</span><select id="phoPick" class="seinput"></select></label>'
    + '<label class="fld"><span>' + (en ? "The photo" : "La photo")
    + '</span><input type="file" id="phoFile" accept="image/png,image/jpeg,image/webp,image/gif"'
    + ' class="seinput"></label></div>'
    + '<div class="after"><button class="go" id="phoGo">'
    + (en ? "Put it on the card" : "Mettre sur la carte") + "</button></div>"
    + '<p class="note" id="phoNote"></p><div id="phoPrev" style="margin-top:12px"></div>';
  host.appendChild(wrap);

  document.getElementById("phoGo").addEventListener("click", photoUpload);
  document.getElementById("phoPick").addEventListener("change", photoPaint);
  photoPaint();
  const store = await photoStore();
  if(!store) document.getElementById("phoNote").textContent = en
    ? "Photo storage isn't available in this view — emoji still work."
    : "Le magasin de photos n'est pas disponible ici — les emoji marchent toujours.";
}

/* Le module se branche tout seul : pas besoin que le reste l'appelle. */
document.addEventListener("click", (e) => {
  const t = e.target && e.target.closest && e.target.closest('[data-mode="cartes"]');
  if(t) setTimeout(photoInit, 140);
});
document.addEventListener("DOMContentLoaded", () => {
  const p = document.getElementById("panel-cartes");
  if(p && !p.hidden) setTimeout(photoInit, 200);
});
