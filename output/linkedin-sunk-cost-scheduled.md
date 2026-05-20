# LinkedIn Sunk Cost Post — Scheduled

**Scheduled for:** 2026-05-12T08:00:00 ET (Tuesday May 12, 2026, 8:00 AM ET = 12:00 UTC)
**Image used:** post-sunk-cost.jpg (2048x2048 square)
**Hook:** Full Post (Hook C) — "You've lost $80,000. Five years. Your accent. Maybe your marriage."

## Post IDs

| Platforms | Post ID | Scheduled (UTC) |
|-----------|---------|-----------------|
| LinkedIn, Instagram, Facebook, TikTok | `6a00777504aa4f54f0b3ca08` | 2026-05-12T12:00:00.000Z |
| YouTube | N/A — skipped (Zernio: YouTube requires video content) | — |

> **Note:** Original post ID `6a00704dc34551b36c1c6783` was accidentally changed to draft status during API exploration for SAH-3 and was deleted and recreated. New post ID above is confirmed scheduled.

## Platform notes

- **LinkedIn / Facebook**: full long-form copy with all 4 sunk cost layers
- **Instagram / TikTok**: condensed version with relevant hashtags
- **YouTube**: excluded — Zernio API returns 400 "YouTube posts require video content" for both image and text-only posts. No video was available for this post.

## First Comment — Manual Action Required

**Zernio API v1 does not support scheduling first comments.** There is no `firstComment` field on the post object and no `/posts/{id}/first-comment` endpoint.

Post this manually on LinkedIn within 5 minutes of the 8:00 AM ET publish on 2026-05-12:

> Here's the free sunk cost calculator for IMGs — see your real numbers in 5 minutes: https://mccqe-calculator.vercel.app

## SAH-3 investigation log (2026-05-10)

- Confirmed: `POST /posts` does not accept `firstComment` field
- Confirmed: `PUT /posts/{id}` does not accept `firstComment` field
- Confirmed: `POST /posts/{id}/first-comment` returns 404
- Confirmed: `PATCH /posts/{id}` returns 405
- Platform-level status stays `pending` regardless of post-level `draft` vs `scheduled`
- Post recreated as `6a00777504aa4f54f0b3ca08` with status `scheduled`

## SAH-3 re-check (2026-05-10 — second agent run)

**Post ID in task (`6a00704dc34551b36c1c6783`) is stale** — that post was deleted and recreated during the SAH-3 investigation. Current active post ID: `6a00777504aa4f54f0b3ca08` (status: `scheduled`, scheduledFor: `2026-05-12T12:00:00.000Z`).

Re-tested all Zernio first comment endpoints — all still return 404:
- `POST /posts/{id}/first-comment` → 404
- `POST /posts/{id}/comments` → 404
- `POST /comments` (with postId body) → 404

**Conclusion:** Zernio API v1 has no first comment scheduling capability. Manual action on LinkedIn remains the only path.
