"""
dashboard.py — Real-Time Trading Dashboard
───────────────────────────────────────────

Generates an HTML dashboard showing:
- Open positions with live P&L
- Recent closed trades (today/week/month)
- Account equity, drawdown, win rate
- Daily signals and screening results
- Sector rotation metrics

Usage:
    python bot/dashboard.py                # Generate dashboard.html
    open dashboard.html                     # Open in browser
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import sqlite3

import pytz
from alpaca.trading.client import TradingClient
from dotenv import load_dotenv
import os

load_dotenv()

ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
PAPER_TRADING = os.getenv("PAPER_TRADING", "true").lower() == "true"
DB_FILE = Path(__file__).parent.parent / "trading_bot.db"
DASHBOARD_FILE = Path(__file__).parent.parent / "dashboard.html"

ET = pytz.timezone("America/New_York")


def get_client() -> TradingClient:
    """Create Alpaca trading client."""
    return TradingClient(ALPACA_API_KEY, ALPACA_SECRET_KEY, paper=PAPER_TRADING)


def get_account_stats() -> Dict:
    """Get account balance and stats."""
    try:
        client = get_client()
        account = client.get_account()

        equity = float(account.equity)
        buying_power = float(account.buying_power)
        cash = float(account.cash)

        return {
            "equity": equity,
            "buying_power": buying_power,
            "cash": cash,
            "status": account.status,
        }
    except Exception as e:
        print(f"Error fetching account stats: {e}")
        return {}


def get_open_positions() -> List[Dict]:
    """Get open positions with current prices."""
    try:
        client = get_client()
        positions = []
        for pos in client.get_all_positions():
            positions.append({
                "symbol": pos.symbol,
                "qty": float(pos.qty),
                "avg_fill_price": float(pos.avg_fill_price),
                "current_price": float(pos.current_price),
                "unrealized_pl": float(pos.unrealized_pl),
                "unrealized_plpc": float(pos.unrealized_plpc),
            })
        return positions
    except Exception as e:
        print(f"Error fetching positions: {e}")
        return []


def get_recent_trades(days: int = 7) -> Tuple[List[Dict], float, float]:
    """
    Get recent closed trades from database.

    Returns: (trades, win_rate, profit_factor)
    """
    trades = []
    try:
        if not DB_FILE.exists():
            return [], 0.0, 0.0

        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        cursor.execute(f"""
            SELECT * FROM trades
            WHERE exit_date >= ? AND status = 'CLOSED'
            ORDER BY exit_date DESC
        """, (cutoff_date,))

        for row in cursor.fetchall():
            trades.append({
                "ticker": row["ticker"],
                "entry_date": row["entry_date"],
                "entry_price": row["entry_price"],
                "exit_date": row["exit_date"],
                "exit_price": row["exit_price"],
                "exit_reason": row["exit_reason"],
                "profit_loss": row["profit_loss"],
                "profit_loss_pct": row["profit_loss_pct"],
                "days_held": row["days_held"],
            })

        # Calculate stats
        if trades:
            wins = sum(1 for t in trades if t["profit_loss"] > 0)
            losses = sum(1 for t in trades if t["profit_loss"] < 0)
            win_rate = (wins / len(trades)) * 100 if trades else 0

            avg_win = sum(t["profit_loss_pct"] for t in trades if t["profit_loss"] > 0) / wins if wins > 0 else 0
            avg_loss = abs(sum(t["profit_loss_pct"] for t in trades if t["profit_loss"] < 0)) / losses if losses > 0 else 0
            profit_factor = (avg_win * wins) / (avg_loss * losses) if avg_loss > 0 else 0
        else:
            win_rate = 0
            profit_factor = 0

        conn.close()
        return trades, win_rate, profit_factor

    except Exception as e:
        print(f"Error fetching trades: {e}")
        return [], 0.0, 0.0


def get_daily_signals() -> Dict:
    """Get today's screening results."""
    try:
        if not DB_FILE.exists():
            return {}

        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        today = datetime.now(ET).strftime("%Y-%m-%d")

        cursor.execute(f"""
            SELECT signal, COUNT(*) as count
            FROM daily_signals
            WHERE DATE(date) = ?
            GROUP BY signal
        """, (today,))

        signals = {}
        for row in cursor.fetchall():
            signals[row["signal"]] = row["count"]

        conn.close()
        return signals

    except Exception as e:
        print(f"Error fetching daily signals: {e}")
        return {}


def generate_html_dashboard() -> str:
    """Generate HTML for the dashboard."""
    account = get_account_stats()
    open_positions = get_open_positions()
    recent_trades, win_rate, profit_factor = get_recent_trades(days=30)
    daily_signals = get_daily_signals()

    # Format currency
    def fmt_currency(val: float) -> str:
        return f"${val:,.2f}"

    def fmt_percent(val: float) -> str:
        color = "green" if val >= 0 else "red"
        return f"<span style='color:{color}; font-weight:bold;'>{val:+.2f}%</span>"

    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Minervini Trading Bot Dashboard</title>
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                margin: 0;
                padding: 20px;
                background: #f5f5f5;
                color: #333;
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
                font-size: 32px;
            }}
            .header p {{
                margin: 5px 0 0 0;
                opacity: 0.9;
            }}
            .grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
                gap: 20px;
                margin-bottom: 20px;
            }}
            .card {{
                background: white;
                border-radius: 8px;
                padding: 20px;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            }}
            .card h2 {{
                margin: 0 0 15px 0;
                font-size: 18px;
                border-bottom: 2px solid #667eea;
                padding-bottom: 10px;
            }}
            .stat {{
                display: flex;
                justify-content: space-between;
                padding: 8px 0;
                border-bottom: 1px solid #eee;
            }}
            .stat:last-child {{
                border-bottom: none;
            }}
            .stat-label {{
                font-weight: 500;
                color: #666;
            }}
            .stat-value {{
                font-weight: bold;
                color: #333;
                font-size: 16px;
            }}
            .positive {{
                color: #28a745;
            }}
            .negative {{
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
            .badge {{
                display: inline-block;
                padding: 4px 8px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
            }}
            .badge-success {{
                background: #d4edda;
                color: #155724;
            }}
            .badge-danger {{
                background: #f8d7da;
                color: #721c24;
            }}
            .badge-warning {{
                background: #fff3cd;
                color: #856404;
            }}
            .last-updated {{
                text-align: center;
                color: #999;
                font-size: 12px;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>📈 Minervini Trading Bot Dashboard</h1>
            <p>Real-time portfolio tracking and performance metrics</p>
        </div>

        <div class="grid">
            <!-- Account Stats Card -->
            <div class="card">
                <h2>Account Statistics</h2>
                <div class="stat">
                    <span class="stat-label">Equity</span>
                    <span class="stat-value">{fmt_currency(account.get('equity', 0))}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Buying Power</span>
                    <span class="stat-value">{fmt_currency(account.get('buying_power', 0))}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Cash</span>
                    <span class="stat-value">{fmt_currency(account.get('cash', 0))}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Status</span>
                    <span class="stat-value">{account.get('status', 'unknown')}</span>
                </div>
            </div>

            <!-- Performance Card -->
            <div class="card">
                <h2>Performance (30 Days)</h2>
                <div class="stat">
                    <span class="stat-label">Total Trades</span>
                    <span class="stat-value">{len(recent_trades)}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Win Rate</span>
                    <span class="stat-value">{win_rate:.1f}%</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Profit Factor</span>
                    <span class="stat-value">{profit_factor:.2f}</span>
                </div>
            </div>

            <!-- Daily Signals Card -->
            <div class="card">
                <h2>Today's Signals</h2>
                <div class="stat">
                    <span class="stat-label">Buy Signals</span>
                    <span class="stat-value">{daily_signals.get('BUY', 0)}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Hold</span>
                    <span class="stat-value">{daily_signals.get('HOLD', 0)}</span>
                </div>
                <div class="stat">
                    <span class="stat-label">Sell Signals</span>
                    <span class="stat-value">{daily_signals.get('SELL', 0)}</span>
                </div>
            </div>
        </div>

        <!-- Open Positions Section -->
        <div class="card">
            <h2>Open Positions</h2>
            {self._render_positions_table(open_positions) if open_positions else '<p style="color: #999;">No open positions</p>'}
        </div>

        <!-- Recent Trades Section -->
        <div class="card">
            <h2>Recent Closed Trades (30 Days)</h2>
            {self._render_trades_table(recent_trades) if recent_trades else '<p style="color: #999;">No closed trades</p>'}
        </div>

        <div class="last-updated">
            Last Updated: {datetime.now(ET).strftime('%Y-%m-%d %H:%M:%S %Z')}
        </div>
    </body>
    </html>
    """

    return html


def _render_positions_table(self, positions: List[Dict]) -> str:
    """Render open positions table."""
    if not positions:
        return '<p style="color: #999;">No open positions</p>'

    rows = ""
    for pos in positions:
        pl_pct = pos["unrealized_plpc"] * 100
        pl_class = "positive" if pl_pct >= 0 else "negative"
        rows += f"""
        <tr>
            <td><strong>{pos['symbol']}</strong></td>
            <td>{pos['qty']:.0f}</td>
            <td>${pos['avg_fill_price']:.2f}</td>
            <td>${pos['current_price']:.2f}</td>
            <td class="{pl_class}">${pos['unrealized_pl']:,.2f}</td>
            <td class="{pl_class}">{pl_pct:+.2f}%</td>
        </tr>
        """

    return f"""
    <table>
        <tr>
            <th>Symbol</th>
            <th>Qty</th>
            <th>Entry</th>
            <th>Current</th>
            <th>Unrealized P&L</th>
            <th>Return %</th>
        </tr>
        {rows}
    </table>
    """


def _render_trades_table(self, trades: List[Dict]) -> str:
    """Render recent trades table."""
    if not trades:
        return '<p style="color: #999;">No closed trades</p>'

    rows = ""
    for trade in trades:
        pl_class = "positive" if trade["profit_loss"] >= 0 else "negative"
        badge_class = "badge-success" if trade["profit_loss"] >= 0 else ("badge-warning" if trade["exit_reason"] == "TIME_EXIT" else "badge-danger")
        rows += f"""
        <tr>
            <td><strong>{trade['ticker']}</strong></td>
            <td>${trade['entry_price']:.2f}</td>
            <td>${trade['exit_price']:.2f}</td>
            <td>{trade['days_held']} days</td>
            <td><span class="badge {badge_class}">{trade['exit_reason']}</span></td>
            <td class="{pl_class}">{trade['profit_loss_pct']:+.2f}%</td>
        </tr>
        """

    return f"""
    <table>
        <tr>
            <th>Symbol</th>
            <th>Entry</th>
            <th>Exit</th>
            <th>Days</th>
            <th>Reason</th>
            <th>Return %</th>
        </tr>
        {rows}
    </table>
    """


def generate_dashboard() -> None:
    """Generate and save dashboard HTML file."""
    print(f"Generating dashboard...")

    # Create temporary class instance for helper methods
    class Dashboard:
        def __init__(self):
            pass

    dashboard_obj = Dashboard()

    # Add helper methods
    dashboard_obj._render_positions_table = _render_positions_table.__get__(dashboard_obj)
    dashboard_obj._render_trades_table = _render_trades_table.__get__(dashboard_obj)

    html = generate_html_dashboard()

    with open(DASHBOARD_FILE, "w") as f:
        f.write(html)

    print(f"✓ Dashboard saved to {DASHBOARD_FILE}")
    print(f"  Open in browser: open {DASHBOARD_FILE}")


if __name__ == "__main__":
    generate_dashboard()
