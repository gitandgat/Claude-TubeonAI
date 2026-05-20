# 7-Day IMG Pivot Challenge: Full Setup Guide

This guide walks through implementing the complete lead magnet funnel: landing page → email capture → Encharge automation → nurture sequence → paid upsells.

## Files Created

1. **7day-pivot-challenge.md** — Complete email sequence + copy (already created ✓)
2. **encharge-setup-pivot-challenge.py** — Encharge automation setup script
3. **pivot-challenge-landing.html** — Landing page with email form
4. **encharge_pivot_handler.py** — Backend API for form handling
5. **IMG-PIVOT-CHALLENGE-SETUP.md** — This guide

---

## Step 1: Run Encharge Automation Setup

### Prerequisites

```bash
# Ensure ENCHARGE_API_KEY is in .env
cat .env | grep ENCHARGE_API_KEY
```

### Execute Setup Script

```bash
python encharge-setup-pivot-challenge.py
```

**Expected Output:**
```
=== 7-Day IMG Pivot Challenge: Encharge Automation Setup ===

[1/4] Creating sequence...
  ✓ Sequence created: <sequence-id>

[2/4] Creating 7 email templates...
  [1/7] day-0: Day 1: Your IMG Pivot Challenge Starts Now...
  [2/7] day-1: Day 2: The Question Isn't "How Do I Stay?"...
  ...
  ✓ All 7 emails created

[3/4] Creating tags...
  ✓ Tags created: challenge-joined, challenge-complete

[4/4] Saving configuration...
  ✓ Configuration saved to encharge-pivot-challenge-config.json
```

### What This Created

- ✓ Encharge sequence: "7-Day IMG Pivot Challenge"
- ✓ 7 emails with automated delays:
  - Email 1: Immediate (Day 0)
  - Email 2: +24 hours (Day 1, 9am ET)
  - Email 3: +48 hours (Day 2, 9am ET)
  - Email 4: +72 hours (Day 3, 9am ET)
  - Email 5: +96 hours (Day 4, 9am ET)
  - Email 6: +120 hours (Day 5, 9am ET)
  - Email 7: +144 hours (Day 6, 9am ET)
- ✓ Tags: `challenge-joined` (entry) and `challenge-complete` (exit)
- ✓ Config file: `encharge-pivot-challenge-config.json`

---

## Step 2: Deploy Landing Page

### Option A: Static Hosting (Recommended for MVP)

Host `pivot-challenge-landing.html` on Vercel, Netlify, or your own server:

```bash
# Netlify CLI
netlify deploy --prod --dir . --single-file pivot-challenge-landing.html

# Or: Upload to your server
scp pivot-challenge-landing.html user@server:/var/www/html/pivotchallenge.html
```

**URL:** `https://yourdomain.com/pivotchallenge` or `https://crosswalkwisdom.com/challenge`

### Option B: Full Website Integration

If you have a React/Next.js site (like the existing Crosswalk Wisdom site):

1. Copy the HTML/CSS into a new React component:

```tsx
// src/pages/pivot-challenge.tsx
export default function PivotChallengePage() {
  return (
    <div style={styles.container}>
      {/* Copy CSS from pivot-challenge-landing.html into style object */}
      {/* Copy HTML structure into JSX */}
    </div>
  )
}
```

2. Update form submission to call your API:

```tsx
const handleSubmit = async (e) => {
  e.preventDefault()
  const response = await fetch('/api/encharge/subscribe', {
    method: 'POST',
    body: JSON.stringify({
      firstName: e.target.firstName.value,
      email: e.target.email.value,
    }),
  })
  // Show success message
}
```

---

## Step 3: Deploy Backend API Handler

### Option A: Add to Existing FastAPI Server

If you already have `webhook_server.py` running on Railway:

1. Merge `encharge_pivot_handler.py` into `webhook_server.py`:

```python
# In webhook_server.py
from encharge_pivot_handler import router as encharge_router

app.include_router(encharge_router)
```

2. Deploy:

```bash
git add .
git commit -m "feat: Add IMG Pivot Challenge API handler"
git push
```

### Option B: Deploy as Standalone Service

```bash
# Install dependencies
pip install fastapi uvicorn httpx python-dotenv

# Run locally
python encharge_pivot_handler.py

# Or deploy to Railway
# 1. Add Procfile:
echo "web: python encharge_pivot_handler.py" > Procfile

# 2. Push to Railway
railway up
```

**Endpoint:** `POST /api/encharge/subscribe`

---

## Step 4: Connect Landing Page to API

Update the form submission in `pivot-challenge-landing.html`:

**Before:**
```javascript
const response = await fetch('/api/encharge/subscribe', {
```

**After (with full URL if different domain):**
```javascript
const response = await fetch('https://your-api-domain.com/api/encharge/subscribe', {
    credentials: 'include',  // Include cookies if needed
```

Or update the `fetch` URL if your landing page and API are on the same domain.

---

## Step 5: Test the Full Funnel

### 1. Test Email Signup

```bash
# Use curl to submit test email
curl -X POST https://your-api-domain.com/api/encharge/subscribe \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "Test",
    "email": "test@example.com"
  }'
```

**Expected Response:**
```json
{
  "success": true,
  "message": "Welcome Test! Check your email for Day 1 of the challenge.",
  "contact_id": "test@example.com",
  "email": "test@example.com",
  "sequence": "7-Day IMG Pivot Challenge",
  "first_email_delay_minutes": 5
}
```

### 2. Check Encharge

1. Log in to Encharge: `https://app.encharge.io`
2. Go to **Contacts** → Search for test@example.com
3. Verify tags: `challenge-joined`
4. Go to **Sequences** → "7-Day IMG Pivot Challenge"
5. Verify email is queued for delivery

### 3. Test Email Delivery

- Wait 5 minutes for first email to send
- Check inbox for Day 1 email: "Your IMG Pivot Challenge Starts Now"
- Verify links work (Fear Audit link in Day 7 email)

---

## Step 6: Configure Encharge Routing & Triggers

### Entry Trigger

1. In Encharge, go to **Sequences** → "7-Day IMG Pivot Challenge"
2. Set **Entry Trigger**:
   - Trigger type: **API**
   - Event: `contact.created` + tag `challenge-joined`
3. Save

### Exit Routing

After Email 7, you want to route completers to post-challenge nurture:

1. Click **Email 7** → **Next Action**
2. Select: "Add tag: `challenge-complete`"
3. Select: "Move to sequence: `Fear Audit Nurture`" (you may need to create this)

### Segmentation Rules

Optional: Create segments in Encharge to track engagement:

- **Completed Challenge**: Tag = `challenge-complete`
- **High Intent**: Clicked Fear Audit link
- **Converted to PDF**: Purchased Courage to Choose ($27)

---

## Step 7: Promote to Your Audience

### Social Media Promotion

Use the pre-written snippets from `7day-pivot-challenge.md`:

#### LinkedIn Post

```
Just launched: The 7-Day IMG Pivot Challenge. 

For unmatched IMGs tired of the $48K limbo.

Shows you 4 actual paths that hire IMG doctors. No residency required. Email daily for 7 days. Completely free.

I walked this path. It works.

→ [Link in comments]

#CrosswalkWisdom #IMGCanada #CareerPivot #IMGDoctor
```

**Link:** `https://your-domain.com/pivotchallenge`

#### Instagram/TikTok Caption

```
7-Day IMG Pivot Challenge starts tomorrow. 
Free email course. 
4 paths paying $65K+. 
No more waiting. 
Link in bio.
```

#### Email to Existing List

If you have existing subscribers:

```
Subject: I'm giving out free stuff (how I left medicine & found something better)

Hey,

I built something that took me 3 years to figure out.

The 7-Day IMG Pivot Challenge — a free email course showing unmatched IMGs 
the 4 actual career paths nobody talks about.

→ [Link]

No spam. Unsubscribe anytime. But I think you'll find value in this.

—Sahawat
```

### Schedule to Zernio

From the existing scheduled posts, add CTAs to the pivot challenge:

```
[First comment on every 5pm ET post]
Free 7-Day IMG Pivot Challenge (for unmatched IMGs): https://your-domain.com/pivotchallenge
```

---

## Step 8: Track & Optimize

### Key Metrics to Watch

1. **Landing Page Views**
   - Google Analytics on pivot-challenge-landing.html
   - Target: 50-100 signups in first 30 days

2. **Email Opens**
   - Check Encharge dashboard
   - Target: 60%+ open rate

3. **Email Clicks**
   - Track clicks to Fear Audit
   - Target: 30%+ click-through rate

4. **PDF Conversions**
   - Track Gumroad sales for Courage to Choose ($27)
   - Target: 15%+ conversion (5-10 sales from 50-100 signups)

5. **Sequence Completion**
   - % who receive all 7 emails
   - % who reach Day 7 (the offer)
   - Target: 40-50% completion rate

### Optimize Each Email

Use Encharge's A/B testing to improve:

1. **Subject lines** — Test curiosity vs. directness
2. **Send times** — Test 9am vs. 3pm ET
3. **CTA links** — Test "Take Fear Audit" vs. "See All 4 Paths"

---

## Step 9: Long-Term Nurture

### After Challenge Completion

Users tagged `challenge-complete` should flow to:

1. **Fear Audit Sequence** (Encharge IDs 436027-436031)
   - Free quiz → personalized report → slight upsell
2. **Courage to Choose Nurture** (3-5 emails)
   - Social proof → testimonials → $27 PDF link
   - Upsell to group coaching if conversion happens

---

## Troubleshooting

### Email Not Sending

```bash
# Check Encharge logs
curl -H "X-Encharge-Token: $ENCHARGE_API_KEY" \
  https://api.encharge.io/v1/contacts/test@example.com
```

Verify:
- [ ] Contact has `challenge-joined` tag
- [ ] Sequence is "Active" (not paused)
- [ ] Entry trigger is enabled
- [ ] Email isn't in spam folder

### Form Submission Failing

Check browser console for errors:

```javascript
// Add console logging to form handler
console.log('Form submitted with:', data)
console.log('API Response:', response)
```

Verify:
- [ ] API endpoint is correct (check CORS if different domain)
- [ ] ENCHARGE_API_KEY is set
- [ ] Email is valid format

### Tags Not Applied

Check Encharge API response:

```bash
curl -X POST https://api.encharge.io/v1/contacts \
  -H "X-Encharge-Token: $ENCHARGE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "firstName": "Test",
    "tags": ["challenge-joined"]
  }'
```

---

## Success Checklist

- [ ] Encharge sequence created with 7 emails
- [ ] Landing page deployed and accessible
- [ ] Form submits successfully to API
- [ ] Test email received in inbox
- [ ] All 7 emails showing in Encharge sequence
- [ ] Fear Audit link working in Day 7 email
- [ ] Promoted on LinkedIn/Instagram/TikTok
- [ ] Tracking set up (Google Analytics + Encharge)
- [ ] Post-challenge routing configured
- [ ] Team trained on follow-up (if applicable)

---

## Next Steps

1. **Run the setup script** (`python encharge-setup-pivot-challenge.py`)
2. **Deploy landing page** (Vercel, Netlify, or your site)
3. **Deploy API handler** (Railway or existing server)
4. **Test full funnel** with test email
5. **Promote** to 100+ scheduled social posts
6. **Monitor metrics** weekly

Expected timeline: **3-5 days** to full launch.

Expected results: **50-100 signups** in first 30 days, feeding into nurture sequences.
