"""
Outlook / Hotmail Client — IMAP with OAuth2 (XOAUTH2)

Personal Microsoft accounts can no longer use device-code flow or register
Azure apps without a paid-verification signup, so this client authenticates
the same way Thunderbird does: authorization-code flow against the consumers
endpoint using Thunderbird's public client ID, then talks IMAP to
outlook.office365.com with XOAUTH2.

One-time setup: python3 authorize_outlook.py
"""
import os
import base64
import imaplib
import json
import logging
import re
from email import message_from_bytes
from email.header import decode_header
from email.utils import parseaddr
from pathlib import Path
from typing import Optional, List, Dict
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

from msal import PublicClientApplication
from msal.token_cache import SerializableTokenCache

load_dotenv()
logger = logging.getLogger(__name__)

# Thunderbird's current public client — MSA-enabled, auth-code flow allowed
DEFAULT_CLIENT_ID = "9e5f94bc-e8a4-4e73-b8be-63364c29d753"
DEFAULT_TENANT = "consumers"
REDIRECT_URI = "https://localhost"
SCOPES = ["https://outlook.office.com/IMAP.AccessAsUser.All"]
IMAP_HOST = "outlook.office365.com"
IMAP_PORT = 993
# Without a socket timeout a dropped connection blocks reads forever
IMAP_TIMEOUT = 60
TOKEN_FILE = Path("outlook_token.json")
AUTH_FLOW_FILE = Path(".outlook_auth_flow.json")


class OutlookClient:
    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        tenant_id: Optional[str] = None,
        token_file: Path = TOKEN_FILE,
        email: Optional[str] = None,
    ) -> None:
        """
        Auth: one-time authorization-code flow (authorize_outlook.py);
        afterwards tokens refresh silently from the MSAL cache in token_file.
        Pass email + token_file to support multiple accounts.
        """
        self.client_id = (
            client_id or os.getenv("OUTLOOK_CLIENT_ID") or DEFAULT_CLIENT_ID
        )
        self.tenant_id = (
            tenant_id or os.getenv("OUTLOOK_TENANT_ID") or DEFAULT_TENANT
        )
        self.email = email or os.getenv("OUTLOOK_EMAIL")
        self.token_file = Path(token_file)
        self._token_cache = None
        self._app = None
        self._imap = None

    # ------------------------------------------------------------------
    # OAuth2 / MSAL
    # ------------------------------------------------------------------

    def _get_token_cache(self) -> SerializableTokenCache:
        """Load or create token cache from file (or OUTLOOK_TOKEN_B64 on Railway)."""
        if self._token_cache:
            return self._token_cache

        cache = SerializableTokenCache()

        token_b64_env = os.getenv("OUTLOOK_TOKEN_B64")
        if token_b64_env and not self.token_file.exists():
            try:
                self.token_file.write_bytes(base64.b64decode(token_b64_env))
                logger.info("Loaded OUTLOOK_TOKEN_B64 from environment")
            except Exception as e:
                logger.warning(f"Failed to decode OUTLOOK_TOKEN_B64: {str(e)}")

        if self.token_file.exists():
            try:
                cache.deserialize(self.token_file.read_text())
                logger.info("Loaded cached Outlook token")
            except Exception as e:
                logger.warning(f"Failed to load token cache: {str(e)}")

        self._token_cache = cache
        return cache

    def _get_msal_app(self) -> PublicClientApplication:
        if self._app:
            return self._app

        self._app = PublicClientApplication(
            client_id=self.client_id,
            authority=f"https://login.microsoftonline.com/{self.tenant_id}",
            token_cache=self._get_token_cache(),
        )
        return self._app

    def _save_cache(self) -> None:
        cache = self._get_token_cache()
        if cache.has_state_changed:
            self.token_file.write_text(cache.serialize())
            logger.debug(f"Saved Outlook token cache to {self.token_file}")

    def get_authorization_url(self) -> str:
        """
        Start an MSAL auth-code flow (with PKCE) and return the sign-in URL.
        The flow state is persisted so redeem_authorization_code() in a later
        process can complete it with matching scopes/verifier.
        """
        app = self._get_msal_app()
        flow = app.initiate_auth_code_flow(
            SCOPES, redirect_uri=REDIRECT_URI, prompt="select_account"
        )
        if "auth_uri" not in flow:
            raise Exception(f"Failed to initiate auth flow: {flow}")

        AUTH_FLOW_FILE.write_text(json.dumps(flow))
        return flow["auth_uri"]

    def redeem_authorization_code(self, redirect_url: str) -> Dict:
        """
        Complete the auth-code flow started by get_authorization_url().
        Accepts the full https://localhost/?code=...&state=... URL copied
        from the browser address bar. Persists the token cache on success.
        """
        if not AUTH_FLOW_FILE.exists():
            raise Exception(
                "No pending auth flow — run authorize_outlook.py without "
                "arguments first to generate a sign-in URL"
            )
        flow = json.loads(AUTH_FLOW_FILE.read_text())

        qs = parse_qs(urlparse(redirect_url.strip()).query)
        auth_response = {k: v[0] for k, v in qs.items()}
        if "code" not in auth_response:
            raise ValueError(
                f"No ?code= parameter in URL. Got: {list(auth_response.keys())}"
            )

        app = self._get_msal_app()
        result = app.acquire_token_by_auth_code_flow(flow, auth_response)

        if not result or "access_token" not in result:
            raise Exception(
                f"Token exchange failed: {result.get('error_description') if result else 'no result'}"
            )

        self._save_cache()
        AUTH_FLOW_FILE.unlink(missing_ok=True)
        username = (result.get("id_token_claims") or {}).get(
            "preferred_username"
        )
        logger.info(f"Outlook authorized for {username or 'account'}")
        return result

    def _get_access_token(self) -> str:
        """Acquire token silently from cache (handles refresh automatically)."""
        app = self._get_msal_app()
        accounts = (
            app.get_accounts(username=self.email) if self.email else []
        ) or app.get_accounts()

        if not accounts:
            raise Exception(
                "No Outlook account in token cache. "
                "Run: python3 authorize_outlook.py"
            )

        if not self.email:
            self.email = accounts[0].get("username")

        result = app.acquire_token_silent(SCOPES, account=accounts[0])
        if not result or "access_token" not in result:
            raise Exception(
                "Silent token refresh failed — re-run: python3 authorize_outlook.py"
            )

        self._save_cache()
        return result["access_token"]

    # ------------------------------------------------------------------
    # IMAP
    # ------------------------------------------------------------------

    def _get_imap(self) -> imaplib.IMAP4_SSL:
        """Connect + authenticate via XOAUTH2 (cached per instance)."""
        if self._imap is not None:
            try:
                self._imap.noop()
                return self._imap
            except Exception:
                self._imap = None

        token = self._get_access_token()
        if not self.email:
            raise Exception(
                "OUTLOOK_EMAIL not set and no account username in cache"
            )

        auth_string = f"user={self.email}\x01auth=Bearer {token}\x01\x01"
        imap = imaplib.IMAP4_SSL(IMAP_HOST, IMAP_PORT, timeout=IMAP_TIMEOUT)
        imap.authenticate("XOAUTH2", lambda _: auth_string.encode())
        logger.info(f"IMAP authenticated as {self.email}")

        self._imap = imap
        return imap

    def close(self) -> None:
        if self._imap is not None:
            try:
                self._imap.logout()
            except Exception:
                pass
            self._imap = None

    @staticmethod
    def _decode_mime_header(value: str) -> str:
        """Decode RFC 2047 encoded header into plain text."""
        try:
            parts = decode_header(value)
            decoded = []
            for text, charset in parts:
                if isinstance(text, bytes):
                    decoded.append(
                        text.decode(charset or "utf-8", errors="replace")
                    )
                else:
                    decoded.append(text)
            return "".join(decoded)
        except Exception:
            return value

    def _ensure_folder(self, folder_name: str) -> str:
        """Create the IMAP folder if missing. Returns folder_name."""
        try:
            imap = self._get_imap()
            typ, data = imap.list()
            existing = []
            for line in data or []:
                if not line:
                    continue
                decoded = line.decode("utf-8", errors="replace")
                match = re.search(r' "?([^"]+)"?$', decoded)
                if match:
                    existing.append(match.group(1).strip('"'))

            if folder_name not in existing:
                logger.info(f"Creating new folder: {folder_name}")
                imap.create(f'"{folder_name}"')

            return folder_name

        except Exception as e:
            logger.error(f"Failed to get/create folder {folder_name}: {str(e)}")
            raise

    def list_unread(self, max_results: int = 100) -> List[Dict]:
        """
        List unread messages from Inbox.
        Returns list of dicts: [{id, subject, sender_email, received_at, body_preview}]
        """
        try:
            imap = self._get_imap()
            imap.select("INBOX")

            typ, data = imap.uid("SEARCH", None, "UNSEEN")
            if typ != "OK":
                raise Exception(f"IMAP SEARCH failed: {typ}")

            uids = (data[0] or b"").split()
            uids = uids[-max_results:]  # most recent N
            logger.info(f"Found {len(uids)} unread messages")

            result = []
            for uid in uids:
                uid_str = uid.decode()
                try:
                    typ, msg_data = imap.uid(
                        "FETCH",
                        uid_str,
                        "(BODY.PEEK[HEADER.FIELDS (SUBJECT FROM DATE)] BODY.PEEK[TEXT]<0.1024>)",
                    )
                    if typ != "OK":
                        logger.warning(f"FETCH failed for uid {uid_str}")
                        continue

                    headers_raw = b""
                    body_raw = b""
                    for part in msg_data:
                        if isinstance(part, tuple) and len(part) == 2:
                            descriptor = part[0].decode(
                                "utf-8", errors="replace"
                            )
                            if "HEADER" in descriptor:
                                headers_raw = part[1]
                            elif "TEXT" in descriptor:
                                body_raw = part[1]

                    msg = message_from_bytes(headers_raw)
                    subject = self._decode_mime_header(msg.get("Subject", ""))
                    sender_email = parseaddr(msg.get("From", ""))[1]
                    received_at = msg.get("Date", "")

                    preview = body_raw.decode("utf-8", errors="replace")
                    preview = re.sub(r"\s+", " ", preview).strip()[:500]

                    result.append(
                        {
                            "id": uid_str,
                            "subject": subject,
                            "sender_email": sender_email,
                            "received_at": received_at,
                            "body_preview": preview,
                        }
                    )

                except Exception as e:
                    logger.warning(
                        f"Failed to fetch message {uid_str}: {str(e)}"
                    )

            return result

        except Exception as e:
            logger.error(f"Failed to list unread: {str(e)}")
            raise

    def apply_category(self, msg_id: str, category: str) -> bool:
        """
        IMAP has no colour categories — the folder name itself carries the
        classification, so this is a logged no-op kept for interface parity.
        """
        logger.debug(
            f"apply_category({category}) skipped — IMAP uses folders instead"
        )
        return True

    def move_to_folder(self, msg_id: str, folder_name: str) -> bool:
        """
        Move message (by UID) from INBOX to named folder. Creates folder if missing.
        Returns: True on success
        """
        try:
            self._ensure_folder(folder_name)
            imap = self._get_imap()
            imap.select("INBOX")

            typ, _ = imap.uid("MOVE", msg_id, f'"{folder_name}"')
            if typ == "OK":
                logger.debug(f"Moved {msg_id} to folder {folder_name}")
                return True

            # Fallback for servers without MOVE: COPY + delete + expunge
            typ, _ = imap.uid("COPY", msg_id, f'"{folder_name}"')
            if typ != "OK":
                raise Exception(f"COPY failed: {typ}")
            imap.uid("STORE", msg_id, "+FLAGS", r"(\Deleted)")
            imap.expunge()
            logger.debug(f"Moved {msg_id} to {folder_name} (via COPY)")
            return True

        except Exception as e:
            logger.error(
                f"Failed to move {msg_id} to {folder_name}: {str(e)}"
            )
            return False

    def archive(
        self, msg_id: str, also_category: Optional[str] = None
    ) -> bool:
        """
        Move message to Archive folder.
        Returns: True on success
        """
        try:
            if also_category:
                self.apply_category(msg_id, also_category)

            return self.move_to_folder(msg_id, "Archive")

        except Exception as e:
            logger.error(f"Failed to archive {msg_id}: {str(e)}")
            return False
