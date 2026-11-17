/* Contrôle des données du récit : chaque page tient debout, chaque carte reprend la page mot pour mot. */
const fs = require("fs"), vm = require("vm"), path = require("path");
const D = __dirname + "/..";
const ctx = {};
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(path.join(D, "recit-data.js"), "utf8") + "\nthis.RECIT = RECIT; this.CAST = CAST;", ctx);
const {RECIT, CAST} = ctx;

let fails = 0, n = 0;
const check = (ok, msg) => { n++; if(!ok){ fails++; console.log("FAIL " + msg); } };
const norm = (s) => String(s).toLowerCase().replace(/[’']/g, "'").replace(/\s+/g, " ").replace(/ /g, " ").trim();

const ids = RECIT.pages.map(p => p.id);
check(new Set(ids).size === ids.length, "ids de pages uniques");
check(ids.every(id => /^p\d\d$/.test(id)), "ids de pages au format pNN");
const chapNs = RECIT.chapitres.map(c => c.n);
check(new Set(chapNs).size === chapNs.length, "numéros de chapitres uniques");
RECIT.chapitres.forEach(c => check(RECIT.actes.some(a => a.n === c.acte), "chapitre " + c.n + " : l'acte existe"));
RECIT.actes.forEach(a => check(a.fr && a.en && a.fin && a.finEn, "acte " + a.n + " : textes complets"));

const speakers = new Set(Object.keys(CAST));
let words = 0, lines = 0;
RECIT.pages.forEach(p => {
  const tag = p.id + " ";
  check(RECIT.chapitres.some(c => c.n === p.ch), tag + "chapitre existant");
  check(p.titre && p.titreEn && p.lieu && p.lieuEn && p.hook && p.hookEn && p.resume, tag + "métadonnées complètes");
  check(p.lines.length >= 8 && p.lines.length <= 14, tag + "8 à 14 lignes (" + p.lines.length + ")");
  const choices = p.lines.filter(l => l.w === "?");
  check(choices.length >= 1, tag + "au moins un choix");
  check(p.lines[p.lines.length - 1].w !== "?", tag + "la page ne finit pas sur un choix");
  check(p.lines[0].w === "N", tag + "la page s'ouvre sur le narrateur");
  const text = [];
  p.lines.forEach(l => {
    if(l.w === "?"){
      check(l.c.length >= 2 && l.c.length <= 4, tag + "choix de 2 à 4 réponses");
      const good = l.c.filter(o => o[2]).length;
      check(good >= 1, tag + "au moins une réponse juste");
      check(good === 1 || good === l.c.length, tag + "une seule juste, ou un choix libre (" + good + "/" + l.c.length + ")");
      l.c.forEach(o => { check(o[0] && o[1], tag + "réponse FR+EN"); text.push(o[0]); });
    }else{
      check(speakers.has(l.w), tag + "locuteur connu " + l.w);
      check(l.fr && l.en, tag + "ligne FR+EN : " + (l.fr || "").slice(0, 30));
      text.push(l.fr);
      words += l.fr.split(/\s+/).length; lines++;
      check(l.fr.split(/\s+/).length <= 22, tag + "ligne courte : " + l.fr.slice(0, 30));
    }
  });
  const hay = norm(text.join(" ").replace(/\{nom\}/g, "Sahawat"));
  check(p.cards.length === 3, tag + "trois cartes");
  p.cards.forEach(c => {
    check((c.s.match(/___/g) || []).length === 1, tag + "un seul trou : " + c.s);
    check(c.a && c.a === c.a.trim(), tag + "réponse propre : " + c.a);
    check(Array.isArray(c.d) && c.d.length === 3 && new Set(c.d).size === 3 && !c.d.includes(c.a), tag + "trois distracteurs distincts : " + c.a);
    check(c.g && c.g.length > 8, tag + "glose anglaise : " + c.a);
    const filled = norm(c.s.replace("___", c.a));
    check(hay.includes(filled), tag + "la carte reprend la page mot pour mot : « " + filled + " »");
    const nw = filled.split(" ").length;
    check(nw >= 4 && nw <= 14, tag + "4 à 14 mots pour L'Ordre (" + nw + ") : " + filled);
    /* un distracteur ne doit pas être aussi juste que la réponse : il ne doit pas apparaître tel quel dans la page à cet endroit */
    c.d.forEach(d => check(!hay.includes(norm(c.s.replace("___", d))), tag + "le distracteur « " + d + " » ne forme pas une phrase de la page"));
  });
});
console.log("lignes :", lines, "· mots par ligne :", (words / lines).toFixed(1));
console.log("pages :", RECIT.pages.length, "· assertions :", n, "· échecs :", fails);
process.exit(fails ? 1 : 0);
