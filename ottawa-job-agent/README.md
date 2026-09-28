# Ottawa Job Application Agent

Fully automated daily job-application agent for Sahawat Nilwatcharamanee, relocating to Ottawa (start date Oct 13, 2026).

## What it does (every 4 hours, 6x/day, via LaunchAgent)

1. **Searches** Ottawa jobs across 6 categories using Claude's web_search:
   crossing guard, Thai Embassy, healthcare/PT, outreach/sales, GoodLife Fitness.
2. **Scans known Greenhouse/Lever boards directly** (`ats_boards.py`) via their free public JSON APIs — no LLM parsing, no extra search cost. The board registry (`known_boards.json`, gitignored) starts empty and only grows from real Greenhouse/Lever URLs seen in that day's web-search results, never guessed company tokens. Remote roles are only accepted when explicitly Canada-friendly (Canada/North America/Global/no qualifier) — a plain "Remote" or "Remote - USA" tag is filtered out.
3. **Filters expired jobs** — drops anything past its deadline or marked closed (two layers: the search excludes them, the agent re-checks).
4. **Scores fit** 0–10 (Haiku).
5. For each fresh job ≥5: generates a **tailored cover letter** + a **branded resume PDF** for that category.
6. For each high-fit job ≥8: builds a **standout microsite** (personal pitch page) + a **30-second video script**.
7. **Auto-applies**: by email (Outlook, OAuth2/XOAUTH2 — see setup below) where an apply-email exists; otherwise attempts the company's website form via Playwright — auto-submits on known ATS platforms (Greenhouse, Lever) after verifying a real confirmation, and best-effort fills + screenshots everything else without submitting (pauses for your review). A **review-only mode** (`agent_config.py`, see below) can hold every application for your review instead of auto-submitting.
8. **Tracks every real application** in `applications.json` — status lifecycle: applied → interview_scheduled → offer / rejected_after_application / rejected_after_interview, or auto-marked ghosted after 21 days of silence. Dashboard at `tracker_dashboard.html`.
9. **Emails a digest** to totomakus@gmail.com every day, even on quiet days — sorted by fit, deadlines flagged (⚠️ ≤3 days), microsite paths + video scripts + resume PDFs + tracker dashboard attached.
10. Dedupes via `seen_jobs.json` so you only ever see new postings.

### Review-before-submit toggle

By default the agent auto-submits applications once a safe confirmation can be verified. To hold every application for manual review instead (forms get filled, screenshot taken, but submit is never clicked):

```bash
python3 agent_config.py on       # switch to review-only
python3 agent_config.py off      # back to auto-submit (default)
python3 agent_config.py status   # check current mode
```

This is a persistent JSON flag (`agent_config.json`, gitignored), not a CLI arg — so it applies the same way to scheduled launchd runs as to manual ones.

### One-time setup: authorize Outlook email sending

Microsoft has permanently disabled Basic Authentication for SMTP AUTH on Outlook.com/Hotmail — `OUTLOOK_APP_PASSWORD` + `smtplib.login()` can no longer send mail (fails every time with `535, 5.7.139`). Application emails now go out via OAuth2 (XOAUTH2), same auth-code-with-PKCE approach as Thunderbird, no Azure app registration needed. One-time action; the token then silently refreshes:

```bash
python3 authorize_outlook_smtp.py
# → prints a sign-in URL. Open it, sign in with Sahawat.nil@outlook.com.
# → browser lands on https://localhost/?code=... showing "can't connect" — expected.
#   Copy the full URL from the address bar, then:
python3 authorize_outlook_smtp.py "<pasted-url>"
# → saves outlook_token_send.json (gitignored)
```

Until this is done, `send_application()` fails for every job with an `apply_email` and those jobs fall through to the "couldn't auto-apply" / website-form path instead.

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
| `jobbank_source.py` | Job Bank (Canada) discovery — paginated, Ottawa-area aware |
| `ats_boards.py` | Direct Greenhouse/Lever board polling (`known_boards.json`) |
| `workday_source.py` | Direct Workday tenant polling — GoodLife + CHEO (`known_workday.json`) |
| `health_boards_source.py` | Ottawa health employers' own boards — CIHI (Njoyn, headless browser), City of Ottawa (SuccessFactors), The Royal (Jobvite) (`known_health_boards.json`) |
| `employer_site.py` | Resolves a posting to the employer's own apply URL, not the aggregator's |
| `walkability.py` | Commute classification from 335 Cooper St (walk / transit / far) |
| `web_applier.py` | Playwright auto-apply for Greenhouse, Lever, and generic career-site forms |
| `workday_applier.py` | Workday wizard auto-apply via his own candidate account (see below) |
| `form_schema.py` | Reads the real application questions off a form (Greenhouse API or DOM) |
| `application_prefill.py` | Answers those questions honestly, flags the ones only he can answer |
| `jobbank_apply.py` / `jobbank_session.py` | Job Bank Direct Apply, using his captured session |
| `resolve_captcha.py` | Reopens a captcha-gated application in a visible browser |
| `tracker.py` / `dashboard_export.py` / `run_history.py` | Outcome tracking, dashboard feed, run log |
| `content_generator.py` | Fit scoring, cover letters, "why them", 30-day plan, video script |
| `resume_builder.py` | Category-tailored PDF resume (fpdf2) |
| `microsite_builder.py` | Branded HTML pitch page + personal pitch hub |
| `email_sender.py` | Outlook application sender + Gmail digest |
| `outlook_oauth.py` | OAuth2 (XOAUTH2) SMTP-send client for Outlook — Basic Auth is dead, see setup above |
| `authorize_outlook_smtp.py` | One-time CLI to authorize Outlook email sending (run this first) |
| `resume_data.py` | Sahawat's profile, summaries, skills, search targets |
| `run.sh` | LaunchAgent entry point |
| `publish.sh` | Deploy microsites live to Vercel |

## Workday auto-apply (GoodLife first)

Workday postings can't be applied to anonymously — the form only exists behind a
candidate account on the employer's own tenant. Sahawat's password never touches
this codebase: `workday_session.py` opens a real, visible browser on a tenant's
Careers site so he can sign in himself, then saves only the resulting session
cookies (Playwright `storage_state`) to a local, gitignored file. Run it once per
tenant (and again whenever a saved session expires):

```bash
/opt/anaconda3/bin/python3 workday_session.py goodlifefitness
```

`workday_applier.py` then reuses that saved session, walks the wizard, answers the
questions through `application_prefill.py`, and **submits only when every required
answer is one it could fill honestly** — anything needing his real input stops the
run one click short of Submit and emails the prefilled package instead.

### Keeping the session alive

Workday drops a session on a server-side **idle** timer of roughly 85 minutes, not
on cookie expiry — a session with 16 of its 19 cookies still unexpired was already
anonymous 85 minutes after its last use. The agent itself only runs every 4 hours,
so between two scheduled runs the session idles out and the next run finds it dead.
That gap is why no Workday application has ever been submitted.

`workday_keepalive.py` closes it: every 45 minutes it loads each tenant's Careers
page with the saved session and writes the rolling cookies back, which is all
Workday's idle timer needs. It never signs in, and it never opens a posting's
`/apply` URL — landing there as a signed-in candidate drops straight into the
wizard and would leave a draft application behind on every firing. A session that
has already expired is reported and **left untouched**, since overwriting a good
file with a logged-out one would cost him a manual sign-in for nothing.

```bash
/opt/anaconda3/bin/python3 workday_keepalive.py                  # all tenants
/opt/anaconda3/bin/python3 workday_keepalive.py goodlifefitness  # just one
```

To run it on a schedule, install `launchd/com.crosswalk.workday-keepalive.plist`
(see the comment at the top of that file). Logs to `workday_keepalive.log`.

Which tenants it's allowed to submit for is a per-tenant `auto_apply` flag in
`known_workday.json`. GoodLife is `true`; everything else — CHEO included — is
`false` and gets the package, until the wizard is proven on one real GoodLife
posting. Check the current state (approval flag + saved-session status) without
touching a browser:

```bash
/opt/anaconda3/bin/python3 workday_applier.py
```

A tenant with no saved session, or an expired one, is safe: the agent degrades to
the prefill package rather than failing the run.

## Health employer boards (the second supply line for the priority track)

With Serper out of credits and every CHEO posting already seen, the
health-informatics track had no fresh supply by Sept 2026. A survey of Ottawa
health employers' career sites found three boards readable without an account,
all rows in `known_health_boards.json` and polled by `health_boards_source.py`:

| Employer | ATS | How it's read |
|---|---|---|
| CIHI (Canadian Institute for Health Information) | Njoyn | headless Chromium — plain requests hit a Radware bot check |
| City of Ottawa (incl. Ottawa Public Health) | SAP SuccessFactors | keyword search, server-rendered, 25 rows/page |
| The Royal | Jobvite | listing needs `nl=1&fr=false` + a Referer or it redirects |

A posting's category is decided on its **title** (data / informatics /
health-information words), not on the description: every clinical posting at a
hospital mentions the EHR, and on the first live poll that tagged nurse
practitioners as health informatics and let them bypass the score gate. None of
these ATSs accept an anonymous application, so the job's URL is the posting
page; the web applier follows Apply, hits the login wall, and emails the prefill
package instead. Smoke-test with `python3 health_boards_source.py`.

Checked the same day and not usable without a browser session or at all, so
nobody re-probes them: The Ottawa Hospital (PeopleSoft, 403), QCH (DLGL
e-recruiter, JS + login), EORLA (Njoyn, needs a session token), Bruyère (UltiPro,
no public board link), Ontario Health / Montfort / CMA (403 to scripts), GC Jobs
(JSF session app), Infoway (no board).

Job Bank got the same treatment: its search is loose full text over NOC titles
and some strings return nothing at all for Ottawa ("health information",
"fitness instructor"), so a starved category now carries several short queries
(`queries` in `jobbank_source.QUERIES`) deduped under one resolve cap.

**Quiet runs send no email.** A run that applied to nothing, has nothing to
review, ghosted nothing and raised no alert skips the digest entirely; a real
alert (e.g. Serper credits) still gets through, once a day.

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

LaunchAgent `com.crosswalk.ottawa-job-agent` runs every 4 hours: 00:00, 04:00, 08:00, 12:00, 16:00, 20:00.
Logs: `job_agent.log`, `launchd.log`.

## Secrets (in repo-root `.env`)

`ANTHROPIC_API_KEY`, `GMAIL_APP_PASSWORD` (optional `VERCEL_TOKEN`). Workday sign-in
uses no env vars at all — see `workday_session.py` above.

Outlook application sending no longer uses a password (`OUTLOOK_APP_PASSWORD` is unused/dead — Basic Auth is disabled by Microsoft) — it uses the OAuth2 token from `python3 authorize_outlook_smtp.py`, see setup above.
