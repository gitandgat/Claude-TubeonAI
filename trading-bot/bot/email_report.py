"""
email_report.py — Daily Email Report
─────────────────────────────────────

Generates and sends a daily trading summary email with:
- Today's trades (entries and exits)
- Account P&L and equity
- Win rate and key metrics
- Sector performance
- Tomorrow's watchlist

Intended to run at market close (4:00 PM ET) via launchd.

Usage:
    python bot/email_report.py              # Send today's report
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple
import sqlite3
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import pytz
from alpaca.trading.client import TradingClient
from dotenv import load_dotenv
import os

load_dotenv()

ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
PAPER_TRADING = os.getenv("PAPER_TRADING", "true").lower() == "true"

DB_FILE = Path(__file__).parent.parent / "trading_bot.db"
SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SENDER_EMAIL = os.getenv("ALERT_SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("ALERT_SENDER_PASSWORD")
REPORT_RECIPIENT = os.getenv("ALERT_RECIPIENT_EMAIL")

ET = pytz.timezone("America/New_York")


def get_client() -> TradingClient:
    """Create Alpaca trading client."""
    return TradingClient(ALPACA_API_KEY, ALPACA_SECRET_KEY, paper=PAPER_TRADING)


def get_account_stats() -> Dict:
    """Get current account balance."""
    try:
        client = get_client()
        account = client.get_account()
        return {
            "equity": float(account.equity),
            "buying_power": float(account.buying_power),
            "cash": float(account.cash),
            "initial_equity": float(account.initial_equity),
        }
    except Exception as e:
        print(f"Error fetching account: {e}")
        return {}


def get_today_trades() -> Tuple[List[Dict], float]:
    """Get trades from today."""
    trades = []
    try:
        if not DB_FILE.exists():
            return [], 0.0

        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        today = datetime.now(ET).strftime("%Y-%m-%d")

        # Closed trades today
        cursor.execute(f"""
            SELECT * FROM trades
            WHERE DATE(exit_date) = ?
            ORDER BY exit_date ASC
        """, (today,))

        daily_pnl = 0.0
        for row in cursor.fetchall():
            trade = {
                "ticker": row["ticker"],
                "entry_price": row["entry_price"],
                "entry_date": row["entry_date"],
                "exit_price": row["exit_price"],
                "exit_date": row["exit_date"],
                "exit_reason": row["exit_reason"],
                "qty": row["entry_qty"],
                "pnl": row["profit_loss"],
                "pnl_pct": row["profit_loss_pct"],
                "days_held": row["days_held"],
            }
            trades.append(trade)
            daily_pnl += trade["pnl"]

        conn.close()
        return trades, daily_pnl

    except Exception as e:
        print(f"Error fetching today's trades: {e}")
        return [], 0.0


def get_month_performance() -> Dict:
    """Get monthly performance metrics."""
    try:
        if not DB_FILE.exists():
            return {}

        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        month_start = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        cursor.execute(f"""
            SELECT
                COUNT(*) as total_trades,
                SUM(CASE WHEN profit_loss > 0 THEN 1 ELSE 0 END) as winning_trades,
                SUM(CASE WHEN profit_loss < 0 THEN 1 ELSE 0 END) as losing_trades,
                SUM(profit_loss) as total_pnl,
                AVG(profit_loss_pct) as avg_return
            FROM trades
            WHERE exit_date >= ? AND status = 'CLOSED'
        """, (month_start,))

        row = cursor.fetchone()
        if row:
            total = row["total_trades"] or 0
            wins = row["winning_trades"] or 0
            win_rate = (wins / total * 100) if total > 0 else 0

            metrics = {
                "total_trades": total,
                "winning_trades": wins,
                "losing_trades": row["losing_trades"] or 0,
                "win_rate": win_rate,
                "total_pnl": row["total_pnl"] or 0,
                "avg_return": row["avg_return"] or 0,
            }
        else:
            metrics = {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0,
                "total_pnl": 0,
                "avg_return": 0,
            }

        conn.close()
        return metrics

    except Exception as e:
        print(f"Error fetching performance: {e}")
        return {}


def get_open_positions() -> List[Dict]:
    """Get current open positions."""
    try:
        client = get_client()
        positions = []
        for pos in client.get_all_positions():
            positions.append({
                "symbol": pos.symbol,
                "qty": float(pos.qty),
                "entry_price": float(pos.avg_fill_price),
                "current_price": float(pos.current_price),
                "unrealized_pl": float(pos.unrealized_pl),
                "unrealized_plpc": float(pos.unrealized_plpc),
            })
        return positions
    except Exception as e:
        print(f"Error fetching positions: {e}")
        return []


def generate_email_html(
    today_trades: List[Dict],
    daily_pnl: float,
    account: Dict,
    month_metrics: Dict,
    open_positions: List[Dict],
) -> str:
    """Generate HTML for the email."""
    timestamp = datetime.now(ET).strftime("%Y-%m-%d %H:%M %Z")

    # Build trade rows
    trades_html = ""
    if today_trades:
        for trade in today_trades:
            status_emoji = "✓" if trade["pnl"] >= 0 else "✗"
            trades_html += f"""
            <tr>
                <td>{trade['ticker']}</td>
                <td>${trade['entry_price']:.2f}</td>
                <td>${trade['exit_price']:.2f}</td>
                <td>{trade['days_held']}d</td>
                <td>{trade['exit_reason']}</td>
                <td style="color: {'green' if trade['pnl'] >= 0 else 'red'}; font-weight: bold;">
                    {status_emoji} {trade['pnl_pct']:+.2f}%
                </td>
            </tr>
            """
    else:
        trades_html = "<tr><td colspan='6' style='text-align: center; color: #999;'>No trades today</td></tr>"

    # Build positions rows
    positions_html = ""
    if open_positions:
        for pos in open_positions:
            pl_pct = pos["unrealized_plpc"] * 100
            positions_html += f"""
            <tr>
                <td>{pos['symbol']}</td>
                <td>{pos['qty']:.0f}</td>
                <td>${pos['entry_price']:.2f}</td>
                <td>${pos['current_price']:.2f}</td>
                <td style="color: {'green' if pl_pct >= 0 else 'red'}; font-weight: bold;">
                    {pl_pct:+.2f}%
                </td>
            </tr>
            """
    else:
        positions_html = "<tr><td colspan='5' style='text-align: center; color: #999;'>No open positions</td></tr>"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>Daily Trading Report</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                color: #333;
                line-height: 1.6;
                max-width: 900px;
                margin: 0 auto;
                padding: 20px;
                background: #f5f5f5;
            }}
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
                border-radius: 8px;
                margin-bottom: 20px;
            }}
            .header h1 {{
                margin: 0;
                font-size: 28px;
            }}
            .header p {{
                margin: 5px 0 0 0;
                opacity: 0.9;
            }}
            .section {{
                background: white;
                border-radius: 8px;
                padding: 20px;
                margin-bottom: 20px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            .section h2 {{
                margin: 0 0 15px 0;
                font-size: 20px;
                border-bottom: 2px solid #667eea;
                padding-bottom: 10px;
            }}
            .metrics {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 15px;
                margin-bottom: 15px;
            }}
            .metric {{
                background: #f9f9f9;
                padding: 15px;
                border-radius: 6px;
                text-align: center;
            }}
            .metric-label {{
                font-size: 12px;
                color: #666;
                margin-bottom: 5px;
            }}
            .metric-value {{
                font-size: 24px;
                font-weight: bold;
                color: #333;
            }}
            .metric-value.positive {{
                color: #28a745;
            }}
            .metric-value.negative {{
                color: #dc3545;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                font-size: 14px;
            }}
            th {{
                background: #f0f0f0;
                padding: 10px;
                text-align: left;
                font-weight: 600;
                border-bottom: 2px solid #667eea;
            }}
            td {{
                padding: 10px;
                border-bottom: 1px solid #eee;
            }}
            tr:hover {{
                background: #f9f9f9;
            }}
            .footer {{
                text-align: center;
                color: #999;
                font-size: 12px;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📊 Daily Trading Report</h1>
            <p>{timestamp}</p>
        </div>

        <!-- Account Summary -->
        <div class="section">
            <h2>Account Summary</h2>
            <div class="metrics">
                <div class="metric">
                    <div class="metric-label">Equity</div>
                    <div class="metric-value">${account.get('equity', 0):,.0f}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Buying Power</div>
                    <div class="metric-value">${account.get('buying_power', 0):,.0f}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Daily P&L</div>
                    <div class="metric-value {'positive' if daily_pnl >= 0 else 'negative'}">{daily_pnl:+.0f}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Win Rate</div>
                    <div class="metric-value">{month_metrics.get('win_rate', 0):.0f}%</div>
                </div>
            </div>
        </div>

        <!-- Today's Trades -->
        <div class="section">
            <h2>Today's Trades ({len(today_trades)})</h2>
            <table>
                <tr>
                    <th>Symbol</th>
                    <th>Entry</th>
                    <th>Exit</th>
                    <th>Days</th>
                    <th>Reason</th>
                    <th>Return %</th>
                </tr>
                {trades_html}
            </table>
        </div>

        <!-- Open Positions -->
        <div class="section">
            <h2>Open Positions ({len(open_positions)})</h2>
            <table>
                <tr>
                    <th>Symbol</th>
                    <th>Qty</th>
                    <th>Entry</th>
                    <th>Current</th>
                    <th>Unrealized %</th>
                </tr>
                {positions_html}
            </table>
        </div>

        <!-- Monthly Performance -->
        <div class="section">
            <h2>Monthly Performance (Last 30 Days)</h2>
            <div class="metrics">
                <div class="metric">
                    <div class="metric-label">Total Trades</div>
                    <div class="metric-value">{month_metrics.get('total_trades', 0)}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Wins</div>
                    <div class="metric-value positive">{month_metrics.get('winning_trades', 0)}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Losses</div>
                    <div class="metric-value negative">{month_metrics.get('losing_trades', 0)}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Total P&L</div>
                    <div class="metric-value {'positive' if month_metrics.get('total_pnl', 0) >= 0 else 'negative'}">
                        {month_metrics.get('total_pnl', 0):+,.0f}
                    </div>
                </div>
            </div>
        </div>

        <div class="footer">
            Minervini Trading Bot | Automated at {timestamp}
        </div>
    </body>
    </html>
    """

    return html


def send_email_report() -> None:
    """Generate and send the daily report email."""
    if not SENDER_EMAIL or not SENDER_PASSWORD or not REPORT_RECIPIENT:
        print("Email credentials not configured. Skipping email report.")
        return

    print("Generating daily report...")

    # Fetch data
    account = get_account_stats()
    today_trades, daily_pnl = get_today_trades()
    month_metrics = get_month_performance()
    open_positions = get_open_positions()

    # Generate HTML
    html = generate_email_html(today_trades, daily_pnl, account, month_metrics, open_positions)

    # Send email
    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"Daily Trading Report - {datetime.now(ET).strftime('%Y-%m-%d')}"
        msg["From"] = SENDER_EMAIL
        msg["To"] = REPORT_RECIPIENT
        msg.attach(MIMEText(html, "html"))

        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.sendmail(SENDER_EMAIL, REPORT_RECIPIENT, msg.as_string())

        print(f"✓ Daily report sent to {REPORT_RECIPIENT}")

    except Exception as e:
        print(f"✗ Error sending email: {e}")


if __name__ == "__main__":
    send_email_report()
