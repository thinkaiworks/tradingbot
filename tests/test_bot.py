import os
import tempfile
import unittest

from bot.backtest import max_drawdown, run_backtest, win_rate
from bot.broker import PaperBroker, Trade
from bot.data import Bar, load_csv, save_csv, synthetic_bars
from bot.indicators import rsi, sma
from bot.risk import RiskManager
from bot.strategy import BUY, HOLD, SELL, RsiReversion, SmaCrossover


def bars_from_closes(closes):
    return [Bar(f"2024-01-{i + 1:02d}", c, c, c, c, 1000) for i, c in enumerate(closes)]


class IndicatorTests(unittest.TestCase):
    def test_sma(self):
        self.assertEqual(sma([1, 2, 3, 4], 2), 3.5)
        self.assertIsNone(sma([1], 2))

    def test_rsi_extremes(self):
        self.assertEqual(rsi(list(range(20)), 14), 100.0)
        self.assertEqual(rsi(list(range(20, 0, -1)), 14), 0.0)
        self.assertIsNone(rsi([1, 2], 14))


class StrategyTests(unittest.TestCase):
    def test_sma_crossover_signals(self):
        s = SmaCrossover(fast=2, slow=4)
        self.assertEqual(s.signal([10, 10, 10, 10, 10]), HOLD)
        self.assertEqual(s.signal([10, 10, 10, 10, 14]), BUY)
        self.assertEqual(s.signal([10, 10, 10, 10, 6]), SELL)

    def test_sma_rejects_bad_periods(self):
        with self.assertRaises(ValueError):
            SmaCrossover(fast=30, slow=10)

    def test_rsi_reversion(self):
        s = RsiReversion(period=5)
        self.assertEqual(s.signal([10, 9, 8, 7, 6, 5]), BUY)
        self.assertEqual(s.signal([5, 6, 7, 8, 9, 10]), SELL)


class BrokerTests(unittest.TestCase):
    def test_round_trip_with_fees(self):
        b = PaperBroker(cash=1000, fee_rate=0.01)
        b.buy("d1", 10, 50)
        self.assertAlmostEqual(b.cash, 1000 - 500 - 5)
        b.sell_all("d2", 12)
        self.assertAlmostEqual(b.cash, 495 + 600 - 6)
        self.assertFalse(b.in_position)

    def test_insufficient_cash(self):
        with self.assertRaises(ValueError):
            PaperBroker(cash=100).buy("d1", 10, 20)


class RiskTests(unittest.TestCase):
    def test_exit_rules(self):
        r = RiskManager(stop_loss=0.05, take_profit=0.1)
        self.assertEqual(r.exit_reason(100, 94), "stop_loss")
        self.assertEqual(r.exit_reason(100, 111), "take_profit")
        self.assertIsNone(r.exit_reason(100, 102))

    def test_position_size_fits_cash(self):
        r = RiskManager(risk_fraction=1.0)
        qty = r.position_size(1000, 10, 0.001)
        self.assertLessEqual(qty * 10 * 1.001, 1000 + 1e-9)


class BacktestTests(unittest.TestCase):
    def test_runs_on_synthetic_data(self):
        bars = synthetic_bars(n=300, seed=1)
        r = run_backtest(bars, SmaCrossover())
        self.assertEqual(len(r.equity_curve), len(bars))
        self.assertGreater(r.end_equity, 0)
        self.assertLessEqual(r.max_drawdown, 0)
        self.assertEqual(r.num_trades % 2, 0)  # position is always closed at the end

    def test_profitable_trend(self):
        closes = [100] * 5 + [100 + i for i in range(1, 30)]
        r = run_backtest(bars_from_closes(closes), SmaCrossover(2, 4), fee_rate=0,
                         risk=RiskManager(stop_loss=0, take_profit=0))
        self.assertGreater(r.total_return, 0)

    def test_max_drawdown(self):
        self.assertAlmostEqual(max_drawdown([100, 120, 90, 130]), -0.25)

    def test_win_rate(self):
        trades = [Trade("a", "buy", 1, 10, 0, ""), Trade("b", "sell", 1, 12, 0, ""),
                  Trade("c", "buy", 1, 10, 0, ""), Trade("d", "sell", 1, 8, 0, "")]
        self.assertEqual(win_rate(trades), 0.5)


class DataTests(unittest.TestCase):
    def test_csv_round_trip(self):
        bars = synthetic_bars(n=10)
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "bars.csv")
            save_csv(bars, path)
            self.assertEqual(load_csv(path), bars)


if __name__ == "__main__":
    unittest.main()
