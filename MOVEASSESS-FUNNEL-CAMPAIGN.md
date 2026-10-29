# MoveAssess → Glute Longevity: Funnel & Campaign Plan
**Date:** 2026-07-02
**Frameworks:** Brunson (value ladder, hook-story-offer) · Hormozi (offer math, lead magnet design) · Welsh (organic LinkedIn distribution)

---

## Strategy in One Line

MoveAssess is the free diagnostic that makes Glute Longevity feel personally *prescribed* rather than sold. The 67 assessment cases are also a 67-post content engine — each post deep-links to its own case via `?case=<id>`.

---

## Funnel Map

```
Social content (TT / LI / IG / YT / FB — case-of-the-day posts)
  │
  ▼
MoveAssess deep link (?case= matches the post's topic)     ← FREE, no login
  │
  ▼
In-app CTA: "Email me my corrective protocol" → email capture   ← ⚠ DOES NOT EXIST YET
  │
  ▼
Encharge: 7-email Movement→Longevity sequence (extends #464212-14)
  │
  ▼
Glute Longevity core offer
  │
  ▼
Backend: 1:1 physician-lens coaching / nutrition app
```

**The hole in the funnel:** MoveAssess currently has zero capture mechanism. Traffic in → traffic out. The protocol-gate email capture is the single P1 build item — everything else is content and email work on existing infrastructure.

---

## Value Ladder (Brunson)

| Rung | Offer | Price | Job |
|---|---|---|---|
| 1 | MoveAssess assessment (all 67 cases) | Free, no login | Bait + authority. "Find your pattern." |
| 2 | Your Corrective Protocol PDF (per-case) | Free + email | Capture. The 8 featured cases already have full 3-phase protocols in app data — PDFs are nearly free to generate via the existing `lead-magnets/` pipeline. |
| 3 | 14-Day Glute Reboot (tripwire) | $27–47 | Buyer creation. Self-serve mini-program; mirrors the Courage to Choose $27 Gumroad pattern. |
| 4 | **Glute Longevity program** (core) | **$97 founding / $147 list** (confirmed 2026-07-03) | The money. Founding price ends when first cohort fills; discount is exchanged for retest data + testimonial. |
| 5 | 1:1 coaching, physician lens | $300+/mo | Backend for the 5–10% who want hands-on. |

Each rung follows **hook → story → offer**: the assessment result is the hook, the former-physician "I watched people lose independence one compensation at a time" narrative is the story, the next rung is the offer.

---

## Offer Design (Hormozi)

**Value equation:** (Dream outcome × Perceived likelihood) ÷ (Time delay × Effort)

| Lever | Current state | Move |
|---|---|---|
| Dream outcome | "stronger glutes" (weak) | **"Move at 70 like you did at 40"** — longevity, independence, no pain |
| Perceived likelihood | generic program | Assessment-personalized: "built for *your* pattern (gluteal inhibition, HL-03)" + physician-designed |
| Time delay | unclear | Promise the first measurable win: "retest your movement in 14 days" |
| Effort | unclear | "15 min/day, no gym" |

**Grand Slam stack for the core offer:**
1. The 90-day program (core)
2. Personal movement assessment result carried into the program (from MoveAssess)
3. Corrective protocol library (the 8 clinical 3-phase protocols)
4. Nutrition companion app access (nutrition.crosswalkwisdom.com)
5. **Guarantee (risk reversal):** "Retest your assessment at day 30. If your pattern hasn't measurably improved, full refund." — The assessment itself becomes the guarantee mechanism. This is the strongest Hormozi move available: the free tool *proves* the paid product worked.
6. Honest scarcity: founding-cohort pricing with a real deadline (not fake countdown).

**Naming:** "The 90-Day Glute Longevity Blueprint" (magnet: "Your Movement Pattern Fix — Free Corrective Protocol").

**Lead magnet logic (Hormozi's rule):** solve the *narrow* problem completely — "what's wrong with my movement" — which reveals the *next* problem — "who will coach me through fixing it." Give away the diagnosis, sell the implementation.

---

## Distribution (Welsh)

**Profile = landing page:**
- LinkedIn headline rewritten to outcome ("Former physician. I help people over 40 move like they're 25 again — start with a free movement assessment")
- Featured section: MoveAssess link + intro video (youtu.be/fHFZkr3690A)

**Content matrix — 4 pillars × 3 formats:**

| Pillar | Text post | Brand card / carousel | Reel |
|---|---|---|---|
| Assessment insight ("your knees cave because…") | ✓ | ✓ (Pivot Map card) | ✓ |
| Longevity science | ✓ | ✓ | — |
| Former-physician story | ✓ | — | ✓ (avatar hook) |
| Proof / client result | ✓ | ✓ | — |

**The 67-case content engine:** one case per day = 2+ months of daily content with zero new research. Post explains the compensation in plain language → deep link `?case=<id>` in **first comment** (house rule). Feeds the existing 5/day Zernio verticals engine as the glute/longevity vertical — no new pipeline needed.

**Cadence (Welsh system):** post daily, 15-min engagement window before/after posting, reply to every comment first hour, weekly email newsletter repurposed from the week's best post.

**Sample hooks** (broadened + "here's what I'd do" reframe, per house style — final posts go through A/B/C/D hook selection + /stop-slop ≥35/50):
- "Your knees don't cave because your knees are weak."
- "I'm a former physician. Here's the 60-second self-test I'd give everyone over 40."
- "Most 'tight hamstrings' aren't tight. They're doing a job that was never theirs."

---

## Email Sequence (7 emails — Encharge)

Extends the live Glute Longevity nurture (#464212-14). **Audience guard:** this runs on the Glute Longevity segment ONLY — never broadcast to the CW healthcare-pivot list.

| # | Timing | Job |
|---|---|---|
| E1 | Instant | Deliver the protocol PDF. One CTA: start Phase 1 today. |
| E2 | Day 1 | Story — ward to world, why movement is the longevity lever. |
| E3 | Day 2 | Education — the compensation cascade (their case as the example). |
| E4 | Day 4 | Proof — case study with numbers. |
| E5 | Day 6 | Offer intro — full value stack + guarantee. |
| E6 | Day 8 | Objections/FAQ — time, age, "I've tried programs before." |
| E7 | Day 10 | Close — founding-cohort deadline + retest guarantee restated. |

All emails: logo header, social buttons, CAN-SPAM footer. Build via `/crosswalk-encharge-email` skill only.

---

## Metrics & Targets

| Stage | Target | Benchmark basis |
|---|---|---|
| Post → assessment click | 1–3% of reach | interactive tools outperform static CTAs |
| Assessment → email | 10–20% | quizzes/assessments = highest-engagement magnet class |
| Email → tripwire | 5–10% | warm, personalized sequence |
| Email → core offer (30d) | 3–5% | standard warm-list close rate |

**Volume reality check:** current list is small and shares ≈ 0 — distribution is the ceiling, not conversion. TikTok is the volume lever (17.9K-view precedent). At 10K monthly assessment visitors × 15% capture × 4% close, this is a real funnel; at 300 visitors it's a proof-of-concept. The campaign's first job is top-of-funnel volume, measured via platform-filtered Zernio analytics + UTM params + Encharge tags.

---

## 30-Day Campaign Calendar

**Week 0 — Build (blocks launch):**
- [ ] P1: Email capture in MoveAssess ("Email me my corrective protocol" gate on protocol section)
- [ ] P1: 8 protocol PDFs via existing `lead-magnets/` pipeline
- [ ] P1: E1–E7 in Encharge + tag wiring
- [ ] P2: LinkedIn profile rewrite + featured section
- [ ] P2: UTM convention (`?case=X&utm_source=tiktok&utm_campaign=case-of-day`)

**Week 1 — Launch the narrative:** "Movement Debt" framing. 5 posts introducing the assessment challenge ("take the 60-second test, comment your pattern"). Avatar-hook reel for the physician story.

**Weeks 2–3 — Case-of-the-day engine:** daily case posts across platforms via the verticals engine. UGC ask: "post your result, tag us." Newsletter each Friday from the best post.

**Week 4 — Open/close the offer:** founding-cohort framing, value stack, retest guarantee, real deadline. E5–E7 fire. Final 48h: deadline posts.

---

## Build List (implementation owner: Claude)

| Priority | Item | Effort |
|---|---|---|
| P1 | Protocol email-gate in MoveAssess + Encharge API hookup | ~half day |
| P1 | 8 branded protocol PDFs (lead-magnets pipeline) | ~2 hrs |
| P1 | 7-email sequence via /crosswalk-encharge-email | ~half day |
| P2 | Case-of-the-day post generator feeding Zernio verticals | ~half day |
| P3 | Tripwire product (14-Day Glute Reboot on Gumroad) | later |

**Pricing (confirmed 2026-07-03):** $97 founding cohort / $147 list. E5 + E7 updated with the founding close. Remaining user action: set the $97 price on the glute.crosswalkwisdom.com checkout and decide the cohort cap to enforce.
