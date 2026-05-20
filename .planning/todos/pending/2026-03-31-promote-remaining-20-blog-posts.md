---
created: 2026-03-31T02:15:00Z
title: Promote remaining 20 blog posts on social media
area: general
files:
  - drafts/blog-social/beyond-the-white-coat/
  - src/data/posts.ts
---

## Problem

"Beyond the White Coat" is done (LinkedIn + Facebook text posts + Instagram/Facebook 7-slide carousel all scheduled for April 6 at 3pm ET). 20 blog posts remain unpromoted.

Each post needs:
1. Run /crosswalk-blog-social <slug> to generate LinkedIn, Instagram, TikTok, Facebook copy
2. Generate 7-slide carousel using the Python/Pillow pattern from /tmp/make_carousel_beyond_white_coat.py
3. Schedule on Zernio: LinkedIn + Facebook (text) + Instagram + Facebook (carousel)

## Solution

Follow the same workflow used for "beyond-the-white-coat":
- Image for each post is in /Users/toto/crosswalk-wisdom-new/public/<slug>.jpg
- 6 original posts use Unsplash URLs (not local) — may need Freepik images for those
- Carousel script template: /tmp/make_carousel_beyond_white_coat.py
- Scheduling script template: /tmp/schedule_carousel_beyond_white_coat.py
- Space posts 1 per week (21-week plan), Mondays at 3pm ET to avoid clashing with April calendar content (5am/9am/11am/1pm slots taken)

## Remaining slugs (in 21-week order)
1. the-cost-of-staying
2. financial-fear-vs-reality
3. neuroscience-of-courage
4. training-for-the-marginal-decade
5. ai-career-co-pilot
6. 90-day-crosswalk
7. fear-of-judgment
8. ai-everyday-life-hacks
9. longevity-mindset
10. specialist-to-generalist
11. managing-administrative-burden
12. safety-net-illusion
13. decision-making-under-uncertainty
14. doctors-guide-to-ai
15. burnout-is-not-a-wellness-problem (original)
16. the-identity-cage (original)
17. sunk-cost-medicine (original)
18. permission-to-pivot (original)
19. the-crossing-guard-philosophy (original)
20. courage-is-a-skill (original)
