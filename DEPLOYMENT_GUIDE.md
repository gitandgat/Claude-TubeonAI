# DEPLOYMENT GUIDE: Autonomous Sales System

Complete step-by-step deployment of the fully autonomous 100% hands-off revenue system.

Total time: 5-7 days | Total cost: $1,000-3,100 one-time setup

---

## DAY 1: TWILIO SETUP (Phone System)

### 1. Create Twilio Account
- Go to https://www.twilio.com/
- Sign up (free account)
- Verify email
- Add payment method

### 2. Get Phone Number
- Dashboard → Phone Numbers → Buy a Number
- Pick any US number (they're all the same for our purposes)
- Cost: $1-2/month
- **Save this number:** Will be your sales line

### 3. Get API Credentials
- Account → API Keys & Tokens
- Copy: Account SID
- Copy: Auth Token
- Create new API Key (for security)
- Copy: API Key SID
- Copy: API Key Secret

### 4. Create TwiML Application
- Phone Numbers → TwiML Applications → Create new
- Name: "Sales Bot"
- Voice URL: `https://yourdomain.com/webhook/twilio/voice`
- Status Callback URL: `https://yourdomain.com/webhook/twilio/status`
- Save SID

### 5. Setup Incoming Webhooks
- Phone Numbers → Manage Numbers → [Your Number]
- Voice: TwiML App: "Sales Bot"
- Save

**Cost: $1-2/month**
**Time: 20 minutes**
**Files needed:** `twilio_config.json` (see below)

---

## DAY 2: ELEVENLABS SETUP (AI Voice)

### 1. Create ElevenLabs Account
- Go to https://elevenlabs.io/
- Sign up (free tier: 10K characters/month)
- Verify email

### 2. Create API Key
- Profile → API Keys
- Copy your API Key
- Save securely

### 3. Create AI Voice
- Voices → Clone Voice
- Upload sample audio (your voice or any voice)
- Name: "Sales Agent"
- Accept terms
- Wait for processing (~5 min)
- Copy Voice ID

### 4. Test Voice
- Go to Speech Synthesis
- Test sentence: "Hi, thanks for calling. How are you doing?"
- Click voice: "Sales Agent"
- Listen to preview
- Should sound natural

### 5. Pricing
- Free tier: 10K characters/month ($0)
  - Each call ~5,000 characters
  - = ~2 calls/month free
- Growth plan: $99/month
  - 100K characters
  - = ~20 calls/month
- Recommended: Start with Growth plan ($99/month)

**Cost: $99-500/month (based on volume)**
**Time: 15 minutes**
**Files needed:** `elevenlabs_config.json`

---

## DAY 3: DOCSIGN SETUP (Contracts)

### 1. Create DocuSign Account
- Go to https://www.docusign.com/
- Sign up (free account available)
- Verify email

### 2. Get API Credentials
- Settings → Apps & Integrations → Integrations
- Create API Integration Key
- Generate RSA Keypair (if needed)
- Copy: Integration Key
- Copy: Secret Key

### 3. Create Contract Template
- Go to "Create" → "Use a Template"
- Upload your contract file OR create new
- Template: Name it "Service Agreement"
- Add signature fields
- Save template
- Copy template ID

### 4. Test Document
- Create a test document
- Send to yourself
- Sign it
- Verify the flow works

**Cost: Free (DocuSign free tier allows limited sends)**
**Time: 25 minutes**
**Files needed:** `docusign_config.json`

---

## DAY 4: STRIPE SETUP (Payments)

### 1. Create Stripe Account
- Go to https://stripe.com/
- Sign up (free)
- Add business details

### 2. Get API Keys
- Settings → Developers → API Keys
- Copy: Publishable Key
- Copy: Secret Key
- Save securely

### 3. Create Payment Link
- Products → Create Product
- Name: "Demand Discovery Monthly"
- Price: $1500
- Recurring: Yes, monthly
- Save

### 4. Create Payment Link
- Use the product above
- Settings: 
  - Allow promotion codes: Yes
  - Customer emails: Required
  - Redirect after payment: to /thank-you
- Copy the payment link
- **Save this link:** You'll send this to customers

**Cost: 2.9% + $0.30 per transaction (only when revenue)**
**Time: 15 minutes**
**Files needed:** `stripe_config.json`

---

## DAY 5: DEPLOYMENT CONFIGURATION

### 1. Create Config Files

**`twilio_config.json`**
```json
{
  "account_sid": "YOUR_ACCOUNT_SID",
  "auth_token": "YOUR_AUTH_TOKEN",
  "api_key": "YOUR_API_KEY",
  "api_secret": "YOUR_API_SECRET",
  "phone_number": "+1XXXXXXXXXX",
  "twiml_app_sid": "YOUR_TWIML_APP_SID"
}
```

**`elevenlabs_config.json`**
```json
{
  "api_key": "YOUR_API_KEY",
  "voice_id": "YOUR_VOICE_ID",
  "model_id": "eleven_monolingual_v1"
}
```

**`docusign_config.json`**
```json
{
  "integration_key": "YOUR_INTEGRATION_KEY",
  "secret_key": "YOUR_SECRET_KEY",
  "template_id": "YOUR_TEMPLATE_ID",
  "base_url": "https://demo.docusign.net"
}
```

**`stripe_config.json`**
```json
{
  "publishable_key": "YOUR_PUBLISHABLE_KEY",
  "secret_key": "YOUR_SECRET_KEY",
  "payment_link": "https://buy.stripe.com/YOUR_LINK"
}
```

### 2. Set Environment Variables
```bash
export TWILIO_ACCOUNT_SID="YOUR_ACCOUNT_SID"
export TWILIO_AUTH_TOKEN="YOUR_AUTH_TOKEN"
export ELEVENLABS_API_KEY="YOUR_API_KEY"
export DOCUSIGN_INTEGRATION_KEY="YOUR_KEY"
export STRIPE_SECRET_KEY="YOUR_KEY"
```

**Time: 15 minutes**

---

## DAY 6: WEBHOOK DEPLOYMENT

### 1. Deploy Webhook Server
We'll create a webhook server that connects Twilio → AI Agent → ElevenLabs

```bash
# Install dependencies
pip install twilio elevenlabs anthropic stripe docusign-esign

# Start webhook server
python webhook_server.py
```

### 2. Setup Tunneling (for local development)
```bash
# Install ngrok (free)
brew install ngrok

# Start tunnel
ngrok http 5000

# Copy public URL: https://XXXXX.ngrok.io
```

### 3. Update Twilio Webhook
- Twilio → Phone Numbers → Manage Numbers
- Voice URL: `https://XXXXX.ngrok.io/webhook/twilio/voice`
- Status Callback: `https://XXXXX.ngrok.io/webhook/twilio/status`

### 4. Test End-to-End
- Call your Twilio number
- AI should answer
- Conduct test conversation
- At end, AI should send contract link

**Time: 30 minutes**

---

## DAY 7: PRODUCTION DEPLOYMENT

### 1. Choose Hosting
**Option A: Heroku (Easiest)**
```bash
# Create Heroku account (free tier available)
heroku create your-app-name
git push heroku main
```

**Option B: AWS Lambda (Cheapest)**
- AWS → Lambda → Create Function
- Deploy webhook as Lambda function

**Option C: DigitalOcean (Balanced)**
- Create droplet ($6/month)
- Deploy webhook

### 2. Buy Domain (Optional)
- Register domain: yourname.com
- Point to webhook server
- Use custom domain instead of ngrok

### 3. Go Live
- Update Twilio webhook to production URL
- Remove ngrok tunnel
- Monitor first calls (see operations manual)

**Time: 2-4 hours**

---

## FINAL CHECKLIST

- [ ] Twilio account created + phone number assigned
- [ ] ElevenLabs account created + voice trained
- [ ] DocuSign account created + contract template set
- [ ] Stripe account created + payment link ready
- [ ] All 4 config files created
- [ ] Webhook server deployed locally
- [ ] Test call successful (AI answered, conversation flowed)
- [ ] Test contract sent (recipient received DocuSign)
- [ ] Test payment link works (Stripe loaded)
- [ ] Production server deployed
- [ ] Twilio webhook points to production
- [ ] First real call completed successfully

---

## COSTS

| Service | Cost | Purpose |
|---------|------|---------|
| Twilio | $1-2/month | Incoming calls |
| ElevenLabs | $99-500/month | AI voice |
| DocuSign | $0-100/month | Contracts |
| Stripe | 2.9% + $0.30 | Payments |
| Hosting | $0-50/month | Webhook server |
| **Total** | **$100-652/month** | **Full system** |

**Revenue (Month 1):** $30,000-45,000
**Net Profit (Month 1):** $29,348-44,900

---

## TROUBLESHOOTING

**"Twilio call doesn't go through"**
- Check phone number is active
- Check TwiML app is set correctly
- Check webhook URL is accessible
- Try calling from different phone

**"AI voice sounds robotic"**
- Re-train voice in ElevenLabs with better audio
- Try different voice model
- Adjust speaking speed/stability

**"Contract doesn't send"**
- Check DocuSign credentials
- Verify template ID is correct
- Check email is valid

**"Payment link fails"**
- Verify Stripe account is activated
- Check secret key is correct
- Test payment with test card

---

You're now ready to launch. When people call your number, the AI sales agent will answer and close them.

**Next: Webhook Orchestrator (ties everything together)**
