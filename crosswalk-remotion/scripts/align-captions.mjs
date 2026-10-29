// Forced-alignment: keep whisper word TIMINGS, replace TEXT with the real script.
// Whisper mis-hears the brand ("Glute Longevity" -> "Groot's long daily") and other
// words; the speaker read a known script, so we align the script to whisper's timeline.
import fs from 'fs';
import path from 'path';

const ROOT = process.cwd();
const WHISPER = path.join(ROOT, 'src', 'data', 'glute-captions.json');
const OUT = WHISPER;

// The script as actually delivered (clean, brand-correct).
const SCRIPT = `If you're watching this, you just applied for the Glute Longevity 6-Week Protocol.
So first, thank you. Give me two minutes and I'll show you exactly what you've signed up to explore,
and why it's different from anything you've tried.
Here's what most people miss. Your glutes aren't about looks.
They're the foundation of how you move, stand, and stay pain-free as you age.
When they go quiet, from sitting all day, from age, from training the wrong way,
your posture starts to collapse. Your knees and your lower back quietly pick up the slack.
And getting older starts to feel like breaking down.
Most glute programs chase the burn. They never rebuild the strength underneath it.
I'm a former physician. And I got tired of watching capable people accept that decline as if it were inevitable.
It isn't. So I built this protocol around what the research actually supports,
progressive, well-dosed strength work that treats your glutes as the engine of longevity.
Six weeks, six modules, a simple weekly plan you'll actually keep up with,
not a punishing one you'll quit in week two. It meets you where you are and builds from there.
You get the full protocol, the training modules, lifetime access, and a money-back guarantee.
Do the work as designed, and if your strength, posture, and comfort haven't improved, I refund you.
The risk is mine, not yours. So here's what happens next.
I personally review your application within twenty-four hours, then send your enrollment details.
When that email lands, just reply, I'm in.
Founding spots are limited on purpose. I keep this group small so I can stay close to it.
Talk soon.`;

const norm = (s) => s.toLowerCase().replace(/[^a-z0-9]/g, '');

// 1) flatten whisper words (drop punctuation-only tokens, keep timings)
const pagesIn = JSON.parse(fs.readFileSync(WHISPER, 'utf8'));
const wWords = [];
for (const pg of pagesIn) {
  for (const t of pg.tokens) {
    if (norm(t.text)) wWords.push({ n: norm(t.text), fromMs: t.fromMs, toMs: t.toMs });
  }
}

// 2) script words (keep display form + a sentence/break flag)
const rawWords = SCRIPT.split(/\s+/).filter(Boolean);
const sWords = rawWords.map((w) => ({
  disp: w,
  n: norm(w),
  brk: /[.,!?]$/.test(w), // natural caption break after this word
}));

// 3) Needleman-Wunsch alignment (script rows vs whisper cols) on normalized words
const A = sWords.length;
const B = wWords.length;
const GAP = -1;
const dp = Array.from({ length: A + 1 }, () => new Int32Array(B + 1));
for (let i = 0; i <= A; i++) dp[i][0] = i * GAP;
for (let j = 0; j <= B; j++) dp[0][j] = j * GAP;
for (let i = 1; i <= A; i++) {
  for (let j = 1; j <= B; j++) {
    const match = sWords[i - 1].n === wWords[j - 1].n ? 2 : -1;
    dp[i][j] = Math.max(dp[i - 1][j - 1] + match, dp[i - 1][j] + GAP, dp[i][j - 1] + GAP);
  }
}
// traceback -> assign each script word a whisper time (or null)
let i = A, j = B;
const timeFor = new Array(A).fill(null);
while (i > 0 && j > 0) {
  const match = sWords[i - 1].n === wWords[j - 1].n ? 2 : -1;
  if (dp[i][j] === dp[i - 1][j - 1] + match) {
    if (match === 2) timeFor[i - 1] = { fromMs: wWords[j - 1].fromMs, toMs: wWords[j - 1].toMs };
    i--; j--;
  } else if (dp[i][j] === dp[i - 1][j] + GAP) {
    i--; // script word with no whisper match -> interpolate later
  } else {
    j--;
  }
}

// 4) fill nulls by interpolation between known anchors
const lastMs = wWords.length ? wWords[wWords.length - 1].toMs : 0;
for (let k = 0; k < A; k++) {
  if (timeFor[k]) continue;
  let prevEnd = 0;
  for (let a = k - 1; a >= 0; a--) if (timeFor[a]) { prevEnd = timeFor[a].toMs; break; }
  let nextStart = lastMs;
  let nextIdx = A;
  for (let a = k + 1; a < A; a++) if (timeFor[a]) { nextStart = timeFor[a].fromMs; nextIdx = a; break; }
  const span = Math.max(1, nextIdx - (k - 1));
  const step = (nextStart - prevEnd) / span;
  const offset = k - (k - 1);
  const from = Math.round(prevEnd + step * offset);
  timeFor[k] = { fromMs: from, toMs: Math.round(prevEnd + step * (offset + 1)) };
}
// enforce monotonic
for (let k = 1; k < A; k++) {
  if (timeFor[k].fromMs < timeFor[k - 1].fromMs) timeFor[k].fromMs = timeFor[k - 1].fromMs;
  if (timeFor[k].toMs < timeFor[k].fromMs) timeFor[k].toMs = timeFor[k].fromMs + 200;
}

// 5) build pages: short phrases (<=5 words), break on punctuation
const pages = [];
let cur = [];
const flush = () => {
  if (!cur.length) return;
  const toks = cur.map((k) => ({
    text: ' ' + sWords[k].disp,
    fromMs: timeFor[k].fromMs,
    toMs: timeFor[k].toMs,
  }));
  // no leading space on each page's first token (cleaner centering)
  toks[0].text = toks[0].text.trimStart();
  const startMs = toks[0].fromMs;
  const endMs = toks[toks.length - 1].toMs;
  pages.push({ text: toks.map((t) => t.text).join('').trim(), startMs, tokens: toks, durationMs: endMs - startMs });
  cur = [];
};
for (let k = 0; k < A; k++) {
  cur.push(k);
  if (cur.length >= 5 || sWords[k].brk) flush();
}
flush();

fs.writeFileSync(OUT, JSON.stringify(pages, null, 2));
console.log('aligned pages:', pages.length, '| script words:', A, '| whisper words:', B);
console.log('reconstructed:', pages.map((p) => p.text).join(' '));
