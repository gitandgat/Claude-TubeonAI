# MoveAssess Nurture Flow — Encharge UI Build Instructions

The 7 emails exist and are verified (created 2026-07-03 via
`create_moveassess_emails.py`). Flows can't be assembled via API on this
plan — this is the one manual step. ~5 minutes in the Encharge UI.

## Flow structure

**Flows → New Flow → name it `MoveAssess Protocol Nurture`**

| Step | Node | Detail |
|---|---|---|
| Trigger | **Tag added** | `moveassess-lead` |
| 1 | Send email | **467328** MoveAssess 1 — Protocol Delivery |
| 2 | Wait | 1 day |
| 3 | Send email | **467329** MoveAssess 2 — Ward to World Story |
| 4 | Wait | 1 day |
| 5 | Send email | **467330** MoveAssess 3 — Compensation Cascade |
| 6 | Wait | 2 days |
| 7 | Send email | **467331** MoveAssess 4 — What Change Looks Like |
| 8 | Wait | 2 days |
| 9 | Send email | **467332** MoveAssess 5 — Glute Longevity Offer |
| 10 | Wait | 2 days |
| 11 | Send email | **467333** MoveAssess 6 — Objections |
| 12 | Wait | 2 days |
| 13 | Send email | **467334** MoveAssess 7 — Retest Close |

Timing lands E1 instant, E2 d1, E3 d2, E4 d4, E5 d6, E6 d8, E7 d10.

## Recommended guard

Add an **exit condition / filter** before steps 9–13: skip if the person has
tag `glute-longevity-customer` (don't sell to people who already bought).

## Testing after activation

Existing tagged contacts do NOT enter a newly activated flow — the trigger
fires on the tag-added *event*. To test end-to-end with a fresh contact:

```bash
# edit TEST_EMAIL in verify_moveassess_capture.py to a new plus-alias first,
# e.g. totomakus+ma-flow-test@gmail.com, then:
python3 verify_moveassess_capture.py
```

E1 should land in the inbox within a minute or two (plus-alias = fresh
contact, so Encharge's already-received suppression doesn't apply).

## Assets the emails depend on (all live, verified 2026-07-03)

- PDF library: https://physical-assessment-app.vercel.app/protocols/protocol-library.pdf
- Per-case PDFs: `/protocols/<case-id>.pdf` (8 featured cases)
- App deep link: https://physical-assessment-app.vercel.app/?case=<case-id>
- Program: https://glute.crosswalkwisdom.com
- Personalization fields: `moveassessCase`, `moveassessCaseName` (set by the
  capture endpoint; liquid defaults cover missing values)

## Pricing (confirmed 2026-07-03)

$97 founding cohort / $147 list. E5 (467332) and E7 (467334) carry the
founding close — updated + verified via `update_moveassess_pricing.py`.
Before activating the flow, set the $97 price on the
glute.crosswalkwisdom.com checkout so the emails and the page agree.
