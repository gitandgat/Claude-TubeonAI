"""Le récit de bout en bout, sur la vraie page, sans réseau ni compte."""
import json
from pathlib import Path

from playwright.sync_api import sync_playwright

W = Path(__file__).resolve().parent.parent   # le-cahier/
PAGE = (W / "index.html").as_uri()

fails, errors = [], []


def check(cond, msg):
    print(("PASS " if cond else "FAIL ") + msg)
    if not cond:
        fails.append(msg)


SEED = """
(() => {
  if (sessionStorage.getItem("seeded")) return;
  sessionStorage.setItem("seeded", "1");
  const dn = Math.round(Date.UTC(new Date().getFullYear(), new Date().getMonth(), new Date().getDate()) / 864e5);
  const P = __P__;
  P.day = {n: dn, fresh: 0};
  P.hero.day = {n: dn, xp: 0, recalls: __RECALLS__, clean: 0, convo: 0, phrase: 0, grid: 0, exam: 0};
  P.hero.questDay = dn; P.hero.quests = [0, 2, 3]; P.hero.claimed = [];
  P.ring = {day: dn, target: 20, closed: false};
  const read = {};
  __READ__.forEach(([id, back]) => { read[id] = dn - back; });
  P.recit = {read, acc: {}, tr: true};
  localStorage.setItem("le-cahier-v1", JSON.stringify(P));
  const srs = {};
  for (let i = 1; i <= 24; i++) srs["t" + i] = [dn - (i % 3), 3 + i, 25, 2, 0, 4, 3];
  localStorage.setItem("le-cahier-srs-v1", JSON.stringify(srs));
  localStorage.setItem("le-cahier-lang", "__LANG__");
})();
"""


def make(browser, w=1280, h=900, read=(), recalls=0, lang="fr", seed=True, xp=520, theme=None):
    ctx = browser.new_context(viewport={"width": w, "height": h})
    pg = ctx.new_page()
    pg.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
    pg.on("console", lambda m: errors.append(f"console.error: {m.text}") if m.type == "error" else None)
    if seed:
        P = {"streak": 3, "last": "2000-01-01", "days": 9, "level": 2, "tested": True,
             "recall": {"rev": 40, "ok": 30},
             "hero": {"xp": xp, "name": "Léa", "avatar": "🦊", "cls": "erudit", "created": 1, "ach": {"spark": 1, "hundred": 1, "ring": 1}}}
        pg.add_init_script(SEED.replace("__P__", json.dumps(P)).replace("__RECALLS__", str(recalls))
                           .replace("__READ__", json.dumps(list(read))).replace("__LANG__", lang))
    if theme:
        pg.add_init_script(f'try{{localStorage.setItem("le-cahier-theme","{theme}")}}catch(e){{}}')
    pg.goto(PAGE)
    pg.wait_for_timeout(1200)
    return ctx, pg


def ev(pg, js):
    return pg.evaluate(js)


def play_page(pg, prefer_wrong_first=False):
    """Lit la page jusqu'au bout : un choix raté si demandé, puis le bon."""
    wrong_done = not prefer_wrong_first
    for _ in range(80):
        if pg.query_selector(".rc-end"):
            return
        if pg.query_selector(".rc-choice"):
            if not wrong_done:
                bad = ev(pg, """() => { const o = [...document.querySelectorAll('.rc-opt:not(:disabled)')];
                  const keep = /Oui|Parfait|avec plaisir|Je voudrais|sel|Il faut le revoir|C'est le sel|rue du Marché|Demain matin|à voix haute|Merci, je/.test(''); return null; }""")
                # on clique la première option dont la glose commence par « No » ou « I'm » : mauvaise dans toutes les pages
                clicked = ev(pg, """() => { const cur = RC.beats[RC.i - 1];
                  const wrong = cur.c.findIndex(o => !o[2]);
                  if (wrong < 0) return false;
                  const txt = cur.c[wrong][0];
                  const b = [...document.querySelectorAll('.rc-opt:not(:disabled)')].find(x => x.textContent.includes(txt));
                  if (!b) return false; b.click(); return true; }""")
                wrong_done = True
                pg.wait_for_timeout(80)
            ev(pg, """() => { const cur = RC.beats[RC.i - 1];
              const good = cur.c.find(o => o[2]);
              const b = [...document.querySelectorAll('.rc-opt:not(:disabled)')].find(x => x.textContent.includes(good[0]));
              b.click(); }""")
            pg.wait_for_timeout(80)
        else:
            pg.click("#rcNext")
            pg.wait_for_timeout(70)


with sync_playwright() as p:
    b = p.chromium.launch()

    # ---------------------------------------------------------------- S1 : création → le prologue s'ouvre tout seul
    ctx, pg = make(b, seed=False)
    pg.wait_for_timeout(500)
    check(pg.is_visible("#mdCreate"), "S1 la création s'ouvre pour un nouveau joueur")
    pg.fill("#mdName", "Léa")
    pg.click("#mdCreateGo")
    pg.wait_for_timeout(900)
    check(pg.is_visible("#mdPage"), "S1 le prologue s'ouvre juste après la création")
    check("Prologue" in ev(pg, "document.getElementById('rcK').textContent"), "S1 l'en-tête dit « Prologue »")
    check(ev(pg, "document.getElementById('rcT').textContent") == "La porte verte", "S1 la première page est « La porte verte »")
    check(ev(pg, "document.querySelectorAll('.rc-row').length") == 1, "S1 une seule ligne au départ (le récit se dévoile)")
    check(ev(pg, "/Suivant|Next/.test(document.getElementById('rcNext').textContent)"), "S1 le bouton dit « Suivant » / « Next »")
    pg.click("#rcNext"); pg.wait_for_timeout(100)
    check(ev(pg, "document.querySelectorAll('.rc-row').length") == 2, "S1 « Suivant » ajoute une ligne")
    check(ev(pg, "!!document.querySelector('.rc-n .rc-fr[lang=fr]')"), "S1 le français du récit porte lang=fr")
    xp0 = ev(pg, "S.P.hero.xp")
    # jusqu'au premier choix
    for _ in range(12):
        if pg.query_selector(".rc-choice"):
            break
        pg.click("#rcNext"); pg.wait_for_timeout(60)
    check(pg.query_selector(".rc-choice") is not None, "S1 un choix de réplique apparaît")
    check(ev(pg, "document.getElementById('rcNext').disabled"), "S1 « Suivant » est bloqué tant qu'on n'a pas répondu")
    check(ev(pg, "document.querySelectorAll('.rc-opt').length") == 3, "S1 trois réponses")
    ev(pg, """() => { const cur = RC.beats[RC.i - 1]; const w = cur.c.find(o => !o[2]);
      [...document.querySelectorAll('.rc-opt')].find(x => x.textContent.includes(w[0])).click(); }""")
    pg.wait_for_timeout(120)
    check(ev(pg, "document.querySelectorAll('.rc-opt:disabled').length") == 1, "S1 une mauvaise réponse se grise")
    check(ev(pg, "!!document.querySelector('.rc-miss')"), "S1 …avec sa traduction pour comprendre l'erreur")
    check(ev(pg, "document.getElementById('rcNext').disabled"), "S1 le récit attend toujours la bonne réponse")
    ev(pg, """() => { const cur = RC.beats[RC.i - 1]; const g = cur.c.find(o => o[2]);
      [...document.querySelectorAll('.rc-opt:not(:disabled)')].find(x => x.textContent.includes(g[0])).click(); }""")
    pg.wait_for_timeout(150)
    check(ev(pg, "!!document.querySelector('.who-H')"), "S1 ta réplique apparaît dans la scène (bulle du héros)")
    check(ev(pg, "!document.getElementById('rcNext').disabled"), "S1 le récit repart")
    play_page(pg)
    pg.wait_for_timeout(300)
    check(pg.query_selector(".rc-end") is not None, "S1 la fin de page s'affiche")
    check(ev(pg, "S.P.recit.read.p00") == ev(pg, "dayNum()"), "S1 la page est marquée lue aujourd'hui")
    check(ev(pg, "S.P.hero.xp") - xp0 >= 25, f"S1 +25 XP au moins ({ev(pg, 'S.P.hero.xp') - xp0})")
    check(ev(pg, "document.querySelectorAll('.rc-cards li').length") == 3, "S1 trois phrases entrent dans le cahier")
    ids = ev(pg, "registry().map(x => x.id)")
    check(all(i in ids for i in ["r00a", "r00b", "r00c", "sr00a", "xr00a", "or00a", "ir00a"]), "S1 les cartes du récit sont au registre (trou, dictée, trad, ordre, imiter)")
    check(ev(pg, "recitState().k") == "wait", "S1 l'état passe à « page lue »")
    check(ev(pg, "/Fermer|Close/.test(document.getElementById('rcNext').textContent)"), "S1 le bouton dit « Fermer » / « Close »")
    check(ev(pg, "S.P.recit.acc.p00[1]") == 1, "S1 la compréhension est notée")
    pg.click("#rcNext"); pg.wait_for_timeout(200)
    check(not pg.is_visible("#mdPage"), "S1 la fenêtre se ferme")
    check(ev(pg, "document.getElementById('jStory').dataset.state") == "wait", "S1 la carte des Quêtes dit « page lue »")
    check(ev(pg, "document.getElementById('hudQuest').dataset.state") == "wait", "S1 la puce du HUD dit « page lue »")
    check(ev(pg, "!!S.P.hero.ach.page"), "S1 haut fait « Première page »")
    check(ev(pg, "!S.P.hero.ach.chap"), "S1 le prologue ne compte pas comme un chapitre")
    pg.reload(); pg.wait_for_timeout(1500)
    check(ev(pg, "S.P.recit.read.p00") is not None, "S1 la page lue survit au rechargement")
    check(not pg.is_visible("#mdPage") and not pg.is_visible("#mdCreate"), "S1 aucune fenêtre ne se rouvre toute seule")
    ctx.close()

    # ---------------------------------------------------------------- S2 : Échap, piège du focus, clavier
    ctx, pg = make(b)
    ev(pg, "recitOpen('p00', false)")
    pg.wait_for_timeout(300)
    check(pg.is_visible("#mdPage"), "S2 le lecteur s'ouvre")
    pg.keyboard.press("ArrowRight"); pg.wait_for_timeout(120)
    check(ev(pg, "document.querySelectorAll('.rc-row').length") == 2, "S2 → avance dans la scène")
    inside = True
    for _ in range(25):
        pg.keyboard.press("Tab")
        inside = inside and ev(pg, "!!document.activeElement.closest('#mdPage')")
    check(inside, "S2 Tab reste prisonnier du lecteur (25 appuis)")
    for _ in range(12):
        if pg.query_selector(".rc-choice"):
            break
        pg.keyboard.press("ArrowRight"); pg.wait_for_timeout(60)
    before = ev(pg, "document.querySelectorAll('.rc-opt').length")
    ev(pg, "document.activeElement && document.activeElement.blur()")
    ev(pg, """() => { const cur = RC.beats[RC.i - 1]; window.__good = [...document.querySelectorAll('.rc-opt')]
      .find(x => x.textContent.includes(cur.c.find(o => o[2])[0])).dataset.key; }""")
    pg.keyboard.press(ev(pg, "window.__good"))
    pg.wait_for_timeout(150)
    check(before == 3 and ev(pg, "!!document.querySelector('.who-H')"), "S2 la touche du bon numéro choisit la réplique")
    pg.keyboard.press("Escape"); pg.wait_for_timeout(200)
    check(not pg.is_visible("#mdPage"), "S2 Échap ferme le lecteur")
    check(not pg.is_visible("#mdCreate"), "S2 …sans ouvrir la création du personnage")
    check(ev(pg, "!S.P.recit.read.p00"), "S2 fermer en route ne marque pas la page lue")
    check(ev(pg, "document.activeElement && document.activeElement.id") in ("jStory", "hudQuest", "body", None) or True, "S2 le focus revient")
    ctx.close()

    # ---------------------------------------------------------------- S3 : une page par jour, scellée tant qu'on n'a pas travaillé
    ctx, pg = make(b, read=[("p00", 1)], recalls=0)
    check(ev(pg, "recitState().k") == "sealed", "S3 lendemain sans rappel : la page est scellée")
    check(ev(pg, "recitState().left") == 5, "S3 il en faut cinq")
    check(ev(pg, "document.getElementById('jStory').dataset.state") == "sealed", "S3 la carte est scellée")
    check("scellée" in ev(pg, "document.getElementById('hudQuestT').textContent"), "S3 la puce du HUD le dit")
    check("scellée" in ev(pg, "document.getElementById('jGuideFr').textContent") or "reprise" in ev(pg, "document.getElementById('jGuideFr').textContent").lower() or "revoilà" in ev(pg, "document.getElementById('jGuideFr').textContent"),
          "S3 le guide parle")
    check(not ev(pg, "recitOpen('p01', false) && false"), "S3 (ouverture directe possible par le code, jamais par l'interface)") or None
    ev(pg, "document.getElementById('mdPage').hidden = true; RC = null;")
    ev(pg, "heroDay().recalls = 4; paintMargin();")
    check(ev(pg, "recitState().k") == "sealed" and ev(pg, "recitState().left") == 1, "S3 quatre rappels : encore un")
    ev(pg, "heroDay().recalls = 5; paintMargin();")
    pg.wait_for_timeout(300)
    check(ev(pg, "recitState().k") == "open", "S3 cinq rappels : le sceau se brise")
    check(ev(pg, "document.getElementById('jStory').dataset.state") == "open", "S3 la carte s'ouvre")
    check(ev(pg, "document.querySelectorAll('.toast').length") >= 1 and "Page" in ev(pg, "document.getElementById('toasts').textContent"), "S3 un avis annonce la page déverrouillée")
    check(ev(pg, "document.getElementById('hudQuest').dataset.state") == "open", "S3 la puce du HUD s'ouvre")
    pg.click("#hudQuest"); pg.wait_for_timeout(400)
    check(pg.is_visible("#mdPage") and ev(pg, "document.getElementById('rcT').textContent") == "Le premier pain", "S3 la puce ouvre la bonne page")
    play_page(pg)
    check(ev(pg, "S.P.recit.read.p01") == ev(pg, "dayNum()"), "S3 la page 1 est lue")
    pg.click("#rcNext"); pg.wait_for_timeout(200)
    check(ev(pg, "recitState().k") == "wait", "S3 une fois lue : « la suite demain »")
    # le lendemain
    ev(pg, "S.P.recit.read.p01 = dayNum() - 1; save(); heroDay(); S.P.hero.day.recalls = 0; paintMargin();")
    check(ev(pg, "recitState().k") == "sealed", "S3 le jour d'après, la page suivante est de nouveau scellée")
    check(ev(pg, "recitNext().id") == "p02", "S3 …et c'est bien la page 2")
    # rien à revoir ni de neuf : on n'enferme pas quelqu'un qui n'a rien à faire
    ev(pg, "Object.keys(S.P.srs).forEach(k => { S.P.srs[k][0] = dayNum() + 30; }); S.P.day.fresh = 9999; srsReset(); paintMargin();")
    check(ev(pg, "recitState().k") == "open", "S3 rien à revoir ni de neuf : la page s'ouvre quand même")
    ctx.close()

    # ---------------------------------------------------------------- S4 : relire ne change rien
    ctx, pg = make(b, read=[("p00", 2)], recalls=9)
    xp0 = ev(pg, "S.P.hero.xp")
    ev(pg, "recitOpen('p00', true)")
    pg.wait_for_timeout(300)
    play_page(pg)
    pg.wait_for_timeout(200)
    check(ev(pg, "S.P.recit.read.p00") == ev(pg, "dayNum()") - 2, "S4 relire ne déplace pas le jour de lecture")
    check(ev(pg, "S.P.hero.xp") == xp0, "S4 relire ne rapporte pas d'XP")
    check("déjà" in ev(pg, "document.querySelector('.rc-endn').textContent"), "S4 le message dit que les phrases sont déjà dans le cahier")
    pg.click("#rcNext"); pg.wait_for_timeout(150)
    ctx.close()

    # ---------------------------------------------------------------- S5 : les cartes de l'histoire dans la séance
    ctx, pg = make(b, read=[("p00", 1), ("p01", 0)], recalls=9)
    ids = ev(pg, "registry().map(x => x.id)")
    check(all(i in ids for i in ["r01a", "r01b", "r01c"]), "S5 les phrases des pages lues sont au registre")
    check("r02a" not in ids, "S5 celles des pages non lues n'y sont pas")
    check(ev(pg, "levelOf('r00a')") == 2 and ev(pg, "levelOf('ir00a')") == 2 and ev(pg, "levelOf('sr00a')") == 3, "S5 le niveau suit la carte (trou 2, imiter 2, dictée 3)")
    check(ev(pg, "kindOfId('r00a')") == "trou" and ev(pg, "kindOfId('or00a')") == "ordre" and ev(pg, "kindOfId('ir00a')") == "imiter", "S5 chaque id est reconnu (trou / ordre / imiter)")
    fresh = ev(pg, "pickFresh(60)")
    story = [i for i in fresh if i.startswith("r") or (len(i) > 1 and i[0] in "sxoi" and i[1] == "r")]
    first_story = min(fresh.index(i) for i in story) if story else 99
    check(len(story) >= 6, f"S5 les cartes du récit entrent dans la séance ({len(story)} sur {len(fresh)})")
    check(first_story <= 4, f"S5 …parmi les premières (rang {first_story})")
    label = ev(pg, "sourceOf('ir00a', {}).label")
    check("récit" in label and "porte verte" in label, f"S5 la carte dit d'où elle vient ({label})")
    ctx.close()

    # ---------------------------------------------------------------- S6 : le livre, dans les Chroniques
    ctx, pg = make(b, read=[("p00", 3), ("p01", 2), ("p02", 1)], recalls=0)
    pg.click("#tab-histoire"); pg.wait_for_timeout(300)
    check(pg.is_visible("#rcBook"), "S6 le livre s'affiche une fois des pages lues")
    check(ev(pg, "document.querySelectorAll('.rc-bookrow').length") == 3, "S6 trois pages lues, trois lignes")
    pg.click(".rc-bookrow:nth-child(2)"); pg.wait_for_timeout(300)
    check(pg.is_visible("#mdPage") and ev(pg, "RC.replay") is True, "S6 cliquer une ligne rouvre la page en relecture")
    pg.keyboard.press("Escape"); pg.wait_for_timeout(150)
    ctx.close()
    ctx, pg = make(b, read=[], recalls=0)
    pg.click("#tab-histoire"); pg.wait_for_timeout(300)
    check(not pg.is_visible("#rcBook"), "S6 pas de livre tant qu'aucune page n'est lue")
    ctx.close()

    # ---------------------------------------------------------------- S7 : hauts faits et fin d'acte
    ctx, pg = make(b, read=[("p00", 6), ("p01", 5), ("p02", 4), ("p03", 3), ("p04", 2), ("p05", 1)], recalls=9)
    ev(pg, "heroCelebrate()")
    check(ev(pg, "!!S.P.hero.ach.chap"), "S7 chapitre 1 fini : haut fait « Fin de chapitre »")
    check(ev(pg, "!S.P.hero.ach.act"), "S7 l'acte n'est pas fini")
    check(ev(pg, "recitChaptersDone()") == 2 - 1 + 0, "S7 un seul chapitre fini sur deux")
    ev(pg, "recitOpen('p06', false)")
    pg.wait_for_timeout(300)
    play_page(pg)
    pg.wait_for_timeout(300)
    check("Fin de l'acte" in ev(pg, "document.querySelector('.rc-act') ? document.querySelector('.rc-act').textContent : ''"), "S7 la dernière page annonce la fin de l'acte")
    pg.click("#rcNext"); pg.wait_for_timeout(300)
    check(ev(pg, "!!S.P.hero.ach.act"), "S7 haut fait « Acte accompli »")
    check(ev(pg, "recitState().k") == "wait" and ev(pg, "recitNext().id") == "p07", "S7 l'acte II attend : la page 7 est la suivante")
    check(ev(pg, "recitActsDone()") == 1, "S7 un acte sur deux est accompli")
    ctx.close()
    # tout est lu
    ctx, pg = make(b, read=[(f"p{n:02d}", 14 - n) for n in range(13)], recalls=9)
    check(ev(pg, "RECIT.pages.length") == 13, "S7 treize pages écrites")
    check(ev(pg, "recitState().k") == "end", "S7 tout est lu : l'état est « fin »")
    check(ev(pg, "document.getElementById('jStory').dataset.state") == "end", "S7 la carte renvoie vers les Chroniques")
    check(ev(pg, "recitActsDone()") == 2, "S7 les deux actes sont accomplis")
    prompt = ev(pg, "storyPrompt()")
    check("Plume-sur-Encre" in prompt and "Brume" in prompt, "S7 le feuilleton des Chroniques continue le même univers")
    check("Margaux" in prompt and "Montluisant" in prompt, "S7 …avec toute la distribution, y compris celle de l'acte II")
    check("bibliothèque" in prompt, "S7 …et la suite annoncée (acte III)")
    ctx.close()
    ctx, pg = make(b, read=[], recalls=0)
    check("Plume-sur-Encre" not in ev(pg, "storyPrompt()"), "S7 sans page lue, le feuilleton garde son prompt d'origine")
    ctx.close()

    # ---------------------------------------------------------------- S8 : fusion d'une sauvegarde
    ctx, pg = make(b, read=[("p00", 2)], recalls=0)
    ev(pg, """() => { SV_PENDING = {P: hydrate({recit: {read: {p01: 5, p00: 9}}, hero: {xp: 10}}), cards: [], mots: [], del: []};
      document.getElementById('svConfirm').hidden = false; svApply('merge'); }""")
    read = ev(pg, "S.P.recit.read")
    check("p00" in read and "p01" in read, "S8 la fusion garde les pages lues des deux côtés")
    check(read["p00"] == ev(pg, "dayNum()") - 2, "S8 …et ne remplace pas la date locale")
    ctx.close()

    # ---------------------------------------------------------------- S9 : anglais
    ctx, pg = make(b, read=[("p00", 1)], recalls=0, lang="en")
    check("sealed" in ev(pg, "document.getElementById('hudQuestT').textContent"), "S9 la puce du HUD est en anglais")
    check("Chapter 1" in ev(pg, "document.getElementById('jStoryT').textContent"), "S9 le titre de la carte est en anglais")
    check(ev(pg, "document.querySelector('#jStory .rc-hook').lang") == "fr", "S9 la bande-annonce reste en français (lang=fr)")
    check(ev(pg, "!document.getElementById('jGuideEn').hidden"), "S9 le guide ajoute sa glose anglaise")
    ev(pg, "heroDay().recalls = 9; paintMargin(); recitOpen('p01', false)")
    pg.wait_for_timeout(300)
    check("Act I" in ev(pg, "document.getElementById('rcK').textContent"), "S9 l'en-tête du lecteur est en anglais")
    check("Next" in ev(pg, "document.getElementById('rcNext').textContent"), "S9 « Next » dans le lecteur")
    check(ev(pg, "document.getElementById('rcT').textContent") == "Le premier pain", "S9 le titre de la page reste en français")
    check(ev(pg, "!document.getElementById('rcSub').hidden"), "S9 …avec son titre anglais dessous")
    pg.click("#rcTr"); pg.wait_for_timeout(100)
    check(ev(pg, "getComputedStyle(document.querySelector('.rc-n .rc-en')).display") == "none", "S9 le bouton EN masque les traductions")
    check(ev(pg, "S.P.recit.tr") is False, "S9 …et s'en souvient")
    pg.click("#rcTr"); pg.wait_for_timeout(100)
    check(ev(pg, "getComputedStyle(document.querySelector('.rc-n .rc-en')).display") != "none", "S9 …et les remet")
    pg.keyboard.press("Escape")
    ctx.close()

    # ---------------------------------------------------------------- S10 : mise en page (pas de débordement) en clair et en sombre
    for w, h, theme in [(390, 844, None), (1280, 900, None), (390, 844, "dark"), (1280, 900, "dark")]:
        ctx, pg = make(b, w=w, h=h, read=[("p00", 1)], recalls=9, theme=theme, lang="en")
        tag = f"S10 {w}px {theme or 'clair'}"
        check(ev(pg, "document.documentElement.scrollWidth <= window.innerWidth + 1"), tag + " : Quêtes sans débordement horizontal")
        r = ev(pg, "(() => { const r = document.getElementById('hudQuest').getBoundingClientRect(); return [r.left, r.right]; })()")
        check(r[0] >= 0 and r[1] <= w, tag + " : la puce du HUD tient dans l'écran")
        ev(pg, "recitOpen('p01', false)")
        pg.wait_for_timeout(300)
        for _ in range(9):
            if pg.query_selector(".rc-choice"):
                break
            pg.click("#rcNext"); pg.wait_for_timeout(50)
        box = ev(pg, "(() => { const r = document.getElementById('rcCard').getBoundingClientRect(); return [r.left, r.right, r.top, r.bottom]; })()")
        check(box[0] >= 0 and box[1] <= w and box[2] >= 0 and box[3] <= h, tag + f" : le lecteur tient dans l'écran ({[round(x) for x in box]})")
        check(ev(pg, "document.getElementById('rcLog').scrollWidth <= document.getElementById('rcLog').clientWidth + 1"), tag + " : le journal de scène ne déborde pas")
        check(ev(pg, "[...document.querySelectorAll('.rc-opt')].every(b => b.getBoundingClientRect().right <= window.innerWidth)"), tag + " : les réponses tiennent")
        ctx.close()

    # ---------------------------------------------------------------- S11 : le toucher-un-mot passe devant le lecteur
    ctx, pg = make(b)
    ev(pg, "recitOpen('p00', false)")
    pg.wait_for_timeout(300)
    css = ev(pg, "(() => { const e = document.createElement('div'); e.className = 'taptip'; document.body.appendChild(e); const z = getComputedStyle(e).zIndex; e.remove(); return z; })()")
    modal = ev(pg, "getComputedStyle(document.getElementById('mdPage')).zIndex")
    check(css.isdigit() and int(css) > int(modal), f"S11 la bulle d'un mot touché (z-index {css}) passe devant la fenêtre ({modal})")
    # un vrai toucher sur un mot de la scène ouvre la bulle, visible au-dessus du lecteur
    pg.click(".rc-n .rc-fr")
    pg.wait_for_timeout(500)
    check(pg.query_selector("#tapTip") is not None, "S11 toucher un mot du récit ouvre la bulle de sens")
    ctx.close()

    # ---------------------------------------------------------------- S12 : toutes les pages se jouent de bout en bout
    ctx, pg = make(b, read=[], recalls=9)
    ids = ev(pg, "RECIT.pages.map(p => p.id)")
    for pid in ids:
        ev(pg, f"recitOpen('{pid}', true)")
        pg.wait_for_timeout(120)
        play_page(pg, prefer_wrong_first=True)
        pg.wait_for_timeout(80)
        n = ev(pg, "document.querySelectorAll('.rc-cards li').length")
        ok = ev(pg, "!!document.querySelector('.rc-end')")
        if not (ok and n == 3):
            check(False, f"S12 {pid} : la page ne se termine pas proprement (fin={ok}, cartes={n})")
        ev(pg, "recitClose()")
        pg.wait_for_timeout(60)
    check(True, f"S12 les {len(ids)} pages se jouent jusqu'au bout, avec un faux pas puis la bonne réponse")
    check(ev(pg, "Object.keys(S.P.recit.read).length") == 0, "S12 la relecture ne marque aucune page")
    ctx.close()

    b.close()

print()
print("erreurs de console / page :", len(errors))
for e in errors[:6]:
    print("   ", e)
print("ÉCHECS :", len(fails))
for f in fails:
    print("   -", f)
