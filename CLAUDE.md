# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

The **Crosswalk Wisdom** content automation hub — a personal monorepo of independent, largely self-contained systems that share one `.env`, one Python environment, and (for some) the Zernio/Encharge accounts. The three actively-developed systems are:

1. **Python content pipeline** (repo root) — repurposes YouTube videos into social media copy using the TubeonAI API, schedules posts to Zernio, and manages Encharge email subscribers.
2. **Remotion video generator** (`crosswalk-remotion/`) — renders animated social videos (Instagram reels, TikTok, LinkedIn, quiz results, explainers) using React + Remotion.
3. **LinkedIn Verticals Engine** (`linkedin_agent/` + `run_verticals.py`) — autonomous daily LinkedIn content engine; the most actively maintained system (see current branch history).

Beyond these, the repo accumulates many smaller independent projects in their own top-level directories (trading bot, avatar renderer, job-application agent, email/file organizers, etc.) — see [Other independent systems](#other-independent-systems). Each has its own README; don't assume conventions from one system carry over to another.

## Environment

Requires a `.env` file at the repo root. Key variables (see `.env.example` for the full list):
- `TUBEONAI_API_KEY` — content pipeline
- `ENCHARGE_API_KEY` — webhook server and email scripts
- `ZERNIO_API_KEY` — all scheduling scripts and the verticals engine
- `ANTHROPIC_API_KEY` / `OPENAI_API_KEY` — LinkedIn agent generation, local repurpose fallback
- Trading-bot and job-agent specific keys (Alpaca, Alpha Vantage, Massive, Google/MSAL OAuth) are only needed inside those subsystems

**Never hardcode the Zernio key** — import it from `zernio_key.py` (`from zernio_key import ZERNIO_API_KEY`). Every scheduling script in this repo follows this pattern; it's the one convention shared across systems.

## Python pipeline commands

```bash
# Repurpose YouTube videos into all 7 platforms (TubeonAI).
# Add URLs to the URLS list inside batch_repurpose.py, then run:
python batch_repurpose.py
# → output/YYYY-MM-DD/<title>.txt, one file per video

# No-API fallback when TubeonAI fails (free local AI via ai_client_factory):
python repurpose_local.py summary.txt --title "Topic"   # or --text "..." / stdin

# Run the quiz webhook server locally (main.py starts this same app)
python webhook_server.py
# → http://localhost:8000/quiz-results (POST)
# → http://localhost:8000/health (GET)
```

Prompt IDs are cached in `prompt_ids.json` after the first run — don't delete it.

## Remotion commands

```bash
cd crosswalk-remotion
npm install

# Open Remotion Studio (preview all compositions)
npm start

# Render a single composition by ID
remotion render src/index.ts <CompositionId> out/<filename>.mp4

# Render all April posts
npm run render:april

# Render a single April post
npm run render:april:one AprilPost-apr-15 out/april/apr-15.mp4 --props '{"postId":"apr-15"}'
```

## LinkedIn Verticals Engine commands

```bash
# Full daily run: snapshot analytics → rebuild per-vertical learning → post all 5 verticals
python3 run_verticals.py

# Generate + print without posting or touching the network
python3 run_verticals.py --dry-run

# Run a single vertical (crosswalk | trainer | fitness | mind | health)
python3 run_verticals.py --vertical fitness

# Snapshot + rebuild winning_patterns.json for all verticals, no posting
python3 run_verticals.py --learn-only

# Tests (no pytest required, but pytest works too)
python3 test_linkedin_agent.py
pytest linkedin_agent/tests/
```

`run_verticals.py` is the production entry point; it **replaces** the older single-account `linkedin_agent/agent.py` / `run_agent.py` described in `linkedin_agent/README.md` (that README documents the pre-verticals MVP and is stale on the pipeline shape — the client/multi-tenant layer and 5-vertical model below are current).

## Architecture

### Python content pipeline (repo root)

| File | Purpose |
|------|---------|
| `main.py` | CLI entry point — orchestrates summary → repurpose → save |
| `tubeonai_client.py` | TubeonAI API wrapper (summaries, prompts, repurpose with polling) |
| `encharge_client.py` | Encharge API wrapper (subscribers, tags, quiz results) |
| `prompts.py` | Platform prompt definitions — edit here to change generated content |
| `webhook_server.py` | FastAPI server deployed to Railway; receives quiz results from the Fear Audit app and tags Encharge subscribers |
| `zernio_key.py` | Centralized Zernio API key loader — import this everywhere, never re-read `.env` for the key |

Scheduling scripts (`schedule-*.py`, `zernio-*.py`) are one-off scripts for specific campaigns or one-time repairs — they call Zernio's API directly and are not meant to be reused as libraries.

### Remotion layer (`crosswalk-remotion/src/`)

| Path | Purpose |
|------|---------|
| `index.tsx` | Remotion entry — calls `registerRoot` |
| `Root.tsx` | Registers all `<Composition>` elements with IDs, dimensions, and `defaultProps` |
| `theme.ts` | Single source of truth for colors (`amber`, `charcoal`, `warmWhite`, etc.) and fonts (Playfair Display / Inter) |
| `compositions/` | One file per video format; receives props and renders the full composition |
| `components/` | Shared primitives: `Logo`, `PhotoBackground` (Ken Burns zoom), `CrosswalkBackground` (animated SVG fallback), `AnimatedLines`, `VideoOverlay` |
| `data/april-posts.ts` | Content data for all April posts (slug, date, image path, hook, sub-text) |
| `data/march-posts.ts` | Same structure for March 26–31 transition posts |

**Composition naming convention:** `ComponentName-slug` (e.g. `TikTokReel-YellowVest`, `AprilPost-apr-15`, `VideoOverlay-01-sunk-cost`). The `Root.tsx` maps post data arrays to compositions dynamically for April/March posts.

**Video dimensions by format:**
- Instagram posts / overlays: 1080×1080
- TikTok / Reels / explainers: 1080×1920
- LinkedIn video: 1920×1080
- LinkedIn banner (static): 1584×396

**Adding a new monthly post batch:** Add entries to the relevant data file in `src/data/`, then add a matching `<Composition>` block in `Root.tsx` (or extend the dynamic `.map()` loop).

### LinkedIn Verticals Engine (`linkedin_agent/`)

Five content verticals (`crosswalk`, `trainer`, `fitness`, `mind`, `health`) all publish to **one** LinkedIn profile, each in its own 08:00/11:00/14:00/17:00/20:00 ET day-part slot — this is how the 5/day LinkedIn cap is fully used without diluting brand voice. Every vertical shares the same proven `FORMAT_SPINE` prompt (first-person, specific-moment, concrete-numbers writing style) but has its own persona, theme rotation, and independent `winning_patterns.json` learning loop, since what performs for fitness content ≠ what performs for career-pivot content.

| File | Purpose |
|------|---------|
| `verticals.py` | Registry of the 5 verticals + the shared `FORMAT_SPINE` prompt template |
| `client_manager.py` | Multi-tenant layer for the *managed ghostwriting service* — a `Client` is a different paying person (own voice/niche/Zernio account/learning data) and is duck-compatible with `Vertical`, so it drops into the same `PostWriter` with no code changes |
| `config.py` | Constants: schedule times, data dirs, cross-post account IDs |
| `engine/analytics_engine.py` | Snapshots per-platform analytics before each run |
| `engine/learning_engine.py` | Rebuilds each vertical's `winning_patterns.json` from analytics |
| `engine/post_writer.py` | Draft → critique → final-revision writer with the AI-slop filter |
| `dedup.py`, `stop_slop_gate.py`, `json_utils.py` | Pure-logic helpers covered by `test_linkedin_agent.py` |
| `data/clients/<slug>/` | Per-tenant config, voice profile, winning patterns, schedule log (created by `client_manager.save_client`) |

`run_verticals.py` (repo root) is the orchestrator, not part of the package, because it's the launchd entry point. Key behaviors baked in from past incidents (see file docstring):
- Arms a hard watchdog (`os._exit`, 20 min) so a hung network call can never silently kill the daily cadence again — this is why launchd calls it through a `perl -e 'alarm ...'` wrapper in `launchd/com.crosswalk.linkedinverticals.plist` too.
- `_wait_for_network()` blocks before any real (non-dry-run) work so a cold-wake with no network yet defers cleanly and exits for launchd to retry, instead of hanging.
- Skips verticals that already have a post scheduled today (`_verticals_already_posted_today`), so **re-running it after a partial failure is always safe** — this is the standard recovery command.
- `verticals_liveness_monitor.py` runs after the daily job (`launchd/com.crosswalk.verticals-monitor.plist`) to reap any run that's still alive past `HUNG_AFTER_SEC` and alert if fewer than 5 posts got scheduled.

## Encharge email flows

Quiz results from the Fear Audit app (deployed separately on Bolt/Vercel) POST to `webhook_server.py`. The stage tag (`quiz-stage-start/stop/elder/human`) triggers the matching automated flow in Encharge. Email sequence IDs are documented in project memory.

## Other independent systems

These live in their own top-level directories, each self-contained with its own dependencies/README — treat them as separate projects that happen to share this repo and `.env`:

| Directory | What it is |
|-----------|------------|
| `trading-bot/` | Algorithmic trading bot (Kavout signals + SMA crossover, Alpaca paper execution, own SQLite DB). See `trading-bot/README.md`. |
| `avatar-engine/` | Local, $0 talking-head video generator (VoiSpark voiceover → SadTalker lip-sync). See `avatar-engine/README.md`. |
| `ottawa-job-agent/` | Fully automated daily job-search/apply agent (Claude web search → scoring → tailored resume/cover letter → auto-apply → digest email). See `ottawa-job-agent/README.md`. |
| `agents/` | Standalone email/file organizer agents (Gmail + Outlook via `email_accounts.json`). |
| `CROSSING-SESSION-LAUNCH/` | One-off launch-day automation (`execute.py`). |
| `lead-magnets/` | JSON → branded PDF/PNG lead-magnet generator + Encharge delivery. |
| `linkedin-schedule` skill / `viral-hooks-deploy`, `hooks-server.js` (root `package.json`) | Smaller/experimental Node tooling, not part of the main pipelines. |

`physical-assessment-app/` is excluded via `.gitignore` — it is its own separate git repository, not part of this one.

## Key external services

- **TubeonAI** — AI video summarisation + content repurposing
- **Encharge** — email automation and subscriber management
- **Zernio** — social media scheduling (5 platforms: LinkedIn, Instagram, Facebook, TikTok, YouTube)
- **Freepik** — background image generation for posts (use web/subscription credits, not API credits)
- **Railway** — hosts `webhook_server.py`
- **Anthropic/OpenAI** — post generation, scoring, and QA rounds in the LinkedIn Verticals Engine
- **VoiSpark** — voiceover generation (used by the avatar engine and video pipelines)
