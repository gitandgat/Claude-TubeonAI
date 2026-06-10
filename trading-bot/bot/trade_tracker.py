"""
trade_tracker.py — Trade Journal (SQLite)
──────────────────────────────────────────

Tracks all trades (entry, exit, P&L) and daily signals for analysis.
Persists trade history for backtesting and performance review.
"""

import sqlite3
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict

log = logging.getLogger(__name__)


class TradeTracker:
    """SQLite-based trade journal and signal logger."""

    def __init__(self, db_path: str = "trading_bot.db"):
        """Initialize or connect to existing SQLite database."""
        if db_path == ":memory:":
            self.db_path = ":memory:"
            self._persistent_conn = sqlite3.connect(":memory:")
        else:
            self.db_path = Path(db_path)
            Path(db_path).parent.mkdir(parents=True, exist_ok=True)
            self._persistent_conn = None

        # Initialize schema immediately
        try:
            self._init_schema()
        except Exception as e:
            log.error(f"Failed to initialize schema: {e}")
            raise

    def _init_schema(self):
        """Create tables if they don't exist."""
        if self.db_path == ":memory:":
            conn = self._persistent_conn
        else:
            db_path = str(self.db_path)
            conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Trades table: tracks entry → exit lifecycle
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS trades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                entry_date TIMESTAMP NOT NULL,
                entry_price REAL NOT NULL,
                entry_qty INTEGER NOT NULL,
                stop_loss_level REAL NOT NULL,
                take_profit_level REAL NOT NULL,
                exit_date TIMESTAMP,
                exit_price REAL,
                exit_qty INTEGER,
                exit_reason TEXT,
                profit_loss REAL,
                profit_loss_pct REAL,
                days_held INTEGER,
                status TEXT DEFAULT 'OPEN',
                bot_variant TEXT DEFAULT 'A'
            )
        """
        )

        # Daily signals: log all signals for analysis
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS daily_signals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TIMESTAMP NOT NULL,
                ticker TEXT NOT NULL,
                price REAL NOT NULL,
                ma_20 REAL,
                ma_50 REAL,
                ma_200 REAL,
                rs_rank INTEGER,
                distance_52w REAL,
                volume_ratio REAL,
                trend_template_pass BOOLEAN,
                signal TEXT,
                kavout_rank TEXT,
                kavout_outlook TEXT,
                kavout_tech TEXT
            )
        """
        )

        # Bot adaptations: audit trail of parameter adjustments
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS bot_adaptations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bot_variant TEXT NOT NULL,
                adapted_at TIMESTAMP NOT NULL,
                old_params TEXT NOT NULL,
                new_params TEXT NOT NULL,
                trigger_metrics TEXT
            )
        """
        )

        # Migration: ensure trailing-stop columns exist (idempotent — runs every
        # startup so the schema self-heals even if the DB file is recreated)
        for column_def in (
            "highest_price_seen REAL",
            "trailing_stop_pct REAL DEFAULT 3.0",
        ):
            try:
                cursor.execute(f"ALTER TABLE trades ADD COLUMN {column_def}")
            except sqlite3.OperationalError:
                pass  # column already exists

        conn.commit()
        if self.db_path != ":memory:":
            conn.close()

    def open_trade(
        self,
        ticker: str,
        entry_date: datetime,
        entry_price: float,
        entry_qty: int,
        stop_loss_level: float,
        take_profit_level: float,
    ) -> int:
        """
        Log a new trade entry.

        Args:
            ticker: Stock symbol
            entry_date: Entry timestamp
            entry_price: Price per share at entry
            entry_qty: Number of shares bought
            stop_loss_level: Stop loss price (e.g., -7%)
            take_profit_level: Take profit price (e.g., +20%)

        Returns:
            Trade ID (used later to close the trade)
        """
        if self.db_path == ":memory:":
            conn = self._persistent_conn
        else:
            conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO trades
                (ticker, entry_date, entry_price, entry_qty, stop_loss_level,
                 take_profit_level, highest_price_seen, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'OPEN')
            """,
                (ticker, entry_date, entry_price, entry_qty, stop_loss_level,
                 take_profit_level, entry_price),
            )
            conn.commit()
            trade_id = cursor.lastrowid
            log.info(
                f"Trade {trade_id} OPENED: {ticker} {entry_qty} @ ${entry_price:.2f} "
                f"(stop=${stop_loss_level:.2f}, target=${take_profit_level:.2f})"
            )
            return trade_id
        except sqlite3.IntegrityError as e:
            log.warning(f"Trade for {ticker} on {entry_date} already exists: {e}")
            return -1
        finally:
            if self.db_path != ":memory:":
                conn.close()

    def update_trade_highest_price(self, trade_id: int, highest_price: float) -> None:
        """Persist the highest price seen for a trade (trailing-stop bookkeeping)."""
        if self.db_path == ":memory:":
            conn = self._persistent_conn
        else:
            conn = sqlite3.connect(str(self.db_path))
        try:
            conn.execute(
                "UPDATE trades SET highest_price_seen = ? WHERE id = ?",
                (highest_price, trade_id),
            )
            conn.commit()
        finally:
            if self.db_path != ":memory:":
                conn.close()

    def close_trade(
        self,
        trade_id: int,
        exit_date: datetime,
        exit_price: float,
        exit_qty: int,
        exit_reason: str,
    ) -> Optional[Dict]:
        """
        Log a trade exit and calculate P&L.

        Args:
            trade_id: Trade ID from open_trade()
            exit_date: Exit timestamp
            exit_price: Price per share at exit
            exit_qty: Number of shares sold
            exit_reason: "TAKE_PROFIT", "STOP_LOSS", "TIME_EXIT", or "MANUAL"

        Returns:
            Trade dict with P&L info, or None if trade not found
        """
        if self.db_path == ":memory:":
            conn = self._persistent_conn
        else:
            conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        try:
            # Get existing trade (explicit columns — schema-width independent)
            cursor.execute(
                """
                SELECT ticker, entry_date, entry_price, entry_qty
                FROM trades WHERE id = ?
            """,
                (trade_id,),
            )
            row = cursor.fetchone()
            if not row:
                log.error(f"Trade {trade_id} not found")
                return None

            ticker, entry_date_str, entry_price, entry_qty = row

            # Calculate P&L
            total_cost = entry_price * entry_qty
            exit_proceeds = exit_price * exit_qty
            profit_loss = exit_proceeds - total_cost
            profit_loss_pct = (profit_loss / total_cost) * 100 if total_cost > 0 else 0

            # Days held
            entry_dt = datetime.fromisoformat(entry_date_str)
            days_held = (exit_date - entry_dt).days

            # Update trade
            cursor.execute(
                """
                UPDATE trades
                SET exit_date = ?, exit_price = ?, exit_qty = ?, exit_reason = ?,
                    profit_loss = ?, profit_loss_pct = ?, days_held = ?, status = 'CLOSED'
                WHERE id = ?
            """,
                (exit_date, exit_price, exit_qty, exit_reason, profit_loss,
                 profit_loss_pct, days_held, trade_id),
            )
            conn.commit()

            result = {
                "trade_id": trade_id,
                "ticker": ticker,
                "entry_price": entry_price,
                "exit_price": exit_price,
                "profit_loss": profit_loss,
                "profit_loss_pct": profit_loss_pct,
                "days_held": days_held,
                "exit_reason": exit_reason,
            }

            log.info(
                f"Trade {trade_id} CLOSED: {ticker} @ ${exit_price:.2f} "
                f"({exit_reason}) | P&L: ${profit_loss:.2f} ({profit_loss_pct:+.2f}%)"
            )
            return result

        except Exception as e:
            log.error(f"Error closing trade {trade_id}: {e}")
            return None
        finally:
            if self.db_path != ":memory:":
                conn.close()

    def log_signal(
        self,
        date: datetime,
        ticker: str,
        price: float,
        ma_20: Optional[float] = None,
        ma_50: Optional[float] = None,
        ma_200: Optional[float] = None,
        rs_rank: Optional[int] = None,
        distance_52w: Optional[float] = None,
        volume_ratio: Optional[float] = None,
        trend_template_pass: Optional[bool] = None,
        signal: Optional[str] = None,
        kavout_rank: Optional[str] = None,
        kavout_outlook: Optional[str] = None,
        kavout_tech: Optional[str] = None,
    ) -> bool:
        """
        Log daily signal data for analysis.

        Returns:
            True if inserted, False if duplicate
        """
        if self.db_path == ":memory:":
            conn = self._persistent_conn
        else:
            conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO daily_signals
                (date, ticker, price, ma_20, ma_50, ma_200, rs_rank, distance_52w,
                 volume_ratio, trend_template_pass, signal, kavout_rank,
                 kavout_outlook, kavout_tech)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (date, ticker, price, ma_20, ma_50, ma_200, rs_rank, distance_52w,
                 volume_ratio, trend_template_pass, signal, kavout_rank,
                 kavout_outlook, kavout_tech),
            )
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False  # Duplicate already logged
        finally:
            if self.db_path != ":memory:":
                conn.close()

    def get_open_trades(self) -> List[Dict]:
        """Get all OPEN trades (for daily exit checks)."""
        if self.db_path == ":memory:":
            conn = self._persistent_conn
        else:
            conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT id, ticker, entry_date, entry_price, entry_qty,
                       stop_loss_level, take_profit_level,
                       highest_price_seen, trailing_stop_pct
                FROM trades
                WHERE status = 'OPEN'
                ORDER BY entry_date ASC
            """
            )
            rows = cursor.fetchall()
            result = [
                {
                    "trade_id": r[0],
                    "ticker": r[1],
                    "entry_date": datetime.fromisoformat(r[2]),
                    "entry_price": r[3],
                    "entry_qty": r[4],
                    "stop_loss_level": r[5],
                    "take_profit_level": r[6],
                    "highest_price_seen": r[7],
                    "trailing_stop_pct": r[8],
                }
                for r in rows
            ]
            return result
        finally:
            if self.db_path != ":memory:":
                conn.close()

    def get_pnl_summary(self, days: int = 30) -> Dict:
        """
        Get P&L summary over last N days.

        Returns:
            {
                "total_trades": int,
                "winning_trades": int,
                "losing_trades": int,
                "win_pct": float,
                "total_pnl": float,
                "avg_win_pct": float,
                "avg_loss_pct": float,
                "profit_factor": float,
                "max_drawdown_pct": float,
            }
        """
        if self.db_path == ":memory:":
            conn = self._persistent_conn
        else:
            conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()

        try:
            cutoff = datetime.now()
            # Get closed trades from last N days
            cursor.execute(
                """
                SELECT profit_loss_pct
                FROM trades
                WHERE status = 'CLOSED'
                  AND exit_date >= datetime('now', ? || ' days')
                ORDER BY exit_date
            """,
                (f"-{days}",),
            )

            pnl_pcts = [r[0] for r in cursor.fetchall()]

            if not pnl_pcts:
                return {
                    "total_trades": 0,
                    "winning_trades": 0,
                    "losing_trades": 0,
                    "win_pct": 0.0,
                    "total_pnl": 0.0,
                    "avg_win_pct": 0.0,
                    "avg_loss_pct": 0.0,
                    "profit_factor": 0.0,
                    "max_drawdown_pct": 0.0,
                }

            wins = [p for p in pnl_pcts if p > 0]
            losses = [p for p in pnl_pcts if p < 0]

            total_pnl = sum(pnl_pcts)
            avg_win = sum(wins) / len(wins) if wins else 0
            avg_loss = sum(losses) / len(losses) if losses else 0
            profit_factor = (
                (sum(wins) / abs(sum(losses))) if losses and sum(losses) != 0 else 0
            )

            # Running max drawdown
            running_max = 0
            max_dd = 0
            for pnl in pnl_pcts:
                running_max = max(running_max, pnl)
                dd = running_max - pnl
                max_dd = max(max_dd, dd)

            return {
                "total_trades": len(pnl_pcts),
                "winning_trades": len(wins),
                "losing_trades": len(losses),
                "win_pct": (len(wins) / len(pnl_pcts)) * 100 if pnl_pcts else 0,
                "total_pnl": total_pnl,
                "avg_win_pct": avg_win,
                "avg_loss_pct": avg_loss,
                "profit_factor": profit_factor,
                "max_drawdown_pct": max_dd,
            }

        finally:
            if self.db_path != ":memory:":
                conn.close()

    def print_summary(self, days: int = 30):
        """Print human-readable P&L summary."""
        summary = self.get_pnl_summary(days)
        print(f"\n{'─' * 60}")
        print(f"Trade Summary (last {days} days)")
        print(f"{'─' * 60}")
        print(f"Total trades:     {summary['total_trades']}")
        print(f"Wins:             {summary['winning_trades']}")
        print(f"Losses:           {summary['losing_trades']}")
        print(f"Win %:            {summary['win_pct']:.1f}%")
        print(f"Total P&L:        {summary['total_pnl']:+.2f}%")
        print(f"Avg win:          {summary['avg_win_pct']:+.2f}%")
        print(f"Avg loss:         {summary['avg_loss_pct']:+.2f}%")
        print(f"Profit factor:    {summary['profit_factor']:.2f}")
        print(f"Max drawdown:     {summary['max_drawdown_pct']:.2f}%")
        print(f"{'─' * 60}\n")
