"""Thin wrapper around the Serper.dev Google Search API (google.serper.dev).

Free-tier replacement for Claude's hosted web_search tool in job_sources.py:
2,500 free queries with no card on file, then cheap prepaid credits after.
Unlike Claude's web_search, Serper only returns SERP snippets (title/link/
snippet) — it never fetches and reads the full posting page — so
job_sources.py still needs a separate structuring step (the local Ollama
model) to turn these snippets into the job schema downstream code expects.
"""

import requests

SERPER_ENDPOINT = "https://google.serper.dev/search"


class SerperCreditsExhausted(Exception):
    """Raised when Serper reports the account is out of query credits — a
    distinct signal from a generic network/API error, so the caller can stop
    hitting the API for the rest of the run and surface a clear alert instead
    of quietly returning empty results for every remaining category."""


class SerperClient:
    def __init__(self, api_key: str):
        self.api_key = api_key

    def search(self, query: str, num: int = 10, gl: str = "ca") -> list:
        """Run one Google search via Serper. Returns the raw 'organic' results
        (each with title/link/snippet, sometimes date), or [] on a transient
        error. Raises SerperCreditsExhausted if the account is out of credits."""
        try:
            r = requests.post(
                SERPER_ENDPOINT,
                headers={"X-API-KEY": self.api_key, "Content-Type": "application/json"},
                json={"q": query, "num": num, "gl": gl},
                timeout=30,
            )
        except requests.exceptions.RequestException as e:
            print(f"[serper_client] Network error: {e}")
            return []

        if r.status_code in (401, 402, 403):
            body = (r.text or "").lower()
            if any(w in body for w in ("credit", "quota", "insufficient", "payment")):
                raise SerperCreditsExhausted(
                    f"Serper API out of credits (HTTP {r.status_code}): {r.text[:200]}"
                )
            print(f"[serper_client] Auth/permission error (HTTP {r.status_code}): {r.text[:200]}")
            return []

        try:
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            print(f"[serper_client] Search error: {e}")
            return []

        return r.json().get("organic", [])
