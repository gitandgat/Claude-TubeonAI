# Le Cahier

French notebook built on spaced recall. The published artifact is the source of truth
(https://claude.ai/artifact/FxAWCmV9EnWvGeNwzpPMgo); this folder mirrors its files.

| File | What it does |
|------|--------------|
| `index.html` | Layout, styles and every tab's panel |
| `cahier.js` | Data, state, saving and sync, tabs, startup |
| `lang.js` | English interface (French stays French) |
| `srs.js` | Spaced repetition: registry of every card kind, scheduling, new-card picking, interleaving |
| `seance.js` | La Séance, the daily review: gap-fill, dictation, translation, gender, conjugation, minimal pairs, word cards, word order, deciding, shadowing |
| `aujourdhui.js` | Aujourd'hui: the day's plan from what is due, what is weak, and the minutes you have |
| `imiter.js` | Imiter: shadowing a real French voice, mic take, self-grade; also the séance card |
| `ordre.js`, `decider.js` | L'Ordre (rebuild the sentence) and Décider (two correct forms, one meaning) as standalone drills |
| `sauvegarde.js` | Backup: export the whole notebook to JSON, import by file or paste, replace or merge |
| `cartes.js`, `socle.js`, `ff625.js`, `captures.js`, `photo.js` | Mes cartes: deck browser, base deck, the 625 list, pop-up dictionary captures, real photos |
| `sons.js`, `voix.js`, `dictee.js`, `voix.mp3` | Minimal pairs, voice picker, dictation; `speakFr()` plays the recorded sprite or falls back to synthesis |
| `histoire.js`, `ref.js`, `tap.js` | The Chronicles (endless story written by Claude at your level — it now continues the Récit's world), conjugation references, tap-a-word meanings |
| `profil.js`, `niveau.js`, `phrase.js`, `parler.js`, `examen.js`, `croise.js` | Profile, level test, writing, conversation (NPC cards), mock exam, crossword |
| `rpg.js` | The hero: classes, HUD, quests, achievements, level-up and creation modals, heat map |
| `recit-data.js` | **The story itself** — `CAST`, `RECIT` (acts, chapters, pages: lines, one reply choice, three cloze cards, teaser, summary, story bible). Rewritable by the weekly engine without touching `recit.js` |
| `recit.js` | **Story engine**: one page a day, unlocked by 5 recalls; the visual-novel reader (`#mdPage`); page → 3 cloze cards into the SRS; the Quêtes card, the HUD quest chip, the Chroniques "book"; story achievements |
| `monde.js` | Maître Encrier (context-aware guide line + method tips) and the night-village canvas behind the HUD |
| `phrases.js`, `voix-map.js`, `voix-AAwSS.mp3` | Weekly sentences + recorded voice; rewritten every Monday by `engine/semaine.py` — do not edit by hand |
| `voix-recit.js`, `voix-rNN.mp3` | The story's recorded voice: every line, every correct reply and every card sentence, one track per page. Built by `engine/voix_recit.py`; merged into `VOIX_REC` at load |
| `voix-mots.js`, `voix-mNN.mp3` | 544 single words (base deck with article, le/la nouns, minimal pairs) in the same voice. Built by `engine/voix_mots.py` |
| `taille.js` | Text size: four steps (100 / 112.5 / 125 / 140 %), A− / A+ in the HUD. Default follows width: 125 % from 760 px, 112.5 % above 560 px, 100 % on phones. Choice kept per device |

SRS id prefixes: `s` dictation, `x` translation, `o` word order, `i` shadowing (all on a cloze card id),
`g` gender, `k` conjugation, `m` minimal pair, `w?_` word cards, `y` decider. Cloze card ids start with
`t`/`v`/`p`/`c`/`q` (hand-made), `n` (weekly sentences) or `r` (story: `r<page><a-c>`, e.g. `r01b`).

## The story layer (story learning)

The app is an RPG whose spine is a story. *The Mist of Forgetting is erasing the words of the village of
Plume-sur-Encre; every word you remember pushes it back.* The metaphor is the method: a word seen again at
the right moment becomes a stone.

- **One page a day.** The very first page is free; each later page opens after 5 recalls that day (or
  straight away when nothing is due) — the story advances only through reviews. Reading never fabricates
  progress: it gives +25 XP, counts for the streak, and nothing else.
- **The page is a scene**: narrator and cast lines (tap a French word for its meaning, 🔊 to hear it, EN
  toggle for translations) with one reply to choose in French. A wrong reply shows what it means and waits.
- **Story → SRS.** Reading a page adds its three sentences — verbatim from the page — as cloze cards, so they
  also become dictation, translation, word-order and shadowing cards. `pickFresh()` puts them first.
  Unread pages contribute nothing (`recitCards()` filters on `S.P.recit.read`).
- **State**: `S.P.recit = {read:{pageId: dayNum}, acc:{pageId:[ok,total]}, tr:bool}`. Backup merge unions `read`.
- **Beyond the authored pages** the Chronicles continue the same world (`recitBible()` feeds `storyPrompt()`).
- **Written so far**: prologue + chapters 1–4 = 13 pages in two acts (A2 French). Act II ends on the Mist heading for
  the old library across the river (`RECIT.bible.next` says so, for the Chronicles prompt).
- **Card rule**: a card must be answerable from its sentence alone (grammar or idiom decides, never a story fact),
  and each distractor must be wrong in that sentence — e.g. never "et quart" next to "et demie".
- To add pages: append to `RECIT.pages` in `recit-data.js` (ids `pNN`, `ch`/`acte` must exist) and run
  `node tests/recit_data_test.cjs` — it checks structure, that every card sentence appears word for word on its
  page, 4–14 words (L'Ordre), three distinct distractors.

## The voice

Every sentence that has a recording plays the real French voice (VoiSpark, cartesia "Calm French Woman"):
the 40 base sentences (`voix.mp3`), the weekly ones (`voix-AAwSS.mp3`), and the whole story (`voix-rNN.mp3`).
`speakFr()` in `dictee.js` is the single entry point; anything without a recording (single words, imported
sentences) falls back to browser synthesis, which now **refuses to read French with a non-French voice**
(it shows a one-time toast telling you to add a French system voice instead).

- Playback loads each track whole into memory (`fetch` → blob URL) so seeking works even when the host
  ignores HTTP Range requests (without this Chrome restarts at 0 and plays the wrong sentence). It stops on
  the real playback position, not a timer started before the seek.
- Story lines are recorded **without the hero's name**: `rcSpoken()` (recit.js) turns "Tu vas m'aider, {nom} ?"
  into "Tu vas m'aider ?". The screen still shows the name. The engine uses the same function.
- To (re)record the story after editing `recit-data.js`:

      python3 engine/voix_recit.py --install    # records only new/changed lines (clips cached in engine/recit-voix/)
      python3 engine/verifier_voix.py           # Whisper re-listens every clip: language + words

  Then publish `voix-recit.js` and the `voix-rNN.mp3` files. Whisper mishears invented names
  (Plume-sur-Encre) and writes times as digits (8 h 10): those differences are expected, not voice faults.

## Tests (run from `le-cahier/tests/`)

    node recit_data_test.cjs      # story data integrity (~900 assertions)
    node srs_test.cjs             # SRS: fuzz, intake, leeches, comeback
    node mission_test.cjs         # daily mission cycle against a fake DOM
    python3 flows.py              # RPG shell end to end (Playwright, file://, no network)
    python3 flows_story.py        # story end to end, incl. playing all 13 pages (~120 assertions)
    python3 flows_voice.py        # real MP3 playback over HTTP: right track, right offset, stops at sentence end;
                                  # never a non-French synthesis voice; text size steps and layout (41 assertions)

The repo root is ESM, hence `.cjs` for the Node tests.
