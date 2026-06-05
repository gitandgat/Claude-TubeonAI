import requests


BASE_URL = "https://api.encharge.io/v1"


class EnchargeClient:
    def __init__(self, api_key: str):
        self.session = requests.Session()
        self.session.headers.update({"X-Encharge-Token": api_key})

    def add_subscriber(self, email: str, name: str = "", tags=None) -> dict:
        """Add or update a subscriber in Encharge."""
        payload = {"email": email}
        if name:
            payload["name"] = name
        if tags:
            # Convert tags list to comma-separated string for Encharge API
            if isinstance(tags, list):
                payload["tags"] = ", ".join(tags)
            else:
                payload["tags"] = tags

        resp = self.session.post(f"{BASE_URL}/people", json={"person": payload})
        resp.raise_for_status()
        return resp.json()

    def create_fields(self, fields: list) -> dict:
        """Create custom person fields in Encharge."""
        resp = self.session.post(f"{BASE_URL}/fields", json=fields)
        resp.raise_for_status()
        return resp.json()

    def get_fields(self) -> list:
        """Get all existing person fields."""
        resp = self.session.get(f"{BASE_URL}/fields")
        resp.raise_for_status()
        return resp.json()

    def add_tag(self, tag: str, email: str = "", contact_id: str = "") -> dict:
        """Add a tag to a person by email or contact ID."""
        payload = {"tag": tag}
        if contact_id:
            payload["id"] = contact_id
        elif email:
            payload["email"] = email
        else:
            raise ValueError("Must provide either email or contact_id")

        resp = self.session.post(f"{BASE_URL}/tags", json=payload)
        resp.raise_for_status()
        # Tags endpoint returns plain text "Created", not JSON
        return {"status": resp.status_code, "message": resp.text}

    def add_quiz_result(self, email: str, first_name: str, stage: str, score: float) -> dict:
        """
        Add a quiz subscriber with their Burnout Crosswalk Assessment results.
        Sets custom fields and applies the appropriate stage tag to trigger
        the matching flow in Encharge.

        Stage values: 'start', 'stop', 'elder', 'human'
        Score: float between 1.0 and 4.0
        """
        # Stage display names for the tag
        stage_tags = {
            "start": "quiz-stage-start",
            "stop":  "quiz-stage-stop",
            "elder": "quiz-stage-elder",
            "human": "quiz-stage-human",
        }
        tag = stage_tags.get(stage.lower(), f"quiz-stage-{stage.lower()}")

        # Upsert the person with quiz fields
        payload = {
            "email": email,
            "firstName": first_name,
            "quizStage": stage.capitalize(),
            "quizScore": str(round(score, 2)),
            "tags": f"quiz-completed, {tag}",
        }
        resp = self.session.post(f"{BASE_URL}/people", json={"person": payload})
        resp.raise_for_status()
        return resp.json()
