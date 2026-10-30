"""Run a strategy over historical bars with the paper broker and report results."""

import math
from dataclasses import dataclass

from .broker import PaperBroker
from .risk import RiskManager
from .strategy import BUY, SELL


@dataclass
class Result:
    start_equity: float
    end_equity: float
    total_return: float
    buy_and_hold_return: float
    max_drawdown: float
    sharpe: float
    num_trades: int
    win_rate: float
    trades: list
    equity_curve: list


def run_backtest(bars, strategy, cash=10_000.0, fee_rate=0.001, risk=None):
    risk = risk or RiskManager()
    broker = PaperBroker(cash=cash, fee_rate=fee_rate)
    closes = []
    equity_curve = []

    for bar in bars:
        closes.append(bar.close)
        price = bar.close

        if broker.in_position:
            reason = risk.exit_reason(broker.entry_price, price)
            if reason:
                broker.sell_all(bar.date, price, reason)

        signal = strategy.signal(closes)
        if signal == BUY and not broker.in_position:
            qty = risk.position_size(broker.cash, price, fee_rate)
            broker.buy(bar.date, price, qty)
        elif signal == SELL and broker.in_position:
            broker.sell_all(bar.date, price)

        equity_curve.append(broker.equity(price))

    if broker.in_position:
        broker.sell_all(bars[-1].date, bars[-1].close, "end_of_data")
        equity_curve[-1] = broker.equity(bars[-1].close)

    return Result(
        start_equity=cash,
        end_equity=equity_curve[-1],
        total_return=equity_curve[-1] / cash - 1,
        buy_and_hold_return=bars[-1].close / bars[0].close - 1,
        max_drawdown=max_drawdown(equity_curve),
        sharpe=sharpe_ratio(equity_curve),
        num_trades=len(broker.trades),
        win_rate=win_rate(broker.trades),
        trades=broker.trades,
        equity_curve=equity_curve,
    )


def max_drawdown(equity_curve):
    peak = equity_curve[0]
    worst = 0.0
    for value in equity_curve:
        peak = max(peak, value)
        worst = min(worst, value / peak - 1)
    return worst


def sharpe_ratio(equity_curve, periods_per_year=252):
    returns = [b / a - 1 for a, b in zip(equity_curve, equity_curve[1:]) if a > 0]
    if len(returns) < 2:
        return 0.0
    mean = sum(returns) / len(returns)
    var = sum((r - mean) ** 2 for r in returns) / (len(returns) - 1)
    if var == 0:
        return 0.0
    return mean / math.sqrt(var) * math.sqrt(periods_per_year)


def win_rate(trades):
    """Share of round trips (buy then sell) that made money after fees."""
    wins = rounds = 0
    cost = None
    for t in trades:
        if t.side == "buy":
            cost = t.qty * t.price + t.fee
        elif cost is not None:
            rounds += 1
            wins += (t.qty * t.price - t.fee) > cost
            cost = None
    return wins / rounds if rounds else 0.0
