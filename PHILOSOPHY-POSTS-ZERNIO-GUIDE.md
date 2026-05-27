# Philosophy Posts → Zernio Scheduling Guide

## Overview

5 philosophy-driven LinkedIn posts created to drive traffic to the philosophy page and Fear Audit. Each post is ready-to-schedule with accompanying 1080×1080 PNG visual.

**Timeline:** 2 weeks (May 27 – June 10, 2026)
**Cadence:** One post every 3-4 days
**Time:** 8:00am ET daily (optimal for breakfast scroll engagement)
**Platforms:** LinkedIn, Instagram, Facebook, TikTok (YouTube as video-only, handled separately)

---

## Post Schedule

| Date | Post | Focus | CTA |
|------|------|-------|-----|
| **May 27 (Day 1)** | Kintsugi Hook | Broken identity reframe | Philosophy page + Fear Audit |
| **May 30 (Day 4)** | Ikigai Hook | Missing purpose pain point | Philosophy page + Fear Audit |
| **June 3 (Day 8)** | Shoshin Hook | Expertise trap / beginner's mind | Philosophy page + IMG Pivot Challenge |
| **June 6 (Day 11)** | Ma Hook | The gap / emptiness reframe | Philosophy page + Fear Audit |
| **June 10 (Day 15)** | Philosophy Overview | East meets West authority | Philosophy page + guide download |

---

## Files Ready to Use

### Visual Assets (1080×1080 PNG)
```
linkedin-post-01-kintsugi.png      (142 KB)
linkedin-post-02-ikigai.png        (161 KB)
linkedin-post-03-shoshin.png       (152 KB)
linkedin-post-04-ma.png            (130 KB)
linkedin-post-05-philosophy.png    (132 KB)
```

### Post Copy (Full Text)
See `LINKEDIN-POSTS-PHILOSOPHY-PAGE.md` for complete post bodies and first-comment CTAs.

---

## Scheduling Instructions

### Option 1: Automated (Python Script)

**Prerequisites:**
```bash
export ZERNIO_API_KEY="your-api-key-here"
```

**Run:**
```bash
python3 schedule-philosophy-posts.py
```

This will:
- Upload all 5 PNG images
- Schedule posts to all 4 platforms (LI/IG/FB/TT)
- Add first comments with resource links
- Space them across the 2-week window
- Save `philosophy-posts-schedule.json` with confirmation IDs

### Option 2: Manual Scheduling (Zernio UI)

For each post, follow these steps:

1. **Go to:** Zernio dashboard → New Post
2. **Title:** Use the post title from the schedule above
3. **Content:** Paste the full body text from `LINKEDIN-POSTS-PHILOSOPHY-PAGE.md`
4. **Media:** Upload the corresponding PNG file (1080×1080)
5. **Platforms:** Select all 4:
   - LinkedIn
   - Instagram
   - Facebook
   - TikTok
6. **Schedule:** Set date + time for 8:00am ET (13:00 UTC)
7. **First Comment:** After publish, add the first comment with the CTA link
8. **Publish**

---

## Post Content Quick Reference

### Post 1: Kintsugi (May 27, 8am ET)
- **Visual:** linkedin-post-01-kintsugi.png
- **Theme:** Broken pottery repaired with gold → brokenness is beautiful
- **Audience:** IMGs feeling broken/failed
- **First Comment:**
  ```
  Read the full Crosswalk Wisdom philosophy + Japanese wisdom integration here:
  → www.crosswalkwisdom.com/philosophy
  
  Take the Fear Audit: www.crosswalkwisdom.com/fear-audit
  ```

### Post 2: Ikigai (May 30, 8am ET)
- **Visual:** linkedin-post-02-ikigai.png
- **Theme:** You have credentials but no soul-alignment → purpose over prestige
- **Audience:** Credentialed professionals feeling hollow
- **First Comment:**
  ```
  Read the full philosophy + five Japanese concepts:
  → www.crosswalkwisdom.com/philosophy
  
  Then take the Fear Audit to see which fears are actually holding you back:
  → www.crosswalkwisdom.com/fear-audit
  ```

### Post 3: Shoshin (June 3, 8am ET)
- **Visual:** linkedin-post-03-shoshin.png
- **Theme:** You know too much → beginner's mind is the superpower
- **Audience:** Experts stuck by their own expertise
- **First Comment:**
  ```
  Full Crosswalk Wisdom Philosophy (with Shoshin + 4 other Japanese concepts):
  → www.crosswalkwisdom.com/philosophy
  
  Free IMG Pivot Challenge (7 days):
  → www.crosswalkwisdom.com/img-pivot-challenge
  ```

### Post 4: Ma (June 6, 8am ET)
- **Visual:** linkedin-post-04-ma.png
- **Theme:** The gap is not void—it's potential → emptiness = transformation
- **Audience:** Those in transition, between identities
- **First Comment:**
  ```
  Full Crosswalk Wisdom Philosophy:
  → www.crosswalkwisdom.com/philosophy
  
  Take the Fear Audit (reveals which of your 5 fears is strongest):
  → www.crosswalkwisdom.com/fear-audit
  ```

### Post 5: Philosophy Overview (June 10, 8am ET)
- **Visual:** linkedin-post-05-philosophy.png
- **Theme:** Eastern philosophy answers what Western coaching misses
- **Audience:** Professionals hitting rock bottom, seeking framework
- **First Comment:**
  ```
  Full Crosswalk Wisdom Philosophy (East meets West):
  → www.crosswalkwisdom.com/philosophy
  
  Download the free philosophy guide:
  → www.crosswalkwisdom.com/download-philosophy-guide
  
  Subscribe to essays on identity, sunk cost, and crossing:
  → www.crosswalkwisdom.com/subscribe
  ```

---

## Expected Outcomes

**Per post:**
- 30–50 profile visits
- 20–30 philosophy page visits
- 5–10 Fear Audit starts
- 2–3 challenge signups

**Total (5 posts):**
- 150–250 profile visits
- 100–150 philosophy page visits
- 25–50 Fear Audit conversions
- 10–15 challenge signups

**Cumulative impact:** Drive 100–150 visitors to philosophy page, seed 25–50 Fear Audit prospects for nurture, generate 10–15 IMG Pivot Challenge leads.

---

## Important Notes

### Zernio Best Practices (per project memory)
1. **Always include first comment** with philosophy page link (not in post body)
2. **Use all 5 platforms** for maximum reach
3. **Never reuse CDN URLs** across campaigns
4. **YouTube:** Needs title field; these are images so typically share as posts, not videos
5. **Instagram:** Requires media upload (PNG provided)
6. **UTC conversion:** 8am ET = 13:00 UTC (EDT)

### Post Spacing
- Day 1 → Day 4 = 3 days
- Day 4 → Day 8 = 4 days
- Day 8 → Day 11 = 3 days
- Day 11 → Day 15 = 4 days

This staggered approach lets each post build momentum (LinkedIn algorithm favors posts 3–5 days old) before the next one lands.

---

## Tracking & Follow-Up

After scheduling, monitor:
- **Philosophy page visits** (Grain analytics)
- **Fear Audit starts** (Encharge tag: `fear-audit-started`)
- **IMG Pivot Challenge signups** (Encharge tag: `challenge-joined`)
- **LinkedIn post engagement** (profile visits, comment quality)

Document in `philosophy-posts-schedule.json` (auto-generated by script).

---

## Rollback / Changes

If a post needs editing before publish:
1. Delete the draft in Zernio
2. Update copy in `LINKEDIN-POSTS-PHILOSOPHY-PAGE.md`
3. Re-run the scheduling script or manually re-publish

If a post performs exceptionally well (>100 visits from one post):
- Boost that post's budget in Zernio if LinkedIn is the driver
- Analyze the hook for future posts
- Consider writing a follow-up post expanding on that concept

---

Generated: May 27, 2026
Status: Ready to schedule
