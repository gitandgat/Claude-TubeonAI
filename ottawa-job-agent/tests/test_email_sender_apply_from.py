"""Applications moved from Sahawat.nil@outlook.com to Sahawat.nil@gmail.com.

The draft has to land in the job-search Gmail (so it already sends from that
address) once its app password is configured, and keep landing in the digest
account until then, so the switch can never silently stop drafts.
"""

import email
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import email_sender


class FakeIMAP:
    instances = []

    def __init__(self, host):
        self.host = host
        self.login_as = None
        self.appended = []
        FakeIMAP.instances.append(self)

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    def login(self, user, password):
        self.login_as = (user, password)

    def append(self, mailbox, flags, when, raw):
        self.appended.append((mailbox, email.message_from_bytes(raw)))


JOB = {"apply_email": "jobs@example.com", "title": "Team Member", "company": "Example"}


def _draft(monkeypatch, **env):
    FakeIMAP.instances.clear()
    monkeypatch.setattr(email_sender.imaplib, "IMAP4_SSL", FakeIMAP)
    monkeypatch.setenv("GMAIL_APP_PASSWORD", "digest-pw")
    if "APPLY_GMAIL_APP_PASSWORD" in env:
        monkeypatch.setenv("APPLY_GMAIL_APP_PASSWORD", env["APPLY_GMAIL_APP_PASSWORD"])
    else:
        monkeypatch.delenv("APPLY_GMAIL_APP_PASSWORD", raising=False)
    ok = email_sender.draft_application(JOB, "Dear team,", "", "Application")
    return ok, FakeIMAP.instances[-1]


def test_apply_from_is_the_job_search_gmail():
    assert email_sender.APPLY_FROM.lower() == "sahawat.nil@gmail.com"


def test_draft_lands_in_job_search_gmail_when_configured(monkeypatch):
    ok, imap = _draft(monkeypatch, APPLY_GMAIL_APP_PASSWORD="apply-pw")
    assert ok
    assert imap.login_as == ("Sahawat.nil@gmail.com", "apply-pw")
    mailbox, msg = imap.appended[0]
    assert mailbox == "[Gmail]/Drafts"
    assert "Sahawat.nil@gmail.com" in msg["From"]
    assert msg["To"] == "jobs@example.com"


def test_falls_back_to_digest_account_until_configured(monkeypatch):
    ok, imap = _draft(monkeypatch)
    assert ok
    assert imap.login_as == (email_sender.NOTIFY_FROM, "digest-pw")
    _, msg = imap.appended[0]
    # No From header: Gmail would rewrite or reject a foreign address in this account.
    assert msg["From"] is None


def test_signature_shows_gmail_not_outlook(monkeypatch):
    _, imap = _draft(monkeypatch, APPLY_GMAIL_APP_PASSWORD="apply-pw")
    _, msg = imap.appended[0]
    body = next(p for p in msg.walk() if p.get_content_type() == "text/plain").get_payload(decode=True).decode()
    assert "Sahawat.nil@gmail.com" in body
    assert "outlook" not in body.lower()
