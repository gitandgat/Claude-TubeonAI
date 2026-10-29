# LinkedIn API Setup Guide

This guide walks you through setting up LinkedIn OAuth 2.0 to enable unlimited LinkedIn post scheduling (bypasses Zernio's 5-posts/day limit).

## Architecture

- **Zernio** (kept): Instagram, Facebook, TikTok, YouTube scheduling (5 posts/day per platform)
- **LinkedIn API** (new): Direct LinkedIn scheduling (no daily limit)
- **Fallback**: If LinkedIn API isn't configured, scheduler automatically falls back to Zernio

## Step 1: Create LinkedIn Developer App

1. Go to https://www.linkedin.com/developers/apps
2. Click **Create app**
3. Fill in:
   - **App name**: "Crosswalk Wisdom AI Agent"
   - **LinkedIn Page**: Select Crosswalk Wisdom page
   - **App logo**: Upload Crosswalk Wisdom logo (150x150px)
   - **Legal agreement**: Check the box
4. Click **Create app**

## Step 2: Request Marketing Developer Platform Access

1. In your app dashboard, go to **Products** tab
2. Search for **Marketing Developer Platform**
3. Click **Request access**
   - This may require review; LinkedIn typically approves within 24-48 hours
4. Once approved, go to **Settings** tab

## Step 3: Get Your Credentials

In your app's **Settings** tab, copy these values:

| Field | Your Value |
|-------|-----------|
| **Client ID** | `LINKEDIN_CLIENT_ID` in `.env` |
| **Client Secret** | `LINKEDIN_CLIENT_SECRET` in `.env` |

In **Credentials** tab, find:
| Field | Your Value |
|-------|-----------|
| **Redirect URLs** | Add `http://localhost:8000/auth/callback` |

## Step 4: Complete OAuth Flow

Run the auth setup script (you'll use this once to get an access token):

```bash
cd /Users/toto/Claude\ TubeonAI
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

from linkedin_api_client import LinkedInAPIClient

# Initialize client
client = LinkedInAPIClient()

# Get authorization URL
auth_url = client.get_auth_url()
print(f'Open this URL in your browser:')
print(auth_url)
print()
print('After authorizing, you will be redirected.')
print('Copy the full redirect URL from the browser address bar.')
"
```

This outputs an authorization URL. Open it in your browser.

You will see:
- LinkedIn asking for permission
- After you authorize, you get redirected to `http://localhost:8000/auth/callback?code=...&state=...`
- **Copy the full URL from the address bar** (even if the page says it can't load)

## Step 5: Exchange Auth Code for Token

Run this to swap the code for an access token:

```bash
python -c "
import os
from dotenv import load_dotenv
load_dotenv()

from linkedin_api_client import LinkedInAPIClient

client = LinkedInAPIClient()
auth_code = input('Paste the authorization code from the redirect URL: ')

# Exchange code for token
token_data = client.exchange_code_for_token(auth_code)

print(f'✓ Access token obtained!')
print(f'Token expires in {token_data.get(\"expires_in\")} seconds')

# Get your user ID
user_info = client.get_me()
user_id = user_info.get('id')
print(f'Your LinkedIn user ID: {user_id}')
"
```

This gives you:
- **Access Token** → add to `.env` as `LINKEDIN_ACCESS_TOKEN`
- **User ID** → convert to URN format

## Step 6: Update .env File

Add these lines to `./.env`:

```bash
# LinkedIn API (for direct post scheduling without Zernio limit)
LINKEDIN_CLIENT_ID=your_client_id_here
LINKEDIN_CLIENT_SECRET=your_client_secret_here
LINKEDIN_ACCESS_TOKEN=your_access_token_here
LINKEDIN_USER_URN=urn:li:person:your_user_id_here
```

Example:
```bash
LINKEDIN_CLIENT_ID=87654321
LINKEDIN_CLIENT_SECRET=abcd1234efgh5678
LINKEDIN_ACCESS_TOKEN=AQEfAbCdEfG1h2i3j4k5lm6nopqrstu
LINKEDIN_USER_URN=urn:li:person:123456789
```

## Step 7: Verify Setup

Run the agent to test:

```bash
cd /Users/toto/Claude\ TubeonAI
python -c "from dotenv import load_dotenv; load_dotenv(); import os; os.system('python run_agent.py --dry-run')"
```

You should see:
```
[6/7] Scheduling post...
Sending to LinkedIn API...
✓ Post scheduled via LinkedIn API!
  Post ID: abc123def456
```

If it shows a warning about LinkedIn API not configured, check that all 4 environment variables are set in `.env`.

## Step 8: Token Refresh

Access tokens expire after ~2 months. When your token expires:

1. Repeat **Step 4** to get a new authorization code
2. Run the exchange code script again
3. Update `LINKEDIN_ACCESS_TOKEN` in `.env`

The system will auto-save a `refresh_token` to `.linkedin_token` file for future refreshes (handled by the client).

## Switching Between Zernio and LinkedIn API

The scheduler automatically:
1. **Tries LinkedIn API first** (if configured) → unlimited posts
2. **Falls back to Zernio** if LinkedIn API fails → 5 posts/day limit applies

To force Zernio only, comment out the LinkedIn credentials in `.env`.

## Troubleshooting

### "LINKEDIN_CLIENT_ID and LINKEDIN_CLIENT_SECRET required"
- Check that both are set in `.env` and saved
- Run `echo $LINKEDIN_CLIENT_ID` to verify

### "No access token. Complete OAuth flow first"
- You skipped **Step 5**
- Run the auth setup script again and complete the code exchange

### "LINKEDIN_USER_URN not set"
- Run the `get_me()` step again and extract your user ID
- Format as `urn:li:person:YOUR_ID_HERE`

### LinkedIn API returns 403 Forbidden
- Your app may not have **Marketing Developer Platform** access approved yet
- Check app dashboard: **Products** → **Marketing Developer Platform** → approval status
- Contact LinkedIn support if it's been >48 hours

## Performance & Limits

- **LinkedIn API rate limits**: 200 requests / hour (scheduling 10 posts/day = 10 requests)
- **Post scheduling window**: Must schedule 24+ hours in advance (LinkedIn requirement)
- **Image uploads**: Direct to LinkedIn via API (no Zernio CDN needed for LinkedIn API path)

---

After setup, the agent will automatically use LinkedIn API for LinkedIn posts while keeping Zernio for multi-platform campaigns (IG/FB/TT/YT). You can now schedule **10+ posts/day to LinkedIn** without hitting Zernio's limit.
