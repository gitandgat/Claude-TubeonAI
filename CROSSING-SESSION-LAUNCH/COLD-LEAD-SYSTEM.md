# Cold-lead system — Crosswalk Wisdom

Two engines feeding the same funnel: cold prospect → Fear Audit → Encharge nurture
→ $97 Crossing Session. Phase 1 is live-safe and running off your daily content.
Phase 2 is built and ready to switch on once Phase 1 proves the funnel.

---

## PHASE 1 — Comment-to-DM (SAFE, ON NOW)

**How it works:** every post your daily agent publishes now ends with
"Comment FEAR and I'll send you the free Fear Audit." Sendpilot watches the
comments and auto-DMs the link to everyone who comments. Opt-in = account-safe,
on-brand, scales with content you already produce.

**What's already done (code):**
- `linkedin_agent/config.py` → `COMMENT_DM_ENABLED`, keyword `FEAR`, 3 rotating CTAs
- `linkedin_agent/agent.py` → appends the CTA to every post (after slop-scoring,
  so it never hurts post quality). Toggle off with env `LINKEDIN_COMMENT_DM=0`.

**Your one-time Sendpilot setup (UI — no API for this):**
1. Sendpilot → connect your LinkedIn account (if not already)
2. Create a **Comment automation**:
   - Trigger keyword: `FEAR`
   - Action: send DM (template below)
   - Apply to: your LinkedIn posts (set as a standing rule if Sendpilot supports
     "all future posts"; otherwise add each day's post URL — the agent posts ~5/day)
3. Optional reply-to-comment: "Sent! Check your DMs 📩" (boosts comment count = reach)

**DM template (paste into Sendpilot):**
> Hi {{firstName}} — here's your free Fear Audit: https://fear-audit.vercel.app
> Takes 3 minutes and tells you which of the three fears (money, judgment, or
> identity) is actually keeping you at the curb. Reply and tell me what you score —
> I read every one.

**Stretch (later):** wire Sendpilot's `message.received` webhook → a serverless
function → tag the lead in Encharge and start the Fear Audit nurture automatically.
Blocked right now: the old Railway webhook is dead (404). Park until Phase 1 has volume.

---

## PHASE 2 — Cold-connect campaigns (BUILT, SWITCH ON WHEN READY)

**How it works:** find LinkedIn creators whose *commenters* are your ICP, scrape
those engagers in Sendpilot, auto-connect with a soft note, and message on accept.
More reach, but it DMs strangers — so it carries real account-ToS risk. Caps matter.

**What's already done (code):**
- `cold_lead_sourcing.py` → Perplexity finds creators / hashtags / subreddits /
  FB groups / search phrases where the ICP gathers. Writes a weekly briefing to
  `CROSSING-SESSION-LAUNCH/cold-targets/YYYY-MM-DD.md` with cold opener templates.
- First run done — see today's briefing for 10 creators + 6 subreddits + 5 FB groups.

**Your steps to switch it on:**
1. Run `python3 cold_lead_sourcing.py` weekly (or I can cron it)
2. In Sendpilot: scrape the briefing's creators' **post commenters** (intent > followers)
3. Build a connect campaign with the briefing's opener templates
4. **Cap at ~15 connects/day** the first 2 weeks; ramp slowly. Warm-only.
5. Manage replies in Sendpilot's unified inbox; move warm ones toward the Fear Audit

**Safety rules (non-negotiable — your 1K account is the asset):**
- Never exceed ~20 connects/day or ~30 messages/day
- No links in the first message (connect note or opener) — LinkedIn flags link-spam
- Personalize the connect note; never blast identical text
- If LinkedIn warns/restricts, STOP immediately for a week

---

## The funnel both engines feed

```
Cold prospect (comment FEAR / accepts connect)
        │
        ▼
Fear Audit (fear-audit.vercel.app) ──► Encharge (fearType tagged)
        │
        ▼
Nurture + daily outreach-briefing.py surfaces them as warm leads
        │
        ▼
$97 Crossing Session (sahawat.gumroad.com/l/crossing-session)
```

## Priority order (don't skip)

1. **Activate Phase 1** (Sendpilot comment automation) — safe, immediate, uses content you already post
2. **Work the 19 warm leads** already in the system (DM-NOW.md) — fastest path to first $
3. **Switch on Phase 2** only after Phase 1 shows the comment→audit→session funnel converts
