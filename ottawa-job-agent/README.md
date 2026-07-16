# Ottawa Job Application Agent

Fully automated daily job-application agent for Sahawat Nilwatcharamanee, relocating to Ottawa (start date Oct 13, 2026).

## What it does (daily, 8am, via LaunchAgent)

1. **Searches** Ottawa jobs across 6 categories using Claude's web_search:
   crossing guard, Thai Embassy, healthcare/PT, outreach/sales, GoodLife Fitness.
2. **Filters expired jobs** — drops anything past its deadline or marked closed (two layers: the search excludes them, the agent re-checks).
3. **Scores fit** 0–10 (Haiku).
4. For each fresh job ≥5: generates a **tailored cover letter** + a **branded resume PDF** for that category.
5. For each high-fit job ≥8: builds a **standout microsite** (personal pitch page) + a **30-second video script**.
6. **Auto-applies**: by email (Outlook) where an apply-email exists; otherwise attempts the company's website form via Playwright — auto-submits on known ATS platforms (Greenhouse, Lever) after verifying a real confirmation, and best-effort fills + screenshots everything else without submitting (pauses for your review).
7. **Tracks every real application** in `applications.json` — status lifecycle: applied → interview_scheduled → offer / rejected_after_application / rejected_after_interview, or auto-marked ghosted after 21 days of silence. Dashboard at `tracker_dashboard.html`.
8. **Emails a digest** to totomakus@gmail.com every day, even on quiet days — sorted by fit, deadlines flagged (⚠️ ≤3 days), microsite paths + video scripts + resume PDFs + tracker dashboard attached.
9. Dedupes via `seen_jobs.json` so you only ever see new postings.

## Tracking application outcomes

`seen_jobs.json` is internal dedup state — `applications.json` (managed by `tracker.py`) is the real outcome tracker. Update it whenever you hear back:

```bash
python3 tracker.py list
python3 tracker.py update "GoodLife" interview_scheduled "phone screen Jul 10"
python3 tracker.py update "Movati" rejected_after_application
python3 tracker.py dashboard   # rebuild tracker_dashboard.html
```

Valid statuses: `applied`, `interview_scheduled`, `offer`, `rejected_after_application`, `rejected_after_interview`, `ghosted`, `withdrawn`. Anything silent for 21+ days is auto-marked `ghosted` on the next daily run.

## Files

| File | Purpose |
|------|---------|
| `job_agent.py` | Orchestrator (run this) |
| `job_sources.py` | Web-search job discovery + deadline/status capture |
| `content_generator.py` | Fit scoring, cover letters, "why them", 30-day plan, video script |
| `resume_builder.py` | Category-tailored PDF resume (fpdf2) |
| `microsite_builder.py` | Branded HTML pitch page + personal pitch hub |
| `email_sender.py` | Outlook application sender + Gmail digest |
| `resume_data.py` | Sahawat's profile, summaries, skills, search targets |
| `run.sh` | LaunchAgent entry point |
| `publish.sh` | Deploy microsites live to Vercel |

## The standout layer (microsites + video)

High-fit jobs get a personal one-page pitch at `microsites/<slug>.html`:
hero with the Doctor→Crossing Guard→Coach story, a 30-second video slot,
"Why [employer]", a "first 30 days" plan, credentials, and a book-a-call CTA.

- Browse all pitches: open `microsites/index.html` (private hub).
- **Publish live:** `./publish.sh` (first run: one-time Vercel login; or set `VERCEL_TOKEN` in `.env` for full automation). Each pitch becomes `https://<project>.vercel.app/<slug>`.
- **Video:** the script is auto-written. Record a 30-second phone selfie reading it (most authentic), save as `microsites/<slug>.mp4`, and it auto-embeds. Re-run `publish.sh`.

## Manual run

```bash
cd ottawa-job-agent
/opt/anaconda3/bin/python3 job_agent.py
```

## Schedule

LaunchAgent `com.crosswalk.ottawa-job-agent` runs daily at 8:00am.
Logs: `job_agent.log`, `launchd.log`.

## Secrets (in repo-root `.env`)

`ANTHROPIC_API_KEY`, `GMAIL_APP_PASSWORD`, `OUTLOOK_APP_PASSWORD` (optional `VERCEL_TOKEN`).
