"""
Outlook/Hotmail SMTP sender — OAuth2 (XOAUTH2), for Sahawat.nil@outlook.com.

Microsoft permanently disabled Basic Authentication for SMTP AUTH on Outlook.com
(error: "535, 5.7.139 Authentication unsuccessful, basic authentication is
disabled") — this is why email_sender.py's old smtplib .login(email, app_password)
call has failed on every single application email. There is no password-based fix;
Modern Auth (OAuth2/XOAUTH2) is required even for personal accounts.

Same auth-code-with-PKCE approach as the repo-root outlook_client.py (which reads
IMAP for a different account, toto_makus@hotmail.com): sign in via Thunderbird's
public, MSA-enabled client ID against the `consumers` tenant, no Azure app
registration needed. Kept as its own module (not a shared import) because the two
callers need different OAuth scopes (IMAP.AccessAsUser.All vs SMTP.Send) and
outlook_client.py's SCOPES is a module-level constant, not per-instance.

One-time setup: python3 authorize_outlook_smtp.py
"""
import base64
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Optional

from msal import PublicClientApplication
from msal.token_cache import SerializableTokenCache

logger = logging.getLogger(__name__)

# Thunderbird's public client — MSA-enabled, auth-code flow allowed, no app registration needed.
CLIENT_ID = "9e5f94bc-e8a4-4e73-b8be-63364c29d753"
TENANT = "consumers"
REDIRECT_URI = "https://localhost"
SCOPES = ["https://outlook.office.com/SMTP.Send"]
SMTP_HOST = "smtp-mail.outlook.com"
SMTP_PORT = 587
SMTP_TIMEOUT_SEC = 30

TOKEN_FILE = Path(__file__).parent / "outlook_token_send.json"
AUTH_FLOW_FILE = Path(__file__).parent / ".outlook_send_auth_flow.json"


class OutlookOAuthSender:
    def __init__(self, token_file: Path = TOKEN_FILE, email: Optional[str] = None) -> None:
        self.token_file = Path(token_file)
        self.email = email
        self._app: Optional[PublicClientApplication] = None
        self._token_cache: Optional[SerializableTokenCache] = None

    def _get_token_cache(self) -> SerializableTokenCache:
        if self._token_cache is not None:
            return self._token_cache

        cache = SerializableTokenCache()
        if self.token_file.exists():
            try:
                cache.deserialize(self.token_file.read_text())
                logger.info("Loaded cached Outlook SMTP-send token")
            except Exception as e:
                logger.warning(f"Failed to load token cache: {str(e)}")

        self._token_cache = cache
        return cache

    def _get_msal_app(self) -> PublicClientApplication:
        if self._app:
            return self._app
        self._app = PublicClientApplication(
            client_id=CLIENT_ID,
            authority=f"https://login.microsoftonline.com/{TENANT}",
            token_cache=self._get_token_cache(),
        )
        return self._app

    def _save_cache(self) -> None:
        cache = self._get_token_cache()
        if cache.has_state_changed:
            self.token_file.write_text(cache.serialize())
            logger.debug(f"Saved Outlook SMTP-send token cache to {self.token_file}")

    def get_authorization_url(self) -> str:
        """Start an MSAL auth-code flow (with PKCE) and return the sign-in URL.
        Flow state is persisted so redeem_authorization_code() in a later
        process (after the browser round-trip) can complete it."""
        app = self._get_msal_app()
        flow = app.initiate_auth_code_flow(SCOPES, redirect_uri=REDIRECT_URI, prompt="select_account")
        AUTH_FLOW_FILE.write_text(__import__("json").dumps(flow))
        return flow["auth_uri"]

    def redeem_authorization_code(self, redirect_url: str) -> dict:
        """Step 2: exchange the pasted https://localhost/?code=... URL for tokens."""
        import json
        from urllib.parse import parse_qs, urlparse

        if not AUTH_FLOW_FILE.exists():
            raise Exception("No pending auth flow — run get_authorization_url() first.")
        flow = json.loads(AUTH_FLOW_FILE.read_text())

        parsed = urlparse(redirect_url)
        auth_response = {k: v[0] for k, v in parse_qs(parsed.query).items()}

        app = self._get_msal_app()
        result = app.acquire_token_by_auth_code_flow(flow, auth_response)
        if "access_token" not in result:
            raise Exception(f"Token exchange failed: {result.get('error_description', result)}")

        AUTH_FLOW_FILE.unlink(missing_ok=True)
        self._save_cache()

        username = (result.get("id_token_claims") or {}).get("preferred_username")
        logger.info(f"Outlook SMTP-send authorized for {username or 'account'}")
        return result

    def _get_access_token(self) -> str:
        """Acquire a token silently from cache (handles refresh automatically)."""
        app = self._get_msal_app()
        accounts = app.get_accounts(username=self.email) if self.email else app.get_accounts()
        if not accounts:
            raise Exception(
                "No Outlook account in the SMTP-send token cache. "
                "Run: python3 authorize_outlook_smtp.py"
            )
        if not self.email:
            self.email = accounts[0].get("username")

        result = app.acquire_token_silent(SCOPES, account=accounts[0])
        if not result or "access_token" not in result:
            raise Exception(
                "Silent token refresh failed — re-run: python3 authorize_outlook_smtp.py"
            )
        self._save_cache()
        return result["access_token"]

    def send_mail(self, from_addr: str, to_addr: str, msg: MIMEMultipart) -> None:
        """Send a fully-built MIME message via XOAUTH2 SMTP AUTH. Raises on failure."""
        token = self._get_access_token()
        auth_string = f"user={self.email or from_addr}\x01auth=Bearer {token}\x01\x01"

        s = smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=SMTP_TIMEOUT_SEC)
        try:
            s.ehlo()
            s.starttls()
            s.ehlo()
            code, resp = s.docmd("AUTH", "XOAUTH2 " + base64.b64encode(auth_string.encode()).decode())
            if code != 235:
                raise Exception(f"XOAUTH2 auth failed ({code}): {resp}")
            s.sendmail(from_addr, to_addr, msg.as_string())
        finally:
            s.quit()
