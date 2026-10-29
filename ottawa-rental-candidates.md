# Ottawa Rental Candidates — auto-monitor log

Appended weekly by `ottawa_rental_monitor.sh` (launchd: com.crosswalk.ottawa-rental-monitor).
Candidates below are **search hits to verify yourself** via the source URL — not confirmed or applied to.
Promising ones → copy into [ottawa-rental-tracker.md](ottawa-rental-tracker.md) and apply using [ottawa-rental-application-packet.md](ottawa-rental-application-packet.md).

## Sweep 2026-06-16 19:06 +07
## Search Results

Based on web searches, I found limited verified individual listings currently available. Here are candidates matching your criteria:

| Address/Building | Area | Rent | Type | Availability | Nearest LRT | Likely landlord | Source URL |
|---|---|---|---|---|---|---|---|
| 425 Elgin Street | Centretown | $1,349–$1,599 CAD | Studio/1-bed | June 2026 promo active | Parliament / uOttawa | Management company (CLV Group) | https://www.rentfaster.ca/properties/425-elgin-street-ottawa-420029 |
| 224 Lyon Street N, Unit 1008 | Centretown | $1,700 CAD | 1-bed condo | July 1, 2026 | Lyon | Unknown | https://www.zolo.ca/ottawa-real-estate/224-lyon-street-north/1008 |
| 341 MacLaren Street (Executive Apartments) | Centretown | $1,499 CAD | Studio | June 2026 | Parliament | Management company | General Kijiji listing (no direct URL provided in results) |

---

## Limitations

**Search results provided general marketplace pages (Kijiji, Facebook Marketplace, RentFaster) rather than individual unit listings.** To access current available units under $1,500 with specific move-in dates around October 1, 2026, you'll need to:

1. **Kijiji** – Browse directly by area: https://www.kijiji.ca/b-apartments-condos/ottawa/sandy-hill/
2. **Facebook Marketplace** – Filter by neighborhood and price: https://www.facebook.com/marketplace/ottawa/apartments-for-rent/
3. **RentFaster** – Search Centretown/Sandy Hill: https://www.rentfaster.ca/

Most current listings appear to show July–August 2026 availability; October 1 moves may require direct landlord contact.

---

**Search queries used:**
- `Kijiji Ottawa apartment studio 1 bedroom rent $1500 Centretown Sandy Hill 2026`
- `Facebook Marketplace Ottawa apartment Centretown Chinatown under $1500 rent`
- `Ottawa O-Train Line 1 apartment rental Centretown Lyon Parliament uOttawa 2026`
- `"425 Elgin" Ottawa apartment rent 2026`
- `"224 Lyon Street" Ottawa apartment July 2026 rent`
SessionEnd hook [_R="${CLAUDE_PLUGIN_ROOT}"; [ -z "$_R" ] && _R="$HOME/.claude/plugins/marketplaces/thedotmack/plugin"; node "$_R/scripts/bun-runner.js" "$_R/scripts/worker-service.cjs" hook claude-code session-complete] failed: Hook command references ${CLAUDE_PLUGIN_ROOT} but the hook is not associated with a plugin. This variable is only available in hooks defined in a plugin's hooks/hooks.json file, not in settings.json. Command: _R="${CLAUDE_PLUGIN_ROOT}"; [ -z "$_R" ] && _R="$HOME/.claude/plugins/marketplaces/thedotmack/plugin"; node "$_R/scripts/bun-runner.js" "$_R/scripts/worker-service.cjs" hook claude-code session-complete

---
2026-06-16 19:16 +07 — weekly mode; skipping non-Monday run (no token spend).
2026-06-17 08:07 +07 — weekly mode; skipping non-Monday run (no token spend).
2026-06-19 08:07 +07 — weekly mode; skipping non-Monday run (no token spend).

## Sweep 2026-06-22 08:07 +07
## PART A — Ottawa Rental Listings (Web Search)

**Note:** Web search reveals most current listings show July–September 2026 availability. October 2026 move-in dates are not yet widely advertised (likely published July–August). 

| Address/Building | Area | Rent | Type | Availability | Nearest LRT | Likely landlord type | Source URL |
|---|---|---|---|---|---|---|---|
| 363 Besserer St (Deauville Apartments) | Sandy Hill | $1,395 | 1-bed | Jul/Aug 1 2026 | Lees (uOttawa nearby) | Institutional/purpose-built | [Kijiji Sandy Hill](https://www.kijiji.ca/b-apartments-condos/ottawa/1-bedroom-sandy-hill/k0c37l1700185) |
| 474 Wilbrod St (Wilbrod Towers) | Sandy Hill | $1,495 | 1-bed | Jul 1 2026 | Lees | Institutional/purpose-built | [Kijiji Sandy Hill](https://www.kijiji.ca/b-apartments-condos/ottawa/1-bedroom-sandy-hill/k0c37l1700185) |
| Stewart St (Akelius) | Sandy Hill | TBD | Studio | TBD | Lees | Institutional | [Kijiji Sandy Hill](https://www.kijiji.ca/b-apartments-condos/ottawa/sandy-hill/k0c37l1700185) |

**No matching candidates with confirmed October 2026 availability found this sweep.**  
*(October listings typically post July–August; check Kijiji, RentCafe, Rentals.ca mid-July for October move-ins)*

---

## PART B — Building Investments Portal

| Address | Rent (CAD) | Availability date |
|---|---|---|
| 139 Stewart Street - 2 | $1,345 | July 1, 2026 |
| 203 - 486 Albert Street | $1,495 | July 1, 2026 |
| 214 - 467 Slater Street | $1,495 | July 1, 2026 |
| 430 Lyon Street North - 2 | $1,245 | September 1, 2026 ⚠ |
| 486 Albert Street - 205 | $1,345 | September 1, 2026 ⚠ |

**Queries used:**  
- Building Investments API: `https://buildinginvestments.managebuilding.com/Resident/public/rentals`  
- Web Search: `"October 2026" OR "October 1" apartment rental Ottawa Centretown Lyon Parliament uOttawa LRT`  
- Web Search: `Ottawa Sandy Hill apartment rental "October" 2026 1-bedroom studio Kijiji`

---

OCT1_BUILDINGINVESTMENTS: NO

Sources:
- [Building Investments Rentals Portal](https://buildinginvestments.managebuilding.com/Resident/public/rentals)
- [Kijiji Centretown Apartments](https://www.kijiji.ca/b-apartments-condos/ottawa/centretown/k0c37l1700185)
- [Kijiji Sandy Hill 1-Bedroom](https://www.kijiji.ca/b-apartments-condos/ottawa/1-bedroom-sandy-hill/k0c37l1700185)
- [Zumper Centretown](https://www.zumper.com/apartments-for-rent/ottawa-on/centretown)
- [RentCafe Sandy Hill](https://www.rentcafe.com/apartments-for-rent/sandy-hill-ottawa-on/)
SessionEnd hook [_R="${CLAUDE_PLUGIN_ROOT}"; [ -z "$_R" ] && _R="$HOME/.claude/plugins/marketplaces/thedotmack/plugin"; node "$_R/scripts/bun-runner.js" "$_R/scripts/worker-service.cjs" hook claude-code session-complete] failed: Hook command references ${CLAUDE_PLUGIN_ROOT} but the hook is not associated with a plugin. This variable is only available in hooks defined in a plugin's hooks/hooks.json file, not in settings.json. Command: _R="${CLAUDE_PLUGIN_ROOT}"; [ -z "$_R" ] && _R="$HOME/.claude/plugins/marketplaces/thedotmack/plugin"; node "$_R/scripts/bun-runner.js" "$_R/scripts/worker-service.cjs" hook claude-code session-complete

---
2026-06-24 08:07 +07 — weekly mode; skipping non-Monday run (no token spend).
2026-06-26 08:07 +07 — weekly mode; skipping non-Monday run (no token spend).

## Sweep 2026-06-29 08:07 +07
You've hit your limit · resets Jul 1 at 3pm (Asia/Bangkok)
SessionEnd hook [_R="${CLAUDE_PLUGIN_ROOT}"; [ -z "$_R" ] && _R="$HOME/.claude/plugins/marketplaces/thedotmack/plugin"; node "$_R/scripts/bun-runner.js" "$_R/scripts/worker-service.cjs" hook claude-code session-complete] failed: Hook command references ${CLAUDE_PLUGIN_ROOT} but the hook is not associated with a plugin. This variable is only available in hooks defined in a plugin's hooks/hooks.json file, not in settings.json. Command: _R="${CLAUDE_PLUGIN_ROOT}"; [ -z "$_R" ] && _R="$HOME/.claude/plugins/marketplaces/thedotmack/plugin"; node "$_R/scripts/bun-runner.js" "$_R/scripts/worker-service.cjs" hook claude-code session-complete

---
2026-07-01 08:07 +07 — weekly mode; skipping non-Monday run (no token spend).
2026-07-03 08:07 +07 — weekly mode; skipping non-Monday run (no token spend).

## Sweep 2026-07-06 08:07 +07
You've hit your limit · resets Jul 8 at 3pm (Asia/Bangkok)
SessionEnd hook [_R="${CLAUDE_PLUGIN_ROOT}"; [ -z "$_R" ] && _R="$HOME/.claude/plugins/marketplaces/thedotmack/plugin"; node "$_R/scripts/bun-runner.js" "$_R/scripts/worker-service.cjs" hook claude-code session-complete] failed: Hook command references ${CLAUDE_PLUGIN_ROOT} but the hook is not associated with a plugin. This variable is only available in hooks defined in a plugin's hooks/hooks.json file, not in settings.json. Command: _R="${CLAUDE_PLUGIN_ROOT}"; [ -z "$_R" ] && _R="$HOME/.claude/plugins/marketplaces/thedotmack/plugin"; node "$_R/scripts/bun-runner.js" "$_R/scripts/worker-service.cjs" hook claude-code session-complete

---
2026-07-08 08:07 +07 — weekly mode; skipping non-Monday run (no token spend).
2026-07-10 08:07 +07 — weekly mode; skipping non-Monday run (no token spend).

## Sweep 2026-07-13 08:07 +07
You've hit your limit · resets Jul 15 at 3pm (Asia/Bangkok)
SessionEnd hook [_R="${CLAUDE_PLUGIN_ROOT}"; [ -z "$_R" ] && _R="$HOME/.claude/plugins/marketplaces/thedotmack/plugin"; node "$_R/scripts/bun-runner.js" "$_R/scripts/worker-service.cjs" hook claude-code session-complete] failed: Hook command references ${CLAUDE_PLUGIN_ROOT} but the hook is not associated with a plugin. This variable is only available in hooks defined in a plugin's hooks/hooks.json file, not in settings.json. Command: _R="${CLAUDE_PLUGIN_ROOT}"; [ -z "$_R" ] && _R="$HOME/.claude/plugins/marketplaces/thedotmack/plugin"; node "$_R/scripts/bun-runner.js" "$_R/scripts/worker-service.cjs" hook claude-code session-complete

---
2026-07-15 08:07 +07 — weekly mode; skipping non-Monday run (no token spend).
