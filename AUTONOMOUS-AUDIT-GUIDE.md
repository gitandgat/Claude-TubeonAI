# Autonomous AI Audit System

Three modular agents for /stop-slop quality control. Choose based on your workflow.

## Option A: Autonomous Loop Agent

**File:** `zernio-auto-audit-fix.py`

Runs on-demand. Loops until 100% compliance or max retries.

```bash
python3 zernio-auto-audit-fix.py
```

**What it does:**
1. Audits all scheduled posts (100% coverage)
2. Identifies posts <35/50
3. Auto-rewrites each failing post using Claude
4. Re-audits to verify all pass
5. Loops up to 5 times until all posts pass
6. Returns detailed JSON report

**Output:** `auto-audit-report.json`
- Loop-by-loop history
- Before/after scores
- Final compliance status

**Use case:** Full system audit, quality guarantee before major publish

---

## Option B: Scheduled Background Agent

**File:** `zernio-scheduled-auditor.py`

Runs daily at 2am (via cron) or on-demand. Only acts if failures found.

```bash
# Run once
python3 zernio-scheduled-auditor.py

# Schedule daily (add to crontab)
0 2 * * * cd /path/to && python3 zernio-scheduled-auditor.py
```

**What it does:**
1. Executes Option A (autonomous loop)
2. Loads results
3. If failures exist: sends Discord notification
4. If all pass: silent success (no noise)

**Notifications:**
- Discord webhook integration
- Email support (optional)
- Embeds: status, passing/failing counts, loop count

**Use case:** Continuous monitoring, only alert on problems

---

## Option C: Pre-Publish Quality Gate

**File:** `zernio-prepublish-gate.py`

Blocks individual posts before Zernio scheduling.

```bash
# Check post quality
python3 zernio-prepublish-gate.py my-post.md

# Auto-fix and save corrected version
python3 zernio-prepublish-gate.py my-post.md --auto-fix
```

**What it does:**
1. Scores single post against /stop-slop
2. If <35/50:
   - Lists specific recommendations
   - Blocks publication (exit code 1)
   - Optionally auto-fixes with `--auto-fix`
3. If ≥35/50:
   - Approves publication (exit code 0)
   - Saves audit report

**Output:**
- `{post_id}-audit.json` — detailed scoring breakdown
- `{post_id}-fixed.md` — auto-fixed version (if `--auto-fix` used)

**Exit codes:**
- `0` = pass (approved for publish)
- `1` = fail (needs revision)

**Use case:** Quality gate in content pipeline, before scheduling

---

## Integration Examples

### Pre-Publish Workflow (Recommended)

```bash
# 1. Write post
nano my-new-post.md

# 2. Check quality
python3 zernio-prepublish-gate.py my-new-post.md

# 3a. If it fails, auto-fix
python3 zernio-prepublish-gate.py my-new-post.md --auto-fix

# 3b. Or manually revise and recheck
nano my-new-post.md
python3 zernio-prepublish-gate.py my-new-post.md

# 4. Once approved, schedule to Zernio
python3 schedule-to-zernio.py my-new-post.md
```

### Continuous Monitoring

```bash
# Add to crontab for nightly checks
0 2 * * * cd /Users/toto/Claude\ TubeonAI && python3 zernio-scheduled-auditor.py >> audit-cron.log 2>&1
```

### Emergency Audit + Fix

```bash
# Full system remediation
python3 zernio-auto-audit-fix.py

# Check report
cat auto-audit-report.json | python3 -m json.tool | less
```

---

## Scoring Breakdown

Each post scored on 5 dimensions (1–10 each, 50 max):

| Dimension | What it measures | Penalized by |
|-----------|------------------|--------------|
| **Directness** | Clear, specific statements | Vague declaratives, throat-clearing |
| **Rhythm** | Varied sentence length, flow | Em-dashes, metronomic length |
| **Trust** | Respects reader intelligence | Passive voice, lazy extremes |
| **Authenticity** | Sounds human, not AI | Adverbs, inanimate actions |
| **Density** | No unnecessary filler | Wh-question starts, meta-joiners |

**Threshold:** ≥35/50 = approved

---

## Anti-Patterns Detected

### Adverbs (4+ = flag)
`really`, `truly`, `literally`, `clearly`, `honestly`, `simply`, `basically`, `actually`, `definitely`, `certainly`, `obviously`, `absolutely`, `essentially`, `quite`, `rather`, `fairly`, `extremely`

### Throat-Clearing (1+ = flag)
`here's what`, `this is`, `that is`, `the fact is`, `the truth is`, `what we`, `the thing is`

### Passive Voice
`is/are/was/were/been + [verb in past participle]`

### Vague Declaratives (1+ = flag)
`the reason`, `the issue`, `the problem`, `the solution`, implications/reasons/causes/effects are

### Inanimate Actions (1+ = flag)
Nouns performing human verbs: "the decision emerges," "the problem becomes"

### Lazy Extremes (1+ = flag)
`always`, `never`, `every`, `everyone`, `nobody`, `everything`, `nothing`

### Em-Dashes (1+ = flag)
`—` (breaks rhythm)

### Meta-Joiners (1+ = flag)
`the rest of`, `as mentioned`, `furthermore`, `moreover`, `additionally`, `in addition`

---

## Sample Output

### Option A Final Report

```json
{
  "status": "SUCCESS",
  "timestamp": "2026-06-06T08:53:34.901283",
  "loops": 1,
  "total_posts": 106,
  "passing": 106,
  "failing": 0,
  "loop_history": [
    {
      "loop": 1,
      "passing": 106,
      "failing": 0
    }
  ]
}
```

### Option C Pre-Publish Gate (Fail)

```
Score: 28.0/50
❌ POST FAILS - Below 35/50 threshold

Recommendations:
  • Remove 4 adverbs (really, truly, literally, etc.)
  • Cut 3 throat-clearing phrases (here's what, this is, etc.)
  • Replace 2 lazy extremes (always, never, every)
```

### Option C Pre-Publish Gate (Pass)

```
Score: 48.0/50
✅ POST PASSES - Ready to publish
```

---

## Configuration

### Discord Webhook (Option B)

Add to `.env`:
```
DISCORD_WEBHOOK_URL=https://discordapp.com/api/webhooks/YOUR_ID/YOUR_TOKEN
```

### API Keys

Requires:
- `ZERNIO_API_KEY` — Zernio API access
- `ANTHROPIC_API_KEY` — Claude API for rewriting

Both in `.env` file.

---

## Troubleshooting

### "Post not found" error in Option A/B
- Zernio API is slow; retry in a few seconds
- Check post IDs are correct in audit report

### Auto-fix produces worse content
- Claude may prioritize grammar over voice
- Use Option C with `--auto-fix` to review before publishing
- Manually revise and re-check

### Discord notifications not sending
- Check webhook URL in `.env`
- Verify network access to discord.com

### Endless loop in Option A
- Max loops capped at 5 (configurable)
- Some posts may require manual revision
- Check `auto-audit-report.json` for still-failing posts

---

## Next Steps

1. **Immediate:** Use Option C pre-publish for new posts
2. **Daily:** Set Option B on cron for nightly monitoring
3. **As-needed:** Run Option A for full system audits
4. **Escalation:** Manual review for consistently failing posts

All three options work together to maintain quality at scale.
