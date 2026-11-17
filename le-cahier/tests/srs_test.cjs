/* Harnais : charge srs.js avec des stubs et vérifie S1–S3 + reprise douce. */
const fs = require("fs"), vm = require("vm");
const dir = __dirname + "/../";
const cards = [];
for(let i = 1; i <= 30; i++) cards.push({id:"t" + i, s:"Phrase numéro " + i + " avec ___ dedans.", a:"mot" + i, d:["a","b","c"], g:"gloss", lv:2});
const ctx = {
  console, Math, Date, Object, Array, Number, String, JSON, Infinity,
  S:{P:{srs:{}, day:{n:0, fresh:0}, recall:{rev:0, ok:0}, level:2, last:"", days:5, hist:{}}, mots:[]},
  ALL:() => cards, GENRE:[], POOL:[], PAIRS:[], DECIDE:[{lv:2}],
  motCards:() => [], motById:() => null, sonItem:() => null,
  newPerDay:() => 10, levelOf:() => 2, weakSpots:() => [],
};
ctx.globalThis = ctx;
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(dir + "srs.js", "utf8") + "\nthis.isLeech=isLeech;this.LEECH_DAY=LEECH_DAY;this.srsPreview=srsPreview;\n", ctx);
const g = ctx;
let fails = 0;
const ok = (c, m) => { console.log((c ? "ok  " : "FAIL") + " " + m); if(!c) fails++; };

/* S1 fuzz */
let min = 99, max = 0;
for(let i = 0; i < 2000; i++){ const d = g.fuzzDays(30); min = Math.min(min, d); max = Math.max(max, d); }
ok(min >= 27 && max <= 33 && max > min, "fuzz on 30 d stays within ±8% and varies: " + min + "–" + max);
ok(g.fuzzDays(1) === 1 && g.fuzzDays(2) === 2, "no fuzz under 3 d");

/* S3 leech */
const t = g.dayNum();
g.S.P.srs["t1"] = [t - 1, 0, 13, 0, 5, 9, 2];          // déjà 5 oublis
g.srsUpdate("t1", 1);
ok(g.isLeech("t1"), "6th lapse suspends the card");
ok(g.leechList().length === 1 && g.leechList()[0] === "t1", "leechList finds it");
g.srsUpdate("t1", 4);
ok(!g.isLeech("t1") && g.S.P.srs["t1"][0] > t, "a pass wakes it up and schedules it");
g.S.P.srs["t2"] = [t - 1, 0, 13, 0, 5, 9, 2];
g.srsUpdate("t2", 1); g.srsUpdate("t2", 1);
ok(g.isLeech("t2"), "failing the retry keeps it asleep");
g.leechResume("t2");
ok(!g.isLeech("t2") && g.S.P.srs["t2"][0] === t, "leechResume makes it due today");

/* S5 + S2 : rétention par type, puis politique d'entrée */
g.S.P.hist = {};
for(let i = 0; i < 20; i++){ g.S.P.srs["t" + (3 + (i % 5))] = [t, 1, 25, 1, 0, 1, 1]; }
// 20 rappels "trou" à 60 %
for(let i = 0; i < 20; i++) g.srsUpdate("t" + (3 + (i % 5)), i < 12 ? 4 : 1);
const r = g.retention30("trou");
ok(r.rev === 20 && Math.abs(r.acc - .6) < .01, "retention30(trou) = 60% over 20");
g.S.P.day.fresh = 0;
const fresh = g.pickFresh(10, null);
const kinds = fresh.map(id => g.kindOfId(id));
ok(!kinds.includes("trou"), "trou (<70%) gets no new card today: " + kinds.join(","));
ok(g.S.intakeHeld.includes("trou"), "intakeHeld lists trou");
ok(kinds.includes("dictee") || kinds.includes("ordre") || kinds.includes("imiter"), "other kinds still get new cards");

/* reprise douce */
const d = new Date(); d.setDate(d.getDate() - 4);
g.S.P.last = d.toLocaleDateString("sv");
g.S.P.comebackDay = 0;
for(let i = 1; i <= 30; i++){ g.S.P.srs["s t".trim() + i] = undefined; }
for(let i = 1; i <= 30; i++){ g.S.P.srs["st" + i] = [t - 2, 3, 25, 2, 0, 2, 2]; g.S.P.srs["xt" + i] = [t - 3, 3, 25, 2, 0, 2, 2]; }
const q = g.srsQueue(null);
ok(q.comeback && q.comeback.away === 4, "comeback detected after 4 days away");
ok(q.due === 20 && q.left > 0, "due capped at 20 with the rest left: due=" + q.due + " left=" + q.left);
ok(q.fresh <= 1, "at most one new card on a comeback day: " + q.fresh);
const st = g.srsStats();
ok(st.due === 20 && st.dueAll > 20 && st.comeback, "srsStats reports the cap and the full count");
g.S.P.last = g.S.P.last; // unchanged
const q2 = g.srsQueue(null);
ok(q2.due === 20, "cap holds for the whole day");

console.log(fails ? fails + " FAILURES" : "ALL PASS");
process.exit(fails ? 1 : 0);
