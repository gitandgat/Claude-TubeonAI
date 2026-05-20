"""
Encharge Quiz Funnel Setup
===========================
Run once to create the custom fields needed for the Burnout Crosswalk Assessment quiz.

After running this, go to Encharge UI and:
  1. Create a Flow triggered by tag "quiz-stage-start"  → delivers Start email sequence
  2. Create a Flow triggered by tag "quiz-stage-stop"   → delivers Stop email sequence
  3. Create a Flow triggered by tag "quiz-stage-elder"  → delivers Elder email sequence
  4. Create a Flow triggered by tag "quiz-stage-human"  → delivers Human email sequence

Usage:
  python setup_encharge.py
"""

import os
import sys
from dotenv import load_dotenv
from encharge_client import EnchargeClient

load_dotenv()

QUIZ_FIELDS = [
    {
        "name": "quizStage",
        "type": "string",
        "title": "Quiz Stage",
        "tooltip": "Burnout Crosswalk Assessment result: Start, Stop, Elder, or Human",
    },
    {
        "name": "quizScore",
        "type": "string",
        "title": "Quiz Score",
        "tooltip": "Average score from Burnout Crosswalk Assessment (1.0 - 4.0)",
    },
]


def main():
    api_key = os.getenv("ENCHARGE_API_KEY")
    if not api_key:
        sys.exit("Error: ENCHARGE_API_KEY not set in .env")

    client = EnchargeClient(api_key)

    # Get existing fields to avoid duplicates
    print("Fetching existing Encharge fields...")
    existing = client.get_fields()
    existing_names = {f["name"] for f in existing} if isinstance(existing, list) else set()
    print(f"  Found {len(existing_names)} existing fields.")

    fields_to_create = [f for f in QUIZ_FIELDS if f["name"] not in existing_names]

    if not fields_to_create:
        print("  All quiz fields already exist. Nothing to create.")
    else:
        print(f"\nCreating {len(fields_to_create)} custom field(s)...")
        result = client.create_fields(fields_to_create)
        for f in fields_to_create:
            print(f"  + Created field: {f['name']} ({f['title']})")

    print("\n✓ Encharge quiz fields are ready.")
    print("\nNext steps in the Encharge UI:")
    print("  1. Create 4 Flows — one per stage tag:")
    print("     - Trigger: Tag Added = 'quiz-stage-start'  → 5-email Start sequence")
    print("     - Trigger: Tag Added = 'quiz-stage-stop'   → 5-email Stop sequence")
    print("     - Trigger: Tag Added = 'quiz-stage-elder'  → 5-email Elder sequence")
    print("     - Trigger: Tag Added = 'quiz-stage-human'  → 5-email Human sequence")
    print("  2. Paste in the email content from: encharge_emails.md")
    print("  3. Connect your quiz webhook to call client.add_quiz_result()")


if __name__ == "__main__":
    main()
