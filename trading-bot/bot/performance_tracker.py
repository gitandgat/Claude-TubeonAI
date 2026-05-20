"""
performance_tracker.py — Daily Performance Metrics
────────────────────────────────────────────────────

Tracks bot performance over time:
- Win rate, profit factor, Sharpe ratio
- Max drawdown, cumulative return
- Daily P&L tracking for validation

Usage:
    python bot/performance_tracker.py              # Print today's summary
    python bot/performance_tracker.py --last-7     # Last 7 days
    python bot/performance_tracker.py --last-30    # Last 30 days
    python bot/performance_tracker.py --csv        # Export to CSV
"""

from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple
import sqlite3
import sys
import csv

import pytz
from alpaca.trading.client import TradingClient
from dotenv import load_dotenv
import os
import math

load_dotenv()

ALPACA_API_KEY = os.getenv("ALPACA_API_KEY")
ALPACA_SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
PAPER_TRADING = os.getenv("PAPER_TRADING", "true").lower() == "true"

DB_FILE = Path(__file__).parent.parent / "trading_bot.db"
ET = pytz.timezone("America/New_York")


def get_client() -> TradingClient:
    """Create Alpaca trading client."""
    return TradingClient(ALPACA_API_KEY, ALPACA_SECRET_KEY, paper=PAPER_TRADING)


def get_account_equity_history(days: int = 30) -> List[Dict]:
    """
    Get daily closing equity for the past N days.
    Returns list of {'date': date, 'equity': float}
    """
    try:
        client = get_client()
        account = client.get_account()

        # For now, return current equity only
        # A production system would track daily snapshots via portfolio history
        today = datetime.now(ET).strftime("%Y-%m-%d")
        return [{
            "date": today,
            "equity": float(account.equity),
        }]
    except Exception as e:
        print(f"Error fetching equity history: {e}")
        return []


def calculate_metrics(days: int = 30) -> Dict:
    """Calculate key performance metrics."""
    try:
        if not DB_FILE.exists():
            return {}

        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cutoff_date = (datetime.now(ET) - timedelta(days=days)).isoformat()

        # Fetch all closed trades in period
        cursor.execute(f"""
            SELECT * FROM trades
            WHERE exit_date >= ? AND status = 'CLOSED'
            ORDER BY exit_date ASC
        """, (cutoff_date,))

        trades = [dict(row) for row in cursor.fetchall()]

        if not trades:
            conn.close()
            return {
                "period_days": days,
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate_pct": 0.0,
                "avg_win_pct": 0.0,
                "avg_loss_pct": 0.0,
                "profit_factor": 0.0,
                "total_pnl": 0.0,
                "avg_pnl_pct": 0.0,
                "max_winning_trade_pct": 0.0,
                "max_losing_trade_pct": 0.0,
                "sharpe_ratio": 0.0,
                "cumulative_return_pct": 0.0,
            }

        # Calculate trade statistics
        wins = [t for t in trades if t["profit_loss"] > 0]
        losses = [t for t in trades if t["profit_loss"] < 0]
        breakevens = [t for t in trades if t["profit_loss"] == 0]

        total_trades = len(trades)
        win_count = len(wins)
        loss_count = len(losses)
        win_rate = (win_count / total_trades * 100) if total_trades > 0 else 0

        # Profit metrics
        total_wins = sum(t["profit_loss"] for t in wins) if wins else 0.0
        total_losses = sum(t["profit_loss"] for t in losses) if losses else 0.0
        total_pnl = total_wins + total_losses

        avg_win_pct = (sum(t["profit_loss_pct"] for t in wins) / len(wins)) if wins else 0.0
        avg_loss_pct = (sum(t["profit_loss_pct"] for t in losses) / len(losses)) if losses else 0.0
        avg_pnl_pct = (sum(t["profit_loss_pct"] for t in trades) / len(trades)) if trades else 0.0

        # Profit factor: sum of wins / absolute sum of losses
        profit_factor = (abs(total_wins) / abs(total_losses)) if total_losses != 0 else 0.0

        # Max win/loss trades
        max_win_pct = max([t["profit_loss_pct"] for t in wins]) if wins else 0.0
        max_loss_pct = min([t["profit_loss_pct"] for t in losses]) if losses else 0.0

        # Sharpe ratio (approximation: daily returns std dev)
        pnl_pcts = [t["profit_loss_pct"] for t in trades]
        if len(pnl_pcts) > 1:
            mean_return = sum(pnl_pcts) / len(pnl_pcts)
            variance = sum((x - mean_return) ** 2 for x in pnl_pcts) / len(pnl_pcts)
            std_dev = math.sqrt(variance)

            # Annualize (252 trading days)
            annual_std = std_dev * math.sqrt(252)
            annual_return = mean_return * 252

            # Risk-free rate ~5% (2026)
            risk_free_rate = 5.0

            sharpe = (annual_return - risk_free_rate) / annual_std if annual_std > 0 else 0.0
        else:
            sharpe = 0.0

        # Cumulative return
        cumulative_return = (total_wins + total_losses) / abs(total_losses) * 100 if total_losses != 0 else 0.0

        conn.close()

        return {
            "period_days": days,
            "total_trades": total_trades,
            "winning_trades": win_count,
            "losing_trades": loss_count,
            "breakeven_trades": len(breakevens),
            "win_rate_pct": win_rate,
            "avg_win_pct": avg_win_pct,
            "avg_loss_pct": avg_loss_pct,
            "profit_factor": profit_factor,
            "total_pnl": total_pnl,
            "avg_pnl_pct": avg_pnl_pct,
            "max_winning_trade_pct": max_win_pct,
            "max_losing_trade_pct": max_loss_pct,
            "sharpe_ratio": sharpe,
            "cumulative_return_pct": cumulative_return,
        }

    except Exception as e:
        print(f"Error calculating metrics: {e}")
        return {}


def print_metrics(metrics: Dict, period_label: str = "30 Days") -> None:
    """Pretty-print performance metrics."""
    if not metrics:
        print(f"No trades in {period_label}")
        return

    print(f"\n{'=' * 60}")
    print(f"PERFORMANCE SUMMARY — {period_label.upper()}")
    print(f"{'=' * 60}\n")

    print(f"Trade Statistics:")
    print(f"  Total Trades:      {metrics['total_trades']}")
    print(f"  Wins:              {metrics['winning_trades']} ({metrics['win_rate_pct']:.1f}%)")
    print(f"  Losses:            {metrics['losing_trades']}")
    print(f"  Breakevens:        {metrics['breakeven_trades']}\n")

    print(f"Returns:")
    print(f"  Avg Win:           {metrics['avg_win_pct']:+.2f}%")
    print(f"  Avg Loss:          {metrics['avg_loss_pct']:+.2f}%")
    print(f"  Max Win:           {metrics['max_winning_trade_pct']:+.2f}%")
    print(f"  Max Loss:          {metrics['max_losing_trade_pct']:+.2f}%")
    print(f"  Avg Trade:         {metrics['avg_pnl_pct']:+.2f}%\n")

    print(f"Risk Metrics:")
    print(f"  Profit Factor:     {metrics['profit_factor']:.2f} (ideal: >1.5)")
    print(f"  Sharpe Ratio:      {metrics['sharpe_ratio']:.2f} (ideal: >1.0)")
    print(f"  Cumulative Return: {metrics['cumulative_return_pct']:+.2f}%\n")

    print(f"Total P&L:           ${metrics['total_pnl']:+,.2f}\n")


def export_to_csv(days: int = 30, filename: str = "bot_performance.csv") -> None:
    """Export trade history to CSV."""
    try:
        if not DB_FILE.exists():
            print("No trades to export")
            return

        conn = sqlite3.connect(DB_FILE)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        cutoff_date = (datetime.now(ET) - timedelta(days=days)).isoformat()

        cursor.execute(f"""
            SELECT
                ticker, entry_date, entry_price, entry_qty,
                exit_date, exit_price, exit_reason,
                profit_loss, profit_loss_pct, days_held
            FROM trades
            WHERE exit_date >= ? AND status = 'CLOSED'
            ORDER BY exit_date ASC
        """, (cutoff_date,))

        rows = cursor.fetchall()
        conn.close()

        output_path = Path(__file__).parent.parent / filename
        with open(output_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "Ticker", "Entry Date", "Entry Price", "Entry Qty",
                "Exit Date", "Exit Price", "Exit Reason",
                "P&L ($)", "P&L (%)", "Days Held"
            ])
            for row in rows:
                writer.writerow([
                    row["ticker"],
                    row["entry_date"],
                    f"{row['entry_price']:.2f}",
                    row["entry_qty"],
                    row["exit_date"],
                    f"{row['exit_price']:.2f}",
                    row["exit_reason"],
                    f"{row['profit_loss']:.2f}",
                    f"{row['profit_loss_pct']:.2f}",
                    row["days_held"],
                ])

        print(f"✓ Exported {len(rows)} trades to {output_path}")

    except Exception as e:
        print(f"Error exporting: {e}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--last-7":
            metrics = calculate_metrics(days=7)
            print_metrics(metrics, "7 Days")
        elif sys.argv[1] == "--last-30":
            metrics = calculate_metrics(days=30)
            print_metrics(metrics, "30 Days")
        elif sys.argv[1] == "--csv":
            export_to_csv(days=30)
        else:
            print(f"Unknown option: {sys.argv[1]}")
            print("Usage: performance_tracker.py [--last-7|--last-30|--csv]")
    else:
        metrics = calculate_metrics(days=1)
        print_metrics(metrics, "Today")

        metrics_7 = calculate_metrics(days=7)
        if metrics_7["total_trades"] > 0:
            print_metrics(metrics_7, "Last 7 Days")
