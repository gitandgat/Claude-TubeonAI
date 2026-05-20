"""
alerts.py — Live Entry & Exit Alerts
──────────────────────────────────────

Sends notifications when:
1. A new entry signal is confirmed
2. A position hits take profit or stop loss
3. Account drawdown exceeds threshold

Supports:
- Email via SMTP
- Slack via webhook
- Can be extended to Discord, Telegram, etc.
"""

from typing import Optional, Dict
from datetime import datetime
import logging
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from dotenv import load_dotenv

load_dotenv()

log = logging.getLogger(__name__)

# Email configuration (from .env)
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SENDER_EMAIL = os.getenv("ALERT_SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("ALERT_SENDER_PASSWORD")
ALERT_RECIPIENT = os.getenv("ALERT_RECIPIENT_EMAIL")

# Slack configuration (from .env)
SLACK_WEBHOOK_URL = os.getenv("SLACK_WEBHOOK_URL")

# Feature flags
SEND_EMAIL_ALERTS = SENDER_EMAIL and SENDER_PASSWORD and ALERT_RECIPIENT
SEND_SLACK_ALERTS = bool(SLACK_WEBHOOK_URL)


def send_email(subject: str, body: str, html: bool = False) -> bool:
    """
    Send an email alert.

    Returns: True if sent successfully, False otherwise
    """
    if not SEND_EMAIL_ALERTS:
        log.warning("Email alerts not configured (missing SMTP credentials)")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"] = SENDER_EMAIL
        msg["To"] = ALERT_RECIPIENT

        if html:
            msg.attach(MIMEText(body, "html"))
        else:
            msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, ALERT_RECIPIENT, msg.as_string())

        log.info(f"Email alert sent: {subject}")
        return True

    except Exception as e:
        log.error(f"Failed to send email: {e}")
        return False


def send_slack_message(
    title: str,
    fields: Dict[str, str],
    color: str = "#36a64f",
) -> bool:
    """
    Send a Slack message via webhook.

    color: "#36a64f" (green), "#ff0000" (red), "#ffa500" (orange)

    Returns: True if sent successfully, False otherwise
    """
    if not SEND_SLACK_ALERTS:
        log.warning("Slack alerts not configured (missing SLACK_WEBHOOK_URL)")
        return False

    try:
        payload = {
            "attachments": [
                {
                    "title": title,
                    "color": color,
                    "fields": [
                        {
                            "title": key,
                            "value": value,
                            "short": True,
                        }
                        for key, value in fields.items()
                    ],
                    "footer": "Minervini Trading Bot",
                    "ts": int(datetime.now().timestamp()),
                }
            ]
        }

        resp = requests.post(SLACK_WEBHOOK_URL, json=payload, timeout=5)
        resp.raise_for_status()

        log.info(f"Slack alert sent: {title}")
        return True

    except Exception as e:
        log.error(f"Failed to send Slack message: {e}")
        return False


def alert_entry_signal(
    ticker: str,
    entry_price: float,
    qty: int,
    stop_loss: float,
    take_profit: float,
    rs_rank: int,
    sector: Optional[str] = None,
    notes: Optional[str] = None,
) -> None:
    """
    Send an alert when a new entry signal is confirmed.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S ET")

    # Email body
    email_subject = f"🟢 ENTRY SIGNAL: {ticker} @ ${entry_price:.2f}"
    email_body = f"""
    Entry Signal Confirmed

    Ticker: {ticker}
    Entry Price: ${entry_price:.2f}
    Quantity: {qty} shares
    Stop Loss: ${stop_loss:.2f} ({((entry_price - stop_loss) / entry_price * 100):.1f}%)
    Take Profit: ${take_profit:.2f} ({((take_profit - entry_price) / entry_price * 100):.1f}%)

    Technical Metrics:
    - RS Rank: {rs_rank}
    {f'- Sector: {sector}' if sector else ''}

    Time: {timestamp}
    {f'Notes: {notes}' if notes else ''}
    """

    # Slack fields
    slack_fields = {
        "Ticker": ticker,
        "Entry": f"${entry_price:.2f}",
        "Qty": f"{qty} shares",
        "Stop Loss": f"${stop_loss:.2f}",
        "Take Profit": f"${take_profit:.2f}",
        "RS Rank": str(rs_rank),
    }
    if sector:
        slack_fields["Sector"] = sector

    send_email(email_subject, email_body)
    send_slack_message(
        title=f"🟢 ENTRY: {ticker}",
        fields=slack_fields,
        color="#36a64f",  # Green
    )


def alert_exit_signal(
    ticker: str,
    exit_price: float,
    qty: int,
    exit_reason: str,  # "TAKE_PROFIT", "STOP_LOSS", "TIME_EXIT"
    entry_price: float,
    profit_loss_pct: float,
) -> None:
    """
    Send an alert when a position is exited.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S ET")

    # Determine emoji based on outcome
    if exit_reason == "TAKE_PROFIT":
        emoji = "🟢"
        color = "#36a64f"  # Green
    elif exit_reason == "STOP_LOSS":
        emoji = "🔴"
        color = "#ff0000"  # Red
    else:  # TIME_EXIT
        emoji = "🟡"
        color = "#ffa500"  # Orange

    # Email body
    email_subject = f"{emoji} EXIT: {ticker} @ ${exit_price:.2f} ({profit_loss_pct:+.2f}%)"
    email_body = f"""
    Position Exited

    Ticker: {ticker}
    Exit Price: ${exit_price:.2f}
    Exit Reason: {exit_reason}
    Quantity: {qty} shares

    P&L:
    - Entry: ${entry_price:.2f}
    - Exit: ${exit_price:.2f}
    - Return: {profit_loss_pct:+.2f}%

    Time: {timestamp}
    """

    # Slack fields
    slack_fields = {
        "Ticker": ticker,
        "Exit": f"${exit_price:.2f}",
        "Reason": exit_reason,
        "Return": f"{profit_loss_pct:+.2f}%",
        "Qty": f"{qty} shares",
    }

    send_email(email_subject, email_body)
    send_slack_message(
        title=f"{emoji} EXIT: {ticker} ({exit_reason})",
        fields=slack_fields,
        color=color,
    )


def alert_drawdown_warning(
    current_equity: float,
    peak_equity: float,
    drawdown_pct: float,
    threshold_pct: float = 15.0,
) -> None:
    """
    Send an alert when account drawdown exceeds threshold.
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S ET")

    # Email body
    email_subject = f"⚠️ DRAWDOWN ALERT: {drawdown_pct:.1f}% below peak"
    email_body = f"""
    Account Drawdown Alert

    Peak Equity: ${peak_equity:,.2f}
    Current Equity: ${current_equity:,.2f}
    Drawdown: {drawdown_pct:.1f}% (threshold: {threshold_pct:.1f}%)

    Recommendation: Review open positions and consider reducing risk.

    Time: {timestamp}
    """

    # Slack fields
    slack_fields = {
        "Peak": f"${peak_equity:,.2f}",
        "Current": f"${current_equity:,.2f}",
        "Drawdown": f"{drawdown_pct:.1f}%",
        "Threshold": f"{threshold_pct:.1f}%",
    }

    send_email(email_subject, email_body)
    send_slack_message(
        title="⚠️ DRAWDOWN WARNING",
        fields=slack_fields,
        color="#ffa500",  # Orange
    )


def alert_market_condition_change(
    market_condition: str,
    details: str,
) -> None:
    """
    Send an alert when market regime changes (e.g., SPY enters downtrend).
    """
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S ET")

    # Email body
    email_subject = f"📊 MARKET CONDITION: {market_condition}"
    email_body = f"""
    Market Condition Change

    Status: {market_condition}
    Details: {details}

    Impact: {('Entries SUSPENDED' if 'downtrend' in market_condition.lower() else 'Entries ALLOWED')}

    Time: {timestamp}
    """

    slack_fields = {
        "Condition": market_condition,
        "Details": details,
        "Status": "Entries SUSPENDED" if "downtrend" in market_condition.lower() else "Entries OK",
    }

    send_email(email_subject, email_body)
    send_slack_message(
        title="📊 MARKET CONDITION CHANGE",
        fields=slack_fields,
        color="#ffa500",  # Orange
    )
