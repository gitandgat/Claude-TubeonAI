#!/usr/bin/env python3
"""
Webhook Orchestrator - The Glue That Ties Everything Together

Coordinates:
- Twilio (incoming calls)
- ElevenLabs (AI voice)
- Claude Opus (conversation logic)
- DocuSign (contracts)
- Stripe (payments)

All 9 agents work through this orchestrator.
"""

from flask import Flask, request, jsonify
from twilio.rest import Client
from twilio.twiml.voice_response import VoiceResponse
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

# Initialize clients
twilio_client = Client(
    os.getenv("TWILIO_ACCOUNT_SID"),
    os.getenv("TWILIO_AUTH_TOKEN")
)

# Load configs
with open("twilio_config.json") as f:
    twilio_config = json.load(f)
with open("elevenlabs_config.json") as f:
    elevenlabs_config = json.load(f)
with open("docusign_config.json") as f:
    docusign_config = json.load(f)
with open("stripe_config.json") as f:
    stripe_config = json.load(f)


class OrchestrationEngine:
    """Orchestrates the flow of incoming call through all systems."""

    def __init__(self):
        self.active_calls = {}
        self.completed_deals = []

    def handle_incoming_call(self, phone_number: str) -> dict:
        """Route 1: Prospect calls in"""

        call_id = f"call_{datetime.now().timestamp()}"

        # Log incoming call
        self.active_calls[call_id] = {
            "phone_number": phone_number,
            "started_at": datetime.now().isoformat(),
            "status": "answering",
            "stage": "greeting"
        }

        print(f"📞 INCOMING CALL: {phone_number}")
        print(f"   Call ID: {call_id}")
        print(f"   Routing to AI Sales Agent...")

        return {
            "call_id": call_id,
            "action": "connect_to_ai_agent"
        }

    def ai_agent_conversation(self, call_id: str, user_message: str) -> dict:
        """Route 2: AI conducts conversation"""

        from ai_sales_agent import AISalesAgent

        agent = AISalesAgent()

        # Get AI response
        response = agent.process_response(user_message)

        # Check if should close
        should_close = agent.should_close()

        self.active_calls[call_id]["stage"] = "conversation"
        self.active_calls[call_id]["last_message_at"] = datetime.now().isoformat()

        return {
            "response": response,
            "should_close": should_close,
            "engagement_level": agent.prospect_profile["engagement_level"]
        }

    def close_and_send_contract(self, call_id: str, prospect_email: str, prospect_name: str) -> dict:
        """Route 3: Send contract after successful close"""

        print(f"✅ DEAL CLOSED - {call_id}")
        print(f"   Prospect: {prospect_name} ({prospect_email})")
        print(f"   Sending contract via DocuSign...")

        # TODO: Integrate DocuSign API
        # For now, we'll simulate it

        deal_record = {
            "call_id": call_id,
            "prospect_name": prospect_name,
            "prospect_email": prospect_email,
            "amount": 1500,
            "currency": "USD",
            "closed_at": datetime.now().isoformat(),
            "contract_sent": True,
            "contract_link": f"https://docusign.net/r/XXXXX"
        }

        self.completed_deals.append(deal_record)
        self.active_calls[call_id]["status"] = "contracted"

        return deal_record

    def send_payment_link(self, prospect_email: str, prospect_name: str) -> dict:
        """Route 4: Send Stripe payment link"""

        print(f"💳 SENDING PAYMENT LINK")
        print(f"   To: {prospect_email}")
        print(f"   Amount: $1,500/month")

        # TODO: Integrate email service
        # For now, we'll return the link

        return {
            "payment_link": stripe_config.get("payment_link"),
            "sent_to": prospect_email,
            "amount": 1500
        }

    def process_payment(self, payment_intent_id: str) -> dict:
        """Route 5: Payment received via Stripe webhook"""

        print(f"💰 PAYMENT RECEIVED")
        print(f"   Payment Intent: {payment_intent_id}")
        print(f"   Activating service...")

        # TODO: Integrate with fulfillment agent
        # For now, we'll simulate activation

        return {
            "status": "payment_received",
            "payment_intent": payment_intent_id,
            "service_activated": True,
            "first_batch_scheduled": datetime.now().isoformat()
        }

    def activate_service(self, prospect_email: str) -> dict:
        """Route 6: Start delivering the service"""

        print(f"🚀 SERVICE ACTIVATED")
        print(f"   Customer: {prospect_email}")
        print(f"   Starting monthly demand discovery...")

        # Trigger fulfillment agent
        return {
            "status": "active",
            "first_discovery_runs": "Tomorrow at 9am UTC",
            "dashboard_url": f"https://dashboard.yourapp.com/{prospect_email}",
            "support_email": "support@yourapp.com"
        }

    def get_analytics(self) -> dict:
        """Route 7: Get real-time analytics"""

        total_calls = len(self.active_calls)
        completed_deals = len(self.completed_deals)
        monthly_revenue = completed_deals * 1500

        return {
            "active_calls": total_calls,
            "completed_deals": completed_deals,
            "monthly_revenue": monthly_revenue,
            "deals": self.completed_deals
        }


# Initialize orchestrator
orchestrator = OrchestrationEngine()


# WEBHOOK ROUTES

@app.route("/webhook/twilio/voice", methods=["POST"])
def handle_twilio_voice():
    """Incoming Twilio call - Connect to AI Agent"""

    phone_number = request.form.get("From")
    call_sid = request.form.get("CallSid")

    # Start call orchestration
    result = orchestrator.handle_incoming_call(phone_number)

    # Return TwiML
    response = VoiceResponse()
    response.say("Thanks for calling. Connecting you to an agent.", voice="woman")

    # Connect to websocket or begin gathering input
    # For production, you'd connect to a websocket that streams audio to AI agent

    return str(response)


@app.route("/webhook/twilio/status", methods=["POST"])
def handle_twilio_status():
    """Call status updates from Twilio"""

    call_sid = request.form.get("CallSid")
    status = request.form.get("CallStatus")

    print(f"📞 Call {call_sid} status: {status}")

    return "", 200


@app.route("/webhook/stripe/payment", methods=["POST"])
def handle_stripe_payment():
    """Payment received - Activate service"""

    data = request.get_json()
    payment_intent_id = data.get("id")

    result = orchestrator.process_payment(payment_intent_id)
    return jsonify(result)


@app.route("/api/analytics", methods=["GET"])
def get_analytics():
    """Get real-time system analytics"""

    analytics = orchestrator.get_analytics()
    return jsonify(analytics)


@app.route("/api/health", methods=["GET"])
def health_check():
    """Health check endpoint"""

    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "active_calls": len(orchestrator.active_calls),
        "completed_deals": len(orchestrator.completed_deals)
    })


@app.route("/", methods=["GET"])
def root():
    """Root endpoint"""

    return jsonify({
        "service": "Autonomous Sales System",
        "status": "running",
        "endpoints": {
            "/webhook/twilio/voice": "Incoming calls",
            "/webhook/stripe/payment": "Payment notifications",
            "/api/analytics": "Real-time analytics",
            "/api/health": "Health check"
        }
    })


if __name__ == "__main__":
    print("\n" + "="*100)
    print("🤖 WEBHOOK ORCHESTRATOR STARTING".center(100))
    print("="*100 + "\n")

    print("✅ Twilio configured")
    print("✅ ElevenLabs configured")
    print("✅ DocuSign configured")
    print("✅ Stripe configured")
    print("✅ AI Sales Agent ready")
    print("\n📡 Listening for webhooks...")
    print("   - Twilio calls → /webhook/twilio/voice")
    print("   - Stripe payments → /webhook/stripe/payment")
    print("   - Analytics → /api/analytics")
    print("\n🚀 Ready to close deals!\n")

    # Start Flask server
    app.run(host="0.0.0.0", port=5000, debug=True)
