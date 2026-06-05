"""
Crosswalk Wisdom Quiz Webhook Server
=====================================
Receives quiz results from the Burnout Crosswalk Assessment
and adds the subscriber to Encharge with their stage tag.
Also handles IMG Pivot Challenge lead magnet form submissions.

Deploy to Railway:
  1. Push this repo to GitHub
  2. railway.app → New Project → Deploy from GitHub
  3. Set environment variable: ENCHARGE_API_KEY=your_key
  4. Railway gives you: https://your-app.up.railway.app

Endpoints:
  POST /quiz-results — Fear Audit quiz results
  POST /api/encharge/subscribe — IMG Pivot Challenge landing page form
  POST /api/encharge/quiz-result — Alias for /quiz-results
  GET /health — Health check

Local dev:
  pip install -r requirements.txt
  python webhook_server.py
"""

import os
import logging
from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr
from typing import Optional, List

from encharge_client import EnchargeClient
from pdf_generator import generate_personalized_html

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Crosswalk Wisdom Webhook")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tighten to your quiz domain after deployment
    allow_methods=["POST", "OPTIONS"],
    allow_headers=["*"],
)


class QuizResult(BaseModel):
    email: EmailStr
    firstName: str
    stage: str          # "start" | "stop" | "elder" | "human"
    score: float        # 1.0 – 4.0
    answers: Optional[List[int]] = None


class ChallengeSignup(BaseModel):
    firstName: str
    email: EmailStr


class FearAuditResult(BaseModel):
    email: EmailStr
    firstName: str
    primaryFear: str    # "financial" | "identity" | "judgment" | "failure" | "grief"
    allAnswers: List[int]
    source: str
    completedAt: str
    tag: str


@app.post("/api/encharge/subscribe")
async def encharge_subscribe(request_data: dict):
    """
    Handle both Fear Audit results and IMG Pivot Challenge signups.
    Routes based on presence of 'primaryFear' field.
    """
    api_key = os.getenv("ENCHARGE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="ENCHARGE_API_KEY not configured")

    # Check if this is a Fear Audit result (has primaryFear field)
    if "primaryFear" in request_data:
        return await handle_fear_audit_result(request_data, api_key)
    else:
        return await handle_challenge_signup(request_data, api_key)


async def handle_fear_audit_result(data: dict, api_key: str) -> dict:
    """Handle Fear Audit quiz results from fear-audit-landing.html."""
    try:
        result = FearAuditResult(**data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid Fear Audit data: {str(e)}")

    logger.info(f"Fear Audit result: {result.email} → fear={result.primaryFear}")

    # Validate fear type
    valid_fears = {"financial", "identity", "judgment", "failure", "grief"}
    fear = result.primaryFear.lower()
    if fear not in valid_fears:
        raise HTTPException(status_code=400, detail=f"Invalid fear type: {result.primaryFear}")

    client = EnchargeClient(api_key)
    client.add_subscriber(
        email=result.email,
        name=result.firstName,
        tags=[f"fear-{fear}", "fear-audit-completed"],
    )

    logger.info(f"Encharge: {result.email} tagged fear-{fear}, enrolled in fear-specific nurture sequence")
    return {
        "success": True,
        "message": f"✓ Check your email for your personalized Fear Report, {result.firstName}!",
        "contact_id": result.email,
        "email": result.email,
        "fear_type": fear,
        "sequence": f"{fear.capitalize()} Fear Nurture Sequence",
        "first_email_delay_minutes": 5,
    }


async def handle_challenge_signup(data: dict, api_key: str) -> dict:
    """Handle IMG Pivot Challenge landing page form submission."""
    try:
        signup = ChallengeSignup(**data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid Challenge signup data: {str(e)}")

    logger.info(f"IMG Pivot Challenge signup: {signup.email} ({signup.firstName})")

    client = EnchargeClient(api_key)
    client.add_subscriber(
        email=signup.email,
        name=signup.firstName,
        tags=["challenge-joined"],
    )

    logger.info(f"Encharge: {signup.email} tagged challenge-joined, enrolled in 7-Day IMG Pivot Challenge")
    return {
        "success": True,
        "message": f"Welcome {signup.firstName}! Check your email for Day 1 of the challenge.",
        "contact_id": signup.email,
        "email": signup.email,
        "sequence": "7-Day IMG Pivot Challenge",
        "first_email_delay_minutes": 5,
    }


@app.post("/quiz-results")
async def receive_quiz_result(result: QuizResult):
    """Receive a quiz submission and trigger the matching Encharge email flow."""
    api_key = os.getenv("ENCHARGE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="ENCHARGE_API_KEY not configured")

    stage = result.stage.lower()
    if stage not in {"start", "stop", "elder", "human"}:
        raise HTTPException(status_code=400, detail=f"Invalid stage: {result.stage}")

    logger.info(f"Quiz result: {result.email} → stage={stage}, score={result.score}")

    client = EnchargeClient(api_key)
    client.add_quiz_result(
        email=result.email,
        first_name=result.firstName,
        stage=stage,
        score=result.score,
    )

    logger.info(f"Encharge updated: {result.email} tagged quiz-stage-{stage}")
    return {"status": "ok", "stage": stage}


@app.post("/api/encharge/quiz-result")
async def quiz_result_alias(result: QuizResult):
    """Alias for /quiz-results for API consistency."""
    return await receive_quiz_result(result)


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("webhook_server:app", host="0.0.0.0", port=8000, reload=True)


# ═════════════════════════════════════════════════════════════════
# SUNK COST TRACKER ENDPOINT
# ═════════════════════════════════════════════════════════════════

class SunkCostTrackerResult(BaseModel):
    email: EmailStr
    score: int                  # 0-100
    years_trapped: int          # 0-20
    money_invested: str         # "$0-5K", "$5-15K", etc.
    relationships_cost: int     # 0-10
    identity_loss: int          # 1-10


@app.post("/api/capture-tracker")
async def capture_sunk_cost_tracker(result: SunkCostTrackerResult):
    """
    Capture Sunk Cost Tracker results.
    Adds to Encharge, triggers 2-email Gumroad → Fear Audit sequence.
    """
    api_key = os.getenv("ENCHARGE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="ENCHARGE_API_KEY not configured")

    logger.info(f"Sunk Cost Tracker: {result.email} → score={result.score}")

    try:
        # Add subscriber to Encharge, then apply tag using contact ID
        client = EnchargeClient(api_key)
        subscriber_response = client.add_subscriber(email=result.email)
        logger.info(f"Subscriber response: {subscriber_response}")

        contact_id = subscriber_response.get("user", {}).get("id")
        if not contact_id:
            raise ValueError(f"No contact ID returned from Encharge: {subscriber_response}")

        client.add_tag(tag="tracker-sunk-cost", contact_id=contact_id)
        logger.info(f"Encharge: {result.email} (ID: {contact_id}) tagged tracker-sunk-cost → 2-email Gumroad sequence triggered")

        return {
            "success": True,
            "message": "Check your inbox in 2 minutes. We sent you the download link.",
            "email": result.email,
            "score": result.score,
            "sequence": "Sunk Cost Tracker → Gumroad → Fear Audit",
        }

    except Exception as e:
        logger.error(f"Tracker capture failed for {result.email}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to capture tracker data: {str(e)}")


@app.get("/guides/sunk-cost")
async def get_sunk_cost_guide(score: int = 72, years: int = 9, money: str = "$30-50K", rels: int = 8, identity: int = 9):
    """
    Serve personalized Sunk Cost guide as HTML.
    Print to PDF in browser: File → Print → Save as PDF
    
    Usage:
      /guides/sunk-cost?score=72&years=9&money=$30-50K&rels=8&identity=9
    """
    from fastapi.responses import HTMLResponse
    
    html = generate_personalized_html(
        score=score,
        years_trapped=years,
        money_invested=money,
        relationships_cost=rels,
        identity_loss=identity,
    )
    return HTMLResponse(content=html)
