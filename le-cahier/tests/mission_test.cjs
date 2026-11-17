/* Harnais pour la mission : un faux DOM minimal, un faux sample, un faux
   micro (SpeechRecognition). Vérifie le cycle : lancer → réplique → micro armé
   → phrase entendue → envoi auto → fin à 0:00 → débriefing → mission comptée. */
const fs = require("fs"), vm = require("vm");
const dir = __dirname + "/../";

function mkEl(id){
  const cls = new Set();
  const el = {id, hidden:false, disabled:false, value:"", checked:false, textContent:"", innerHTML:"",
    scrollTop:0, scrollHeight:0, children:[], _l:{}, dataset:{}, style:{setProperty(){}},
    classList:{add:(...c)=>c.forEach(x=>cls.add(x)), remove:(...c)=>c.forEach(x=>cls.delete(x)),
      toggle:(c,on)=>{ const v = on === undefined ? !cls.has(c) : on; v ? cls.add(c) : cls.delete(c); return v; },
      contains:(c)=>cls.has(c)},
    addEventListener(t, f){ (this._l[t] = this._l[t] || []).push(f); },
    fire(t, e){ (this._l[t] || []).forEach(f => f(e || {})); },
    appendChild(c){ this.children.push(c); return c; },
    append(...cs){ cs.forEach(c => this.children.push(c)); },
    remove(){}, focus(){}, closest(){ return mkEl("label"); },
    set className(v){}, get className(){ return ""; }
  };
  return el;
}
const els = {};
const $ = (id) => els[id] || (els[id] = mkEl(id));
$("cvSpeak").checked = false;          /* pas de lecture à voix haute : armement immédiat */

/* faux micro du navigateur */
let srInstance = null;
class FakeSR {
  constructor(){ this._l = {}; srInstance = this; this.started = 0; }
  addEventListener(t, f){ (this._l[t] = this._l[t] || []).push(f); }
  start(){ this.started++; }
  stop(){ (this._l.end || []).forEach(f => f({})); }
  say(text){
    (this._l.result || []).forEach(f => f({resultIndex:0, results:[Object.assign([{transcript:text}], {isFinal:true})]}));
    (this._l.end || []).forEach(f => f({}));
  }
}

let sampleCalls = 0;
const fakeSample = async (turns, opts) => { sampleCalls++; const text = "Réplique " + sampleCalls + " ?";
  if(opts && opts.onText) opts.onText({text}); return {text}; };
fakeSample.json = async () => ({verdict:"Bien.", note:15, fautes:[], evite:"", resume:"ok", recurrents:[], ampleur:"juste",
  cartes:[{s:"Je ___ au marché.", a:"vais", d:["va","vont","allez"], g:"I go to the market."}]});

const timers = [];
let now = 1e12;
const ctx = {
  console, Math, JSON, Object, Array, String, Number, Promise, Set,
  Date:{now:() => now},
  document:{createElement:(t)=>mkEl(t), createTextNode:(t)=>({nodeType:3, textContent:t})},
  window:{SpeechRecognition:FakeSR},
  setTimeout:(f, ms) => { const t = {f, at:now + (ms || 0), id:timers.length}; timers.push(t); return t.id; },
  clearTimeout:(id) => { if(timers[id]) timers[id].f = null; },
  setInterval:(f, ms) => { const t = {f, at:now + ms, every:ms, id:timers.length}; timers.push(t); return t.id; },
  clearInterval:(id) => { if(timers[id]) timers[id].f = null; },
  $, LANG:"fr", tr:(s)=>s, LEVELS:["A1","A2","B1","B2","C1","C2"],
  PH_ERR:{not_granted:"ng", upstream_error:"ue"},
  speakFr(){}, imModelSec:() => 2, dayNum:() => 20000, xpGain(){}, noteLevelRaw(){}, scored(){}, paintMargin(){},
  save(){}, today:() => "2026-11-15", cleanCards:(c)=>c.map(x=>({...x})), saveCards(){}, srsReset(){},
  profilDomains:() => ["quotidien"],
  S:{sample:fakeSample, dictation:null, P:{level:2, parle:{n:0, points:0}, convos:[]}, cards:[]},
};
ctx.globalThis = ctx;
vm.createContext(ctx);
vm.runInContext(fs.readFileSync(dir + "parler.js", "utf8") + "\nthis.CV_get=()=>CV;\n", ctx);

async function flush(){ for(let i = 0; i < 20; i++) await Promise.resolve(); }
async function advance(ms){
  const end = now + ms;
  for(;;){
    const due = timers.filter(t => t.f && t.at <= end).sort((a, b) => a.at - b.at)[0];
    if(!due){ now = end; break; }
    now = due.at;
    const f = due.f;
    if(due.every) due.at += due.every; else due.f = null;
    f(); await flush();
  }
}

let fails = 0;
const ok = (c, m) => { console.log((c ? "ok  " : "FAIL") + " " + m); if(!c) fails++; };

(async () => {
  ctx.parlerInit();
  ok(!$("cvMic").hidden, "mic button visible with browser recognition");
  ok($("cvMissionState").textContent.includes("Pas encore"), "mission box says not done yet");

  await ctx.cvMissionStart(); await flush();
  const CV = () => ctx.CV_get();
  ok(CV().mission && sampleCalls === 1, "mission started, partner spoke first");
  ok(!$("cvClock").hidden && $("cvClock").textContent === "3:00", "clock shown at 3:00");

  await advance(200);
  ok(srInstance && srInstance.started === 1, "mic armed itself after the reply (browser recognition)");

  srInstance.say("Bonjour, je voudrais un rendez-vous");
  ok($("cvIn").value === "Bonjour, je voudrais un rendez-vous", "heard text lands in the field, leading space trimmed");
  await advance(1400);
  ok(CV().n === 1 && sampleCalls === 2, "pause auto-sent the turn and the partner replied");
  ok($("cvIn").value === "", "field cleared after sending");

  await advance(200);
  ok(srInstance.started === 2, "mic re-armed for the next turn");
  srInstance.say("Oui, demain matin");
  await advance(1400);
  ok(CV().n === 2, "second turn sent");

  /* taper désarme l'envoi auto */
  await advance(200);
  srInstance.say("Attendez");
  $("cvIn").fire("input");
  await advance(2000);
  ok(CV().n === 2 && $("cvIn").value === "Attendez", "typing cancels the auto-send");
  $("cvIn").value = "";

  await advance(181 * 1000);
  ok(CV().done, "at 0:00 the debrief ran");
  ok(ctx.S.P.parle.day && ctx.S.P.parle.day.done && ctx.S.P.parle.day.note === 15, "mission counted for the day with its note");
  ok(ctx.S.P.parle.missions === 1, "mission total incremented");
  ok(ctx.S.cards.length === 1, "debrief cards joined the deck");
  ok($("cvClock").hidden && !$("cvMissionGo").hidden, "clock hidden, start button back");
  ok($("cvMissionState").textContent.includes("Faite aujourd'hui"), "mission box now says done");
  ok($("cvNote").textContent.startsWith("Mission faite."), "closing line shown");

  /* mission trop courte : pas de débriefing, pas de crédit */
  ctx.S.P.parle.day = null;
  await ctx.cvMissionStart(); await flush();
  ctx.cvMissionEnd(); await flush();
  ok(!CV().done && !CV().mission, "ending with no turns cancels without a debrief");
  ok(!ctx.S.P.parle.day, "no credit for an empty mission");

  /* arrêt demandé pendant qu'une réplique est en route */
  await ctx.cvMissionStart();          /* resolves after the reply */
  await advance(200);
  srInstance.say("Une phrase"); srInstance.say("et une autre");
  ctx.S.sample = async (t, o) => { await new Promise(r => ctx.setTimeout(r, 3000)); return {text:"lent"}; };
  ctx.S.sample.json = fakeSample.json;
  await advance(1400);                 /* auto-send starts a slow reply */
  ok(CV().busy, "a slow reply is in flight");
  ctx.cvMissionEnd();
  ok(CV().wantEnd && !CV().done, "stop during a reply is queued, not dropped");
  await advance(5000);
  ok(CV().done || !CV().mission, "queued stop honoured once the reply landed");

  console.log(fails ? fails + " FAILURES" : "ALL PASS");
  process.exit(fails ? 1 : 0);
})().catch(e => { console.error(e); process.exit(2); });
