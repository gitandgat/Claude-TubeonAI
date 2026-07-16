# Email & File Organizer Agents — Setup Guide

## What Was Built

Two autonomous daily agents to help manage your digital life:

### 1. File Organizer Agent
- **What it does**: Scans Desktop, Downloads, Documents, Pictures, Movies, Music directories
- **Analysis**: Classifies files by category (Media, Documents, Projects, Finance, etc.)
- **Duplicate detection**: Two-pass MD5 deduplication (finds wasted space)
- **Output**: Daily JSON report + email digest with findings
- **Safety**: Analysis only — never moves or deletes files (you approve changes first)

**Try it now:**
```bash
python -m agents.file_organizer_agent --dirs ~/Desktop --no-email
cat reports/file_organizer_*.json  # View the JSON report
```

### 2. Email Organizer Agent
- **What it does**: Reads unread emails from Gmail and Outlook
- **Classification**: Categories (Work, Finance, Invoices, Personal, Receipts, Marketing)
- **Actions**: 
  - Automatically labels and moves emails to matching folders
  - Archives marketing emails
  - Flags important emails (Invoice, Contract, Urgent, etc.)
- **Output**: Daily JSON report + email digest with summary
- **Multi-provider**: Seamlessly handles both Gmail and Outlook

**Note**: Gmail and Outlook OAuth2 setup required (see below)

---

## OAuth2 Setup (One-Time, Required Before Using Email Agent)

### Gmail Setup (Required)

**Step 1: Google Cloud Console**
1. Go to [console.cloud.google.com](https://console.cloud.google.com)
2. Create or select a project
3. APIs & Services → Enable APIs → Search "Gmail API" → Enable
4. OAuth consent screen:
   - User type: External
   - Scopes: Add `https://www.googleapis.com/auth/gmail.modify`
   - Test users: Add `totomakus@gmail.com`
5. Credentials → Create OAuth client ID:
   - Type: Desktop app
   - Name: "Crosswalk Email Organizer"
6. Download JSON → Save as `gmail_credentials.json` in repo root

**Step 2: Authorize Locally**
```bash
python -c "
from gmail_client import GmailClient
c = GmailClient()
c._get_service()  # Browser opens → authorize → token saved
print('Gmail auth complete!')
"
```

**Step 3: For Railway Deployment**
```bash
base64 gmail_credentials.json | tr -d '\n'  # Copy output → set as GMAIL_CREDENTIALS_B64
base64 gmail_token.json | tr -d '\n'        # Copy output → set as GMAIL_TOKEN_B64
```

---

### Outlook Setup (No Azure Account Needed)

Personal Microsoft accounts (Hotmail/Outlook.com) can't register Azure apps
without a paid-verification signup, and Microsoft blocked device-code flow
for all first-party apps. So `outlook_client.py` authenticates the same way
Thunderbird does: authorization-code flow (with PKCE) against the consumers
endpoint using Thunderbird's public client ID
(`9e5f94bc-e8a4-4e73-b8be-63364c29d753`), then talks **IMAP with XOAUTH2**
to `outlook.office365.com`.

**One-time authorization (two steps):**

```bash
# Step 1: generate the sign-in URL
python3 authorize_outlook.py
# → open the printed URL, sign in with your Hotmail account, accept permissions.
#   The browser lands on https://localhost/?code=... and shows a
#   "can't connect" error — that's EXPECTED. Copy the full URL.

# Step 2: redeem the code (paste the URL in quotes)
python3 authorize_outlook.py "https://localhost/?code=...&state=..."
# → saves outlook_token.json + runs an unread-mail smoke test
```

Tokens refresh silently afterwards. If refresh ever fails (MSA refresh
tokens expire after ~90 days of disuse), just re-run the two steps.

**For Railway Deployment**
```bash
base64 outlook_token.json | tr -d '\n'  # Copy output → set as OUTLOOK_TOKEN_B64
```
Note: Railway's filesystem is ephemeral, so the refreshed cache isn't
persisted between runs — if the cron ever starts failing auth, re-authorize
locally and update `OUTLOOK_TOKEN_B64`.

---

## Environment Variables to Add

Create a `.env` file (or add to existing) with:

```bash
# Gmail OAuth
GMAIL_CLIENT_ID=<from Google Cloud Console>
GMAIL_CLIENT_SECRET=<from Google Cloud Console>

# Outlook (defaults built into outlook_client.py — only OUTLOOK_EMAIL is required)
OUTLOOK_CLIENT_ID=9e5f94bc-e8a4-4e73-b8be-63364c29d753  # Thunderbird public client
OUTLOOK_TENANT_ID=consumers
OUTLOOK_EMAIL=toto_makus@hotmail.com

# Email delivery (for daily digest emails)
NOTIFY_EMAIL=totomakus@gmail.com
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=totomakus@gmail.com
SMTP_PASSWORD=<gmail-app-password>  # See note below
SMTP_FROM=totomakus@gmail.com
```

**Gmail App Password Note:**
Gmail SMTP requires an app-specific password (not your regular Gmail password).
- Go to [myaccount.google.com/security](https://myaccount.google.com/security)
- Two-Step Verification → App passwords
- Generate one for "Mail / Other"
- Copy and paste into `SMTP_PASSWORD`

---

## CLI Usage

### File Organizer
```bash
# Scan default directories (Desktop, Downloads, Documents, etc.)
python -m agents.file_organizer_agent

# Scan specific directories
python -m agents.file_organizer_agent --dirs ~/Desktop ~/Downloads --no-email

# Generate report only, no email
python -m agents.file_organizer_agent --no-email
```

### Email Organizer
```bash
# Run both Gmail and Outlook
python -m agents.email_organizer_agent

# Gmail only
python -m agents.email_organizer_agent --gmail-only

# Outlook only
python -m agents.email_organizer_agent --outlook-only

# Dry run (classify, no label/move operations)
python -m agents.email_organizer_agent --dry-run

# No email digest
python -m agents.email_organizer_agent --no-email
```

---

## Scheduling — Local Cron (chosen over Railway)

Both agents run daily via the Mac's crontab (system clock = Bangkok time):

```
0 8 * * *  → email organizer (Gmail + Outlook)   → logs/email_organizer_cron.log
0 9 * * *  → file organizer (Desktop + Downloads) → logs/file_organizer_cron.log
```

View/edit with `crontab -l` / `crontab -e`. Railway was skipped because it
bills per usage and the file organizer must scan the local filesystem anyway.

**macOS permission note:** if `logs/file_organizer_cron.log` shows permission
errors for Desktop/Downloads, grant Full Disk Access to `/usr/sbin/cron` in
System Settings → Privacy & Security → Full Disk Access.

The full 6-directory scan (incl. Documents/Pictures/Movies/Music) takes hours
due to MD5 hashing — run it manually when wanted:
`python3 -m agents.file_organizer_agent`

---

## File Structure

```
agents/
├── __init__.py                  # Package marker
├── email_organizer_agent.py     # Email agent CLI
└── file_organizer_agent.py      # File agent CLI

gmail_client.py                  # Gmail API wrapper (OAuth2)
outlook_client.py                # Outlook/Microsoft Graph wrapper (MSAL)
email_organizer.py               # Email classification engine
file_organizer.py                # File scanning & dedup logic
report_mailer.py                 # SMTP email sender
file_report_generator.py         # Report formatting helpers

reports/                          # Daily JSON reports (local output)
railway.toml                      # Cron schedule config for Railway
```

---

## Report Formats

### File Organizer Report (`reports/file_organizer_YYYY-MM-DD.json`)
```json
{
  "run_at": "ISO8601 timestamp",
  "scan_dirs": ["~/Desktop", "~/Downloads", ...],
  "total_files": 1562,
  "total_size_bytes": 2890000000,
  "by_category": {
    "Media": 1276,
    "Documents": 30,
    "Projects": 207,
    "Finance": 18
  },
  "duplicate_groups": [
    {
      "group_key": "md5hash",
      "files": ["/path/to/file1", "/path/to/file2"],
      "size_bytes": 102400,
      "wasted_bytes": 102400
    }
  ],
  "total_duplicate_wasted_bytes": 7738362,
  "pending_approval": true
}
```

### Email Organizer Report (`reports/email_organizer_YYYY-MM-DD.json`)
```json
{
  "run_at": "ISO8601 timestamp",
  "total_processed": 14,
  "archived": 5,
  "labeled": {
    "Work": 4,
    "Finance": 2,
    "Invoices": 1,
    "Personal": 1,
    "Receipts": 1
  },
  "emails": [
    {
      "msg_id": "...",
      "provider": "gmail",
      "subject": "Invoice #1042",
      "sender": "billing@acme.com",
      "category": "Invoices",
      "action": "label_and_move",
      "is_important": true,
      "reason": "Subject matched keyword 'invoice'"
    }
  ],
  "errors": []
}
```

---

## Troubleshooting

### "gmail_credentials.json not found"
- Download from Google Cloud Console (step 1 of Gmail setup above)
- Place in repo root: `/Users/toto/Claude TubeonAI/gmail_credentials.json`

### "OUTLOOK_CLIENT_ID not found"
- Set in `.env` file and reload with `python -c "from dotenv import load_dotenv; load_dotenv()"`
- Or set as Railway environment variable if deploying to production

### No emails are being processed
- Check that unread emails exist in your inbox
- Run with `--dry-run` to see classification output without applying actions
- Check logs for errors: `tail -f *.log` (if logging to file)

### Emails are classified incorrectly
- Email classification uses keyword matching in subject + snippet
- Edit `CATEGORY_KEYWORDS` and `MARKETING_KEYWORDS` in `email_organizer.py`
- Re-run: `python -m agents.email_organizer_agent --dry-run` to test changes

### Duplicate detection is slow
- Hashing large files (>500 MB) is skipped by design
- Two-pass dedup (filename+size → MD5) is more efficient than hashing everything
- To speed up scanning, use `--dirs` to scan fewer directories

---

## Next Steps

1. **Try the File Organizer first** (no OAuth needed):
   ```bash
   python -m agents.file_organizer_agent --dirs ~/Desktop --no-email
   ```

2. **Set up Gmail OAuth** (follow Gmail setup above)

3. **Test Email Organizer with Gmail**:
   ```bash
   python -m agents.email_organizer_agent --gmail-only --dry-run
   ```

4. **(Optional) Set up Outlook** if you have an Outlook/Microsoft account

5. **Deploy to Railway**:
   - Set all env vars in Railway dashboard
   - Set `GMAIL_CREDENTIALS_B64`, `GMAIL_TOKEN_B64`, `OUTLOOK_TOKEN_B64`
   - Redeploy → agents run automatically every day

---

## Questions?

Check the plan file for architecture details:
- `/Users/toto/.claude/plans/atomic-hatching-quasar.md`

All code follows the existing project patterns:
- Client classes: `encharge_client.py`, `tubeonai_client.py`
- Logging: `import logging; logger = logging.getLogger(__name__)`
- Env vars: `from dotenv import load_dotenv; load_dotenv()`
