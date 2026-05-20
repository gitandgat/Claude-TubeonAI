"""
Compare Performance — Side-by-side comparison of Bot A, B, C
──────────────────────────────────────────────────────────
Queries bots.db and displays metrics for all three variants.

Usage:
  python compare_performance.py [--last-7] [--last-30] [--all-time] [--csv]

Default: --last-7
"""

import sqlite3
import sys
import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple
import pytz

ET = pytz.timezone("America/New_York")
DB_PATH = "bots.db"


def get_trades_by_variant(variant: str, days: int = 7) -> List[Dict]:
    """Fetch closed trades for a variant, optionally filtered by age."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    if days:
        cutoff = (datetime.now(ET) - timedelta(days=days)).isoformat()
        cursor.execute(
            """
            SELECT id, ticker, entry_price, entry_qty, exit_price, exit_qty,
                   profit_loss_pct, entry_date, exit_date
            FROM trades
            WHERE status = 'CLOSED' AND bot_variant = ?
            AND exit_date >= ?
            ORDER BY exit_date DESC
            """,
            (variant, cutoff),
        )
    else:
        cursor.execute(
            """
            SELECT id, ticker, entry_price, entry_qty, exit_price, exit_qty,
                   profit_loss_pct, entry_date, exit_date
            FROM trades
            WHERE status = 'CLOSED' AND bot_variant = ?
            ORDER BY exit_date DESC
            """,
            (variant,),
        )

    rows = cursor.fetchall()
    conn.close()

    return [
        {
            "id": row[0],
            "ticker": row[1],
            "entry_price": row[2],
            "entry_qty": row[3],
            "exit_price": row[4],
            "exit_qty": row[5],
            "pnl_pct": row[6],
            "entry_date": row[7],
            "exit_date": row[8],
        }
        for row in rows
    ]


def calculate_metrics(trades: List[Dict]) -> Dict:
    """Calculate performance metrics from trades."""
    if not trades:
        return {
            "total_trades": 0,
            "win_rate": 0.0,
            "profit_factor": 1.0,
            "avg_win_pct": 0.0,
            "avg_loss_pct": 0.0,
            "max_drawdown": 0.0,
            "cumulative_pnl": 0.0,
            "sharpe_ratio": 0.0,
        }

    pnl_list = [t["pnl_pct"] for t in trades]
    wins = [p for p in pnl_list if p > 0]
    losses = [p for p in pnl_list if p < 0]

    total_trades = len(pnl_list)
    win_rate = (len(wins) / total_trades * 100) if total_trades else 0.0
    avg_win = sum(wins) / len(wins) if wins else 0.0
    avg_loss = sum(losses) / len(losses) if losses else 0.0

    profit_factor = 1.0
    if losses:
        sum_wins = sum(wins) if wins else 0.0
        sum_losses = abs(sum(losses))
        profit_factor = sum_wins / sum_losses if sum_losses > 0 else 1.0

    cumulative_pnl = sum(pnl_list)
    max_drawdown = min(pnl_list) if pnl_list else 0.0

    # Sharpe ratio (simplified: std dev of returns vs return)
    if len(pnl_list) > 1:
        mean_return = sum(pnl_list) / len(pnl_list)
        variance = sum((x - mean_return) ** 2 for x in pnl_list) / len(pnl_list)
        std_dev = variance ** 0.5
        sharpe_ratio = (mean_return / std_dev) if std_dev > 0 else 0.0
    else:
        sharpe_ratio = 0.0

    return {
        "total_trades": total_trades,
        "win_rate": win_rate,
        "profit_factor": profit_factor,
        "avg_win_pct": avg_win,
        "avg_loss_pct": avg_loss,
        "max_drawdown": max_drawdown,
        "cumulative_pnl": cumulative_pnl,
        "sharpe_ratio": sharpe_ratio,
    }


def format_metrics_table(days: int = 7) -> str:
    """Format all three variants' metrics as a table."""
    variants = {"A": "Static", "B": "Adaptive", "C": "Hybrid"}
    period_str = f"Last {days} days" if days else "All-time"

    # Fetch trades and calculate metrics
    all_metrics = {}
    for variant, label in variants.items():
        trades = get_trades_by_variant(variant, days=days)
        metrics = calculate_metrics(trades)
        all_metrics[variant] = (label, metrics, len(trades))

    # Build table
    lines = []
    lines.append("╔══════════════════════════════════════════════════════════════════╗")
    lines.append("║            3-BOT PARALLEL PERFORMANCE COMPARISON                ║")
    lines.append(f"║                      {period_str.center(50)} ║")
    lines.append("╚══════════════════════════════════════════════════════════════════╝")
    lines.append("")

    # Header row
    header = "Metric              │ Bot A (Static)   │ Bot B (Adaptive) │ Bot C (Hybrid) "
    lines.append(header)
    lines.append("─" * 79)

    # Data rows
    metrics_to_show = [
        ("Trades", "total_trades", "d"),
        ("Win Rate", "win_rate", ".1f%"),
        ("Profit Factor", "profit_factor", ".2f"),
        ("Avg Win %", "avg_win_pct", ".2f%"),
        ("Avg Loss %", "avg_loss_pct", ".2f%"),
        ("Sharpe Ratio", "sharpe_ratio", ".2f"),
        ("Cumulative P&L", "cumulative_pnl", ".2f%"),
        ("Max Drawdown", "max_drawdown", ".2f%"),
    ]

    for label, key, fmt in metrics_to_show:
        parts = []
        for variant in ["A", "B", "C"]:
            _, metrics, _ = all_metrics[variant]
            value = metrics[key]

            if fmt == "d":
                formatted = f"{value:d}"
            elif fmt.endswith("%"):
                formatted = f"{value:{fmt[:-1]}}"
            else:
                formatted = f"{value:{fmt}}"

            parts.append(formatted.rjust(15))

        line = f"{label.ljust(19)}│{parts[0]} │{parts[1]} │{parts[2]}"
        lines.append(line)

    lines.append("")

    # Determine leader
    best_variant = None
    best_pnl = None
    for variant in ["A", "B", "C"]:
        _, metrics, _ = all_metrics[variant]
        if best_pnl is None or metrics["cumulative_pnl"] > best_pnl:
            best_pnl = metrics["cumulative_pnl"]
            best_variant = variant

    if best_variant:
        variant_name = variants[best_variant]
        lines.append(f"🏆 Bot {best_variant} ({variant_name}) is currently leading.")
    else:
        lines.append("No closed trades yet.")

    return "\n".join(lines)


def export_csv(days: int = 7, filename: str = "bot_comparison.csv") -> None:
    """Export metrics to CSV."""
    variants = ["A", "B", "C"]
    rows = []

    for variant in variants:
        trades = get_trades_by_variant(variant, days=days)
        metrics = calculate_metrics(trades)
        row = {
            "Variant": f"Bot {variant}",
            "Trades": metrics["total_trades"],
            "Win Rate (%)": f"{metrics['win_rate']:.1f}",
            "Profit Factor": f"{metrics['profit_factor']:.2f}",
            "Avg Win (%)": f"{metrics['avg_win_pct']:.2f}",
            "Avg Loss (%)": f"{metrics['avg_loss_pct']:.2f}",
            "Sharpe Ratio": f"{metrics['sharpe_ratio']:.2f}",
            "Cumulative P&L (%)": f"{metrics['cumulative_pnl']:.2f}",
            "Max Drawdown (%)": f"{metrics['max_drawdown']:.2f}",
        }
        rows.append(row)

    with open(filename, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"✓ Comparison exported to {filename}")


def main() -> None:
    """Main entry point."""
    days = 7  # Default
    export = False

    for arg in sys.argv[1:]:
        if arg == "--last-7":
            days = 7
        elif arg == "--last-30":
            days = 30
        elif arg == "--all-time":
            days = None
        elif arg == "--csv":
            export = True

    # Display table
    print(format_metrics_table(days))

    # Export if requested
    if export:
        period = f"last_7" if days == 7 else f"last_30" if days == 30 else "all_time"
        filename = f"bot_comparison_{period}.csv"
        export_csv(days=days, filename=filename)


if __name__ == "__main__":
    main()
