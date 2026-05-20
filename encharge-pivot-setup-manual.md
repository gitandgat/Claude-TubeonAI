# Encharge Manual Setup for 7-Day IMG Pivot Challenge

Since Encharge doesn't expose sequence creation via API, we'll set up the sequence manually (takes 5-10 minutes) and use the API only for contact/tag management.

## Step 1: Create Sequence in Encharge UI (5 minutes)

1. Log in to https://app.encharge.io
2. Go to **Sequences** → **Create New Sequence**
3. Name: `7-Day IMG Pivot Challenge`
4. Description: `Free 7-day email course for unmatched IMGs in Canada`

## Step 2: Add 7 Emails to Sequence

For each email below, click **Add Email** and fill in:
- **Subject**
- **Body** (copy from 7day-pivot-challenge.md)
- **Send Delay** (set timing as specified)

### Email 1: Day 1 (Immediate)

**Subject:** Day 1: Your IMG Pivot Challenge Starts Now (The 1 Question That Changes Everything)

**Send Delay:** Immediate (when tagged)

**Body:** [Copy from 7day-pivot-challenge.md — Day 0 email]

---

### Email 2: Day 2 (24 hours)

**Subject:** Day 2: The Question Isn't "How Do I Stay?" (It's "Why Do I Feel Stuck?")

**Send Delay:** 24 hours after previous email

**Body:** [Copy from 7day-pivot-challenge.md — Day 1 email]

---

### Email 3: Day 3 (48 hours)

**Subject:** Day 3: The 4 Paths Nobody Tells Unmatched IMGs Exist

**Send Delay:** 24 hours after previous email

**Body:** [Copy from 7day-pivot-challenge.md — Day 2 email]

---

### Email 4: Day 4 (72 hours)

**Subject:** Day 4: Why You Haven't Switched Yet (And It's Not What You Think)

**Send Delay:** 24 hours after previous email

**Body:** [Copy from 7day-pivot-challenge.md — Day 3 email]

---

### Email 5: Day 5 (96 hours)

**Subject:** Day 5: Permission Doesn't Come From Your Board (It Comes From You)

**Send Delay:** 24 hours after previous email

**Body:** [Copy from 7day-pivot-challenge.md — Day 4 email]

---

### Email 6: Day 6 (120 hours)

**Subject:** Day 6: Your 30-Day IMG Pivot Playbook (The Exact Steps)

**Send Delay:** 24 hours after previous email

**Body:** [Copy from 7day-pivot-challenge.md — Day 5 email]

---

### Email 7: Day 7 (144 hours) — THE OFFER

**Subject:** Day 7: Here's What Happens Next (Your Real Next Step)

**Send Delay:** 24 hours after previous email

**Body:** [Copy from 7day-pivot-challenge.md — Day 6 email]

**IMPORTANT:** In the body, make sure to include these working links:
- Free Fear Audit: `https://fear-audit.vercel.app`
- Courage to Choose $27 PDF: `https://gumroad.com/l/courage-to-choose` (or your actual Gumroad link)

---

## Step 3: Configure Entry Trigger

In the sequence settings:

1. **Entry Trigger:** `API` (manual tag-based)
2. **Trigger Tag:** `challenge-joined`
3. Save sequence

When anyone is tagged with `challenge-joined`, they auto-enroll.

---

## Step 4: Configure Exit Action

After Email 7:

1. Click **Email 7** → **Next Action**
2. Select **Add Tag:** `challenge-complete`
3. Select **Move to Sequence:** (optional) Route to Fear Audit nurture sequence IDs 436027-436031

---

## Step 5: Get Sequence ID

Once saved:

1. In Sequences list, click the 7-Day IMG Pivot Challenge sequence
2. Copy the **Sequence ID** from the URL: `https://app.encharge.io/sequences/{SEQUENCE_ID}`
3. Save it to a file: `encharge-pivot-sequence-id.txt`

---

## Step 6: Deploy Landing Page & API

Now that the sequence exists, deploy the contact management layer:

```bash
# 1. Deploy landing page
netlify deploy --prod --single-file pivot-challenge-landing.html

# 2. Deploy API handler (adds contacts to Encharge)
python encharge_pivot_handler.py

# 3. Test by submitting email to landing page
# Should see "Check your email for Day 1" confirmation
# Contact should appear in Encharge with challenge-joined tag
```

---

## Step 7: Test Full Funnel

1. Visit your landing page
2. Submit test email: `test@yourmail.com`
3. Check that:
   - ✓ Form shows success message
   - ✓ Contact appears in Encharge (Contacts page)
   - ✓ Contact has `challenge-joined` tag
   - ✓ First email queues for delivery
4. Wait 5 minutes
5. Check inbox for Day 1 email

---

## Step 8: Verify Email Delivery

1. Check Encharge **Logs** for email delivery status
2. Click the contact in Encharge → **Activity** → Verify email was sent
3. Check spam folder if not in inbox

---

## Total Setup Time

- Encharge UI setup: **5-10 minutes**
- Landing page deployment: **2 minutes**
- API deployment: **2 minutes**
- Testing: **5 minutes**
- **Total: ~15-20 minutes to fully live**

---

## Promotion

Once tested, add CTAs to your scheduled posts (via Zernio first comment):

```
Free 7-Day IMG Pivot Challenge for unmatched IMGs:
https://your-domain.com/pivotchallenge

Get Day 1 in 5 minutes.
```

---

## Success Checklist

- [ ] Sequence created in Encharge (7 emails)
- [ ] Landing page deployed
- [ ] API running locally or on server
- [ ] Test email submitted to landing page
- [ ] Test email appeared in Encharge with `challenge-joined` tag
- [ ] Day 1 email received in inbox
- [ ] Day 7 email includes Fear Audit + Courage to Choose links
- [ ] Promoted to social posts
