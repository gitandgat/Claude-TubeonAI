/* Le Cahier — la taille du texte.

   Quatre crans : 100 %, 112,5 %, 125 %, 140 %. Sans choix de l'utilisateur, c'est la
   feuille de style qui décide (125 % dès 760 px de large, 112,5 % au-dessus de 560 px,
   100 % sur téléphone) : rien ne saute à l'ouverture. Le choix reste sur cet appareil
   (localStorage) : c'est un confort de lecture, pas une donnée du cahier.

   Ce fichier se charge le premier, pour poser la taille avant que le reste ne se dessine. */

const TAILLE_KEY = "le-cahier-texte";
const TAILLES = [100, 112.5, 125, 140];

function tailleLue(){
  try{
    const v = localStorage.getItem(TAILLE_KEY);
    return v !== null && TAILLES[+v] !== undefined ? +v : null;
  }catch(e){ return null; }
}

/* Le cran en vigueur, choisi ou par défaut (même règle que la feuille de style). */
function tailleActuelle(){
  const v = tailleLue();
  if(v !== null) return v;
  const mq = (q) => typeof matchMedia === "function" && matchMedia(q).matches;
  return mq("(min-width:760px)") ? 2 : mq("(min-width:561px)") ? 1 : 0;
}

function tailleAppliquer(v){
  const root = document.documentElement;
  if(v === null) root.removeAttribute("data-text");
  else root.setAttribute("data-text", String(v));
}
tailleAppliquer(tailleLue());

/* La carte du monde : dix colonnes si les noms y tiennent, sinon deux rangées de cinq.
   On mesure plutôt que de deviner : la police, la langue et la largeur décident. */
function navFit(){
  const w = document.querySelector(".world");
  if(!w) return;
  w.classList.remove("rows2");
  if(typeof matchMedia === "function" && matchMedia("(max-width:560px)").matches) return;
  const tight = [...w.querySelectorAll(".tab")].some(t =>
    t.scrollWidth > t.clientWidth + 1 || [...t.children].some(c => c.scrollWidth > c.clientWidth + 1));
  if(tight) w.classList.add("rows2");
}

function taillePeindre(){
  const v = tailleActuelle(), en = typeof LANG !== "undefined" && LANG === "en";
  const dn = document.getElementById("txtDown"), up = document.getElementById("txtUp");
  const pct = String(TAILLES[v]).replace(".", en ? "." : ",") + " %";
  if(dn){
    dn.disabled = v <= 0;
    dn.title = (en ? "Smaller text" : "Texte plus petit") + " · " + pct;
    dn.setAttribute("aria-label", dn.title);
  }
  if(up){
    up.disabled = v >= TAILLES.length - 1;
    up.title = (en ? "Larger text" : "Texte plus grand") + " · " + pct;
    up.setAttribute("aria-label", up.title);
  }
}

function tailleChanger(d){
  const v = Math.max(0, Math.min(TAILLES.length - 1, tailleActuelle() + d));
  try{ localStorage.setItem(TAILLE_KEY, String(v)); }catch(e){}
  tailleAppliquer(v);
  taillePeindre();
  navFit();
}

let TAILLE_READY = false;
function tailleInit(){
  if(TAILLE_READY) return;
  TAILLE_READY = true;
  const dn = document.getElementById("txtDown"), up = document.getElementById("txtUp");
  if(dn) dn.addEventListener("click", () => tailleChanger(-1));
  if(up) up.addEventListener("click", () => tailleChanger(1));
  taillePeindre();
  navFit();
  /* La police arrive après le premier dessin, la fenêtre change de taille : on remesure. */
  if(document.fonts && document.fonts.ready) document.fonts.ready.then(navFit);
  const sheet = document.querySelector(".sheet");
  if(sheet && typeof ResizeObserver === "function"){
    let raf = 0;
    new ResizeObserver(() => { cancelAnimationFrame(raf); raf = requestAnimationFrame(navFit); }).observe(sheet);
  }
}
