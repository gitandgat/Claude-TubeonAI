---
created: 2026-03-30T00:00:00Z
title: Set up Burnout Quiz funnel and Encharge flow
area: general
files:
  - bolt-new-quiz-prompt.md
  - create_quiz_emails.py
  - encharge_emails.md
  - quiz_email_ids.json
---

## Problem

The Burnout Crosswalk Assessment quiz and its email funnel are built but not yet live.
All 5 "Courage to Choose" emails are in Encharge (IDs 436357–436361) but no Flow exists
to trigger them. The quiz itself hasn't been built on bolt.new yet.

## Solution

**Step 1 — Encharge Flow (10 min, manual in Encharge UI)**
- Flows → New Flow → Trigger: Tag Added = `quiz-completed`
- Email 436357 immediately → 436358 Day 2 → 436359 Day 5 → 436360 Day 8 → 436361 Day 12
- Activate the flow

**Step 2 — Build quiz on bolt.new (~30 min)**
- Paste full prompt from `bolt-new-quiz-prompt.md` into bolt.new
- Test by submitting a real email → verify person appears in Encharge with `quiz-completed` tag
- Confirm Email 1 arrives: "You crossed a line most people don't."

**Step 3 — Optional: 4 stage-specific nurture flows**
- Triggered by: `quiz-stage-start`, `quiz-stage-stop`, `quiz-stage-elder`, `quiz-stage-human`
- 5 emails each — content already written in `encharge_emails.md`
- Timing: Immediate → Day 2 → Day 4 → Day 7 → Day 10
