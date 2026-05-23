# IMG Pivot Challenge — Deployment & Setup Guide

**Status:** ✅ All code merged and ready to deploy

---

## ✅ What's Done

### 1. **API Handler** (MERGED into webhook_server.py)
- New endpoint: `POST /api/encharge/subscribe`
- Receives landing page form submission
- Creates contact in Encharge + adds `challenge-joined` tag
- Triggers auto-enrollment in 7-Day IMG Pivot Challenge sequence
- **File:** `/Users/toto/Claude TubeonAI/webhook_server.py`
- **Status:** Ready to deploy

### 2. **Landing Page** (CREATED as React component)
- New page: `ImgPivotChallengePage.tsx`
- Route: `/imgpivot` on www.crosswalkwisdom.com
- Dark luxury branding (matches Crosswalk Wisdom theme)
- Email capture form → API submission
- Success/error messaging
- CAN-SPAM compliant footer
- **File:** `/Users/toto/crosswalk-wisdom-new/src/pages/ImgPivotChallengePage.tsx`
- **Status:** Ready to deploy

### 3. **Encharge Sequence** (MANUAL SETUP REQUIRED)
- Use manual guide: `encharge-pivot-setup-manual.md`
- Create sequence via Encharge UI (5–10 min copy-paste)
- Entry trigger: `challenge-joined` tag
- Exit action: `challenge-complete` tag + route to Fear Audit sequences
- **Status:** Pending your manual setup in Encharge

---

## 📋 Deployment Checklist

### Phase 1: Encharge Sequence (You do this manually)
- [ ] Log into https://app.encharge.io
- [ ] Follow `encharge-pivot-setup-manual.md` to create the 7-email sequence
- [ ] Get the Sequence ID and note it

### Phase 2: Deploy React Landing Page
- [ ] Push to GitHub (crosswalk-wisdom-new repo)
- [ ] Vercel automatically deploys to www.crosswalkwisdom.com
- [ ] Verify `/imgpivot` route is live

### Phase 3: Deploy API to Railway
- [ ] Push webhook_server.py changes to GitHub (Claude TubeonAI repo)
- [ ] Railway automatically redeploys webhook server
- [ ] Verify `POST /api/encharge/subscribe` is live

### Phase 4: Test Full Funnel
- [ ] Test with curl command (below)
- [ ] Verify contact appears in Encharge with `challenge-joined` tag
- [ ] Visit www.crosswalkwisdom.com/imgpivot in browser
- [ ] Submit test email via form
- [ ] Wait 5 minutes, check inbox for Day 1 email

### Phase 5: Promote
- [ ] Add CTAs to 100+ existing scheduled social posts
- [ ] Promote via LinkedIn, Instagram, TikTok, email

---

## 🚀 Detailed Steps

### Step 1: Manual Encharge Setup (5–10 min)

Follow **encharge-pivot-setup-manual.md** exactly:

1. Log into Encharge UI
2. Create sequence: "7-Day IMG Pivot Challenge"
3. Copy-paste all 7 email bodies from the guide
4. Set send delays: 0, 1440, 2880, 4320, 5760, 7200, 8640 minutes
5. Configure entry trigger: tag `challenge-joined`
6. Configure exit action: tag `challenge-complete`
7. Get Sequence ID from URL

**CRITICAL:** Verify Day 7 email includes:
```
Fear Audit: https://fear-audit.vercel.app
Courage to Choose: https://sahawat.gumroad.com/l/courage-to-choose
```

### Step 2: Deploy Landing Page

Your React site (crosswalk-wisdom-new) is already configured with Vercel auto-deployment.

**Just commit and push:**
```bash
cd ~/crosswalk-wisdom-new
git add -A
git commit -m "feat: Add IMG Pivot Challenge landing page"
git push
```

Vercel will automatically deploy. Route will be live at:
```
https://www.crosswalkwisdom.com/imgpivot
```

**Verify:**
- Open https://www.crosswalkwisdom.com/imgpivot in browser
- See Crosswalk Wisdom navbar + landing page form
- Form should load without errors

### Step 3: Deploy API to Railway

Your webhook_server.py is already merged with the new endpoint.

**Just commit and push:**
```bash
cd ~/Claude\ TubeonAI
git add webhook_server.py
git commit -m "feat: Add IMG Pivot Challenge form handler"
git push
```

Railway will automatically redeploy. API will be live at:
```
https://crosswalk-webhook.up.railway.app/api/encharge/subscribe
```

(Replace `crosswalk-webhook` with your actual Railway URL if different)

**Update landing page API endpoint if needed:**
- In ImgPivotChallengePage.tsx, line ~37:
- Default: `https://crosswalk-webhook.up.railway.app`
- If your Railway URL is different, update it

### Step 4: Test Full Funnel

**Test 1: Direct API Test (via curl)**
```bash
curl -X POST https://crosswalk-webhook.up.railway.app/api/encharge/subscribe \
  -H "Content-Type: application/json" \
  -d '{
    "firstName": "Test",
    "email": "test@example.com"
  }'
```

Expected response:
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

**Test 2: Browser Form Test**
1. Go to https://www.crosswalkwisdom.com/imgpivot
2. Enter: First name = "Test2", Email = "test2@example.com"
3. Click "Start the Challenge"
4. Should see green success message: "Check your email!"

**Test 3: Verify Encharge**
1. Log into Encharge
2. Go to Contacts
3. Search for "test2@example.com"
4. Verify:
   - ✓ Contact exists
   - ✓ Has tag: `challenge-joined`
   - ✓ Enrolled in "7-Day IMG Pivot Challenge" sequence
5. Go to contact's Activity
6. Verify first email is queued for delivery

**Test 4: Verify Email Delivery**
1. Wait 5 minutes
2. Check test email inbox (test2@example.com)
3. Should have Day 1 email: "Your IMG Pivot Challenge Starts Now"
4. Verify email shows Sahawat's signature

**Test 5: Verify All 7 Emails**
1. In Encharge, go to the 7-Day IMG Pivot Challenge sequence
2. Verify all 7 emails are created
3. Verify timing is correct (0, 24h, 48h, 72h, 96h, 120h, 144h)
4. Verify Day 7 email has Fear Audit + Courage to Choose links

---

## 📊 Expected Results

**First 7 days (after going live):**
- Landing page views: 50–100
- Email signups: 20–30 (from social traffic)
- Day 1 email open rate: 60%+

**First 30 days:**
- Total signups: 50–100
- Open rate: 60%+
- Click to Fear Audit: 30%+
- Conversions to $27 PDF: 5–10 (potential $135–$270 revenue)
- Challenge completion: 40–50%

---

## 🔗 API Endpoints (Live)

Once deployed, these endpoints are available:

| Endpoint | Method | Purpose | Response |
|----------|--------|---------|----------|
| `/api/encharge/subscribe` | POST | Landing page form | `{success, message, contact_id, sequence}` |
| `/api/encharge/quiz-result` | POST | Fear Audit quiz callback | `{status, stage}` |
| `/quiz-results` | POST | Fear Audit quiz callback (original) | `{status, stage}` |
| `/health` | GET | Health check | `{status: "ok"}` |

---

## 🛠️ Troubleshooting

### Landing page form not submitting
- Check browser console for errors
- Verify API endpoint URL in ImgPivotChallengePage.tsx
- Confirm Railway API is live: `curl https://crosswalk-webhook.up.railway.app/health`

### Contact not appearing in Encharge
- Check API response for errors
- Verify ENCHARGE_API_KEY is set in Railway environment variables
- Confirm email format is valid

### Email not arriving
- Wait 5 minutes (delivery queue delay)
- Check Encharge Logs for email status
- Verify contact has `challenge-joined` tag in Encharge
- Check spam folder

### Day 7 email missing links
- In Encharge UI, edit Day 7 email
- Verify these links are in the body:
  - `https://fear-audit.vercel.app`
  - `https://sahawat.gumroad.com/l/courage-to-choose`

---

## 📝 Next Steps

1. **Today:** Manual Encharge setup (10 min)
2. **Today:** Test with curl (2 min)
3. **Tomorrow:** Deploy React landing page (git push)
4. **Tomorrow:** Test form in browser
5. **This week:** Deploy to Railway (git push)
6. **This week:** Run full funnel test
7. **Next week:** Promote to 100+ social posts via Zernio

---

## 📞 Support

If anything breaks during deployment:

1. **Check Railway logs:**
   ```bash
   railway logs --follow
   ```

2. **Check Vercel logs:**
   - Dashboard → crosswalk-wisdom-new → Deployments

3. **Verify environment variables:**
   - Railway: ENCHARGE_API_KEY set?
   - React: VITE_API_URL correct?

4. **Test health check:**
   ```bash
   curl https://crosswalk-webhook.up.railway.app/health
   ```

---

## 📦 Files Changed

**Backend:**
- `/Users/toto/Claude TubeonAI/webhook_server.py` ✓ Merged

**Frontend:**
- `/Users/toto/crosswalk-wisdom-new/src/pages/ImgPivotChallengePage.tsx` ✓ Created
- `/Users/toto/crosswalk-wisdom-new/src/App.tsx` ✓ Route added

**Manual Setup Required:**
- `encharge-pivot-setup-manual.md` — Follow this for Encharge sequence

---

**Ready to deploy! 🚀**
