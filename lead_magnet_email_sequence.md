# Lead Magnet Email Sequence Template
## Alex Hormozi-Inspired 3-Video Automation for Encharge

---

## EMAIL 1: The Hook (Immediate Send)
**Subject:** Your free mini-course is ready (watch video 1 now)
**Send:** Immediately after signup
**Video:** Problem Identification

```
Hi [FIRST_NAME],

Thanks for signing up!

Your first video lesson is below. Watch it now—it'll only take 5 minutes, but it might change everything about how you approach this.

[EMBEDDED VIDEO: Video 1 - The Problem]

This is the #1 mistake I see people make. Sound familiar?

In the next email, I'll show you exactly how to fix it.

See you tomorrow,
[SENDER NAME]

P.S. — Save the worksheet I included in the email below. You'll need it for lesson 2.
```

---

## EMAIL 2: The Pattern (Day 1, 10 AM ET)
**Subject:** Here's exactly what I did differently
**Send:** 24 hours after signup, 10 AM ET
**Video:** Solution Framework

```
Hi [FIRST_NAME],

Yesterday I showed you the problem. Today, I'm showing you the solution.

This is the framework that changed everything for me:

[EMBEDDED VIDEO: Video 2 - The Solution]

Three simple principles:
1. The Identification Phase (how to find it)
2. The Implementation Phase (how to do it)
3. The Integration Phase (how to make it stick)

Most people skip principle #1. That's why they fail.

Use the worksheet from yesterday to apply this to your specific situation. Get it done today.

Tomorrow's email will show you how to scale this.

Talk soon,
[SENDER NAME]

P.S. — Stuck on any part? Reply to this email. We read every response.
```

---

## EMAIL 3: The Proof (Day 2, 10 AM ET)
**Subject:** What happens when you actually implement this
**Send:** 48 hours after signup, 10 AM ET
**Video:** Opportunity/Results

```
Hi [FIRST_NAME],

By now you've seen the problem and learned the solution.

What comes next?

[EMBEDDED VIDEO: Video 3 - The Opportunity]

Here's what you get when you actually do the work:

✓ Clarity on where you're really standing
✓ A repeatable process for solving this forever
✓ The confidence to execute at scale

This changes everything.

But here's the thing—knowing isn't doing.

Most people will watch this, feel motivated, then go back to their old habits.

That's why I created [OFFER NAME]. It's not for everyone. It's only for people ready to actually change.

[CTA BUTTON: Learn More About [OFFER NAME]]

If you're serious about this, click above. We'll walk you through the full implementation together.

If not, no hard feelings. Keep the worksheets—they're yours to keep.

All the best,
[SENDER NAME]

P.S. — For the next 3 days, I'm offering an exclusive bonus to anyone who enrolls: [BONUS DESCRIPTION]. After that, it's gone.
```

---

## EMAIL 4: The Follow-Up (Day 5, 10 AM ET)
**Subject:** 3-day warning: The bonus expires tomorrow
**Send:** 5 days after signup, 10 AM ET
**Video:** None

```
Hi [FIRST_NAME],

Quick reminder: The exclusive bonus I mentioned expires tomorrow at midnight.

If you've completed the mini-course and you're ready to go deeper, now's the time to join.

[CTA BUTTON: Get [OFFER NAME] + Exclusive Bonus]

Only 2 spots left at the current tier.

[SENDER NAME]

P.S. — This bonus took me 6 months to create. It's only available to mini-course completers, and only for the next 24 hours.
```

---

## EMAIL 5: Last Chance (Day 7, 6 PM ET)
**Subject:** Last chance: Bonus expires in 2 hours
**Send:** 7 days after signup, 6 PM ET
**Video:** None

```
Hi [FIRST_NAME],

This is it.

The bonus I created ends in exactly 2 hours. After that, it's gone forever.

If you're ready to implement everything from the mini-course at scale, now's the time.

[CTA BUTTON: Get [OFFER NAME] Before It's Gone]

Talk soon,
[SENDER NAME]
```

---

## Encharge Implementation Notes

### Subscriber Tags Strategy
```
Auto-apply these tags on signup:
- lead-magnet-subscriber
- [COURSE-TOPIC]-interested
- video-lesson-1-sent
- video-lesson-2-sent (auto-apply day 1, 11 PM ET)
- video-lesson-3-sent (auto-apply day 2, 11 PM ET)
- ready-for-offer (auto-apply day 5)

Use tags for:
- Segmenting who gets which follow-up emails
- Tracking completion rates
- A/B testing subject lines by topic
```

### Automations
```
1. Signup Automation → Send Email 1 immediately
2. Wait 24h → Send Email 2 (Video 2)
3. Wait 24h → Send Email 3 (Video 3 + Offer CTA)
4. Wait 72h → Send Email 4 (3-day warning)
5. Wait 48h → Send Email 5 (Last chance)

Alternative Path:
- If [FIRST_NAME] not filled: Send trigger asking for it
- If subscriber bounces: Auto-remove from sequence
- If subscriber clicks CTA: Tag "ready-to-buy" and move to sales sequence
```

### Email Customization Points
Replace these with real content:
- `[FIRST_NAME]` — Encharge variable
- `[SENDER NAME]` — Your name
- `[COURSE-TOPIC]` — The specific lesson topic
- `[OFFER NAME]` — Your paid offer name
- `[BONUS DESCRIPTION]` — What the bonus is
- `[EMBEDDED VIDEO]` — Remotion video URL

### Video Hosting
Each email references a Remotion-generated video. Videos should be:
- MP4 format, 15-30 seconds (for email preview)
- Hosted on your CDN or video platform
- Embedded with fallback image
- Clickable to full-length version on landing page

---

## Metrics to Track

**Email Level:**
- Open rate (target: 35-45%)
- Click rate (target: 8-12%)
- Unsubscribe rate (target: <0.5%)

**Conversion Level:**
- Landing page CTR (target: 25-35%)
- Video completion rate (target: 60-70%)
- Offer conversion rate (measure separately)

**Sequence Level:**
- % completing all 3 videos (target: 40-50%)
- % clicking offer CTA (target: 15-25%)
- Cost per lead (depends on traffic source)
- LTV of this segment vs others

---

## A/B Testing Recommendations

**Test 1: Subject Line Tone**
- Option A: Curiosity gap ("Here's what I didn't tell you")
- Option B: Direct benefit ("Watch video 2 now")

**Test 2: Video Length**
- Option A: 30-second teaser in email
- Option B: Full video embedded

**Test 3: CTA Timing**
- Option A: CTA in Email 3 only
- Option B: CTA in Emails 3, 4, and 5

**Test 4: Bonus Urgency**
- Option A: No expiration, always available
- Option B: Limited time (48 hours)
- Option C: Limited quantity (10 spots)

---

## Integration with Crosswalk Wisdom

This sequence integrates with:
1. **TubeonAI**: Could repurpose course videos to social clips
2. **Remotion**: Generates the 3 core videos
3. **Zernio**: Schedule social media promotion of landing page
4. **Encharge**: This email automation
5. **Landing Page**: Captures emails and triggers this sequence

Full tech stack: Landing page → Encharge subscription → Email sequence → Video delivery → Offer conversion
