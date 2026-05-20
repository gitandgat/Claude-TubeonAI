---
created: 2026-03-31T17:47:56Z
title: Set up SendPilot comment-to-DM automations for Fear Audit posts
area: tooling
files: []
---

## Problem

All 17 Fear Audit posts (Wave 2: Mar 24–Apr 9, Wave 3: Apr 14–May 2) are scheduled on Zernio with the CTA "Comment FEAR below and I will DM you the link." The actual comment-to-DM automation must be configured **manually in the SendPilot UI** for each LinkedIn post — there is no API endpoint to create these automations programmatically.

## Solution

As each post goes live on LinkedIn, go to SendPilot dashboard and create a comment automation:
- Trigger word: `FEAR`
- Action: Send DM with Fear Audit link: https://fear-audit.vercel.app/
- DM template: something like "Hey [first name], here's your Fear Audit link: https://fear-audit.vercel.app/ — takes about 5 minutes and shows you exactly which fear is keeping you stuck."
- Do this for all 17 post URLs as they go live

**Stretch goal**: Wire the `message.received` webhook from SendPilot to a Vercel serverless function that tags the lead in Encharge and triggers the Fear Audit nurture sequence automatically (Encharge sequence IDs: 436027–436031).
