# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repo is

The **Crosswalk Wisdom** content automation hub. It has two independent systems:

1. **Python content pipeline** (repo root) — repurposes YouTube videos into social media copy using the TubeonAI API, schedules posts to Zernio, and manages Encharge email subscribers.
2. **Remotion video generator** (`crosswalk-remotion/`) — renders animated social videos (Instagram reels, TikTok, LinkedIn, quiz results, explainers) using React + Remotion.

## Environment

Both systems require a `.env` file at the repo root:
- `TUBEONAI_API_KEY` — required for content pipeline
- `ENCHARGE_API_KEY` — required for webhook server and email scripts
- `ZERNIO_API_KEY` — required for scheduling scripts

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

## Architecture

### Python layer

| File | Purpose |
|------|---------|
| `main.py` | CLI entry point — orchestrates summary → repurpose → save |
| `tubeonai_client.py` | TubeonAI API wrapper (summaries, prompts, repurpose with polling) |
| `encharge_client.py` | Encharge API wrapper (subscribers, tags, quiz results) |
| `prompts.py` | Platform prompt definitions — edit here to change generated content |
| `webhook_server.py` | FastAPI server deployed to Railway; receives quiz results from the Fear Audit app and tags Encharge subscribers |

Scheduling scripts (`schedule-*.py`) are one-off scripts for specific campaigns — they call Zernio's API directly.

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

## Encharge email flows

Quiz results from the Fear Audit app (deployed separately on Bolt/Vercel) POST to `webhook_server.py`. The stage tag (`quiz-stage-start/stop/elder/human`) triggers the matching automated flow in Encharge. Email sequence IDs are documented in project memory.

## Key external services

- **TubeonAI** — AI video summarisation + content repurposing
- **Encharge** — email automation and subscriber management
- **Zernio** — social media scheduling (5 platforms: LinkedIn, Instagram, Facebook, TikTok, YouTube)
- **Freepik** — background image generation for posts (use web/subscription credits, not API credits)
- **Railway** — hosts `webhook_server.py`
