"""Make the agent's modules importable from tests/ and keep the suite offline.

Every test here is pure-logic or fixture-driven: no test makes a network call,
writes into the repo's real data files, or invokes Ollama. The two guards that
enforce that live here — the sys.path insert, and a placeholder for the SMTP
password so importing anything that reaches email_sender never touches .env.
"""

import os
import sys
from pathlib import Path

AGENT_DIR = Path(__file__).resolve().parent.parent
if str(AGENT_DIR) not in sys.path:
    sys.path.insert(0, str(AGENT_DIR))

# email_sender reads this at import time. setdefault, never overwrite: a real
# value in the environment stays untouched, and .env is never read by tests.
os.environ.setdefault("GMAIL_APP_PASSWORD", "unused-offline")
