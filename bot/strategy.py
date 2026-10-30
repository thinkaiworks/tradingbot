"""Trading strategies. Each returns "buy", "sell" or "hold" for the latest bar."""

from .indicators import rsi, sma

BUY, SELL, HOLD = "buy", "sell", "hold"


class SmaCrossover:
    """Buy when the fast SMA crosses above the slow SMA, sell when it crosses below."""

    name = "sma"

    def __init__(self, fast=10, slow=30):
        if fast >= slow:
            raise ValueError("fast period must be smaller than slow period")
        self.fast = fast
        self.slow = slow

    def signal(self, closes):
        if len(closes) < self.slow + 1:
            return HOLD
        prev_fast, prev_slow = sma(closes[:-1], self.fast), sma(closes[:-1], self.slow)
        fast, slow = sma(closes, self.fast), sma(closes, self.slow)
        if prev_fast <= prev_slow and fast > slow:
            return BUY
        if prev_fast >= prev_slow and fast < slow:
            return SELL
        return HOLD


class RsiReversion:
    """Buy when RSI is oversold, sell when it is overbought."""

    name = "rsi"

    def __init__(self, period=14, oversold=30, overbought=70):
        self.period = period
        self.oversold = oversold
        self.overbought = overbought

    def signal(self, closes):
        value = rsi(closes, self.period)
        if value is None:
            return HOLD
        if value < self.oversold:
            return BUY
        if value > self.overbought:
            return SELL
        return HOLD


STRATEGIES = {SmaCrossover.name: SmaCrossover, RsiReversion.name: RsiReversion}
