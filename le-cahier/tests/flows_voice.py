"""La voix et la taille du texte, de bout en bout, sur un vrai serveur HTTP.

Le serveur de test (http.server) ne gère pas les requêtes « Range » : c'est le cas le plus dur
pour une piste où l'on se déplace. Les lectures sont réelles (Chromium décode le MP3) : on
vérifie où la lecture commence et où elle s'arrête, pas seulement qu'on l'a demandée.
"""
import functools
import http.server
import json
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

W = Path(__file__).resolve().parent.parent   # le-cahier/
ROOT = W

fails, errors = [], []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        fails.append(msg)


class Quiet(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *a):
        pass


srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(Quiet, directory=str(ROOT)))
threading.Thread(target=srv.serve_forever, daemon=True).start()
PAGE = f"http://127.0.0.1:{srv.server_address[1]}/index.html"

SEED = """
(() => {
  if (sessionStorage.getItem("seeded")) return;
  sessionStorage.setItem("seeded", "1");
  const dn = Math.round(Date.UTC(new Date().getFullYear(), new Date().getMonth(), new Date().getDate()) / 864e5);
  const P = __P__;
  P.day = {n: dn, fresh: 0};
  P.hero.day = {n: dn, xp: 0, recalls: 9, clean: 0, convo: 0, phrase: 0, grid: 0, exam: 0};
  P.hero.questDay = dn; P.hero.quests = [0, 2, 3]; P.hero.claimed = [];
  P.ring = {day: dn, target: 20, closed: false};
  P.recit = {read: {}, acc: {}, tr: true};
  localStorage.setItem("le-cahier-v1", JSON.stringify(P));
  const srs = {};
  for (let i = 1; i <= 24; i++) srs["t" + i] = [dn - (i % 3), 3 + i, 25, 2, 0, 4, 3];
  localStorage.setItem("le-cahier-srs-v1", JSON.stringify(srs));
  localStorage.setItem("le-cahier-lang", "__LANG__");
  __TEXT__
})();
"""

SPY = """
(() => {
  window.__spoken = [];
  if (!("speechSynthesis" in window)) return;
  speechSynthesis.speak = (u) => window.__spoken.push({text: u.text, lang: u.lang, voice: u.voice ? u.voice.name : null});
})();
"""


def make(b, w=1280, h=860, lang="fr", text=None):
    ctx = b.new_context(viewport={"width": w, "height": h})
    pg = ctx.new_page()
    pg.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
    pg.on("console", lambda m: errors.append(f"console.error: {m.text}") if m.type == "error" else None)
    P = {"streak": 3, "last": "2000-01-01", "days": 9, "level": 2, "tested": True,
         "recall": {"rev": 40, "ok": 30},
         "hero": {"xp": 520, "name": "Léa", "avatar": "🦊", "cls": "erudit", "created": 1,
                  "ach": {"spark": 1, "hundred": 1, "ring": 1}}}
    t = f'localStorage.setItem("le-cahier-texte", "{text}");' if text is not None else ""
    pg.add_init_script(SEED.replace("__P__", json.dumps(P)).replace("__LANG__", lang).replace("__TEXT__", t))
    pg.add_init_script(SPY)
    pg.goto(PAGE)
    pg.wait_for_timeout(1300)
    return ctx, pg


def ev(pg, js):
    return pg.evaluate(js)


def playing(pg):
    """L'élément audio en cours : sa piste, sa position, s'il joue."""
    return ev(pg, """(() => { const a = vrCur; if (!a) return null;
      const name = Object.keys(vrEls).find(k => vrEls[k] === a) || a.src.split('/').pop();
      return {src: name, t: a.currentTime, paused: a.paused, blob: a.src.startsWith('blob:')}; })()""")


def seg_of(pg, text):
    return ev(pg, f"VOIX_REC[dStrip({json.dumps(text)})] || null")


with sync_playwright() as p:
    # Sortie audio factice à horloge réelle : sans elle, Chrome sans écran dépend de la carte
    # son du Mac, dont l'horloge peut se figer et fausser les mesures de position.
    b = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required", "--disable-audio-output"])

    # ---------------------------------------------------------------- V1 : le récit lit avec la vraie voix
    ctx, pg = make(b)
    check(ev(pg, "typeof VOIX_REC_RECIT === 'object' && Object.keys(VOIX_REC_RECIT).length") == 164,
          "V1 la carte des voix du récit est chargée (164 phrases)")
    check(ev(pg, "Object.keys(VOIX_REC_RECIT).every(k => VOIX_REC[k])"), "V1 …et fusionnée dans VOIX_REC")
    missing = ev(pg, """RECIT.pages.flatMap(p => p.lines.filter(l => l.w !== '?').map(l => rcSpoken(l.fr))
      .concat(p.lines.filter(l => l.w === '?').flatMap(l => l.c.filter(o => o[2]).map(o => rcSpoken(o[0]))))
      .concat(p.cards.map(c => c.s.replace('___', c.a)))).filter(t => !VOIX_REC[dStrip(t)])""")
    check(missing == [], f"V1 chaque réplique, réponse juste et phrase de carte a son enregistrement ({len(missing)} sans)")
    check(ev(pg, "rcSpoken('Tu vas m\\u2019aider, {nom} ?'.replace('\\u2019', \"'\"))") == "Tu vas m'aider ?",
          "V1 le prénom est retiré de ce qui est dit (« Tu vas m'aider ? »)")
    check(ev(pg, "rcSpoken('{nom}, va à la boulangerie.')") == "Va à la boulangerie.", "V1 …et en tête de phrase (« Va à la boulangerie. »)")
    pg.click("#jStory .go")
    pg.wait_for_timeout(900)
    a = playing(pg)
    first = ev(pg, "rcSpoken(RECIT.pages[0].lines[0].fr)")
    seg = seg_of(pg, first)
    check(a is not None and a["src"] == "voix-r00.mp3", f"V1 la première réplique joue la piste de la page ({a and a['src']})")
    check(a is not None and a["blob"], "V1 …chargée entière en mémoire (on peut s'y déplacer sans l'aide du serveur)")
    check(a is not None and seg[0] - .05 <= a["t"] <= seg[0] + seg[1] + .3,
          f"V1 …au bon endroit de la piste (t={a and round(a['t'], 2)}, phrase {seg[0]}–{round(seg[0] + seg[1], 2)})")
    check(ev(pg, "window.__spoken.length") == 0, "V1 aucune synthèse du navigateur")
    pg.wait_for_timeout(int((seg[1] + 1.0) * 1000))
    a = playing(pg)
    check(a["paused"], "V1 la lecture s'arrête d'elle-même")
    end = seg[0] + seg[1]
    check(end - .15 <= a["t"] <= end + .3, f"V1 …à la fin de la phrase, pas avant (t={round(a['t'], 2)}, fin {round(end, 2)})")
    # une réplique d'un personnage, avec le prénom à l'écran mais pas dans la voix
    for _ in range(12):
        if ev(pg, "RC.i") >= 10 or pg.query_selector(".rc-choice"):
            break
        pg.click("#rcNext"); pg.wait_for_timeout(150)
    pg.keyboard.press("Escape")
    ctx.close()

    # ---------------------------------------------------------------- V2 : Le Trou (« gap fill ») a sa voix
    ctx, pg = make(b)
    pg.click("#tab-trou"); pg.wait_for_timeout(300)
    item = ev(pg, "({s: T.item.s, a: T.item.a, id: T.item.id})")
    full = item["s"].replace("___", item["a"])
    seg = seg_of(pg, full)
    check(seg is not None, f"V2 la phrase « {full[:40]}… » a un enregistrement")
    pg.fill("#trouIn", item["a"])
    pg.keyboard.press("Enter")
    pg.wait_for_timeout(700)
    a = playing(pg)
    want_src = seg[2] if len(seg) > 2 else "voix.mp3"
    check(a is not None and a["src"] == want_src, f"V2 la réponse déclenche la vraie voix ({a and a['src']})")
    check(a is not None and seg[0] - .05 <= a["t"] <= seg[0] + seg[1] + .3, f"V2 …sur la bonne phrase (t={a and round(a['t'], 2)})")
    check(ev(pg, "window.__spoken.length") == 0, "V2 …et pas la synthèse")
    btn = ev(pg, "[...document.querySelectorAll('#trouAfter button')].map(b => b.textContent)")
    check(any("Écouter" in t or "Listen" in t for t in btn), f"V2 un bouton « Écouter » reste pour réentendre ({btn})")
    pg.wait_for_timeout(int((seg[1] + 1.0) * 1000))
    a = playing(pg)
    check(a["paused"] and seg[0] + seg[1] - .15 <= a["t"] <= seg[0] + seg[1] + .3,
          f"V2 elle s'arrête à la fin de la phrase (t={round(a['t'], 2)}, fin {round(seg[0] + seg[1], 2)})")
    ev(pg, "[...document.querySelectorAll('#trouAfter button')].find(b => /Écouter|Listen/.test(b.textContent)).click()")
    pg.wait_for_timeout(500)
    a = playing(pg)
    check(a is not None and not a["paused"], "V2 « Écouter » rejoue la phrase")
    ev(pg, "[...document.querySelectorAll('#trouAfter button')].find(b => /suivante|Next/i.test(b.textContent)).click()")
    pg.wait_for_timeout(200)
    check(playing(pg)["paused"], "V2 « Phrase suivante » coupe la voix")
    ctx.close()

    # ---------------------------------------------------------------- V3 : la Séance dit la phrase à trou après la réponse
    ctx, pg = make(b)
    pg.click("#tab-seance"); pg.wait_for_timeout(400)
    found = False
    for _ in range(40):
        if ev(pg, "SE && SE.cur && SE.cur.kind") == "trou" and ev(pg, "SE.i < SE.q.length - 2"):
            found = True
            break
        if ev(pg, "SE.i >= SE.q.length - 3"):
            break
        ev(pg, "SE.i++; renderCard()")
        pg.wait_for_timeout(60)
    check(found, "V3 une carte à trou dans la séance")
    c = ev(pg, "({s: SE.cur.data.s, a: SE.cur.data.a})")
    full = c["s"].replace("___", c["a"])
    seg = seg_of(pg, full)
    pg.fill("#seIn", c["a"])
    pg.keyboard.press("Enter")
    pg.wait_for_timeout(700)
    a = playing(pg)
    check(seg is not None and a is not None and not a["paused"] and seg[0] - .05 <= a["t"] <= seg[0] + seg[1] + .3,
          f"V3 après la réponse, la phrase entière est dite par la vraie voix (t={a and round(a['t'], 2)})")
    check(ev(pg, "window.__spoken.length") == 0, "V3 …sans synthèse")
    check(ev(pg, "[...document.querySelectorAll('#seAfter button')].some(b => /Écouter|Listen/.test(b.textContent))"),
          "V3 un bouton pour la réentendre")
    before = ev(pg, "vrToken")
    ev(pg, "nextCard()")
    kind = ev(pg, "SE.cur.kind")
    pg.wait_for_timeout(60)
    a = playing(pg)
    check(ev(pg, "vrToken") > before and (a is None or a["paused"] or kind in ("dictee", "son", "mot", "imiter")),
          f"V3 la carte suivante coupe la voix (carte suivante : {kind}, en pause : {a and a['paused']})")
    ctx.close()

    # ---------------------------------------------------------------- V4 : jamais une voix anglaise pour du français
    ctx, pg = make(b)
    ev(pg, """(() => {
      window.SpeechSynthesisUtterance = class { constructor(t){ this.text = t; } };
      speechSynthesis.getVoices = () => [{name: 'Samantha', lang: 'en-US', voiceURI: 'Samantha', localService: true}];
    })()""")
    ev(pg, "synthFr('le parapluie', 1)")
    pg.wait_for_timeout(200)
    check(ev(pg, "window.__spoken.length") == 0, "V4 seulement des voix anglaises : on ne lit pas le français avec elles")
    toast = ev(pg, "document.getElementById('toasts').textContent")
    check("voix française" in toast or "French voice" in toast, "V4 …et on le dit une fois, avec la marche à suivre")
    ev(pg, """speechSynthesis.getVoices = () => [{name: 'Samantha', lang: 'en-US', voiceURI: 'Samantha', localService: true},
      {name: 'Amélie', lang: 'fr-CA', voiceURI: 'Amélie', localService: true}, {name: 'Thomas', lang: 'fr-FR', voiceURI: 'Thomas', localService: true}]""")
    ev(pg, "synthFr('le parapluie', 1)")
    pg.wait_for_timeout(200)
    s = ev(pg, "window.__spoken")
    check(len(s) == 1 and s[0]["voice"] in ("Amélie", "Thomas") and s[0]["lang"].startswith("fr"),
          f"V4 une voix française existe : c'est elle qui parle ({s})")
    # la liste des voix arrive en retard (Chrome) : on attend, puis on parle français
    ev(pg, """(() => { window.__spoken.length = 0; speechSynthesis.getVoices = () => [];
      setTimeout(() => { speechSynthesis.getVoices = () => [{name: 'Thomas', lang: 'fr-FR', voiceURI: 'Thomas', localService: true}];
        speechSynthesis.dispatchEvent(new Event('voiceschanged')); }, 300); })()""")
    ev(pg, "VOICES_WAIT = null; synthFr('la gare', 1)")
    pg.wait_for_timeout(120)
    check(ev(pg, "window.__spoken.length") == 0, "V4 liste des voix pas encore là : on attend au lieu de parler n'importe comment")
    pg.wait_for_timeout(500)
    s = ev(pg, "window.__spoken")
    check(len(s) == 1 and s[0]["voice"] == "Thomas", f"V4 …puis on parle avec la voix française ({s})")
    ctx.close()

    # ---------------------------------------------------------------- V5 : un mot seul (non enregistré) passe par la synthèse française
    ctx, pg = make(b)
    ev(pg, """(() => { window.SpeechSynthesisUtterance = class { constructor(t){ this.text = t; } };
      speechSynthesis.getVoices = () => [{name: 'Thomas', lang: 'fr-FR', voiceURI: 'Thomas', localService: true}]; })()""")
    ev(pg, "speakFr('parapluie', .9)")
    pg.wait_for_timeout(150)
    s = ev(pg, "window.__spoken")
    check(len(s) == 1 and s[0]["voice"] == "Thomas", "V5 un mot sans enregistrement : synthèse, voix française")
    ctx.close()

    # ---------------------------------------------------------------- T : la taille du texte
    def root_px(pg):
        return ev(pg, "parseFloat(getComputedStyle(document.documentElement).fontSize)")

    ctx, pg = make(b, 1280, 800)
    check(ev(pg, "document.documentElement.getAttribute('data-text')") is None, "T1 sans choix : pas d'attribut, la feuille de style décide")
    check(root_px(pg) == 20, f"T1 grand écran : texte à 125 % par défaut ({root_px(pg)} px)")
    body_px = ev(pg, "parseFloat(getComputedStyle(document.body).fontSize)")
    check(abs(body_px - 23.125) < .2, f"T1 le texte courant passe de 18,5 à ~23 px ({body_px})")
    pg.click("#txtUp"); pg.wait_for_timeout(150)
    check(root_px(pg) == 22.4 and ev(pg, "document.getElementById('txtUp').disabled"), "T2 A+ : 140 %, et A+ s'éteint au dernier cran")
    for _ in range(3):
        pg.click("#txtDown"); pg.wait_for_timeout(100)
    check(root_px(pg) == 16 and ev(pg, "document.getElementById('txtDown').disabled"), "T2 A− ×3 : 100 %, A− s'éteint au premier cran")
    pg.click("#txtUp"); pg.wait_for_timeout(100)
    check(ev(pg, "localStorage.getItem('le-cahier-texte')") == "1", "T3 le choix est gardé sur l'appareil")
    pg.reload(); pg.wait_for_timeout(1300)
    check(root_px(pg) == 18, f"T3 …et retrouvé au rechargement ({root_px(pg)} px)")
    ctx.close()

    ctx, pg = make(b, 390, 844)
    check(root_px(pg) == 16, "T4 téléphone : 100 % par défaut, rien ne change")
    check(ev(pg, "document.documentElement.scrollWidth <= innerWidth + 1"), "T4 …sans débordement")
    ctx.close()

    for w, h in [(1280, 800), (1440, 900), (1024, 768), (768, 1024)]:
        for lvl in range(4):
            ctx, pg = make(b, w, h, text=lvl)
            tag = f"T5 {w}px cran {lvl}"
            over = ev(pg, "document.documentElement.scrollWidth - innerWidth")
            labels = ev(pg, """[...document.querySelectorAll('.world .tab')].filter(t => t.scrollWidth > t.clientWidth + 1
              || [...t.children].some(c => c.scrollWidth > c.clientWidth + 1)).map(t => t.id)""")
            cols = ev(pg, "getComputedStyle(document.querySelector('.world')).gridTemplateColumns.split(' ').length")
            ok = over <= 1 and labels == []
            if not ok:
                check(False, f"{tag} : débordement {over}px, onglets trop serrés {labels}")
            # le lecteur tient dans l'écran
            ev(pg, "recitOpen('p00', true)")
            pg.wait_for_timeout(250)
            box = ev(pg, "(() => { const r = document.getElementById('rcCard').getBoundingClientRect(); return [r.left, r.right, r.top, r.bottom]; })()")
            if not (box[0] >= 0 and box[1] <= w + .5 and box[2] >= 0 and box[3] <= h + .5):
                check(False, f"{tag} : le lecteur sort de l'écran {[round(x) for x in box]}")
            if w == 1440 and lvl == 2:
                check(cols == 10, f"T5 1440px, 125 % : la carte du monde tient sur une rangée ({cols} colonnes)")
            if cols not in (5, 10):
                check(False, f"{tag} : la carte du monde a {cols} colonnes (10 ou 5 attendues)")
            ctx.close()
    check(True, "T5 4 largeurs × 4 crans : pas de débordement, aucun nom d'onglet coupé, le lecteur tient dans l'écran")

    b.close()

srv.shutdown()
print()
print("erreurs de console / page :", len(errors))
for e in errors[:8]:
    print("   ", e)
print("ÉCHECS :", len(fails))
for f in fails:
    print("   -", f)
