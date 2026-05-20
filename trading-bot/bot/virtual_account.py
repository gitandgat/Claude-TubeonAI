"""
Virtual Account Simulator
────────────────────────────
Simulates a paper trading account for each bot variant (A, B, C).
No Alpaca API — uses Polygon prices and SQLite for state.
Each variant gets $100K initial capital, tracked independently.
"""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from trade_tracker import TradeTracker


class VirtualAccount:
    """
    Manages a virtual trading account for a bot variant.
    Tracks cash, positions, and P&L independently per bot.
    """

    def __init__(
        self,
        bot_variant: str,
        initial_equity: float = 100_000.0,
        db_path: str = "bots.db",
    ):
        """
        Initialize a virtual account for a specific bot variant.

        Args:
            bot_variant: 'A', 'B', or 'C'
            initial_equity: Starting cash (default $100K)
            db_path: Path to SQLite database (shared across all variants)
        """
        self.bot_variant = bot_variant
        self.initial_equity = initial_equity
        self.db_path = db_path
        self.tracker = TradeTracker(db_path)

        # Initialize schema and account state if needed
        self._init_schema()
        self._init_account()

    def _init_schema(self) -> None:
        """Create bot_accounts and bot_adaptations tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Ensure trades table exists and has bot_variant column
        cursor.execute("PRAGMA table_info(trades)")
        columns = {row[1] for row in cursor.fetchall()}

        if not columns:
            # trades table doesn't exist, create it (basic schema for testing)
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ticker TEXT NOT NULL,
                    entry_date TIMESTAMP,
                    entry_price REAL,
                    entry_qty INTEGER,
                    exit_date TIMESTAMP,
                    exit_price REAL,
                    exit_qty INTEGER,
                    stop_loss_level REAL,
                    take_profit_level REAL,
                    status TEXT DEFAULT 'OPEN',
                    profit_loss_pct REAL,
                    exit_reason TEXT,
                    bot_variant TEXT DEFAULT 'A'
                )
            """
            )
        elif "bot_variant" not in columns:
            cursor.execute("ALTER TABLE trades ADD COLUMN bot_variant TEXT DEFAULT 'A'")

        # Bot account state
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS bot_accounts (
                bot_variant TEXT PRIMARY KEY,
                initial_equity REAL DEFAULT 100000.0,
                cash REAL DEFAULT 100000.0,
                updated_at TIMESTAMP
            )
        """
        )

        # Adaptation audit trail
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS bot_adaptations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                bot_variant TEXT,
                adapted_at TIMESTAMP,
                old_params TEXT,
                new_params TEXT,
                trigger_metrics TEXT
            )
        """
        )

        conn.commit()
        conn.close()

    def _init_account(self) -> None:
        """Initialize account row if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT * FROM bot_accounts WHERE bot_variant = ?", (self.bot_variant,)
        )
        if cursor.fetchone() is None:
            cursor.execute(
                """
                INSERT INTO bot_accounts (bot_variant, initial_equity, cash, updated_at)
                VALUES (?, ?, ?, ?)
            """,
                (self.bot_variant, self.initial_equity, self.initial_equity, datetime.now()),
            )
            conn.commit()
        conn.close()

    @property
    def equity(self) -> float:
        """Total account value = cash + market value of open positions."""
        cash = self.cash
        position_value = 0.0

        for trade in self.get_open_trades():
            # Estimate position value using entry price (no real-time quote here)
            # In practice, bot should fetch current price before calling this
            position_value += (trade["entry_price"] or 0) * (trade["entry_qty"] or 0)

        return cash + position_value

    @property
    def cash(self) -> float:
        """Current cash balance."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT cash FROM bot_accounts WHERE bot_variant = ?", (self.bot_variant,))
        row = cursor.fetchone()
        conn.close()
        return row[0] if row else self.initial_equity

    @property
    def open_positions(self) -> Dict[str, Dict]:
        """Returns {ticker: {qty, entry_price, stop_loss, take_profit}}."""
        positions = {}
        for trade in self.get_open_trades():
            ticker = trade["ticker"]
            positions[ticker] = {
                "qty": trade["entry_qty"],
                "entry_price": trade["entry_price"],
                "stop_loss": trade["stop_loss_level"],
                "take_profit": trade["take_profit_level"],
            }
        return positions

    def buy(
        self,
        ticker: str,
        price: float,
        qty: int,
        stop_loss: float,
        take_profit: float,
    ) -> int:
        """
        Open a position. Deduct cost from cash.

        Returns:
            Trade ID
        """
        cost = price * qty

        # Validate cash
        if cost > self.cash:
            raise ValueError(f"Insufficient cash: need ${cost:,.0f}, have ${self.cash:,.0f}")

        # Deduct from cash
        self._update_cash(self.cash - cost)

        # Create trade record (TradeTracker handles this)
        trade_id = self.tracker.open_trade(
            ticker=ticker,
            entry_date=datetime.now(),
            entry_price=price,
            entry_qty=qty,
            stop_loss_level=stop_loss,
            take_profit_level=take_profit,
        )

        # Tag the trade with bot_variant
        self._tag_trade_with_variant(trade_id)

        return trade_id

    def sell(
        self,
        trade_id: int,
        ticker: str,
        price: float,
        qty: int,
        exit_reason: str,
    ) -> float:
        """
        Close a position. Add proceeds back to cash.

        Args:
            trade_id: ID from open_trade()
            ticker: Stock symbol
            price: Exit price
            qty: Shares to close
            exit_reason: 'STOP_LOSS', 'TAKE_PROFIT', 'TIME_EXIT', 'MANUAL'

        Returns:
            P&L percentage
        """
        proceeds = price * qty

        # Close in TradeTracker (calculates P&L)
        result = self.tracker.close_trade(
            trade_id=trade_id,
            exit_date=datetime.now(),
            exit_price=price,
            exit_qty=qty,
            exit_reason=exit_reason,
        )

        pnl_pct = result["profit_loss_pct"] if result else 0.0

        # Add proceeds back to cash
        self._update_cash(self.cash + proceeds)

        return pnl_pct

    def get_open_trades(self) -> List[Dict]:
        """Returns list of all open trades for this bot variant."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT id, ticker, entry_date, entry_price, entry_qty,
                   stop_loss_level, take_profit_level
            FROM trades
            WHERE status = 'OPEN' AND bot_variant = ?
            ORDER BY entry_date DESC
        """,
            (self.bot_variant,),
        )
        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "id": row[0],
                "ticker": row[1],
                "entry_date": row[2],
                "entry_price": row[3],
                "entry_qty": row[4],
                "stop_loss_level": row[5],
                "take_profit_level": row[6],
            }
            for row in rows
        ]

    def _update_cash(self, new_cash: float) -> None:
        """Update cash balance in bot_accounts."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE bot_accounts SET cash = ?, updated_at = ? WHERE bot_variant = ?",
            (new_cash, datetime.now(), self.bot_variant),
        )
        conn.commit()
        conn.close()

    def _tag_trade_with_variant(self, trade_id: int) -> None:
        """Add bot_variant to the trade record (for variant filtering)."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE trades SET bot_variant = ? WHERE id = ?",
            (self.bot_variant, trade_id),
        )
        conn.commit()
        conn.close()
