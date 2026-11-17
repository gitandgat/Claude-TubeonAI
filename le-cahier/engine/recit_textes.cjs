/* Le Cahier — les textes à enregistrer pour le récit.

   Charge recit-data.js et recit.js dans un contexte vide, puis écrit sur la sortie standard,
   page par page, tout ce que le lecteur peut dire à voix haute :
     · chaque réplique (sans le prénom : rcSpoken() de recit.js, la même fonction que le lecteur),
     · chaque réponse juste que le héros peut choisir,
     · chaque phrase de carte, trou comblé.
   Une page = une piste (voix-rNN.mp3). Doublons retirés par dStrip(), comme la carte des voix.

   Usage : node engine/recit_textes.cjs            (CAHIER_DIR=<dossier> pour lire ailleurs) */
const fs = require("fs"), vm = require("vm"), path = require("path");

const DIR = process.env.CAHIER_DIR || path.join(__dirname, "..");
const ctx = {};
vm.createContext(ctx);
vm.runInContext(
  fs.readFileSync(path.join(DIR, "recit-data.js"), "utf8") + "\n" +
  fs.readFileSync(path.join(DIR, "recit.js"), "utf8") +
  "\nthis.RECIT = RECIT; this.rcSpoken = rcSpoken;", ctx);
const {RECIT, rcSpoken} = ctx;

/* Identique à dStrip() de dictee.js. */
const dStrip = (s) => s.normalize("NFD").replace(/[̀-ͯ]/g, "").toLowerCase().replace(/[^a-z0-9]/g, "");

const pages = RECIT.pages.map((p) => {
  const seen = new Set(), texts = [];
  const add = (t) => {
    const clean = String(t).trim();
    const k = dStrip(clean);
    if (clean && k && !seen.has(k)) { seen.add(k); texts.push(clean); }
  };
  p.lines.forEach((l) => {
    if (l.w === "?") l.c.filter((o) => o[2]).forEach((o) => add(rcSpoken(o[0])));
    else add(rcSpoken(l.fr));
  });
  p.cards.forEach((c) => add(c.s.replace("___", c.a)));
  return {id: p.id, texts};
});

process.stdout.write(JSON.stringify({pages}, null, 1) + "\n");
