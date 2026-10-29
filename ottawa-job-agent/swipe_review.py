"""Mobile-friendly swipe review for jobs sitting in tracker 'pending' status —
a faster way to triage the day's matches on your phone than scrolling the
digest email. Swipe (or tap the buttons): right = "interested", left =
"not interested". This only records your decision in the tracker — it does
NOT trigger auto-apply or a Gmail draft on its own (Sahawat asked Sep18 for
swipe-to-triage first, auto-apply-on-interested is a separate step to build
later, and the standing no-autonomous-send rule still applies regardless).

Run:
    python3 swipe_review.py [port]

Then open the printed URL on your phone (same wifi as this Mac), or
http://localhost:<port> right here.
"""

import json
import socket
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

import tracker

BASE = Path(__file__).resolve().parent
PREFILLED_DIR = BASE / "prefilled"
DEFAULT_PORT = 8765

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8" />
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover" />
<meta name="robots" content="noindex" />
<title>Job Review</title>
<style>
  :root { color-scheme: light dark; }
  * { box-sizing: border-box; }
  body {
    margin: 0; height: 100vh; overflow: hidden;
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    background: #f2f2f4; color: #1a1a1a;
    display: flex; flex-direction: column;
  }
  @media (prefers-color-scheme: dark) {
    body { background: #17181a; color: #f0f0f0; }
    .card { background: #24262a !important; }
    .meta { color: #b8b8bd !important; }
  }
  header {
    padding: 14px 16px 8px; text-align: center; flex: none;
  }
  header h1 { font-size: 17px; margin: 0; font-weight: 600; }
  header .count { font-size: 13px; opacity: 0.6; margin-top: 2px; }
  .stack {
    flex: 1; position: relative; margin: 8px 16px 0;
    max-width: 480px; width: calc(100% - 32px); align-self: center;
  }
  .card {
    position: absolute; inset: 0; background: #fff; border-radius: 20px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.15);
    padding: 20px; display: flex; flex-direction: column;
    touch-action: none; user-select: none; overflow-y: auto;
    transition: transform 0.25s ease, opacity 0.25s ease;
  }
  .card.dragging { transition: none; }
  .badge {
    position: absolute; top: 24px; padding: 6px 14px; border: 3px solid;
    border-radius: 8px; font-weight: 800; font-size: 20px; letter-spacing: 1px;
    opacity: 0; transform: rotate(-12deg);
  }
  .badge.like { left: 20px; color: #22c55e; border-color: #22c55e; }
  .badge.skip { right: 20px; color: #ef4444; border-color: #ef4444; transform: rotate(12deg); }
  .score-chip {
    align-self: flex-start; font-size: 12px; font-weight: 700; padding: 3px 9px;
    border-radius: 999px; background: #eef2ff; color: #4338ca; margin-bottom: 10px;
  }
  .title { font-size: 21px; font-weight: 700; line-height: 1.25; margin: 0 0 4px; }
  .company { font-size: 15px; font-weight: 500; opacity: 0.8; margin: 0 0 10px; }
  .meta { font-size: 13px; color: #666; line-height: 1.6; margin-bottom: 12px; }
  .reason {
    font-size: 13.5px; background: #fafafa; border-left: 3px solid #ccc;
    padding: 8px 10px; border-radius: 6px; margin-bottom: 10px; line-height: 1.45;
  }
  @media (prefers-color-scheme: dark) { .reason { background: #1c1d20; border-color: #444; } }
  .links { margin-top: auto; padding-top: 10px; display: flex; gap: 10px; flex-wrap: wrap; }
  .links a {
    font-size: 13px; color: #4338ca; text-decoration: none; font-weight: 600;
  }
  .empty {
    flex: 1; display: flex; align-items: center; justify-content: center;
    text-align: center; padding: 30px; font-size: 15px; opacity: 0.6;
  }
  .controls {
    flex: none; display: flex; justify-content: center; gap: 28px;
    padding: 18px 0 max(18px, env(safe-area-inset-bottom));
  }
  .controls button {
    width: 60px; height: 60px; border-radius: 50%; border: none;
    font-size: 26px; box-shadow: 0 4px 14px rgba(0,0,0,0.18); cursor: pointer;
  }
  .btn-skip { background: #fff; color: #ef4444; }
  .btn-like { background: #fff; color: #22c55e; }
  @media (prefers-color-scheme: dark) { .controls button { background: #24262a; } }
</style>
</head>
<body>
<header>
  <h1>Job Review</h1>
  <div class="count" id="count"></div>
</header>
<div class="stack" id="stack"></div>
<div class="controls" id="controls" style="display:none">
  <button class="btn-skip" onclick="decide('not_interested')">✕</button>
  <button class="btn-like" onclick="decide('interested')">♥</button>
</div>

<script>
let queue = [];
let totalPending = 0;
let dragging = null;

async function load() {
  const res = await fetch('/api/queue');
  const data = await res.json();
  queue = data.jobs;
  totalPending = data.total_pending;
  render();
}

function render() {
  const stack = document.getElementById('stack');
  const controls = document.getElementById('controls');
  const count = document.getElementById('count');
  stack.innerHTML = '';
  if (!queue.length) {
    stack.innerHTML = '<div class="empty">Nothing waiting for review right now — the next pipeline run will bring more.</div>';
    controls.style.display = 'none';
    count.textContent = '';
    return;
  }
  controls.style.display = 'flex';
  count.textContent = queue.length < totalPending
    ? `${queue.length} of ${totalPending} (top fit first — reload for more after this batch)`
    : queue.length + ' waiting';
  // Render up to 3 cards, deepest first, so the top of the DOM is the top card.
  queue.slice(0, 3).reverse().forEach((job, i, arr) => {
    const depth = arr.length - 1 - i;
    const el = document.createElement('div');
    el.className = 'card';
    el.style.transform = `translateY(${depth * 8}px) scale(${1 - depth * 0.03})`;
    el.style.zIndex = 10 - depth;
    el.innerHTML = cardHtml(job);
    if (depth === 0) attachDrag(el, job);
    stack.appendChild(el);
  });
}

function esc(s) {
  const d = document.createElement('div');
  d.textContent = s || '';
  return d.innerHTML;
}

function cardHtml(job) {
  const score = (job.score !== undefined && job.score !== null) ? job.score : '?';
  const bits = [job.location, job.commute, job.source].filter(Boolean).map(esc).join(' · ');
  const reason = job.no_apply_reason ? `<div class="reason">${esc(job.no_apply_reason)}</div>` : '';
  const links = [];
  if (job.url) links.push(`<a href="${esc(job.url)}" target="_blank" rel="noopener">View posting →</a>`);
  if (job.apply_url && job.apply_url !== job.url) links.push(`<a href="${esc(job.apply_url)}" target="_blank" rel="noopener">Apply link →</a>`);
  if (job.prefill_path) links.push(`<a href="/prefilled/${esc(job.prefill_path.split('/').pop())}" target="_blank" rel="noopener">Prefilled package →</a>`);
  return `
    <div class="badge like">INTERESTED</div>
    <div class="badge skip">SKIP</div>
    <div class="score-chip">Fit ${esc(String(score))}/10</div>
    <div class="title">${esc(job.title)}</div>
    <div class="company">${esc(job.company)}</div>
    <div class="meta">${bits}</div>
    ${reason}
    <div class="links">${links.join('')}</div>
  `;
}

function attachDrag(el, job) {
  let startX = 0, startY = 0, dx = 0, moved = false;
  const like = el.querySelector('.badge.like');
  const skip = el.querySelector('.badge.skip');

  function onDown(e) {
    const p = e.touches ? e.touches[0] : e;
    startX = p.clientX; startY = p.clientY; dx = 0; moved = false;
    el.classList.add('dragging');
    document.addEventListener('mousemove', onMove);
    document.addEventListener('mouseup', onUp);
    document.addEventListener('touchmove', onMove, { passive: false });
    document.addEventListener('touchend', onUp);
  }
  function onMove(e) {
    const p = e.touches ? e.touches[0] : e;
    dx = p.clientX - startX;
    const dy = p.clientY - startY;
    if (Math.abs(dx) > 6) { moved = true; e.preventDefault && e.preventDefault(); }
    el.style.transform = `translate(${dx}px, ${dy * 0.15}px) rotate(${dx / 18}deg)`;
    const t = Math.min(Math.abs(dx) / 100, 1);
    like.style.opacity = dx > 0 ? t : 0;
    skip.style.opacity = dx < 0 ? t : 0;
  }
  function onUp() {
    document.removeEventListener('mousemove', onMove);
    document.removeEventListener('mouseup', onUp);
    document.removeEventListener('touchmove', onMove);
    document.removeEventListener('touchend', onUp);
    el.classList.remove('dragging');
    if (Math.abs(dx) > 100) {
      commit(dx > 0 ? 'interested' : 'not_interested');
    } else {
      el.style.transform = '';
      like.style.opacity = 0; skip.style.opacity = 0;
    }
  }
  el.addEventListener('mousedown', onDown);
  el.addEventListener('touchstart', onDown, { passive: true });

  el._commit = commit;
  function commit(decision) {
    const flyX = decision === 'interested' ? 600 : -600;
    el.style.transform = `translate(${flyX}px, -40px) rotate(${flyX / 18}deg)`;
    el.style.opacity = '0';
    decide(decision, job, el);
  }
}

async function decide(decision, job, el) {
  job = job || queue[0];
  if (!job) return;
  queue = queue.filter(j => j.id !== job.id);
  setTimeout(render, el ? 220 : 0);
  try {
    await fetch('/api/decide', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: job.id, decision })
    });
  } catch (e) {
    console.error('Failed to record decision', e);
  }
}

load();
</script>
</body>
</html>
"""


# Only these are ever read by cardHtml() in the page's JS. The full tracker
# entry also carries history/notes/next_step/etc, which bloated /api/queue to
# ~870KB for ~1000 pending jobs — too large to reliably cross the Tailscale
# tunnel on a phone (this is what caused "the network connection was lost").
_CARD_FIELDS = (
    "score", "location", "commute", "source",
    "no_apply_reason", "url", "apply_url", "prefill_path",
    "title", "company",
)

# The stack only ever shows 3 cards at a time, so there's no reason to ship
# every pending job in one response — cap each load to a batch of the
# top-scored jobs. Reload the page for the next batch once you swipe through.
QUEUE_BATCH_SIZE = 200

# score_fit clusters most postings at 7-9 and caps CHIM-required health
# informatics roles at 3 for certification reasons (see memory
# project_chima_nce_certification) — so raw score alone buries the tracks
# Sahawat actually asked to be watched closely (health informatics/CHEO,
# GoodLife) under higher-scoring but lower-priority categories like
# crossing_guard or sustainability_nonprofit. This tier runs before score.
_CATEGORY_TIER = {
    "health_informatics": 0,
    "health_other": 0,
    "goodlife": 1,
    "healthcare_pt": 1,  # personal-training/fitness roles, not health data — rides with goodlife
}
_DEFAULT_TIER = 2

# These no_apply_reason patterns mean there's no employer-site form to
# finish — the posting only lives on a job board/aggregator (Indeed,
# Glassdoor, ZipRecruiter) that the pipeline treats as discovery-only per
# the plan, or is a re-scrape of a listing already applied to elsewhere.
# Nothing new to review card-by-card, so these sink to the back of the
# queue instead of crowding out postings that need a real decision.
_DEAD_END_MARKERS = (
    "job board", "job-board", "bot-check", "reposted from a bot-blocked",
    "already sent an application to",
)


def _is_dead_end(reason) -> bool:
    reason = (reason or "").lower()
    return any(marker in reason for marker in _DEAD_END_MARKERS)


def _priority(job: dict) -> tuple:
    tier = _CATEGORY_TIER.get(job.get("category"), _DEFAULT_TIER)
    dead_end = 1 if _is_dead_end(job.get("no_apply_reason")) else 0
    return (dead_end, tier, -(job.get("score") or 0))


def _queue() -> dict:
    data = tracker._load()
    jobs = [
        {**{k: entry.get(k) for k in _CARD_FIELDS}, "id": jid, "category": entry.get("category")}
        for jid, entry in data.items()
        if entry.get("status") == "pending"
    ]
    jobs.sort(key=_priority)
    return {"jobs": jobs[:QUEUE_BATCH_SIZE], "total_pending": len(jobs)}


class Handler(BaseHTTPRequestHandler):
    # Default is HTTP/1.0, which closes the connection after every response —
    # fine on localhost/LAN but fragile for a large JSON body over a WireGuard
    # tunnel (Tailscale) on a possibly-cellular phone connection.
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def _send(self, body: bytes, content_type: str, status: int = 200):
        try:
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except (BrokenPipeError, ConnectionResetError) as e:
            sys.stderr.write(f"!! client dropped mid-response: {e!r}\n")

    def _send_json(self, obj, status: int = 200):
        self._send(json.dumps(obj).encode(), "application/json", status)

    def do_GET(self):
        path = urlparse(self.path).path
        if path == "/":
            self._send(PAGE.encode(), "text/html; charset=utf-8")
        elif path == "/api/queue":
            self._send_json(_queue())
        elif path.startswith("/prefilled/"):
            name = Path(path).name
            f = PREFILLED_DIR / name
            if f.suffix == ".html" and f.parent.resolve() == PREFILLED_DIR.resolve() and f.exists():
                self._send(f.read_bytes(), "text/html; charset=utf-8")
            else:
                self._send(b"not found", "text/plain", 404)
        else:
            self._send(b"not found", "text/plain", 404)

    def do_POST(self):
        path = urlparse(self.path).path
        if path != "/api/decide":
            self._send(b"not found", "text/plain", 404)
            return
        length = int(self.headers.get("Content-Length", 0))
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            self._send_json({"error": "bad json"}, 400)
            return
        jid = payload.get("id")
        decision = payload.get("decision")
        if not jid or decision not in ("interested", "not_interested"):
            self._send_json({"error": "id and decision (interested|not_interested) required"}, 400)
            return
        entry = tracker.update_status(jid, decision, "swiped via mobile review")
        if entry is None:
            self._send_json({"error": "job not found"}, 404)
            return
        self._send_json({"ok": True})


def _lan_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    except OSError:
        return "localhost"
    finally:
        s.close()


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PORT
    server = ThreadingHTTPServer(("0.0.0.0", port), Handler)
    print(f"Swipe review running.")
    print(f"  On this Mac:        http://localhost:{port}")
    print(f"  On your phone (same wifi): http://{_lan_ip()}:{port}")
    print("Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
