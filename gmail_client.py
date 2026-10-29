"""
Gmail API Client — OAuth2-based wrapper for Gmail operations
"""
import os
import logging
from pathlib import Path
from typing import Optional, List, Dict
from dotenv import load_dotenv

from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from google.oauth2.credentials import Credentials as UserCredentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth import default
from googleapiclient.discovery import build
import base64

load_dotenv()
logger = logging.getLogger(__name__)

SCOPES = ["https://www.googleapis.com/auth/gmail.modify"]
CREDENTIALS_FILE = Path("gmail_credentials.json")
TOKEN_FILE = Path("gmail_token.json")


class GmailClient:
    def __init__(
        self,
        credentials_file: Path = CREDENTIALS_FILE,
        token_file: Path = TOKEN_FILE,
    ) -> None:
        """
        Authenticates via OAuth2 (browser flow on first run).
        credentials_file: downloaded from Google Cloud Console
        token_file: auto-written after first auth; auto-refreshed thereafter
        """
        self._service = None
        self.credentials_file = Path(credentials_file)
        self.token_file = Path(token_file)

    def _get_service(self):
        """Build and cache the Gmail service object."""
        if self._service:
            return self._service

        creds = None

        # Handle token file from env var (Railway)
        token_b64_env = os.getenv("GMAIL_TOKEN_B64")
        if token_b64_env and not self.token_file.exists():
            try:
                token_content = base64.b64decode(token_b64_env)
                self.token_file.write_bytes(token_content)
                logger.info("Loaded GMAIL_TOKEN_B64 from environment")
            except Exception as e:
                logger.warning(f"Failed to decode GMAIL_TOKEN_B64: {str(e)}")

        # Handle credentials file from env var (Railway)
        creds_b64_env = os.getenv("GMAIL_CREDENTIALS_B64")
        if creds_b64_env and not self.credentials_file.exists():
            try:
                creds_content = base64.b64decode(creds_b64_env)
                self.credentials_file.write_bytes(creds_content)
                logger.info("Loaded GMAIL_CREDENTIALS_B64 from environment")
            except Exception as e:
                logger.warning(
                    f"Failed to decode GMAIL_CREDENTIALS_B64: {str(e)}"
                )

        # Try to load existing token
        if self.token_file.exists():
            try:
                creds = UserCredentials.from_authorized_user_file(
                    str(self.token_file), SCOPES
                )
                logger.info("Loaded cached Gmail token")
            except Exception as e:
                logger.warning(f"Failed to load cached token: {str(e)}")
                creds = None

        # Refresh token if needed
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                logger.info("Refreshed Gmail token")
            except Exception as e:
                logger.warning(f"Failed to refresh token: {str(e)}")
                creds = None

        # If no valid creds, run OAuth flow
        if not creds:
            if not self.credentials_file.exists():
                raise FileNotFoundError(
                    f"Gmail credentials file not found: {self.credentials_file}. "
                    "Download from Google Cloud Console and place in repo root."
                )

            try:
                flow = InstalledAppFlow.from_client_secrets_file(
                    str(self.credentials_file), SCOPES
                )
                creds = flow.run_local_server(port=0)
                logger.info("Completed Gmail OAuth flow")
            except Exception as e:
                logger.error(f"OAuth flow failed: {str(e)}")
                raise

        # Save token for next time
        try:
            creds_dict = {
                "token": creds.token,
                "refresh_token": creds.refresh_token,
                "token_uri": creds.token_uri,
                "client_id": creds.client_id,
                "client_secret": creds.client_secret,
                "scopes": creds.scopes,
            }
            import json

            self.token_file.write_text(json.dumps(creds_dict))
            logger.debug(f"Saved Gmail token to {self.token_file}")
        except Exception as e:
            logger.warning(f"Failed to save token: {str(e)}")

        self._service = build("gmail", "v1", credentials=creds)
        return self._service

    def _get_or_create_label(self, label_name: str) -> str:
        """
        Return the label ID for label_name.
        Creates the label if it does not exist.
        Returns: label_id (str)
        """
        try:
            service = self._get_service()
            results = service.users().labels().list(userId="me").execute()
            labels = results.get("labels", [])

            for label in labels:
                if label["name"] == label_name:
                    logger.debug(f"Found existing label: {label_name}")
                    return label["id"]

            logger.info(f"Creating new label: {label_name}")
            label_body = {"name": label_name, "labelListVisibility": "labelShow"}
            created = (
                service.users()
                .labels()
                .create(userId="me", body=label_body)
                .execute()
            )
            return created["id"]

        except Exception as e:
            logger.error(f"Failed to get/create label {label_name}: {str(e)}")
            raise

    def list_unread(self, max_results: int = 100) -> List[Dict]:
        """
        List unread messages in INBOX.
        Returns list of dicts: [{id, threadId, subject, sender, snippet, labelIds}]
        """
        try:
            service = self._get_service()
            results = (
                service.users()
                .messages()
                .list(
                    userId="me",
                    q="is:unread",
                    maxResults=max_results,
                )
                .execute()
            )

            messages = results.get("messages", [])
            logger.info(f"Found {len(messages)} unread messages")

            detailed = []
            for msg in messages:
                try:
                    detail = self.get_message_detail(msg["id"])
                    detailed.append(detail)
                except Exception as e:
                    logger.warning(
                        f"Failed to get detail for message {msg['id']}: {str(e)}"
                    )

            return detailed

        except Exception as e:
            logger.error(f"Failed to list unread: {str(e)}")
            raise

    def get_message_detail(self, msg_id: str) -> Dict:
        """
        Fetch full headers (From, Subject, Date) for a single message.
        Returns: {id, subject, sender, date, snippet, labelIds}
        """
        try:
            service = self._get_service()
            msg = (
                service.users()
                .messages()
                .get(userId="me", id=msg_id, format="full")
                .execute()
            )

            headers = msg["payload"].get("headers", [])
            subject = next(
                (h["value"] for h in headers if h["name"] == "Subject"), ""
            )
            sender = next(
                (h["value"] for h in headers if h["name"] == "From"), ""
            )
            date = next(
                (h["value"] for h in headers if h["name"] == "Date"), ""
            )

            snippet = msg.get("snippet", "")
            label_ids = msg.get("labelIds", [])

            return {
                "id": msg_id,
                "threadId": msg.get("threadId", ""),
                "subject": subject,
                "sender": sender,
                "date": date,
                "snippet": snippet,
                "labelIds": label_ids,
            }

        except Exception as e:
            logger.error(f"Failed to get message detail {msg_id}: {str(e)}")
            raise

    def apply_label(self, msg_id: str, label_name: str) -> bool:
        """
        Apply label_name to msg_id. Creates label if missing.
        Returns: True on success
        """
        try:
            label_id = self._get_or_create_label(label_name)
            service = self._get_service()
            (
                service.users()
                .messages()
                .modify(
                    userId="me", id=msg_id, body={"addLabelIds": [label_id]}
                )
                .execute()
            )
            logger.debug(f"Applied label {label_name} to {msg_id}")
            return True

        except Exception as e:
            logger.error(
                f"Failed to apply label {label_name} to {msg_id}: {str(e)}"
            )
            return False

    def remove_inbox_label(self, msg_id: str) -> bool:
        """Remove INBOX label (effectively archives without marking as archived)."""
        try:
            service = self._get_service()
            (
                service.users()
                .messages()
                .modify(
                    userId="me", id=msg_id, body={"removeLabelIds": ["INBOX"]}
                )
                .execute()
            )
            logger.debug(f"Removed INBOX label from {msg_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to remove INBOX from {msg_id}: {str(e)}")
            return False

    def move_to_folder(self, msg_id: str, folder_label: str) -> bool:
        """
        In Gmail, 'folders' are labels.
        Applies folder_label, removes INBOX label.
        Returns: True on success
        """
        try:
            label_id = self._get_or_create_label(folder_label)
            service = self._get_service()
            (
                service.users()
                .messages()
                .modify(
                    userId="me",
                    id=msg_id,
                    body={
                        "addLabelIds": [label_id],
                        "removeLabelIds": ["INBOX"],
                    },
                )
                .execute()
            )
            logger.debug(f"Moved {msg_id} to {folder_label}")
            return True

        except Exception as e:
            logger.error(
                f"Failed to move {msg_id} to {folder_label}: {str(e)}"
            )
            return False

    def archive(self, msg_id: str, also_label: Optional[str] = None) -> bool:
        """
        Archive: remove INBOX label (and optionally apply a label first).
        Returns: True on success
        """
        try:
            service = self._get_service()
            body = {"removeLabelIds": ["INBOX"]}

            if also_label:
                label_id = self._get_or_create_label(also_label)
                body["addLabelIds"] = [label_id]

            (
                service.users()
                .messages()
                .modify(userId="me", id=msg_id, body=body)
                .execute()
            )
            logger.debug(f"Archived {msg_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to archive {msg_id}: {str(e)}")
            return False

    def batch_modify(
        self,
        msg_ids: List[str],
        add_labels: Optional[List[str]] = None,
        remove_labels: Optional[List[str]] = None,
    ) -> bool:
        """
        Batch-modify multiple messages in one API call (quota-efficient).
        add_labels/remove_labels: list of label names (not IDs — converts internally)
        Returns: True on success
        """
        try:
            if not msg_ids:
                return True

            service = self._get_service()
            add_label_ids = []
            remove_label_ids = []

            if add_labels:
                for label_name in add_labels:
                    label_id = self._get_or_create_label(label_name)
                    add_label_ids.append(label_id)

            # Convert remove_labels names to IDs
            if remove_labels:
                results = service.users().labels().list(userId="me").execute()
                labels = {
                    label["name"]: label["id"]
                    for label in results.get("labels", [])
                }
                for label_name in remove_labels:
                    if label_name in labels:
                        remove_label_ids.append(labels[label_name])
                    elif label_name == "INBOX":
                        remove_label_ids.append("INBOX")

            body = {}
            if add_label_ids:
                body["addLabelIds"] = add_label_ids
            if remove_label_ids:
                body["removeLabelIds"] = remove_label_ids

            (
                service.users()
                .messages()
                .batchModify(userId="me", body={"ids": msg_ids, **body})
                .execute()
            )

            logger.info(
                f"Batch modified {len(msg_ids)} messages (add: {add_labels or []}, remove: {remove_labels or []})"
            )
            return True

        except Exception as e:
            logger.error(f"Failed batch modify: {str(e)}")
            return False
