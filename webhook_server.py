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


@app.post("/api/encharge/subscribe")
async def img_pivot_challenge_signup(signup: ChallengeSignup):
    """Handle IMG Pivot Challenge landing page form submission."""
    api_key = os.getenv("ENCHARGE_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="ENCHARGE_API_KEY not configured")

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
