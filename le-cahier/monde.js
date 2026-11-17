/* Le Cahier — le monde : le guide et le ciel.

   Maître Encrier ne dit que ce que le cahier sait vraiment : la flamme, l'anneau,
   les cartes dues, l'heure. Ses phrases sont courtes et de niveau A2, donc de
   l'écoute comprise en plus d'un décor. Le ciel, lui, est du décor pur. */

const GUIDE = {name:"Maître Encrier", face:"🧙"};

/* La série n'est « en danger » que si elle vit encore : on a joué hier. Après vingt
   jours d'absence, elle est déjà tombée — on ne prétend pas la sauver à minuit. */
function streakAtRisk(){
  if(new Date().getHours() < 18 || S.P.streak <= 0 || S.P.last === today()) return false;
  const last = dayOfStr(S.P.last);
  return last != null && last >= dayNum() - 1;
}

/* Il ne dit que ce qu'il sait vraiment : l'histoire d'abord (c'est elle qui donne
   envie de revenir), puis l'état de la série, de l'anneau, des cartes. */
function guideLine(){
  const p = S.P, h = p.hero, en = rpgEn();
  const nm = h.name || (en ? "traveller" : "voyageur");
  const st = srsStats(), ring = ringState();
  const hr = new Date().getHours();
  const hello = hr < 18 ? "Bonjour" : "Bonsoir", helloEn = hr < 18 ? "Hello" : "Good evening";
  const due = st.due + st.fresh;
  const missionDone = !!(p.parle.day && p.parle.day.day === dayNum() && p.parle.day.done);
  const rs = typeof recitState === "function" ? recitState() : null;
  const n = (k, one, many) => k + " " + (k > 1 ? many : one);

  if(rs && rs.k === "open" && rs.first) return {
    fr:"Il était une fois… un village qui perd ses mots. Entre dans l'histoire, " + nm + ".",
    en:"Once upon a time… a village that loses its words. Step into the story, " + nm + "."};
  if(p.recall.rev === 0 && p.days === 0) return {
    fr:"Bienvenue, " + nm + ". Je suis Maître Encrier, ton guide. Ta première quête t'attend ci-dessous.",
    en:"Welcome, " + nm + ". I am Master Inkwell, your guide. Your first quest awaits below."};
  if(st.comeback) return {
    fr:"Te revoilà, " + nm + " ! La route a été longue. On reprend doucement : vingt cartes aujourd'hui.",
    en:"You're back, " + nm + "! The road was long. We resume gently: twenty cards today."};
  if(streakAtRisk()) return {
    fr:"La nuit tombe. Ta flamme de " + n(p.streak, "jour", "jours") + " vacille : cinq cartes suffisent.",
    en:"Night is falling. Your " + p.streak + "-day flame flickers: five cards are enough."};
  if(rs && rs.k === "sealed") return {
    fr:"La page du jour est scellée, " + nm + ". Encore " + n(rs.left, "carte", "cartes") + " pour briser le sceau.",
    en:"Today's page is sealed, " + nm + ". " + n(rs.left, "more card", "more cards") + " to break the seal."};
  if(rs && rs.k === "open") return {
    fr:"Ta page du jour est ouverte, " + nm + " : « " + rs.next.titre + " ». Margaux, Théo et la Brume t'attendent.",
    en:"Today's page is open, " + nm + ": “" + rs.next.titreEn + "”. Margaux, Théo and the Mist are waiting."};
  if(rs && rs.k === "wait") return {
    fr:"Belle lecture, " + nm + " ! La suite demain. En attendant, fais travailler tes mots.",
    en:"Nicely read, " + nm + "! More tomorrow. Meanwhile, put your words to work."};
  if(ring.closed) return {
    fr:"Bravo, " + nm + " ! Ton anneau est fermé. Le reste est un cadeau.",
    en:"Well done, " + nm + "! Your ring is closed. Anything more is a gift."};
  if(S.sample && !missionDone) return {
    fr:hello + ", " + nm + ". Une mission t'attend à la taverne : trois minutes, à l'oral.",
    en:helloEn + ", " + nm + ". A mission awaits at the tavern: three minutes, spoken."};
  if(due > 0) return {
    fr:hello + ", " + nm + ". Il y a " + n(due, "carte", "cartes") + " à voir aujourd'hui. Allons-y !",
    en:helloEn + ", " + nm + ". There " + (due > 1 ? "are " : "is ") + n(due, "card", "cards") + " to see today. Let's go!"};
  return {
    fr:hello + ", " + nm + ". Rien à revoir : va bâtir des phrases à la forge.",
    en:helloEn + ", " + nm + ". Nothing to review: go and build sentences at the forge."};
}

/* Des conseils qui sont la méthode même, pas des banalités. */
const GUIDE_TIPS = [
  {fr:"Écris la réponse avant de regarder les propositions : se souvenir, c'est ce qui fait tenir.",
   en:"Write the answer before looking at the options: remembering is what makes it stick."},
  {fr:"Une carte ratée revient vite. C'est voulu : l'erreur travaille pour toi.",
   en:"A missed card comes back soon. That is deliberate: the mistake works for you."},
  {fr:"Dis les phrases à voix haute. C'est la bouche qui apprend l'accent.",
   en:"Say the sentences aloud. It is the mouth that learns the accent."},
  {fr:"Dix minutes tous les jours valent mieux que deux heures le dimanche.",
   en:"Ten minutes every day beat two hours on a Sunday."},
  {fr:"Apprends le genre avec le mot : le chien, la pomme. Jamais après.",
   en:"Learn the gender with the word: le chien, la pomme. Never afterwards."},
  {fr:"Touche un mot dans une phrase : son sens apparaît.",
   en:"Touch a word in a sentence: its meaning appears."},
  {fr:"Un jour manqué n'est pas une défaite : le joker te protège une fois par semaine.",
   en:"A missed day is not a defeat: the joker protects you once a week."},
  {fr:"Quand tu hésites entre deux formes, dis d'abord ce que tu veux dire. Le sens choisit la forme.",
   en:"When you hesitate between two forms, say first what you mean. The meaning picks the form."}
];

function paintGuide(showTip){
  const box = $("jGuide");
  if(!box) return;
  const en = rpgEn();
  /* Un conseil ne reste que le temps d'un regard : la prochaine repeinture
     (une carte faite, un onglet changé) rend la parole à ce qui se passe vraiment. */
  const line = showTip === true ? GUIDE_TIPS[S.guideN % GUIDE_TIPS.length] : guideLine();
  $("jGuideFace").textContent = GUIDE.face;
  const fr = $("jGuideFr");
  fr.textContent = line.fr;
  fr.lang = "fr";
  const e = $("jGuideEn");
  e.textContent = line.en;
  e.hidden = !en;
  const b = $("jGuideTip");
  b.title = en ? "A tip about the method" : "Un conseil de méthode";
  b.setAttribute("aria-label", b.title);
}

function guideInit(){
  const b = $("jGuideTip");
  if(!b) return;
  b.addEventListener("click", () => {
    /* Le premier conseil dépend du jour ; ensuite, ils défilent. */
    S.guideN = S.guideN == null ? dayNum() % GUIDE_TIPS.length : S.guideN + 1;
    paintGuide(true);
  });
}

/* ---------- le ciel : un village de nuit derrière le HUD ----------
   Décor pur, lent et discret : il ne porte aucune information. Il s'arrête
   quand l'onglet est caché, et se fige si l'on préfère moins de mouvement. */
function skyInit(){
  const cv = $("hudSky");
  if(!cv || !cv.getContext) return;
  const ctx = cv.getContext("2d");
  if(!ctx) return;
  const reduce = typeof matchMedia === "function" && matchMedia("(prefers-reduced-motion: reduce)").matches;
  let W = 0, H = 0, dpr = 1, stars = [], houses = [], raf = 0, last = 0;
  /* Les couleurs viennent des jetons de la page ; les valeurs de repli sont les mêmes. */
  const css = getComputedStyle(document.documentElement);
  const tok = (n, d) => css.getPropertyValue(n).trim() || d;
  const GOLD = tok("--gold-hi", "#F8DE93"), HILL = tok("--ground-3", "#2631A0");

  /* mulberry32 : le même village à chaque visite */
  const rng = (seed) => () => {
    seed = (seed + 0x6D2B79F5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };

  const layout = () => {
    const r = cv.getBoundingClientRect();
    dpr = Math.min(2, window.devicePixelRatio || 1);
    W = Math.max(1, Math.round(r.width));
    H = Math.max(1, Math.round(r.height));
    cv.width = W * dpr;
    cv.height = H * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    const R = rng(1789);
    stars = Array.from({length:Math.round(W / 15)}, () =>
      ({x:R() * W, y:R() * H * .72, r:.4 + R() * 1.1, p:R() * 6.28, s:.6 + R() * 1.6}));
    houses = [];
    let x = -12;
    while(x < W + 24){
      const w = 22 + R() * 30, h = 12 + R() * 22, tower = R() < .1;
      houses.push({x, w, h:tower ? h + 20 : h, tower, roof:8 + R() * 9,
        wins:Array.from({length:1 + ((R() * 3) | 0)}, () => ({dx:4 + R() * (w - 11), dy:4 + R() * 8, p:R() * 6.28}))});
      x += w + 3 + R() * 9;
    }
  };

  const draw = (t) => {
    ctx.clearRect(0, 0, W, H);
    ctx.fillStyle = GOLD;
    stars.forEach(s => {
      ctx.globalAlpha = reduce ? .6 : .3 + .55 * (Math.sin(t * .0012 * s.s + s.p) * .5 + .5);
      ctx.beginPath(); ctx.arc(s.x, s.y, s.r, 0, 6.2832); ctx.fill();
    });
    ctx.globalAlpha = 1;

    const narrow = W < 600;
    const mr = narrow ? 12 : Math.max(9, Math.min(20, H * .1));
    const mx = narrow ? W * .84 : W * .56, my = narrow ? 36 : Math.max(mr + 8, H * .17);
    const g = ctx.createRadialGradient(mx, my, mr * .5, mx, my, mr * 3.6);
    g.addColorStop(0, GOLD); g.addColorStop(1, "transparent");
    ctx.globalAlpha = .4; ctx.fillStyle = g; ctx.fillRect(mx - mr * 3.6, my - mr * 3.6, mr * 7.2, mr * 7.2); ctx.globalAlpha = 1;
    ctx.fillStyle = GOLD; ctx.beginPath(); ctx.arc(mx, my, mr, 0, 6.2832); ctx.fill();

    ctx.globalAlpha = .55; ctx.fillStyle = HILL;
    ctx.beginPath(); ctx.moveTo(0, H);
    for(let x = 0; x <= W; x += 6) ctx.lineTo(x, H - 30 - Math.sin(x * .011 + 1) * 9 - Math.sin(x * .029) * 4);
    ctx.lineTo(W, H); ctx.fill(); ctx.globalAlpha = 1;

    houses.forEach(hs => {
      ctx.fillStyle = "#050824";
      const top = H - hs.h;
      ctx.fillRect(hs.x, top, hs.w, hs.h + 2);
      ctx.beginPath();
      if(hs.tower){
        ctx.moveTo(hs.x + hs.w * .18, top); ctx.lineTo(hs.x + hs.w / 2, top - hs.roof * 2.4); ctx.lineTo(hs.x + hs.w * .82, top);
      }else{
        ctx.moveTo(hs.x - 2, top); ctx.lineTo(hs.x + hs.w / 2, top - hs.roof); ctx.lineTo(hs.x + hs.w + 2, top);
      }
      ctx.fill();
      hs.wins.forEach(w => {
        ctx.globalAlpha = reduce ? .7 : .45 + .45 * Math.sin(t * .0021 + w.p);
        ctx.fillStyle = GOLD;
        ctx.fillRect(hs.x + w.dx, top + w.dy, 3, 4);
      });
      ctx.globalAlpha = 1;
    });
  };

  const loop = (t) => {
    raf = requestAnimationFrame(loop);
    if(t - last < 45) return;           /* ~22 images par seconde suffisent à des étoiles */
    last = t;
    draw(t);
  };
  const run = () => { if(!reduce && !raf && !document.hidden) raf = requestAnimationFrame(loop); };
  const halt = () => { if(raf){ cancelAnimationFrame(raf); raf = 0; } };

  layout();
  draw(0);
  if(!reduce){
    run();
    document.addEventListener("visibilitychange", () => { if(document.hidden) halt(); else run(); });
  }
  if(typeof ResizeObserver === "function")
    new ResizeObserver(() => { layout(); draw(performance.now()); }).observe(cv);
}
