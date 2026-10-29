"""
Generic IMAP Client — plain password login (SSL)

For providers without OAuth requirements (e.g. Namecheap PrivateEmail).
Reuses all IMAP mailbox logic from OutlookClient (list_unread,
move_to_folder, archive, _ensure_folder); only authentication differs.
"""
import imaplib
import logging
import os
from typing import Optional

from dotenv import load_dotenv

from keychain_secrets import get_secret
from outlook_client import OutlookClient

load_dotenv()
logger = logging.getLogger(__name__)


class ImapClient(OutlookClient):
    def __init__(
        self,
        host: str,
        email: str,
        password_env: str = "IMAP_PASSWORD",
        port: int = 993,
        password: Optional[str] = None,
    ) -> None:
        """
        password is read from the env var named by password_env —
        never store it in code or config files.
        """
        self.host = host
        self.port = port
        self.email = email
        self.password = password or get_secret(password_env)
        self._imap = None

        if not self.password:
            raise ValueError(
                f"IMAP password for {email} not found — set {password_env} in .env"
            )

    def _get_imap(self) -> imaplib.IMAP4_SSL:
        """Connect + plain LOGIN (cached per instance)."""
        if self._imap is not None:
            try:
                self._imap.noop()
                return self._imap
            except Exception:
                self._imap = None

        imap = imaplib.IMAP4_SSL(self.host, self.port, timeout=60)
        imap.login(self.email, self.password)
        logger.info(f"IMAP authenticated as {self.email} ({self.host})")

        self._imap = imap
        return imap
