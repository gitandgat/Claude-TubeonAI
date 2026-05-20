"""
FastAPI handler for 7-Day IMG Pivot Challenge email capture.
Integrates landing page form with Encharge subscription and sequence routing.

Add this to your existing FastAPI server or deploy as a standalone service.
"""
from __future__ import annotations
import os, httpx, json
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr

ENCHARGE_KEY = os.getenv("ENCHARGE_API_KEY")
ENCHARGE_BASE = "https://api.encharge.io/v1"
HDR = {"X-Encharge-Token": ENCHARGE_KEY, "Content-Type": "application/json"}

app = FastAPI()


class SubscribeRequest(BaseModel):
    firstName: str
    email: EmailStr
    tag: str = "challenge-joined"
    source: str = "pivot-challenge-landing"


class EnchargeContact:
    """Encharge contact management."""

    @staticmethod
    async def create_or_update(email: str, first_name: str, tags: list[str] | None = None) -> dict:
        """Create or update a contact in Encharge."""
        body = {
            "email": email,
            "firstName": first_name,
            "tags": tags or [],
            "customFields": {
                "source": "pivot-challenge-landing",
                "joinedAt": datetime.now().isoformat(),
            },
        }

        async with httpx.AsyncClient() as client:
            # Try to create; Encharge will update if exists
            r = await client.post(
                f"{ENCHARGE_BASE}/contacts",
                headers=HDR,
                json=body,
            )

            if r.status_code not in (200, 201):
                raise Exception(f"Encharge API error: {r.status_code} {r.text}")

            return r.json()

    @staticmethod
    async def add_tag(email: str, tag: str) -> dict:
        """Add a tag to an existing contact."""
        body = {"tag": tag}

        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{ENCHARGE_BASE}/contacts/{email}/tags",
                headers=HDR,
                json=body,
            )

            if r.status_code not in (200, 201):
                raise Exception(f"Failed to add tag: {r.status_code} {r.text}")

            return r.json()


@app.post("/api/encharge/subscribe")
async def subscribe_to_challenge(req: SubscribeRequest) -> dict:
    """
    Subscribe user to the 7-Day IMG Pivot Challenge.

    Steps:
    1. Create/update contact in Encharge
    2. Add 'challenge-joined' tag (triggers sequence)
    3. Return success with sequence info
    """
    try:
        # 1. Create or update contact
        contact = await EnchargeContact.create_or_update(
            email=req.email,
            first_name=req.firstName,
            tags=[req.tag],
        )

        contact_id = contact.get("id") or contact.get("email")

        return {
            "success": True,
            "message": f"Welcome {req.firstName}! Check your email for Day 1 of the challenge.",
            "contact_id": contact_id,
            "email": req.email,
            "sequence": "7-Day IMG Pivot Challenge",
            "first_email_delay_minutes": 5,
            "subsequent_emails_daily": True,
            "timezone": "America/New_York",
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/encharge/quiz-result")
async def handle_quiz_result(data: dict) -> dict:
    """
    Handle Fear Audit quiz results (from fear-audit.vercel.app).
    Tags user based on stage and routes to appropriate email sequence.
    """
    try:
        email = data.get("email")
        stage = data.get("stage")  # quiz-stage-start, quiz-stage-stop, quiz-stage-elder, quiz-stage-human

        if not email or not stage:
            raise ValueError("Missing email or stage")

        # Tag the user with their quiz result
        await EnchargeContact.add_tag(email, stage)

        # Optional: Add additional tags based on stage
        if stage == "quiz-stage-stop":
            await EnchargeContact.add_tag(email, "high-intent")
        elif stage == "quiz-stage-elder":
            await EnchargeContact.add_tag(email, "ready-to-pivot")

        return {
            "success": True,
            "email": email,
            "stage": stage,
            "tagged": True,
            "next_sequence": "post-quiz-nurture",
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/health")
async def health() -> dict:
    """Health check endpoint."""
    return {
        "status": "ok",
        "service": "encharge-pivot-handler",
        "routes": [
            "POST /api/encharge/subscribe",
            "POST /api/encharge/quiz-result",
            "GET /api/health",
        ],
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info",
    )
