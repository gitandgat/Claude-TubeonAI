# Managed LinkedIn Ghostwriting — Service Playbook

You already own a working $0 clone of ghostwriting-ai.com (Oiti, $49–79/mo). This
turns it into a **done-for-you managed service**: you onboard a paying client as a
new tenant, the agent writes + schedules in their voice, you keep the margin.

> Strategic note: sell the **outcome** (posts that sound like them, on autopilot),
> not software. Validate with paying clients first. Only build self-serve SaaS once
> demand is proven — see the gate at the bottom.

---

## The offer

**"I run an AI that writes LinkedIn posts in your exact voice — 5 a week,
scheduled, first comment included. You approve, it posts. Cancel anytime."**

Why it sells against Oiti and human ghostwriters:
- **vs Oiti ($49–79/mo):** they still have to write/steer it themselves. You do it for them.
- **vs human ghostwriters ($1.5k–5k/mo):** you're a fraction of the price at near-100% margin
  (runs on free local Ollama, or pennies/post on Claude Haiku).

### Pricing

| Tier | Price/mo | What's delivered |
|------|----------|------------------|
| **Starter** | $300 | 3 posts/week, voice-matched, scheduled, first-comment CTA |
| **Growth** | $500 | 5 posts/week + monthly analytics report + a learning loop that tunes to their data |
| **Authority** | $900 | Growth + 1 short video/week (your Remotion pipeline) cross-posted to IG/TT/YT |

5 Growth clients = **$2,500 MRR** at near-zero marginal cost. Start there.

---

## The wedge: free voice-match demo

The thing that closes the sale is showing them it works *in their voice* before they pay.

1. Ask the prospect for ~10–20 of their recent LinkedIn posts (or copy them from their profile).
2. Paste into a text file, posts separated by a line with `---` or blank lines.
3. Run:

   ```bash
   AI_PROVIDER=claude python3 -m linkedin_agent.onboard_client \
       --name "Jane Doe" \
       --niche "fractional CFO for SaaS startups" \
       --posts-file prospects/jane.txt \
       --num 3 --hashtags "#Finance #SaaS"
   ```

4. It clones their voice, generates 3 posts, and saves them to
   `linkedin_agent/data/clients/<slug>/demo_posts.md`. Send those 3 posts: *"I made
   these with an AI trained on your last 20 posts — took 2 minutes. Want this running
   for you every week?"*

No client credentials needed for the demo. It's pure value, zero risk to them.

---

## Onboarding a paid client (going live)

1. Demo done + they said yes → get their Zernio account connected (or their LinkedIn).
2. Re-run onboarding with their live account id:

   ```bash
   AI_PROVIDER=claude python3 -m linkedin_agent.onboard_client \
       --name "Jane Doe" --niche "..." --posts-file prospects/jane.txt \
       --zernio-account-id "<their_account_id>"
   ```

3. The client config is saved as a tenant in `linkedin_agent/data/clients/<slug>/`
   with its own voice profile, schedule log, and (over time) winning-patterns learning
   data — fully isolated from your own verticals.
4. Set their `zernio_account_id` in `linkedin_agent/data/clients/<slug>/config.json`
   (the id Zernio assigns when their LinkedIn is connected under your dashboard).
5. Preview, then schedule one post live:

   ```bash
   # preview only — needs no account id
   python3 -m linkedin_agent.client_runner --client jane-doe --dry-run
   # schedule one post to THEIR account (next 8am ET, or pass --at ISO)
   AI_PROVIDER=claude python3 -m linkedin_agent.client_runner --client jane-doe
   ```

   Safety: `client_runner` refuses to post live unless `zernio_account_id` is set, so a
   client's post can never land on your profile by accident.
6. **Automate the cadence with launchd** (this Mac sleeps; launchd runs on wake — cron
   skips missed jobs). Add `~/Library/LaunchAgents/com.crosswalk.client-jane.plist` firing
   the command above Mon–Fri = 5 posts/week. One LaunchAgent per client.

---

## Outreach (use your proven high-touch playbook, not volume)

Target who you already understand: IMG/health creators, fractional execs, coaches,
solo founders who know they "should post on LinkedIn" but don't.

**DM 1 — the offer-by-demo (best opener):**
> Hey {name} — I trained an AI on your last 20 LinkedIn posts and had it write 3 in your
> voice. Genuinely sound like you. Want me to send them? No pitch, just curious if it's useful.

**DM 2 — the time angle:**
> You clearly know your stuff but post maybe once a month. I run a service that ghostwrites
> 5 posts/week in your exact voice — you approve, it posts. Want a free sample in your voice?

**DM 3 — referral ask (to your warm network):**
> Quick one — do you know any founders/experts who want to post on LinkedIn but never find
> time? I just opened 5 spots for a done-for-you AI ghostwriting service. Happy to pay a
> referral fee.

---

## Validation gate (before building SaaS)

Do **not** build multi-tenant self-serve software until:
- [ ] 5 paying clients onboarded via this manual flow
- [ ] They renew month 2 (proves retention, not just novelty)
- [ ] You've felt the real support load per client

Hit all three → *then* a self-serve product is worth the engineering. Until then, every
hour goes to selling and delivering, not platform code.
