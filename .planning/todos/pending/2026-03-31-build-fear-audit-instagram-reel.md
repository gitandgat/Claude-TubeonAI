---
created: 2026-03-31T17:47:30Z
title: Build Fear Audit Instagram Reel in Remotion
area: general
files:
  - crosswalk-remotion/src/compositions/TikTokReel.tsx
  - crosswalk-remotion/src/Root.tsx
---

## Problem

The 5-scene Fear Audit Instagram Reel script was approved in conversation but never built — session got pulled into LinkedIn banner and headshot work instead.

## Solution

Build a new TikTokReel composition using the approved script:

- Composition ID: `TikTokReel-fear-audit`
- Format: 1080×1920, ~60s, 30fps
- Scene breakdown:
  1. Hook (0–8s): "Most physicians don't leave medicine because they hate it." — dark bg, white text, particle drift, silence
  2. Fear Named (8–20s): "They stay because they're terrified of who they'll be without it." — stethoscope SVG fading to question mark, ambient music begins
  3. Pivot (20–35s): Crossing guard story — cinematic crosswalk background from assets, stop sign SVG, spring entrance
  4. Invitation (35–48s): "If you're a physician quietly asking yourself..." — clean minimal slide, warm tone shift
  5. CTA (48–60s): "The Fear Audit. 3 minutes. fear-audit.vercel.app" — bold text, particle burst, URL hold 5s

- Register in Root.tsx
- Render to `out/fear-audit-reel.mp4`
- Use existing cinematic crosswalk backgrounds from `public/assets/`
