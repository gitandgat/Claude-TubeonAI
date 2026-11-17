"""Parcours de bout en bout du habillage RPG, sur la vraie page, sans réseau ni compte."""
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
  if (P.hero) P.hero.day = Object.assign({n: dn, xp: 0, recalls: 0, clean: 0, convo: 0, phrase: 0, grid: 0, exam: 0}, P.hero.day || {});
  localStorage.setItem("le-cahier-v1", JSON.stringify(P));
  const srs = {};
  for (let i = 1; i <= 24; i++) srs["t" + i] = [dn - (i % 3), 3 + i, 25, 2, 0, 4, 3];
  localStorage.setItem("le-cahier-srs-v1", JSON.stringify(srs));
  localStorage.setItem("le-cahier-lang", "__LANG__");
})();
"""


def make(browser, w=1280, h=900, P=None, lang="fr", seed=True):
    ctx = browser.new_context(viewport={"width": w, "height": h})
    pg = ctx.new_page()
    pg.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
    pg.on("console", lambda m: errors.append(f"console.error: {m.text}") if m.type == "error" else None)
    if seed:
        P = P or {}
        P.setdefault("level", 3); P.setdefault("tested", True)
        P.setdefault("hero", {"xp": 1300, "name": "Sahawat", "avatar": "🦊", "cls": "erudit", "created": 1, "ach": {}, "quests": [0, 2, 3], "claimed": []})
        pg.add_init_script(SEED.replace("__P__", json.dumps(P)).replace("__LANG__", lang))
    pg.goto(PAGE)
    pg.wait_for_timeout(1200)
    return ctx, pg


def ev(pg, js):
    return pg.evaluate(js)


with sync_playwright() as p:
    b = p.chromium.launch()

    # ---------------------------------------------------------------- F1 : création
    ctx, pg = make(b, seed=False)
    pg.wait_for_timeout(700)
    check(pg.is_visible("#mdCreate"), "F1 la création du personnage s'ouvre pour un nouveau joueur")
    pg.fill("#mdName", "Léa")
    pg.click("#mdAvatars button:nth-child(2)")
    pg.click("#mdClasses .cls:nth-child(2)")
    pg.click("#mdCreateGo")
    pg.wait_for_timeout(300)
    check(not pg.is_visible("#mdCreate"), "F1 la fenêtre se ferme")
    check(ev(pg, "document.getElementById('hudName').textContent") == "Léa", "F1 le nom apparaît dans le HUD")
    check(ev(pg, "document.getElementById('hudClass').textContent") == "Scribe", "F1 la classe apparaît dans le HUD")
    check(ev(pg, "document.getElementById('hudAvatar').textContent") == "🦉", "F1 le visage choisi apparaît")
    saved = ev(pg, "JSON.parse(localStorage.getItem('le-cahier-v1')).hero")
    check(saved["name"] == "Léa" and saved["cls"] == "scribe" and saved["created"], "F1 le personnage est sauvegardé")
    pg.reload(); pg.wait_for_timeout(1500)
    check(not pg.is_visible("#mdCreate"), "F1 la création ne se rouvre pas après rechargement")
    ctx.close()

    # ---------------------------------------------------------------- F2 : plus tard
    ctx, pg = make(b, seed=False)
    pg.wait_for_timeout(700)
    pg.click("#mdCreateSkip"); pg.wait_for_timeout(300)
    check(not pg.is_visible("#mdCreate"), "F2 « Plus tard » ferme la fenêtre")
    lang = ev(pg, "LANG")
    check(ev(pg, "document.getElementById('hudName').textContent") == ("Adventurer" if lang == "en" else "Aventurier"),
          f"F2 nom par défaut (« Aventurier » / « Adventurer » selon la langue : {lang})")
    pg.reload(); pg.wait_for_timeout(1500)
    check(not pg.is_visible("#mdCreate"), "F2 on ne redemande pas")
    # Échap ferme aussi
    ctx.close()
    ctx, pg = make(b, seed=False); pg.wait_for_timeout(700)
    pg.keyboard.press("Escape"); pg.wait_for_timeout(200)
    check(not pg.is_visible("#mdCreate"), "F2 Échap ferme la création")
    # piège du focus
    ctx.close()
    ctx, pg = make(b, seed=False); pg.wait_for_timeout(700)
    inside = True
    for _ in range(18):
        pg.keyboard.press("Tab")
        inside = inside and ev(pg, "!!document.activeElement.closest('#mdCreate')")
    check(inside, "F2 Tab reste prisonnier de la fenêtre (18 appuis)")
    ctx.close()

    # ---------------------------------------------------------------- F3/F4/F5/F6 : XP, classes, quêtes, hauts faits
    ctx, pg = make(b)
    ev(pg, "S.P.hero.cls = 'scribe'; S.P.hero.xp = 1000;")
    ev(pg, "xpGain(100, 'phrase')")
    check(ev(pg, "S.P.hero.xp") == 1125, "F4 Scribe : +25 % sur les phrases (100 → 125)")
    ev(pg, "xpGain(100, 'recalls')")
    check(ev(pg, "S.P.hero.xp") == 1225, "F4 Scribe : aucun bonus sur les rappels")
    ev(pg, "S.P.hero.cls = 'erudit'; S.P.hero.xp = 1000; xpGain(100, 'recalls')")
    check(ev(pg, "S.P.hero.xp") == 1110, "F4 Érudit : +10 % sur les rappels")
    ev(pg, "S.P.hero.cls = ''; S.P.hero.xp = 1000; xpGain(100, 'recalls')")
    check(ev(pg, "S.P.hero.xp") == 1100, "F4 sans classe : pas de bonus")

    ev(pg, "S.P.hero.cls = 'erudit'; S.P.hero.ach = {}; S.P.hero.xp = 1790; S.P.recall = {rev: 0, ok: 0}; S.P.streak = 0; S.P.parle = {n: 0, points: 0, missions: 0}; S.P.phrase = {n: 0, ok: 0}; S.P.dictee = {done: 0, words: 0, right: 0}; S.P.rings = 0; S.P.level = 1; S.P.backupAt = 0; S.mots = []; S.P.srs = {}; srsReset();")
    ev(pg, "S.P.hero.justLevelled = null; xpGain(30, null);")
    check(ev(pg, "S.P.hero.justLevelled") == 7, "F3 franchir 1800 XP annonce le niveau 7")
    ev(pg, "paintMargin()")
    pg.wait_for_timeout(200)
    check(pg.is_visible("#mdLevel"), "F3 la fenêtre de montée de niveau s'ouvre")
    check(ev(pg, "document.getElementById('mdLevelN').textContent") == "7", "F3 elle affiche 7")
    check(ev(pg, "S.P.hero.justLevelled") is None, "F3 l'événement est consommé")
    pg.keyboard.press("Escape"); pg.wait_for_timeout(200)
    check(not pg.is_visible("#mdLevel"), "F3 Échap la ferme")
    ev(pg, "paintMargin(); paintMargin();")
    pg.wait_for_timeout(200)
    check(not pg.is_visible("#mdLevel"), "F3 elle ne revient pas toute seule")

    xp0 = ev(pg, "S.P.hero.xp")
    ev(pg, "S.P.recall = {rev: 1, ok: 1}; heroCelebrate();")
    check(ev(pg, "!!S.P.hero.ach.spark"), "F6 « Première étincelle » se débloque à 1 rappel")
    xp1 = ev(pg, "S.P.hero.xp")
    check(xp1 - xp0 == 20, f"F6 +20 XP exactement ({xp1 - xp0})")
    ev(pg, "heroCelebrate(); heroCelebrate(); paintMargin();")
    check(ev(pg, "S.P.hero.xp") == xp1, "F6 un haut fait ne paie jamais deux fois")
    check(pg.locator("#toasts .toast").count() >= 1, "F6 un avis s'affiche")

    ev(pg, "S.P.hero.quests = [0]; S.P.hero.claimed = []; S.P.hero.questDay = heroDay().n; heroDay().recalls = 20;")
    xq = ev(pg, "S.P.hero.xp")
    ev(pg, "heroCelebrate()")
    check(ev(pg, "S.P.hero.xp") - xq == 40, "F5 la quête « 20 rappels » rapporte 40 XP")
    ev(pg, "heroCelebrate(); heroCelebrate();")
    check(ev(pg, "S.P.hero.xp") - xq == 40, "F5 …une seule fois")
    ctx.close()

    # ---------------------------------------------------------------- F7 : le combat
    ctx, pg = make(b)
    pg.click("#tab-seance"); pg.wait_for_timeout(500)
    total = ev(pg, "SE.q.length")
    check(total > 3, f"F7 la séance a des cartes ({total})")
    check(ev(pg, "document.querySelectorAll('#seHearts svg').length") == 5, "F7 cinq cœurs")
    check(ev(pg, "document.querySelectorAll('#seHearts svg.lost').length") == 0, "F7 aucun cœur perdu au départ")
    w0 = float(ev(pg, "parseFloat(document.getElementById('seFill').style.width)"))
    check(abs(w0 - 100) < 0.5, f"F7 la vie de l'adversaire commence à 100 % ({w0})")
    ev(pg, "seJudge('ok', 'ok', null, null, 5)")
    w1 = float(ev(pg, "parseFloat(document.getElementById('seFill').style.width)"))
    check(w1 < w0, f"F7 un rappel juste fait baisser la barre ({w0:.0f} → {w1:.0f})")
    check(ev(pg, "document.querySelectorAll('#seHearts svg.lost').length") == 0, "F7 …sans perdre de cœur")
    ev(pg, "nextCard()")
    pg.wait_for_timeout(200)
    ev(pg, "seJudge('no', 'ok')")
    check(ev(pg, "document.querySelectorAll('#seHearts svg.lost').length") == 1, "F7 un rappel raté coûte un cœur")
    check(ev(pg, "document.getElementById('seCard').classList.contains('shake')"), "F7 la carte tremble")
    check(ev(pg, "SE.q.length") == total + 1, "F7 la carte ratée revient dans la file (voulu)")
    check(ev(pg, "document.getElementById('seFoe').textContent.length") > 3, "F7 l'adversaire a un nom")
    check(ev(pg, "document.getElementById('seCount').textContent").startswith("PV "), "F7 compteur « PV »")
    # clavier : 1-4 notent une carte de fiche, hors fenêtre
    ctx.close()

    # ---------------------------------------------------------------- F8 : la taverne
    ctx, pg = make(b)
    pg.click("#tab-parler"); pg.wait_for_timeout(400)
    who = ev(pg, "document.getElementById('cvMissionWho').textContent")
    check("rencontres" in who and len(who) > 30, f"F8 la mission annonce qui l'on rencontre ({who[:70]}…)")
    a = ev(pg, "JSON.stringify(missionScene())"); c = ev(pg, "JSON.stringify(missionScene())")
    check(a == c, "F8 la scène du jour est stable (même scène à chaque appel)")
    missing = ev(pg, "Object.values(SCENES).flat().map(s => s.q).filter(q => !NPCS[q])")
    check(missing == [], f"F8 chaque scène a un interlocuteur nommé (manquants : {missing})")
    ev(pg, "showNpc({q:'ton voisin', o:\"dans l'entrée\", b:'il se plaint du bruit'})")
    check(ev(pg, "document.getElementById('cvNpN').textContent") == "M. Bélanger", "F8 le voisin s'appelle M. Bélanger")
    check(ev(pg, "document.getElementById('cvNpP').textContent") == "🧔", "F8 …avec son visage")
    ev(pg, "showNpc({q:'x', o:'', b:'sujet libre', free:true})")
    check(ev(pg, "document.getElementById('cvNpN').textContent") == "À ta demande", "F8 situation libre : « À ta demande »")
    ev(pg, "document.getElementById('cvLog').appendChild(Object.assign(document.createElement('div'),{className:'bub them',textContent:'Bonjour'}))")
    check(pg.locator(".bub.them").count() == 1, "F8 une réplique s'affiche")
    ctx.close()

    # ---------------------------------------------------------------- F12 : rareté
    P = {"hero": {"xp": 1300, "name": "T", "avatar": "🦊", "cls": "erudit", "created": 1, "ach": {}, "quests": [0], "claimed": []}}
    ctx = b.new_context(viewport={"width": 1280, "height": 900}); pg = ctx.new_page()
    pg.on("pageerror", lambda e: errors.append(f"pageerror: {e}"))
    pg.add_init_script("""(() => { if (sessionStorage.getItem('s')) return; sessionStorage.setItem('s','1');
      const dn = Math.round(Date.UTC(new Date().getFullYear(), new Date().getMonth(), new Date().getDate()) / 864e5);
      localStorage.setItem('le-cahier-v1', JSON.stringify({level:3,tested:true,hero:{xp:1300,name:'T',avatar:'🦊',cls:'erudit',created:1,ach:{},quests:[0],claimed:[]}}));
      const mots = [], srs = {}, now = Date.now();
      [['chien',4],['pomme',2],['parapluie',3],['fenêtre',1],['tiroir',0]].forEach(([fr,held],k)=>{ const id='m'+k;
        mots.push({id,fr,pic:'🐕',note:'',g:'m',pos:'nom',from:'socle',lv:1,at:now-k});
        ['wr_','wp_','ws_','wg_'].forEach((p,j)=>{ srs[p+id]=[dn+(j<held?20:2),j<held?30:5,25,3,0,5,4]; }); });
      localStorage.setItem('le-cahier-srs-v1', JSON.stringify(srs)); localStorage.setItem('le-cahier-mots-v1', JSON.stringify(mots)); })();""")
    pg.goto(PAGE); pg.wait_for_timeout(1200)
    pg.click("#tab-cartes"); pg.wait_for_timeout(600)
    tiers = ev(pg, "[...document.querySelectorAll('#ckList .ckitem')].map(li => [li.querySelector('.ckword').textContent, li.querySelector('.rar').textContent])")
    expect = {"le chien": "Légendaire", "la pomme": "Rare", "le parapluie": "Épique", "la fenêtre": "Peu commun", "le tiroir": "Commun"}
    got = {k.strip(): v for k, v in tiers}
    # l'article dépend du genre semé (tout « m »)
    en = ev(pg, "LANG") == "en"
    names = ({"chien": "Legendary", "pomme": "Rare", "parapluie": "Epic", "fenêtre": "Uncommon", "tiroir": "Common"} if en else
             {"chien": "Légendaire", "pomme": "Rare", "parapluie": "Épique", "fenêtre": "Peu commun", "tiroir": "Commun"})
    ok = all(any(w.endswith(n) and r == t for w, r in got.items()) for n, t in names.items())
    check(ok, f"F12 la rareté suit les cartes tenues ({got})")
    ctx.close()

    # ---------------------------------------------------------------- F9 : anglais
    ctx, pg = make(b, lang="en")
    labs = ev(pg, "[...document.querySelectorAll('.world .tab')].map(t => t.querySelector('.tl').textContent + '|' + t.querySelector('.ts').textContent)")
    want = ["Quests|Today", "Battle|Session", "Inventory|My cards", "Forge|Write", "Tavern|Talk", "Hero|Character",
            "Dungeon|Mock exam", "Ear|Sounds", "Library|References", "Chronicles|Story"]
    check(labs == want, f"F9 la carte du monde en anglais ({labs})")
    check(ev(pg, "document.querySelector('.navlabel').textContent") == "Training hall", "F9 « Salle d'armes » → Training hall")
    check(ev(pg, "document.querySelector('.mstat .k').textContent") in ("Streak",), "F9 marge traduite")
    check("days" in ev(pg, "document.getElementById('streakPill').textContent"), "F9 la flamme dit « days »")
    ev(pg, "S.P.hero.name = ''; paintHud();")
    check(ev(pg, "document.getElementById('hudName').textContent") == "Adventurer", "F9 nom par défaut « Adventurer »")
    pg.click("#tab-perso"); pg.wait_for_timeout(300)
    cls = ev(pg, "[...document.querySelectorAll('#hClasses .cls b')].map(x => x.textContent)")
    check(cls == ["Scholar", "Scribe", "Troubadour", "Wayfarer"], f"F9 classes en anglais ({cls})")
    pg.click("#langBtn"); pg.wait_for_timeout(300)
    check(ev(pg, "document.querySelector('.world .tab .tl').textContent") == "Quêtes", "F9 retour au français")
    ctx.close()

    # ---------------------------------------------------------------- F13 : chaque panneau, deux largeurs
    tabs = ["jour", "seance", "cartes", "phrase", "parler", "perso", "examen", "sons", "ref", "histoire",
            "trou", "ordre", "decider", "imiter", "motus", "genre", "video", "croise", "dictee", "niveau", "profil"]
    for w in (390, 1280):
        ctx, pg = make(b, w=w, h=900)
        bad = []
        for t in tabs:
            pg.click(f"#tab-{t}"); pg.wait_for_timeout(120)
            over = ev(pg, "document.documentElement.scrollWidth - document.documentElement.clientWidth")
            vis = ev(pg, f"!document.getElementById('panel-{t}').hidden")
            if over > 0 or not vis:
                bad.append((t, over, vis))
        check(not bad, f"F13 {w}px : aucun débordement horizontal, panneau visible sur {len(tabs)} onglets ({bad})")
        ctx.close()

    # ---------------------------------------------------------------- thème
    ctx, pg = make(b)
    bg1 = ev(pg, "getComputedStyle(document.body).backgroundColor")
    pg.click("#themeBtn"); pg.wait_for_timeout(200)
    th = ev(pg, "document.documentElement.getAttribute('data-theme')")
    bg2 = ev(pg, "getComputedStyle(document.body).backgroundColor")
    check(th in ("dark", "light") and bg1 != bg2, f"thème : la bascule change le fond ({bg1} → {bg2})")
    mono = ev(pg, "getComputedStyle(document.querySelector('.hud-rank')).fontFamily")
    check("IBM Plex Mono" in mono, f"police mono bien appliquée au HUD ({mono[:40]})")
    clipped = ev(pg, "(() => { const s = document.getElementById('hudXp'), bar = document.getElementById('hudXpBar'); return s.scrollHeight > bar.clientHeight + 1; })()")
    check(not clipped, "le texte d'XP n'est pas rogné par la barre")
    ctx.close()
    b.close()

print("\nerreurs de console / page :", len(errors))
for e in errors[:15]:
    print("  ", e[:220])
print("ÉCHECS :", len(fails))
for f in fails:
    print("  -", f)
