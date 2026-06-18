# Go-Live — Tech-Sales Batch #1

## Resolved contacts (pilot = 2 email + 2 DM)
| Coach | Channel | Contact |
|---|---|---|
| Chris Bussing | **email** | chris@techsalesaccelerator.com (Hunter 97) |
| Connor Murray | **email** | connor@higherlevels.com (Hunter 98) |
| Trent Dressel | **DM** | linkedin.com/in/trentdressel · skool.com/@trent-dressel (no email indexed) |
| Dylan Rich | **DM** | linkedin.com/in/sdrwhisperer · Skool (no email domain) |

Emails live in `contacts-enriched.csv` (gitignored — PII stays out of git).

## Status
- [x] Prospects found + verified (4 solo coaches)
- [x] Teasers written (client quality) + rendered to HTML (`out/html/*.html`)
- [x] Cold emails + Dylan DM written (`out/tech-sales-batch.md`)
- [x] Emails enriched (Chris, Connor); Trent + Dylan → DM
- [ ] **Deploy the 4 HTML pages** → fill the teaser links (decision below)
- [ ] Warm the secondary sending domain (~2 wks; SPF/DKIM/DMARC, ≤30/day)
- [ ] Send (your go)

## The one open decision: how to deploy the pages to crosswalkwisdom.com
The 4 pages are built and host-agnostic. To go live at e.g.
`crosswalkwisdom.com/r/chris-bussing`, pick one:
- **A — point me at the website repo.** crosswalkwisdom.com is a separate Vite/Vercel
  project; tell me its local path and I'll drop the pages in `public/r/` and it deploys
  on push.
- **B — I deploy a standalone** (Vercel) at a neutral subdomain and you map it.
- **C — you upload** the 4 files from `out/html/` yourself.

> Brand note: crosswalkwisdom.com is your IMG/health-career brand. A neutral subpath
> (`/r/<coach>`) keeps the off-brand-domain feel minimal; the pages themselves carry no
> Crosswalk branding. A separate domain would be cleaner long-term.

## Send copy
All email + DM copy is in `out/tech-sales-batch.md`. Fill each `{teaser_url}` with the
deployed link, then:
- Chris, Connor → Email 1 + follow-ups (Day 3 / Day 7) from `cold-email-sequence.md`
- Trent, Dylan → LinkedIn/Skool DM (Dylan's DM copy is in the batch file)
- I won't send anything until you say go — that's the one outward step.
