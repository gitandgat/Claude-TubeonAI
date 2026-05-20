import time
import requests


BASE_URL = "https://app.tubeonai.com/api/developer/v1"
POLL_INTERVAL = 5  # seconds between progress checks


class TubeonAIClient:
    def __init__(self, api_key: str):
        self.session = requests.Session()
        self.session.headers.update({"Authorization": f"Bearer {api_key}"})

    # ── Summaries ─────────────────────────────────────────────────────────────

    def create_summary(self, youtube_url: str) -> dict:
        resp = self.session.post(
            f"{BASE_URL}/summaries",
            json={"url": youtube_url, "type": "youtube"},
        )
        resp.raise_for_status()
        return resp.json()

    def wait_for_summary(self, summary_id: str) -> dict:
        print(f"  Waiting for summary {summary_id}...")
        while True:
            resp = self.session.get(f"{BASE_URL}/summaries/{summary_id}/progress")
            resp.raise_for_status()
            data = resp.json()["data"]

            status = data["status"]
            pct = data.get("progress", {}).get("percentage", 0)
            msg = data.get("progress", {}).get("message", status)
            print(f"  [{pct}%] {msg}")

            if status == "completed":
                return self.get_summary(summary_id)
            if status == "failed":
                raise RuntimeError(f"Summary failed for {summary_id}")

            time.sleep(POLL_INTERVAL)

    def get_summary(self, summary_id: str) -> dict:
        resp = self.session.get(f"{BASE_URL}/summaries/{summary_id}")
        resp.raise_for_status()
        return resp.json()

    # ── Prompts ───────────────────────────────────────────────────────────────

    def create_prompt(self, title: str, prompt: str) -> str:
        """Create a saved prompt and return its ID."""
        resp = self.session.post(
            f"{BASE_URL}/prompts",
            json={"title": title, "prompt": prompt},
        )
        resp.raise_for_status()
        return resp.json()["data"]["id"]

    def list_prompts(self) -> list:
        resp = self.session.get(f"{BASE_URL}/prompts", params={"limit": 100})
        resp.raise_for_status()
        return resp.json()["data"]

    # ── Repurpose ─────────────────────────────────────────────────────────────

    def create_repurpose(self, summary_id: str, prompt_id: str, fmt: str = "custom") -> dict:
        resp = self.session.post(
            f"{BASE_URL}/repurpose",
            json={"summary_id": summary_id, "prompt_id": prompt_id, "format": fmt},
        )
        resp.raise_for_status()
        return resp.json()

    def wait_for_repurpose(self, check_status_url: str) -> str:
        print(f"  Polling repurpose status...")
        while True:
            resp = self.session.get(check_status_url)
            resp.raise_for_status()
            data = resp.json()["data"]

            status = data["status"]
            print(f"  Status: {status}")

            if status == "completed":
                return data["content"]
            if status == "failed":
                raise RuntimeError(f"Repurpose failed: {check_status_url}")

            time.sleep(POLL_INTERVAL)
