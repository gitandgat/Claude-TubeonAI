---
created: 2026-03-31T17:47:56Z
title: Retry scheduling Mar 26 Fear Audit LinkedIn post
area: tooling
files:
  - reschedule-with-overlays.py
  - crosswalk-remotion/out/overlays/02-what-will-people-think.mp4
---

## Problem

Post #2 (Wave 2, Mar 26) failed to schedule via Zernio because LinkedIn's daily post limit (5/day) was hit during the `reschedule-with-overlays.py` run. The overlay video `02-what-will-people-think.mp4` was never successfully posted. 16 of 17 Fear Audit posts went through; this one remains unscheduled.

## Solution

Run a one-off Zernio API call to schedule just this post:
- Upload `crosswalk-remotion/out/overlays/02-what-will-people-think.mp4` via `POST /media`
- Create post with content from Wave 2 post #2 ("What will people think?") + DM_CTA
- Schedule for `2026-03-26T09:00:00.000Z` (or next available slot if date already passed)
- Platforms: LinkedIn, Instagram, Facebook (same PLATFORMS config as reschedule-with-overlays.py)
