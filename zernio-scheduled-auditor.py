#!/usr/bin/env python3
"""
Scheduled background auditor - runs daily, only acts if failures found.
Sends results to Discord webhook.
"""

import os
import json
import requests
import time
import subprocess
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DISCORD_WEBHOOK = os.getenv('DISCORD_WEBHOOK_URL')

# A virality score under this (out of 100) = mechanically clean but dead on
# arrival (broken hook). Worth an alert even when stop-slop all-passes. Posts at
# 50-69 are "could be sharper" — reported, not alerted, to avoid nightly noise.
VIRALITY_ALERT_BELOW = 50


def _severe_virality(report):
    """Engagement-weak posts severe enough to alert on (broken hooks)."""
    return [p for p in report.get('virality_weak_posts', [])
            if (p.get('virality_score') or 0) < VIRALITY_ALERT_BELOW]


def run_auto_audit():
    """Execute the autonomous audit-fix loop"""
    try:
        result = subprocess.run(
            ['python3', 'zernio-auto-audit-fix.py'],
            cwd=os.path.dirname(os.path.abspath(__file__)),
            capture_output=True,
            text=True,
            timeout=600
        )
        return result.returncode == 0
    except Exception as e:
        return False

def load_report():
    """Load the auto-audit report"""
    try:
        with open('auto-audit-report.json', 'r') as f:
            return json.load(f)
    except:
        return None

def send_discord_message(report):
    """Send results to Discord webhook"""
    if not DISCORD_WEBHOOK:
        return

    status_emoji = "✅" if report['status'] == 'SUCCESS' else "⚠️"
    color = 3066993 if report['status'] == 'SUCCESS' else 16776960  # Green or Yellow

    embed = {
        "title": f"{status_emoji} Zernio Content Audit Report",
        "description": "Automated quality check: /stop-slop (blocking) + virality (advisory)",
        "color": color,
        "fields": [
            {
                "name": "Status",
                "value": report['status'],
                "inline": True
            },
            {
                "name": "Posts Passing",
                "value": f"{report['passing']}/{report['total_posts']}",
                "inline": True
            },
            {
                "name": "Posts Failing",
                "value": str(report['failing']),
                "inline": True
            },
            {
                "name": "Loops Required",
                "value": str(report['loops']),
                "inline": True
            },
            {
                "name": "Timestamp",
                "value": report['timestamp'],
                "inline": False
            }
        ]
    }

    if report['failing'] > 0 and report['failing_posts']:
        failing_list = "\n".join([
            f"• {p['post_id'][:12]}... (Score: {p['score']}/50)"
            for p in report['failing_posts'][:5]
        ])
        embed['fields'].append({
            "name": "Still Failing",
            "value": failing_list,
            "inline": False
        })

    # Virality (advisory) — engagement signal stop-slop can't see.
    if report.get('virality_target') is not None:
        vt = report['virality_target']
        total = report.get('total_posts', 0)
        below = report.get('virality_below_target', 0)
        severe = _severe_virality(report)
        summary = f"{total - below}/{total} ≥{vt}/100"
        if severe:
            summary += f" — {len(severe)} dead on arrival (<{VIRALITY_ALERT_BELOW}/100)"
        embed['fields'].append({
            "name": "Virality (advisory)",
            "value": summary,
            "inline": False
        })
        if severe:
            severe_list = "\n".join(
                f"• {p['post_id'][:12]}... ({p.get('virality_score')}/100, hook {p.get('hook')}/10)"
                for p in severe[:5]
            )
            embed['fields'].append({
                "name": "Broken hooks to rewrite",
                "value": severe_list,
                "inline": False
            })

    payload = {"embeds": [embed]}

    try:
        requests.post(DISCORD_WEBHOOK, json=payload, timeout=10)
    except Exception as e:
        print(f"Failed to send Discord message: {e}")

def send_email_report(report):
    """Send results via email (optional)"""
    # Implementation would depend on email service
    # For now, just log
    print(f"\n📧 Email report would be sent here")
    print(f"   Subject: Zernio Content Audit - {report['status']}")
    print(f"   Status: {report['passing']}/{report['total_posts']} passing")
    if report.get('virality_target') is not None:
        print(f"   Virality: {report.get('virality_below_target', 0)} below "
              f"{report['virality_target']}/100 "
              f"({len(_severe_virality(report))} dead on arrival)")

def main():
    print("=" * 70)
    print("SCHEDULED BACKGROUND AUDITOR")
    print("=" * 70)
    print(f"Run time: {datetime.now().isoformat()}\n")

    # Run the audit
    print("Running autonomous audit-fix loop...")
    success = run_auto_audit()

    if not success:
        print("✗ Audit failed to complete")
        return

    # Load report
    report = load_report()
    if not report:
        print("✗ Could not load report")
        return

    print("\n" + "=" * 70)
    print("RESULTS")
    print("=" * 70)
    print(f"Status: {report['status']}")
    print(f"Passing: {report['passing']}/{report['total_posts']}")
    print(f"Failing: {report['failing']}")
    print(f"Loops: {report['loops']}")
    severe = _severe_virality(report)
    if report.get('virality_target') is not None:
        print(f"Virality: {report.get('virality_below_target', 0)} below "
              f"{report['virality_target']}/100 ({len(severe)} dead on arrival)")

    # Notify on stop-slop failures OR genuinely dead-hook posts. Advisory posts
    # at 50-69 virality show in the embed but don't trigger a nightly ping (noise).
    if report['failing'] > 0 or severe:
        if report['failing'] > 0:
            print(f"\n⚠️  Action required: {report['failing']} posts still failing stop-slop")
        if severe:
            print(f"\n⚠️  {len(severe)} clean-but-dead posts "
                  f"(virality <{VIRALITY_ALERT_BELOW}/100) — weak hooks")
        send_discord_message(report)
        send_email_report(report)
    else:
        print(f"\n✓ All posts passing, no broken hooks - no action needed")

    print(f"\nReport saved to auto-audit-report.json")

if __name__ == '__main__':
    main()
