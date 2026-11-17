/* Le Cahier — la liste de départ du livre (625 mots, Wyner).
   Elle est en anglais à dessein : la méthode veut que tu la traduises
   toi-même, avec tes images et le genre. On la traduit ici, catégorie
   par catégorie, et chaque mot devient une carte. */

const FF625 = [
  {k:"ANIMALS", fr:"Animaux", en:"Animals", w:["dog", "cat", "fish", "bird", "cow", "pig", "mouse", "horse", "wing", "animal"]},
  {k:"FOODS", fr:"Nourriture", en:"Food", w:["egg", "cheese", "bread", "soup", "cake", "chicken", "pork", "beef", "apple", "banana", "orange", "lemon", "corn", "rice", "oil", "seed", "knife", "spoon", "fork", "plate", "cup", "breakfast", "lunch", "dinner", "sugar", "salt", "bottle", "food"]},
  {k:"BEVERAGES", fr:"Boissons", en:"Drinks", w:["coffee", "tea", "wine", "beer", "juice", "water", "milk", "beverage"]},
  {k:"BODY", fr:"Le corps", en:"Body", w:["head", "neck", "face", "beard", "hair", "eye", "mouth", "lip", "nose", "tooth", "ear", "tear (drop)", "tongue", "back", "toe", "finger", "foot", "hand", "leg", "arm", "shoulder", "heart", "blood", "brain", "knee", "sweat", "disease", "bone", "voice", "skin", "body"]},
  {k:"CLOTHING", fr:"V\u00eatements", en:"Clothing", w:["hat", "dress", "suit", "skirt", "shirt", "T-shirt", "pants", "shoes", "pocket", "coat", "stain", "clothing"]},
  {k:"HOME", fr:"La maison", en:"Home", w:["table", "chair", "bed", "dream", "window", "door", "bedroom", "kitchen", "bathroom", "pencil", "pen", "photograph", "soap", "book", "page", "key", "paint", "letter", "wall", "paper", "floor", "ceiling", "roof", "pool", "lock", "telephone", "garden", "yard", "needle", "bag", "box", "gift", "card", "ring", "tool"]},
  {k:"LOCATIONS", fr:"Lieux", en:"Places", w:["city", "house", "apartment", "street/road", "airport", "train station", "bridge", "hotel", "restaurant", "farm", "court", "school", "office", "room", "town", "university", "club", "bar", "park", "camp", "store/shop", "theater", "library", "hospital", "church", "market", "country (United States", "France", "etc.)", "building", "ground", "space (outer space)", "bank", "location"]},
  {k:"NATURE", fr:"La nature", en:"Nature", w:["sea", "ocean", "river", "mountain", "rain", "snow", "tree", "sun", "moon", "world", "Earth", "forest", "sky", "plant", "wind", "soil/earth", "flower", "valley", "root", "lake", "star", "grass", "leaf", "air", "sand", "beach", "wave", "fire", "ice", "island", "hill", "heat", "nature"]},
  {k:"PEOPLE", fr:"Les gens", en:"People", w:["son", "daughter", "mother", "father", "parent (= mother/father)", "baby", "man", "woman", "brother", "sister", "family", "grandfather", "grandmother", "husband", "wife", "king", "queen", "president", "neighbor", "boy", "girl", "child (= boy/girl)", "adult (= man/woman)", "human (≠ animal)", "friend (add a friend’s name)", "victim", "player", "fan", "crowd", "person"]},
  {k:"JOBS", fr:"M\u00e9tiers", en:"Jobs", w:["Teacher", "student", "lawyer", "doctor", "patient", "waiter", "secretary", "priest", "police", "army", "soldier", "artist", "author", "manager", "reporter", "actor", "job"]},
  {k:"TRANSPORTATION", fr:"Transports", en:"Transport", w:["train", "plane", "car", "truck", "bicycle", "bus", "boat", "ship", "tire", "gasoline", "engine", "(train) ticket", "transportation"]},
  {k:"ELECTRONICS", fr:"\u00c9lectronique", en:"Electronics", w:["clock", "lamp", "fan", "cell phone", "network", "computer", "program (computer)", "laptop", "screen", "camera", "television", "radio"]},
  {k:"MATERIALS", fr:"Mati\u00e8res", en:"Materials", w:["glass", "metal", "plastic", "wood", "stone", "diamond", "clay", "dust", "gold", "copper", "silver", "material"]},
  {k:"SOCIETY", fr:"Soci\u00e9t\u00e9", en:"Society", w:["religion", "heaven", "hell", "death", "medicine", "money", "dollar", "bill", "marriage", "wedding", "team", "race (ethnicity)", "sex (the act)", "sex (gender)", "murder", "prison", "technology", "energy", "war", "peace", "attack", "election", "magazine", "newspaper", "poison", "gun", "sport", "race (sport)", "exercise", "ball", "game", "price", "contract", "drug", "sign", "science", "God"]},
  {k:"ART", fr:"Art", en:"Art", w:["band", "song", "instrument (musical)", "music", "movie", "art"]},
  {k:"COLORS", fr:"Couleurs", en:"Colours", w:["red", "green", "blue (light/dark)", "yellow", "brown", "pink", "orange", "black", "white", "gray", "colour"]},
  {k:"TIME", fr:"Le temps", en:"Time", w:["year", "month", "week", "day", "hour", "minute", "second", "morning", "afternoon", "evening", "night", "time"]},
  {k:"SEASONS", fr:"Saisons", en:"Seasons", w:["summer", "spring", "winter", "fall", "season"]},
  {k:"MONTHS", fr:"Mois", en:"Months", w:["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]},
  {k:"DAYS OF THE WEEK", fr:"Jours", en:"Weekdays", w:["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]},
  {k:"DIRECTIONS", fr:"Directions", en:"Directions", w:["top", "bottom", "side", "front", "back", "outside", "inside", "up", "down", "left", "right", "straight", "north", "south", "east", "west", "direction"]},
  {k:"MATH/MEASUREMENTS", fr:"Mesures", en:"Measures", w:["meter", "centimeter", "kilogram", "inch", "foot", "pound", "half", "circle", "square", "temperature", "date", "weight", "edge", "corner"]},
  {k:"MISCELLANEOUS NOUNS", fr:"Divers", en:"Odds and ends", w:["map", "dot", "consonant", "vowel", "light", "sound", "yes", "no", "piece", "pain", "injury", "hole", "image", "pattern", "noun", "verb", "adjective"]},
  {k:"NUMBERS", fr:"Nombres", en:"Numbers", w:["0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "30", "31", "32", "40", "41", "42", "50", "51", "52", "60", "61", "62", "70", "71", "72", "80", "81", "82", "90", "91", "92", "100", "101", "102", "110", "111", "1000", "1001", "10000", "100000", "million", "billion", "1st", "2nd", "3rd", "4th", "5th", "number"]},
  {k:"PRONOUNS", fr:"Pronoms", en:"Pronouns", w:["I", "you (singular)", "he", "she", "it", "we", "you (plural", "as in “y’all”)", "they"]},
  {k:"ADJECTIVES", fr:"Adjectifs", en:"Adjectives", w:["long", "short (vs. long)", "tall", "short (vs. tall)", "wide", "narrow", "big/large", "small/little", "slow", "fast", "hot", "cold", "warm", "cool", "new", "old (new)", "young", "old (young)", "good", "bad", "wet", "dry", "sick", "healthy", "loud", "quiet", "happy", "sad", "beautiful", "ugly", "deaf", "blind", "nice", "mean", "rich", "poor", "thick", "thin", "expensive", "cheap", "flat", "curved", "male", "female", "tight", "loose", "high", "low", "soft", "hard", "deep", "shallow", "clean", "dirty", "strong", "weak", "dead", "alive", "heavy", "light (heavy)", "dark", "light (dark)", "nuclear", "famous"]},
  {k:"VERBS", fr:"Verbes", en:"Verbs", w:["work", "play", "walk", "run", "drive", "fly", "swim", "go c", "stop", "follow", "think", "speak/say", "eat", "drink", "kill", "die", "smile", "laugh", "cry", "buy", "pay", "sell", "shoot (a gun)", "learn", "jump", "smell", "hear (a sound)", "listen (music)", "taste", "touch", "see (a bird)", "watch (TV)", "kiss", "burn", "melt", "dig", "explode", "sit", "stand", "love", "pass by", "cut", "fight", "lie down", "dance", "sleep", "wake up", "sing", "count", "marry", "pray", "win", "lose", "mix/stir", "bend", "wash", "cook", "open", "close", "write", "call", "turn", "build", "teach", "grow", "draw", "feed", "catch", "throw", "clean", "find", "fall", "push", "pull", "carry", "break", "wear", "hang", "shake", "sign", "beat", "lift"]}
];

/* ---------- traduction d'une catégorie, à la demande ---------- */
let FF = null;

const ffHas = (fr) => (S.mots || []).some(m => m.fr.toLowerCase() === String(fr).toLowerCase());

function ffPrompt(cat, words){
  return "Traduis en français cette tranche de la liste de départ d'un apprenant.\n\n"
    + "Catégorie : " + cat.en + "\nMots anglais : " + words.join(", ") + "\n\n"
    + "Pour chaque mot :\n"
    + "- fr : le mot français courant, SANS article (le sens exact du mot anglais ; "
    + "respecte les précisions entre parenthèses, ex. « short (vs. tall) » = petit).\n"
    + "- g : \"m\" ou \"f\" si c'est un nom, \"\" sinon.\n"
    + "- pic : UN emoji qui montre la chose, ou \"\" si rien ne la montre honnêtement.\n"
    + "- en : le mot anglais de départ, tel quel.\n\n"
    + "Garde l'ordre et n'ajoute rien. Réponds uniquement par un tableau JSON :\n"
    + '[{"fr":"chien","g":"m","pic":"🐕","en":"dog"}]';
}

async function ffRun(i){
  if(!S.sample){ $("ffNote").textContent = PH_ERR.not_granted; return; }
  const cat = FF625[i];
  const todo = cat.w.slice(0, 60);
  FF = {i, cat, batch:[]};
  $("ffNote").textContent = (typeof LANG !== "undefined" && LANG === "en")
    ? "Claude is translating " + cat.en + "…" : "Claude traduit « " + cat.fr + " »…";
  let raw = null;
  try{
    raw = await S.sample.json(ffPrompt(cat, todo), {modelTier:"default", cache:false});
  }catch(e){
    $("ffNote").textContent = PH_ERR[(e && e.code)] || PH_ERR.upstream_error;
    return;
  }
  FF.batch = (Array.isArray(raw) ? raw : [])
    .map(x => ({fr:String(x && x.fr || "").trim(), g:(x && (x.g === "m" || x.g === "f")) ? x.g : "",
      pic:String(x && x.pic || "").trim().slice(0, 4), en:String(x && x.en || "").trim(),
      keep:true}))
    .filter(x => x.fr && !ffHas(x.fr));
  ffDraw();
}

function ffDraw(){
  const en = typeof LANG !== "undefined" && LANG === "en";
  const ul = $("ffList");
  ul.innerHTML = "";
  ul.hidden = !FF || !FF.batch.length;
  $("ffAct").hidden = ul.hidden;
  if(ul.hidden){
    $("ffNote").textContent = en ? "Nothing new in that category — it's already in your deck."
      : "Rien de neuf dans cette catégorie : tout est déjà dans ton paquet.";
    return;
  }
  FF.batch.forEach(c => {
    const li = document.createElement("li");
    const b = document.createElement("button");
    b.className = "sug"; b.type = "button";
    b.setAttribute("aria-pressed", "true");
    const w = document.createElement("span");
    w.className = "sw";
    w.append(Object.assign(document.createElement("span"),
        {className:"sfr", textContent:(c.g ? (c.g === "m" ? "le " : "la ") : "") + c.fr}),
      Object.assign(document.createElement("span"), {className:"sen", textContent:c.en}));
    b.append(Object.assign(document.createElement("span"),
        {className:"spic", textContent:c.pic || "·"}), w,
      Object.assign(document.createElement("span"), {className:"schk", textContent:"✓"}));
    b.addEventListener("click", () => {
      c.keep = !c.keep;
      b.setAttribute("aria-pressed", c.keep ? "true" : "false");
    });
    li.appendChild(b);
    ul.appendChild(li);
  });
  $("ffNote").textContent = FF.batch.length + (en ? " words — untick anything that's off."
    : " mots — décoche ce qui ne va pas.");
}

function ffKeep(){
  const en = typeof LANG !== "undefined" && LANG === "en";
  let n = 0;
  FF.batch.filter(c => c.keep).forEach(c => {
    if(ffHas(c.fr)) return;
    if(typeof motMake === "function" && motMake(c.fr, c.pic, "", c.g, c.g ? "nom" : "", "625")) n++;
  });
  if(typeof drawMots === "function") drawMots();
  srsReset(); paintMargin(); ffPaint();
  FF.batch = [];
  ffDraw();
  $("ffNote").textContent = n + (en ? " words added — " + n * 2 + " to " + n * 4 + " cards."
    : " mots ajoutés — " + n * 2 + " à " + n * 4 + " cartes.");
}

function ffPaint(){
  const en = typeof LANG !== "undefined" && LANG === "en";
  const box = $("ffCats");
  box.innerHTML = "";
  let tot = 0;
  FF625.forEach((c, i) => {
    tot += c.w.length;
    const b = document.createElement("button");
    b.type = "button"; b.className = "chip";
    b.textContent = (en ? c.en : c.fr) + " " + c.w.length;
    b.addEventListener("click", () => ffRun(i));
    box.appendChild(b);
  });
  $("ffCount").textContent = tot + (en ? " words in the book's list" : " mots dans la liste du livre");
}

let FF_READY = false;
function ff625Init(){
  if(FF_READY) return ffPaint();
  FF_READY = true;
  $("ffKeep").addEventListener("click", ffKeep);
  ffPaint();
}
