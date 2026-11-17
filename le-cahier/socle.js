/* Le Cahier — le socle : le vocabulaire de base, concret et imageable.
   Dans l'esprit de la liste de départ de Fluent Forever : des mots
   fréquents qu'on peut montrer du doigt, une image, un genre, zéro
   traduction. Chaque mot donne quatre cartes. */

const BASE = [
  {t:"Animaux", en:"Animals", w:[
    ["chien","m","🐕"],["chat","m","🐈"],["cheval","m","🐎"],["vache","f","🐄"],
    ["mouton","m","🐑"],["cochon","m","🐖"],["poule","f","🐔"],["canard","m","🦆"],
    ["oiseau","m","🐦"],["poisson","m","🐟"],["souris","f","🐭"],["lapin","m","🐇"],
    ["ours","m","🐻"],["loup","m","🐺"],["renard","m","🦊"],["lion","m","🦁"],
    ["éléphant","m","🐘"],["singe","m","🐒"],["araignée","f","🕷️"],["abeille","f","🐝"],
    ["papillon","m","🦋"],["grenouille","f","🐸"],["serpent","m","🐍"],["tortue","f","🐢"]]},

  {t:"Nourriture", en:"Food", w:[
    ["pain","m","🥖"],["fromage","m","🧀"],["beurre","m","🧈"],["œuf","m","🥚"],
    ["viande","f","🥩"],["poulet","m","🍗"],["riz","m","🍚"],["soupe","f","🍲"],
    ["salade","f","🥗"],["pomme","f","🍎"],["banane","f","🍌"],["orange","f","🍊"],
    ["citron","m","🍋"],["fraise","f","🍓"],["raisin","m","🍇"],["pêche","f","🍑"],
    ["tomate","f","🍅"],["carotte","f","🥕"],["oignon","m","🧅"],["champignon","m","🍄"],
    ["gâteau","m","🍰"],["chocolat","m","🍫"],["sucre","m","🍬"],["sel","m","🧂"],
    ["miel","m","🍯"],["glace","f","🍨"]]},

  {t:"Boissons", en:"Drinks", w:[
    ["eau","f","💧"],["vin","m","🍷"],["bière","f","🍺"],["café","m","☕"],
    ["thé","m","🍵"],["lait","m","🥛"],["jus","m","🧃"],["bouteille","f","🍾"]]},

  {t:"Le corps", en:"The body", w:[
    ["main","f","✋"],["bras","m","💪"],["jambe","f","🦵"],["pied","m","🦶"],
    ["œil","m","👁️"],["oreille","f","👂"],["nez","m","👃"],["bouche","f","👄"],
    ["dent","f","🦷"],["langue","f","👅"],["cœur","m","❤️"],["cerveau","m","🧠"],
    ["doigt","m","👆"],["sang","m","🩸"],["os","m","🦴"],["tête","f","🙂"],
    ["dos","m","🔙"],["peau","f","🤚"]]},

  {t:"Vêtements", en:"Clothes", w:[
    ["chemise","f","👔"],["pantalon","m","👖"],["robe","f","👗"],["jupe","f","🩱"],
    ["manteau","m","🧥"],["chaussure","f","👟"],["chaussette","f","🧦"],["chapeau","m","🎩"],
    ["écharpe","f","🧣"],["gant","m","🧤"],["lunettes","f","👓"],["montre","f","⌚"],
    ["sac","m","👜"],["ceinture","f","🥋"],["parapluie","m","☂️"]]},

  {t:"La maison", en:"The house", w:[
    ["maison","f","🏠"],["porte","f","🚪"],["fenêtre","f","🪟"],["escalier","m","🪜"],
    ["chambre","f","🛏️"],["cuisine","f","🍳"],["jardin","m","🌳"],["clé","f","🔑"],
    ["chaise","f","🪑"],["lit","m","🛏️"],["canapé","m","🛋️"],["miroir","m","🪞"],
    ["lampe","f","💡"],["tiroir","m","🗄️"],["mur","m","🧱"],["toit","m","🏚️"],
    ["douche","f","🚿"],["savon","m","🧼"]]},

  {t:"La cuisine", en:"Kitchen", w:[
    ["assiette","f","🍽️"],["verre","m","🥛"],["tasse","f","☕"],["cuillère","f","🥄"],
    ["fourchette","f","🍴"],["couteau","m","🔪"],["casserole","f","🍳"],["four","m","🔥"],
    ["frigo","m","🧊"],["serviette","f","🧻"]]},

  {t:"La nature", en:"Nature", w:[
    ["soleil","m","☀️"],["lune","f","🌙"],["étoile","f","⭐"],["nuage","m","☁️"],
    ["pluie","f","🌧️"],["neige","f","❄️"],["vent","m","🌬️"],["orage","m","⛈️"],
    ["mer","f","🌊"],["plage","f","🏖️"],["montagne","f","⛰️"],["forêt","f","🌲"],
    ["arbre","m","🌳"],["fleur","f","🌸"],["herbe","f","🌿"],["feuille","f","🍂"],
    ["feu","m","🔥"],["terre","f","🌍"],["pierre","f","🪨"],["rivière","f","🏞️"]]},

  {t:"La ville", en:"The town", w:[
    ["ville","f","🏙️"],["rue","f","🛣️"],["pont","m","🌉"],["église","f","⛪"],
    ["école","f","🏫"],["hôpital","m","🏥"],["gare","f","🚉"],["magasin","m","🏪"],
    ["marché","m","🧺"],["banque","f","🏦"],["restaurant","m","🍴"],["hôtel","m","🏨"],
    ["bureau","m","🏢"],["bibliothèque","f","📚"],["musée","m","🏛️"],["parc","m","🏞️"],
    ["pharmacie","f","💊"],["boulangerie","f","🥖"]]},

  {t:"Transports", en:"Transport", w:[
    ["voiture","f","🚗"],["bus","m","🚌"],["train","m","🚆"],["avion","m","✈️"],
    ["vélo","m","🚲"],["bateau","m","🚢"],["moto","f","🏍️"],["camion","m","🚚"],
    ["métro","m","🚇"],["billet","m","🎫"]]},

  {t:"Les gens", en:"People", w:[
    ["homme","m","👨"],["femme","f","👩"],["enfant","m","🧒"],["garçon","m","👦"],
    ["fille","f","👧"],["bébé","m","👶"],["père","m","👨‍🦰"],["mère","f","👩‍🦰"],
    ["frère","m","👬"],["sœur","f","👭"],["ami","m","🤝"],["voisin","m","🏘️"],
    ["médecin","m","🩺"],["professeur","m","👩‍🏫"],["infirmière","f","👩‍⚕️"],["pompier","m","🚒"],
    ["policier","m","👮"],["boulanger","m","🥐"],["serveur","m","🧑‍🍳"],["client","m","🧾"]]},

  {t:"Le temps", en:"Time", w:[
    ["jour","m","📆"],["nuit","f","🌙"],["matin","m","🌅"],["soir","m","🌆"],
    ["heure","f","🕐"],["semaine","f","📅"],["mois","m","🗓️"],["année","f","🎊"],
    ["hiver","m","⛄"],["été","m","🏖️"],["printemps","m","🌷"],["automne","m","🍁"],
    ["anniversaire","m","🎂"],["midi","m","🕛"]]},

  {t:"Couleurs", en:"Colours", w:[
    ["rouge","","🔴"],["bleu","","🔵"],["vert","","🟢"],["jaune","","🟡"],
    ["noir","","⚫"],["blanc","","⚪"],["violet","","🟣"],["marron","","🟤"],
    ["gris","","🩶"],["rose","","🌸"]]},

  {t:"Verbes", en:"Verbs", w:[
    ["manger","","🍽️"],["boire","","🥤"],["dormir","","😴"],["marcher","","🚶"],
    ["courir","","🏃"],["parler","","💬"],["écouter","","👂"],["regarder","","👀"],
    ["lire","","📖"],["écrire","","✍️"],["acheter","","🛒"],["ouvrir","","🔓"],
    ["fermer","","🔒"],["donner","","🤲"],["monter","","⬆️"],["descendre","","⬇️"],
    ["sortir","","🚪"],["travailler","","💼"],["jouer","","🎮"],["chanter","","🎤"],
    ["danser","","💃"],["nager","","🏊"],["conduire","","🚗"],["cuisiner","","👨‍🍳"],
    ["rire","","😄"],["pleurer","","😢"],["attendre","","⏳"],["payer","","💳"]]}
];

const basePos = (g) => g ? "nom" : "";

/* Les mots déjà dans le paquet, normalisés une fois : vidé à chaque
   changement du paquet (voir srsReset). */
let MOTSET = null;
function baseAdded(word){
  if(!MOTSET) MOTSET = new Set((S.mots || []).map(m => motNorm(m.fr)));
  return MOTSET.has(String(word).toLowerCase());
}

function baseAddTheme(idx){
  const th = BASE[idx];
  if(!th) return;
  let n = 0;
  th.w.forEach(([word, g, pic]) => {
    if(baseAdded(word)) return;
    const m = {
      id:Date.now().toString(36) + Math.random().toString(36).slice(2, 6),
      fr:word, pic:pic, note:"", g:g, pos:basePos(g), from:"socle", lv:1, at:Date.now()
    };
    S.mots = S.mots.concat([m]);
    n++;
  });
  S.mots = S.mots.slice(0, MOT_CAP);
  saveMots();
  srsReset();
  paintMargin();
  drawMots();
  paintBase();
  const en = typeof LANG !== "undefined" && LANG === "en";
  $("sbNote").textContent = n === 0
    ? (en ? "Already all in your deck." : "Déjà tous dans ton paquet.")
    : en
    ? n + " words added. Each one starts with a word → picture card, then picture → word, sound and gender on later days."
    : n + " mots ajoutés. Chacun commence par une fiche mot → image ; image → mot, son et genre suivent les jours d'après.";
}

function paintBase(){
  const en = typeof LANG !== "undefined" && LANG === "en";
  const box = $("sbThemes");
  box.innerHTML = "";
  let total = 0, have = 0;
  BASE.forEach((th, i) => {
    const got = th.w.filter(w => baseAdded(w[0])).length;
    total += th.w.length; have += got;
    const b = document.createElement("button");
    b.type = "button";
    b.className = "chip" + (got === th.w.length ? " on" : "");
    b.textContent = (en ? th.en : th.t) + " " + got + "/" + th.w.length;
    b.addEventListener("click", () => baseAddTheme(i));
    box.appendChild(b);
  });
  $("sbCount").textContent = have + " / " + total + (en ? " words in circulation" : " mots dans le cycle");
}

let SB_READY = false;
function baseInit(){
  if(SB_READY) return paintBase();
  SB_READY = true;
  $("sbAll").addEventListener("click", () => {
    BASE.forEach((_, i) => baseAddTheme(i));
    const en = typeof LANG !== "undefined" && LANG === "en";
    $("sbNote").textContent = en ? "Whole base deck in circulation." : "Tout le socle est dans le cycle.";
  });
  paintBase();
}
