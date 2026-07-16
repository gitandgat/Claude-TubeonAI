# LinkedIn AI Agent — MVP

Fully autonomous LinkedIn content engine for Crosswalk Wisdom. Researches ICP pain points, learns brand voice, writes high-quality posts with 3 QA rounds, generates matching infographics, and schedules via Zernio.

## What It Does

**7-step daily pipeline:**
1. **Voice Engine** — Fetches 100 past LinkedIn posts from Zernio, builds 3000-word voice fingerprint
2. **Research Engine** — Scans Reddit (r/IMGreddit, r/MCCQE, etc.) + LinkedIn for viral post templates
3. **Hook Generator** — Creates 10 scroll-stopping hooks, auto-selects best via Claude scoring
4. **Post Writer** — 3 QA rounds: draft → critique → final revision (AI slop filter included)
5. **Infographic** — Generates 1080×1080 PNG with hook + insight using shot-scraper
6. **Scheduler** — Uploads image to Zernio CDN, schedules LinkedIn post at 8am ET
7. **Notifier** — Logs run, prints summary, optionally sends email

## Installation

No new dependencies needed — uses existing:
- `zernio_client.py` (post scheduling)
- `encharge_client.py` (optional email notifications)
- Claude API, Anthropic SDK

Requires:
- `requests` (Reddit API, LinkedIn scraper)
- `beautifulsoup4` (LinkedIn scraper)
- `shot-scraper` (image rendering)
- `pytz` (timezone handling)

```bash
pip install requests beautifulsoup4 shot-scraper pytz
```

## Usage

### Full Daily Run
```bash
python run_agent.py
```
Runs the complete pipeline: voice → research → hook → write (3 QA) → image → schedule → notify.

### Voice Profile Only
```bash
python run_agent.py --voice-only
```
Rebuilds the voice fingerprint from the last 100 published posts (cached for 7 days).

### Research Scan Only
```bash
python run_agent.py --research-only
```
Scans Reddit + LinkedIn for current pain points, prints brief.

### Dry Run
```bash
python run_agent.py --dry-run
```
Full pipeline without actually scheduling to Zernio. Useful for testing.

## Configuration

Edit `linkedin_agent/config.py` to customize:
- **Subreddits**: `TARGET_SUBREDDITS` (add/remove research sources)
- **Schedule time**: `LINKEDIN_SCHEDULE_TIME` (default: 8am ET)
- **Daily limit**: `LINKEDIN_DAILY_LIMIT` (LinkedIn allows 5/day)
- **Post length**: `POST_MIN_LENGTH`, `POST_MAX_LENGTH` (600-1200 words)
- **Banned phrases**: `BANNED_PHRASES` (AI slop filter)

## Output Files

All runs generate logs and artifacts:
- `linkedin_agent/data/voice_profile.json` — Analyzed brand voice (7-day cache)
- `linkedin_agent/data/daily_research.json` — Today's pain points + opportunities
- `linkedin_agent/data/schedule_log.jsonl` — Every scheduled post (post ID, hook, time)
- `linkedin_agent/data/run_log.jsonl` — Every run (success/failure, component status)
- `linkedin_agent/data/infographics/` — Generated PNG images
- `linkedin_agent/data/performance.json` — Manual performance tracking (see Self-Learning)

## Self-Learning Loop (MVP)

For MVP, the learning loop is **manual-assist**:

1. **Track performance** — Add top-performing posts to `linkedin_agent/data/performance.json`:
   ```json
   {
     "2026-05-29": {
       "post_id": "abc123",
       "hook": "Your hook text",
       "impressions": 5000,
       "likes": 150,
       "comments": 42,
       "shares": 8
     }
   }
   ```

2. **Voice engine** will re-analyze weekly, giving higher weight to top performers.

3. **Next iteration** — Wire LinkedIn Marketing API to auto-populate performance data from actual analytics.

## Troubleshooting

### "Failed to load voice profile"
- First run requires 100+ published posts on LinkedIn (via Zernio)
- Check Zernio API key is valid in `.env`
- Run `python run_agent.py --voice-only` to debug

### "No pain points found in research"
- Reddit or LinkedIn scraper is blocked
- Check internet connection, try `python run_agent.py --research-only` 
- May need to rotate User-Agent in `clients/reddit_client.py`

### "Image file not found" (infographic)
- `shot-scraper` is not installed or not in PATH
- Install: `pip install shot-scraper`
- Or skip image generation — posts still schedule without images

### "Post validation failed"
- Post exceeds 1200 words or under 600 words
- Contains banned AI phrases (check `BANNED_PHRASES` in config)
- Missing CTA or closing question
- Review the post in dry-run mode: `python run_agent.py --dry-run`

### "Daily limit reached"
- You've already scheduled 5 posts to LinkedIn today
- Wait until tomorrow or edit `LINKEDIN_DAILY_LIMIT` in config

## Architecture

```
linkedin_agent/
├── config.py                    # All constants, env vars, settings
├── clients/
│   ├── reddit_client.py         # Reddit API (public JSON endpoints)
│   └── linkedin_scraper.py      # Google search + BeautifulSoup
├── engine/
│   ├── voice_engine.py          # Analyzes 100 posts → fingerprint
│   ├── research_engine.py       # Reddit + LinkedIn → pain points
│   ├── hook_generator.py        # 10 hooks → auto-select best
│   ├── post_writer.py           # 3 QA rounds, AI slop filter
│   └── infographic.py           # HTML → PNG (shot-scraper)
├── scheduler.py                 # Wraps ZernioClient
├── notifier.py                  # Logs, prints, emails
├── agent.py                     # Orchestrator (7-step pipeline)
├── data/                        # Outputs, caches, logs
└── README.md                    # This file
```

## Next Iterations (Post-MVP)

1. **LinkedIn API analytics** — Wire LinkedIn Marketing API to fetch actual impressions/likes/comments, auto-populate `performance.json`
2. **Weekly learning** — Automatically re-weight voice profile based on top performers
3. **Scheduling flexibility** — Allow multi-post days, custom scheduling
4. **Template discovery** — Identify and save viral post templates for reuse
5. **Engagement loop** — Monitor comments in real-time, suggest reply templates
6. **Email sequence** — Generate companion Encharge email for each post

## Support

For issues or questions, check:
1. `linkedin_agent/data/run_log.jsonl` — Last run status
2. Run `python run_agent.py --dry-run` — Test without scheduling
3. Run `python run_agent.py --research-only` — Check ICP research works
