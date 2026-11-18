/* Les mots seuls que le cahier dit à voix haute : le socle (avec article), les noms du « le ou la »,
   les paires minimales. Même article que artOf() de cartes.js. */
const fs = require("fs"), vm = require("vm"), path = require("path");
const DIR = process.env.CAHIER_DIR || path.join(__dirname, "..");
const read = (f) => fs.readFileSync(path.join(DIR, f), "utf8");
const c = {}; vm.createContext(c);
vm.runInContext(read("socle.js") + "\nthis.BASE = BASE;", c);
vm.runInContext(read("sons.js").slice(0, read("sons.js").indexOf("let SN")) + "\nthis.PAIRS = PAIRS;", c);
const cah = read("cahier.js"); const gi = cah.indexOf("const GENRE");
vm.runInContext(cah.slice(gi, cah.indexOf("];", gi) + 2) + "\nthis.GENRE = GENRE;", c);
const PL = {lunettes:1, ciseaux:1, gens:1, vacances:1, toilettes:1};
const art = (fr, g) => { const w = fr.toLowerCase(); if (PL[w]) return "les ";
  const v = /^[aeiouyàâäéèêëîïôöûùüœæh]/i.test(w); return g === "m" ? (v ? "un " : "le ") : (v ? "une " : "la "); };
const out = new Set();
c.BASE.forEach(t => t.w.forEach(([fr, g]) => { out.add(fr); out.add((g === "m" || g === "f" ? art(fr, g) : "") + fr); }));
c.GENRE.forEach(g => { out.add(g.n); out.add(art(g.n, g.g) + g.n); });
c.PAIRS.forEach(p => { out.add(p.a); out.add(p.b); });
process.stdout.write(JSON.stringify({texts: [...out]}) + "\n");
