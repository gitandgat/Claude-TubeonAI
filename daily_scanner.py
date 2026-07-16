#!/usr/bin/env python3
"""
Daily Automated Scanner
Runs every day, finds new opportunities, sends you a report
"""

import os
import json
from datetime import datetime
from multiplatform_discovery import (
    run_multiplatform_discovery,
    IndieHackersScanner,
    ProductHuntScanner,
    TwitterScanner,
    QuoraScanner,
    YouTubeScanner,
)


def run_daily_scan():
    """Run the full discovery daily."""

    print("\n" + "="*120)
    print(f"📅 DAILY OPPORTUNITY SCAN - {datetime.now().strftime('%Y-%m-%d %H:%M')}".center(120))
    print("="*120 + "\n")

    # Run discovery
    opportunities = run_multiplatform_discovery()

    # Create daily report
    daily_report = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "timestamp": datetime.now().isoformat(),
        "total_found": len(opportunities),
        "top_5": [
            {
                "rank": i,
                "platform": opp.platform,
                "title": opp.title,
                "score": opp.score,
                "url": opp.url,
            }
            for i, opp in enumerate(opportunities[:5], 1)
        ],
        "by_platform": {},
        "by_service": {},
    }

    # Count by platform
    for opp in opportunities:
        platform = opp.platform
        if platform not in daily_report["by_platform"]:
            daily_report["by_platform"][platform] = 0
        daily_report["by_platform"][platform] += 1

    # Count by service
    for opp in opportunities:
        for svc in opp.matched_services:
            if svc not in daily_report["by_service"]:
                daily_report["by_service"][svc] = 0
            daily_report["by_service"][svc] += 1

    # Save daily report
    report_filename = f"daily_scan_{datetime.now().strftime('%Y%m%d')}.json"
    with open(report_filename, "w") as f:
        json.dump(daily_report, f, indent=2)

    # Save to rolling history
    try:
        with open("scan_history.json") as f:
            history = json.load(f)
    except FileNotFoundError:
        history = {"scans": []}

    history["scans"].append(daily_report)
    # Keep last 30 scans
    if len(history["scans"]) > 30:
        history["scans"] = history["scans"][-30:]

    with open("scan_history.json", "w") as f:
        json.dump(history, f, indent=2)

    print("\n" + "="*120)
    print("📊 DAILY SUMMARY".center(120))
    print("="*120 + "\n")

    print(f"Total opportunities found: {daily_report['total_found']}\n")

    print("Top 5 today:\n")
    for item in daily_report["top_5"]:
        print(f"  {item['rank']}. [{item['platform']}] {item['title'][:60]}")
        print(f"     Score: {item['score']}/100\n")

    print("By platform:")
    for platform, count in daily_report["by_platform"].items():
        print(f"  {platform}: {count}")

    print("\nBy service:")
    for service, count in daily_report["by_service"].items():
        print(f"  {service}: {count}")

    print(f"\n💾 Report saved: {report_filename}")
    print(f"📈 History saved: scan_history.json\n")

    return daily_report


def setup_daily_scheduler():
    """Instructions for setting up daily runs."""

    print("\n" + "="*120)
    print("⏰ SETUP DAILY AUTOMATION".center(120))
    print("="*120 + "\n")

    print("Option 1: macOS/Linux (Cron)\n")
    print("Run this command once:")
    print("  crontab -e\n")

    print("Add this line (runs every morning at 9am):")
    print("  0 9 * * * cd /Users/toto/Claude\\ TubeonAI && python daily_scanner.py\n")

    print("─"*120 + "\n")

    print("Option 2: Windows (Task Scheduler)\n")
    print("1. Open Task Scheduler")
    print("2. Create Basic Task → Name: 'Daily Opportunity Scan'")
    print("3. Trigger: Daily at 9:00 AM")
    print("4. Action: Start Program")
    print("   Program: python")
    print("   Arguments: daily_scanner.py")
    print("   Start in: C:\\Users\\YourUser\\Claude TubeonAI\n")

    print("─"*120 + "\n")

    print("Option 3: Python Schedule (runs in background)\n")
    print("Create run_scheduler.py with:")
    print("""
import schedule
import time
from daily_scanner import run_daily_scan

schedule.every().day.at("09:00").do(run_daily_scan)

while True:
    schedule.run_pending()
    time.sleep(60)
    """)

    print("Then run: python run_scheduler.py\n")


def generate_email_report(report: dict) -> str:
    """Generate an email-friendly report."""

    subject = f"Opportunity Scan - {report['date']} ({report['total_found']} found)"

    body = f"""
Daily Opportunity Report - {report['date']}
{'='*60}

Total opportunities found: {report['total_found']}

TOP 5 OPPORTUNITIES:
"""

    for item in report["top_5"]:
        body += f"\n{item['rank']}. [{item['platform']}] {item['title']}\n"
        body += f"   Score: {item['score']}/100\n"
        body += f"   {item['url']}\n"

    body += f"\n\nOPPORTUNITIES BY PLATFORM:\n"
    for platform, count in report["by_platform"].items():
        body += f"  {platform}: {count}\n"

    body += f"\nOPPORTUNITIES BY SERVICE:\n"
    for service, count in report["by_service"].items():
        body += f"  {service}: {count}\n"

    body += f"""

Next step: Open message_templates.json to send outreach messages

Generated: {report['timestamp']}
"""

    return {"subject": subject, "body": body}


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        setup_daily_scheduler()
    else:
        report = run_daily_scan()

        # Optional: Generate email report
        email = generate_email_report(report)
        print("\n" + "="*120)
        print("📧 EMAIL REPORT (for sending to yourself)".center(120))
        print("="*120)
        print(f"\nSubject: {email['subject']}\n")
        print(email['body'])
