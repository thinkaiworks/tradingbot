"""Command line entry point: python -m bot --help"""

import argparse

from .backtest import run_backtest
from .data import load_csv, synthetic_bars
from .risk import RiskManager
from .strategy import RsiReversion, SmaCrossover


def build_strategy(args):
    if args.strategy == "sma":
        return SmaCrossover(fast=args.fast, slow=args.slow)
    return RsiReversion(period=args.rsi_period, oversold=args.oversold, overbought=args.overbought)


def main(argv=None):
    p = argparse.ArgumentParser(prog="bot", description="Backtest a trading strategy (paper trading only).")
    p.add_argument("--data", help="CSV file with date,open,high,low,close,volume (default: synthetic data)")
    p.add_argument("--strategy", choices=["sma", "rsi"], default="sma")
    p.add_argument("--cash", type=float, default=10_000.0)
    p.add_argument("--fee", type=float, default=0.001, help="fee rate per trade (0.001 = 0.1%%)")
    p.add_argument("--fast", type=int, default=10)
    p.add_argument("--slow", type=int, default=30)
    p.add_argument("--rsi-period", type=int, default=14)
    p.add_argument("--oversold", type=float, default=30)
    p.add_argument("--overbought", type=float, default=70)
    p.add_argument("--stop-loss", type=float, default=0.05)
    p.add_argument("--take-profit", type=float, default=0.15)
    p.add_argument("--show-trades", action="store_true")
    args = p.parse_args(argv)

    bars = load_csv(args.data) if args.data else synthetic_bars()
    strategy = build_strategy(args)
    risk = RiskManager(stop_loss=args.stop_loss, take_profit=args.take_profit)
    r = run_backtest(bars, strategy, cash=args.cash, fee_rate=args.fee, risk=risk)

    print(f"Strategy:        {strategy.name}  ({len(bars)} bars, {bars[0].date} to {bars[-1].date})")
    print(f"Start equity:    {r.start_equity:,.2f}")
    print(f"End equity:      {r.end_equity:,.2f}")
    print(f"Total return:    {r.total_return:+.2%}")
    print(f"Buy and hold:    {r.buy_and_hold_return:+.2%}")
    print(f"Max drawdown:    {r.max_drawdown:.2%}")
    print(f"Sharpe ratio:    {r.sharpe:.2f}")
    print(f"Trades:          {r.num_trades}")
    print(f"Win rate:        {r.win_rate:.0%}")

    if args.show_trades:
        print("\nDate        Side  Qty         Price       Reason")
        for t in r.trades:
            print(f"{t.date}  {t.side:<4}  {t.qty:<10.4f}  {t.price:<10.2f}  {t.reason}")


if __name__ == "__main__":
    main()
