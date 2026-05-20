---
created: 2026-03-31T17:47:04.522Z
title: Build re-engagement flow in Encharge for inactive subscribers
area: general
files: []
---

## Problem

3 re-engagement emails were created via API (IDs 438003, 438004, 438005) but the Encharge automation flow hasn't been built yet. Subscribers inactive for 6+ months won't receive the sequence until the flow is live.

## Solution

Build the flow manually in Encharge UI:
- Trigger: subscriber has not opened an email in 180+ days (or use a segment filter for last activity)
- Step 1: Send email 438003 ("Still there, {{firstName}}?") — Day 0
- Step 2: Wait 5 days → Send email 438004 ("Something free that might help") — Day 5
- Step 3: Wait 5 days → Send email 438005 ("Should I keep sending you emails?") — Day 10
- After email 3: if no click → remove from active list / move to unsubscribed segment

Also verify all 3 emails look correct in preview (logo, social buttons, CAN-SPAM footer) before activating.
