"""
Adaptation Engine
─────────────────
Analyzes trading results and suggests parameter adjustments for Bot B and Bot C.
Keeps all adjustments within safe bounds to prevent overfitting.
"""

import json
import sqlite3
from datetime import datetime
from typing import Dict, Optional

from trade_tracker import TradeTracker


class AdaptationEngine:
    """
    Reads recent trading metrics and outputs bounded parameter adjustments.
    Used by Bot B (full adaptive) and Bot C (hybrid adaptive).
    """

    def __init__(self, bot_variant: str, db_path: str = "bots.db"):
        """
        Initialize the adaptation engine for a bot variant.

        Args:
            bot_variant: 'A', 'B', or 'C'
            db_path: Path to SQLite database
        """
        self.bot_variant = bot_variant
        self.db_path = db_path
        self.tracker = TradeTracker(db_path)

    def get_recent_metrics(self, lookback_trades: int = 10) -> Dict:
        """
        Analyze the last N trades to compute metrics.

        Returns:
            {
                'total_trades': int,
                'win_rate': float (0-100),
                'profit_factor': float,
                'avg_win_pct': float,
                'avg_loss_pct': float,
                'max_drawdown_pct': float,
                'avg_days_held': float
            }
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Get last N closed trades
        cursor.execute(
            """
            SELECT profit_loss_pct, days_held FROM trades
            WHERE status = 'CLOSED' AND bot_variant = ?
            ORDER BY exit_date DESC
            LIMIT ?
        """,
            (self.bot_variant, lookback_trades),
        )
        trades = cursor.fetchall()
        conn.close()

        if not trades:
            return {
                "total_trades": 0,
                "win_rate": 50.0,
                "profit_factor": 1.0,
                "avg_win_pct": 0.0,
                "avg_loss_pct": 0.0,
                "max_drawdown_pct": 0.0,
                "avg_days_held": 0.0,
            }

        pnl_list = [trade[0] for trade in trades]
        days_list = [trade[1] or 0 for trade in trades]

        wins = [p for p in pnl_list if p > 0]
        losses = [p for p in pnl_list if p < 0]

        win_rate = (len(wins) / len(pnl_list) * 100) if pnl_list else 0.0
        avg_win = sum(wins) / len(wins) if wins else 0.0
        avg_loss = sum(losses) / len(losses) if losses else 0.0

        # Profit factor = sum(wins) / abs(sum(losses))
        profit_factor = 1.0
        if losses:
            sum_wins = sum(wins) if wins else 0.0
            sum_losses = abs(sum(losses))
            profit_factor = sum_wins / sum_losses if sum_losses != 0 else 1.0

        # Max drawdown (simple: largest losing streak)
        max_dd = min(pnl_list) if pnl_list else 0.0

        avg_days = sum(days_list) / len(days_list) if days_list else 0.0

        return {
            "total_trades": len(trades),
            "win_rate": win_rate,
            "profit_factor": profit_factor,
            "avg_win_pct": avg_win,
            "avg_loss_pct": avg_loss,
            "max_drawdown_pct": max_dd,
            "avg_days_held": avg_days,
        }

    def suggest_b_params(self, current_params: Dict) -> Dict:
        """
        Bot B: Adaptive parameter tuning.
        Adjusts rs_threshold, atr_multiplier, vix_max, max_risk_pct.

        Bounds:
            - rs_threshold: 60-85 (default 70)
            - atr_multiplier: 1.5-3.0 (default 2.0)
            - vix_max: 25-40 (default 30)
            - max_risk_pct: 0.5-2.0 (default 1.25)

        Logic:
            - win_rate < 40%: tighten RS (+5), tighten VIX (-5)
            - win_rate > 65%: relax RS (-5), relax VIX (+5)
            - profit_factor < 1.0: widen stops (atr +0.5)
            - profit_factor > 2.0: tighten stops (atr -0.3)
            - max_drawdown > 8%: reduce risk (-0.25)
            - max_drawdown < 2%: increase risk (+0.25)
        """
        metrics = self.get_recent_metrics()

        new_params = {
            "rs_threshold": current_params.get("rs_threshold", 70),
            "atr_multiplier": current_params.get("atr_multiplier", 2.0),
            "vix_max": current_params.get("vix_max", 30),
            "vix_min": current_params.get("vix_min", 10),
            "max_risk_pct": current_params.get("max_risk_pct", 1.25),
            "take_profit_pct": current_params.get("take_profit_pct", 20.0),
            "max_open_positions": current_params.get("max_open_positions", 5),
            "max_position_pct": current_params.get("max_position_pct", 20.0),
        }

        wr = metrics["win_rate"]
        pf = metrics["profit_factor"]
        dd = metrics["max_drawdown_pct"]

        # Win rate adjustments
        if wr < 40:
            new_params["rs_threshold"] += 5
            new_params["vix_max"] -= 5
        elif wr > 65:
            new_params["rs_threshold"] -= 5
            new_params["vix_max"] += 5

        # Profit factor adjustments
        if pf < 1.0:
            new_params["atr_multiplier"] += 0.5
        elif pf > 2.0:
            new_params["atr_multiplier"] -= 0.3

        # Drawdown adjustments
        if dd > 8:
            new_params["max_risk_pct"] -= 0.25
        elif dd < 2 and dd > 0:
            new_params["max_risk_pct"] += 0.25

        # Apply bounds
        new_params["rs_threshold"] = max(60, min(85, new_params["rs_threshold"]))
        new_params["atr_multiplier"] = max(1.5, min(3.0, new_params["atr_multiplier"]))
        new_params["vix_max"] = max(25, min(40, new_params["vix_max"]))
        new_params["max_risk_pct"] = max(0.5, min(2.0, new_params["max_risk_pct"]))

        return new_params

    def suggest_c_params(self, current_params: Dict) -> Dict:
        """
        Bot C: Hybrid (fixed Minervini, adaptive position sizing).
        Only adjusts max_risk_pct based on recent performance.

        Bounds:
            - max_risk_pct: 0.5-2.0 (default 1.25)

        Logic:
            - drawdown > 5%: reduce to 0.75%
            - win_rate > 60% AND drawdown < 3%: increase to 1.5%
            - otherwise: return to default 1.25%
        """
        metrics = self.get_recent_metrics()

        new_params = {
            "max_risk_pct": current_params.get("max_risk_pct", 1.25),
        }

        wr = metrics["win_rate"]
        dd = metrics["max_drawdown_pct"]

        if dd > 5:
            new_params["max_risk_pct"] = 0.75
        elif wr > 60 and dd < 3:
            new_params["max_risk_pct"] = 1.5

        # Bounds
        new_params["max_risk_pct"] = max(0.5, min(2.0, new_params["max_risk_pct"]))

        return new_params

    def log_adaptation(
        self,
        old_params: Dict,
        new_params: Dict,
        metrics: Optional[Dict] = None,
    ) -> None:
        """
        Log the adaptation event to bot_adaptations table for audit trail.

        Args:
            old_params: Previous parameter values
            new_params: New parameter values
            metrics: Triggering metrics (optional)
        """
        if metrics is None:
            metrics = self.get_recent_metrics()

        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            INSERT INTO bot_adaptations
            (bot_variant, adapted_at, old_params, new_params, trigger_metrics)
            VALUES (?, ?, ?, ?, ?)
        """,
            (
                self.bot_variant,
                datetime.now(),
                json.dumps(old_params),
                json.dumps(new_params),
                json.dumps(metrics),
            ),
        )

        conn.commit()
        conn.close()

    def get_adaptation_history(self, limit: int = 10) -> list:
        """Get recent adaptation events for this variant."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT adapted_at, old_params, new_params FROM bot_adaptations
            WHERE bot_variant = ?
            ORDER BY adapted_at DESC
            LIMIT ?
        """,
            (self.bot_variant, limit),
        )

        rows = cursor.fetchall()
        conn.close()

        return [
            {
                "adapted_at": row[0],
                "old_params": json.loads(row[1]),
                "new_params": json.loads(row[2]),
            }
            for row in rows
        ]
