# LinkedIn Image Uploader - Setup Guide

Automate adding images to your LinkedIn scheduled posts. One command, zero manual steps.

---

## ⚠️ IMPORTANT: This is Complex

Be honest with yourself: Do you want to set this up now, or just add the images manually (5 min) and build a simpler skill for next time?

**If manual is faster for you right now:** Skip steps 1-3, just do the uploads manually on LinkedIn, and I'll build a better solution next time.

**If you want full automation:** Follow steps 1-5 below.

---

## Step 1: Create LinkedIn Developer App

### 1.1 Go to LinkedIn Developers
- Visit: https://www.linkedin.com/developers/apps
- Sign in with your LinkedIn account

### 1.2 Create New App
1. Click **"Create app"**
2. Fill in the form:
   - **App name:** "LinkedIn Image Uploader"
   - **LinkedIn Page:** Select or create a LinkedIn page (required)
   - **App logo:** Upload any image
   - **Terms:** Check the box
   - Click **"Create app"**

### 1.3 Get Your Credentials
1. Go to your app's **"Auth"** tab
2. Copy these values (keep them secret):
   - **Client ID**
   - **Client Secret**

### 1.4 Add Redirect URL
1. In the **"Auth"** tab, find "Authorized redirect URLs for your app"
2. Click **"Add redirect URL"**
3. Add: `http://localhost:8000/callback`
4. Click **"Update"**

---

## Step 2: Set Environment Variables

### On macOS/Linux:

```bash
# Add to ~/.bash_profile or ~/.zshrc
export LINKEDIN_CLIENT_ID="your-client-id-here"
export LINKEDIN_CLIENT_SECRET="your-client-secret-here"

# Save file, then reload:
source ~/.zshrc  # or ~/.bash_profile
```

### On Windows (PowerShell):

```powershell
[Environment]::SetEnvironmentVariable("LINKEDIN_CLIENT_ID", "your-client-id-here", "User")
[Environment]::SetEnvironmentVariable("LINKEDIN_CLIENT_SECRET", "your-client-secret-here", "User")
# Restart PowerShell
```

**Verify they're set:**
```bash
echo $LINKEDIN_CLIENT_ID
echo $LINKEDIN_CLIENT_SECRET
```

Both should print your values.

---

## Step 3: Install Dependencies

```bash
cd ~/Claude\ TubeonAI

pip install requests
# or
pip3 install requests
```

---

## Step 4: Authenticate with LinkedIn

### First Time Only:

```bash
cd ~/Claude\ TubeonAI

python linkedin_oauth.py
# or
python3 linkedin_oauth.py
```

**What happens:**
1. Browser opens with LinkedIn authorization page
2. You click "Authorize"
3. Browser closes, token is saved locally
4. Done!

**Token saved to:** `~/.linkedin/config.json` (private, only you can read)

---

## Step 5: Run Image Uploader

```bash
cd ~/Claude\ TubeonAI

python linkedin_image_uploader.py
# or
python3 linkedin_image_uploader.py
```

**Script will:**
1. ✅ Find your 7 images
2. ✅ Get your scheduled LinkedIn posts
3. ✅ Match images to posts
4. ✅ Ask you to confirm matches
5. ✅ Upload images and attach to posts
6. ✅ Done!

**Time to run:** ~2 minutes

---

## Troubleshooting

### "No access token provided"
- Run `python linkedin_oauth.py` first
- Make sure environment variables are set

### "No posts found"
- Make sure you have scheduled posts on LinkedIn
- Check that your access token is valid

### "Could not match images to posts"
- Make sure you have exactly 7 images in `~/Downloads/Agency LinkedIn Post Pictures/`
- Check image filenames match the script

### "Request failed with status code 401"
- Your access token expired
- Run `python linkedin_oauth.py` again to re-authenticate

### "SSL certificate error"
```bash
# If you get SSL errors, try:
python -m pip install --upgrade certifi
```

---

## For Future Campaigns

Once you have this set up:

1. Generate graphics in Gemini → Downloads folder
2. Rename them: `01-linkedin-post-X.png`, `02-linkedin-post-X.png`, etc.
3. Schedule posts on LinkedIn (text only, no images)
4. Run: `python linkedin_image_uploader.py`
5. Done!

Or, I can build a full `/linkedin-batch-publish` skill that does everything in one command.

---

## Security Notes

- ✅ Your access token is stored locally (`~/.linkedin/config.json`)
- ✅ Only readable by you (mode 0600)
- ✅ Never shared with anyone
- ✅ You can revoke it anytime in LinkedIn Developer dashboard

**Never:**
- Share your Client Secret
- Commit credentials to git
- Put them in code

---

## Need Help?

If something breaks:
1. Check the error message (usually tells you what's wrong)
2. Try the Troubleshooting section above
3. Or just do it manually (5 min) and we'll build a better solution next time

---

## What's Next

After this works:
- I'll build a `/linkedin-batch-publish` skill that combines everything
- Next campaign: One command, fully automated
- No manual matching, no naming, zero steps

---

**Ready? Start with Step 1 above.**
