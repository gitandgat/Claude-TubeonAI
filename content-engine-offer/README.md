# Competitor Content Engine — Seed Prospect List

Day-2 artifact for the 30-day "build & sell an automation" plan.
Flagship product = the **YouTube Parasite + Content Improvement** system (rebranded
**Competitor Content Engine**), sold cold into **career-course/cohort creators**.

## The core logic: sell the challenger, parasite the king

- **Buyers = challengers.** Career coaches who **sell a course/cohort AND publish content**,
  but are **NOT** the category king. They feel the pain of losing the content race.
- **Parasite target = the king.** The biggest channel in their sub-vertical (ByteByteGo,
  NeetCode, Linda Raynier, Mayuko, Exponent...). We mine the king's best videos to build
  the challenger 30 days of better content + a gap report.
- **Cold open = a free sample:** "Here are 5 pieces I mined from [king], plus 3 topics they
  win on that you ignore. Built it free. Want the other 25?"

## ICP filter (this matters more than the vertical)

KEEP a prospect only if **all** are true:
1. Sells a course / cohort / paid program (one-to-many = $1.5k is trivial)
2. Actively publishes content (YouTube/podcast/LinkedIn)
3. Is **NOT** already a category king (kings have content teams — they're targets, not buyers)

DROP: 1:1-only mentors (e.g. MentorCruise book-by-month tier — wrong budget).

## Columns

| column | meaning |
|---|---|
| `tier` | `challenger` = buy-ready ICP. `borderline-king` = verify they still feel pain before pitching. |
| `parasite_target_king` / `king_channel` | what we mine for their free sample |
| `content_depth_note` | the angle/gap to lead the cold email with |
| `confidence` | how well the course+channel existence is grounded in research (High/Med/Low) |
| `needs` | what's still required before sending — **email enrichment not yet done** |

## The pipeline (built + verified)

Three runnable scripts, all yt-dlp-first (no paid keys to start):

| script | does | status |
|---|---|---|
| `lead_scraper.py` | discovers challenger-tier channels per sub-vertical, drops kings by sub count | ✅ ran live: tech sales → 10 challengers (`scraped/tech-sales.csv`) |
| `free_sample_generator.py` | mines a king's videos + prospect's, AI gap analysis → 1-page teaser | ✅ ran live on Trent Dressel via local Ollama ($0); `out/trent-dressel-RAW.md` |
| `enrich_emails.py` | adds emails via Hunter; **gates if no key, never fabricates** | ✅ ran live (gated, 0 fabricated); reuses repo `keychain_secrets` if present |

```bash
# 1. expand the seed
python lead_scraper.py --vertical "tech sales" --max-channels 25
python lead_scraper.py --all          # all 8 sub-verticals

# 2. enrich (needs a website column + a key)
export HUNTER_API_KEY=...             # or wire keychain_secrets
python enrich_emails.py --in scraped/tech-sales.csv --website-col website

# 3. generate each prospect's free sample
python free_sample_generator.py --prospect "Trent Dressel" \
  --prospect-channel <url> --king "Patrick Dang" --king-channel <url> \
  --vertical "tech sales career" --out out/trent.md
```

The flagship proof artifact (sales-ready, hand-polished from the real machine output)
is `out/trent-dressel-gap-teaser.md`.

## Known next steps / honest gaps

1. **Quality tier on the generator.** The local Ollama output is proof-of-life but
   slop-prone; for client-facing samples point the AI factory at Claude
   (`AI_PROVIDER=claude`) or run the draft through `/stop-slop`.
2. **Website resolution for enrichment.** Coaches hosted on Maven/Skool/Gumroad/Patreon
   need their *own* domain (from the channel About page) before Hunter can find an email —
   `enrich_emails.py` flags these rather than guessing.
3. **Tier filter** — confirm the 4 `borderline-king` rows (Greg Hogg, Gaurav Sen,
   Andrew LaCivita, Madeline Mann) still feel competitive pain, or cut them.
4. **Scale the scrape** — `lead_scraper.py --all` to widen every sub-vertical toward the
   200–400 prospects the Week-3 outbound push needs.

## Sources

Grounded in live web research (Jun 2026). Key references: Maven course pages,
Feedspot career/UX YouTuber lists, CourseReport/igotanoffer interview-coaching roundups,
and per-creator sites/LinkedIn. Subscriber figures only included where verified in search.
