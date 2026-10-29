#!/usr/bin/env python3
"""
Conversation Tracker
Track who you messaged, responses, and deals closed
"""

import os
import json
import csv
from datetime import datetime
from typing import List


class ConversationTracker:
    """Track all outreach and responses."""

    def __init__(self, filename="conversations.json"):
        self.filename = filename
        self.load()

    def load(self):
        """Load existing conversations."""
        try:
            with open(self.filename) as f:
                self.data = json.load(f)
        except FileNotFoundError:
            self.data = {
                "conversations": [],
                "stats": {
                    "total_messaged": 0,
                    "total_responses": 0,
                    "total_closed": 0,
                    "total_revenue": 0,
                },
                "created": datetime.now().isoformat(),
                "last_updated": datetime.now().isoformat(),
            }

    def save(self):
        """Save conversations."""
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.filename, "w") as f:
            json.dump(self.data, f, indent=2)

    def add_outreach(
        self,
        platform: str,
        person_name: str,
        title: str,
        message_sent: str,
        url: str,
        service: str,
    ):
        """Record that you messaged someone."""

        conv = {
            "id": f"{platform}_{datetime.now().timestamp()}",
            "platform": platform,
            "person_name": person_name,
            "title": title,
            "message_sent": message_sent,
            "url": url,
            "service": service,
            "date_messaged": datetime.now().isoformat(),
            "status": "messaged",
            "response": None,
            "response_date": None,
            "call_scheduled": False,
            "call_date": None,
            "deal_closed": False,
            "deal_amount": 0,
            "notes": "",
        }

        self.data["conversations"].append(conv)
        self.data["stats"]["total_messaged"] += 1
        self.save()

        print(f"✅ Recorded: messaged {person_name} on {platform}")
        return conv["id"]

    def log_response(self, conv_id: str, response_text: str, is_interested: bool):
        """Log when someone responds."""

        for conv in self.data["conversations"]:
            if conv["id"] == conv_id:
                conv["response"] = response_text
                conv["response_date"] = datetime.now().isoformat()
                conv["status"] = "responded" if is_interested else "not_interested"
                self.data["stats"]["total_responses"] += 1
                self.save()

                print(
                    f"✅ Updated: {conv['person_name']} responded - {conv['status']}"
                )
                return

        print(f"❌ Conversation ID not found: {conv_id}")

    def log_call(self, conv_id: str, call_date: str, notes: str):
        """Log scheduled call."""

        for conv in self.data["conversations"]:
            if conv["id"] == conv_id:
                conv["call_scheduled"] = True
                conv["call_date"] = call_date
                conv["notes"] = notes
                conv["status"] = "call_scheduled"
                self.save()

                print(f"✅ Updated: call scheduled for {call_date}")
                return

        print(f"❌ Conversation ID not found: {conv_id}")

    def log_deal(self, conv_id: str, amount: int, notes: str):
        """Log closed deal."""

        for conv in self.data["conversations"]:
            if conv["id"] == conv_id:
                conv["deal_closed"] = True
                conv["deal_amount"] = amount
                conv["notes"] = notes
                conv["status"] = "deal_closed"
                self.data["stats"]["total_closed"] += 1
                self.data["stats"]["total_revenue"] += amount
                self.save()

                print(
                    f"✅ Updated: Deal closed! ${amount} from {conv['person_name']}"
                )
                return

        print(f"❌ Conversation ID not found: {conv_id}")

    def display_dashboard(self):
        """Show current status."""

        print("\n" + "="*120)
        print("📊 OUTREACH DASHBOARD".center(120))
        print("="*120 + "\n")

        stats = self.data["stats"]
        convs = self.data["conversations"]

        # Summary
        print("📈 SUMMARY:\n")
        print(f"  Total messaged: {stats['total_messaged']}")
        print(f"  Got responses: {stats['total_responses']}")
        print(f"  Conversion rate: {int(stats['total_responses']/max(1, stats['total_messaged'])*100)}%")
        print(f"  Deals closed: {stats['total_closed']}")
        print(f"  Total revenue: ${stats['total_revenue']:,}\n")

        if stats["total_closed"] > 0:
            avg_deal = stats["total_revenue"] / stats["total_closed"]
            print(f"  Average deal size: ${avg_deal:,.0f}\n")

        # Recent conversations
        print("📋 RECENT CONVERSATIONS:\n")

        for conv in sorted(convs, key=lambda x: x["date_messaged"], reverse=True)[
            :10
        ]:
            status_emoji = {
                "messaged": "📤",
                "responded": "💬",
                "call_scheduled": "📞",
                "deal_closed": "✅",
                "not_interested": "❌",
            }.get(conv["status"], "❓")

            print(f"{status_emoji} {conv['person_name']} [{conv['platform']}]")
            print(f"   Title: {conv['title'][:60]}")
            print(f"   Status: {conv['status']}")

            if conv["deal_closed"]:
                print(f"   💰 DEAL: ${conv['deal_amount']}")

            if conv["response"]:
                print(f"   Response: {conv['response'][:100]}")

            if conv["notes"]:
                print(f"   Notes: {conv['notes']}")

            print()

        # By status
        print("\n📊 STATUS BREAKDOWN:\n")
        status_counts = {}
        for conv in convs:
            status = conv["status"]
            status_counts[status] = status_counts.get(status, 0) + 1

        for status, count in sorted(status_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {status}: {count}")

        # By platform
        print("\n🌐 BY PLATFORM:\n")
        platform_counts = {}
        for conv in convs:
            platform = conv["platform"]
            platform_counts[platform] = platform_counts.get(platform, 0) + 1

        for platform, count in sorted(platform_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {platform}: {count}")

        # By service
        print("\n💼 BY SERVICE:\n")
        service_counts = {}
        for conv in convs:
            service = conv["service"]
            service_counts[service] = service_counts.get(service, 0) + 1

        for service, count in sorted(service_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {service}: {count}")

        print("\n" + "="*120 + "\n")

    def export_csv(self, filename="conversations.csv"):
        """Export to CSV for spreadsheet."""

        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)

            # Headers
            headers = [
                "Date Messaged",
                "Platform",
                "Name",
                "Title",
                "Service",
                "Status",
                "Response Date",
                "Call Date",
                "Deal Closed",
                "Amount",
                "Notes",
                "URL",
            ]
            writer.writerow(headers)

            # Rows
            for conv in self.data["conversations"]:
                writer.writerow(
                    [
                        conv["date_messaged"],
                        conv["platform"],
                        conv["person_name"],
                        conv["title"][:60],
                        conv["service"],
                        conv["status"],
                        conv["response_date"] or "",
                        conv["call_date"] or "",
                        "YES" if conv["deal_closed"] else "NO",
                        conv["deal_amount"] if conv["deal_closed"] else "",
                        conv["notes"],
                        conv["url"],
                    ]
                )

        print(f"✅ Exported to {filename}")


def demo_tracker():
    """Show how to use the tracker."""

    print("\n" + "="*120)
    print("🎯 CONVERSATION TRACKER - DEMO".center(120))
    print("="*120 + "\n")

    tracker = ConversationTracker("conversations_demo.json")

    # Example: log some outreach
    print("Example 1: Log that you messaged someone\n")
    conv_id = tracker.add_outreach(
        platform="Twitter",
        person_name="@creator",
        title="Wish there was an easy way to turn YouTube videos into TikToks",
        message_sent="I actually built exactly this. DM?",
        url="https://twitter.com/creator/status/456",
        service="youtube_repurposing",
    )

    print("\nExample 2: Log their response\n")
    tracker.log_response(
        conv_id, "OMG yes, I've been looking for this! Tell me more", True
    )

    print("\nExample 3: Log scheduled call\n")
    tracker.log_call(conv_id, "2026-06-10 14:00", "Discussed pricing, they interested")

    print("\nExample 4: Log closed deal\n")
    tracker.log_deal(conv_id, 1500, "Closed $1500/month LinkedIn content service")

    # Show dashboard
    tracker.display_dashboard()

    # Export
    tracker.export_csv("conversations_demo.csv")

    print("\n✅ Demo complete!")
    print("📁 Files created:")
    print("   • conversations_demo.json (tracker data)")
    print("   • conversations_demo.csv (spreadsheet)\n")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == "demo":
            demo_tracker()
        elif sys.argv[1] == "dashboard":
            tracker = ConversationTracker()
            tracker.display_dashboard()
        elif sys.argv[1] == "export":
            tracker = ConversationTracker()
            tracker.export_csv()
    else:
        print("Usage:")
        print("  python conversation_tracker.py demo          # See example")
        print("  python conversation_tracker.py dashboard      # Show status")
        print("  python conversation_tracker.py export         # Export to CSV")
