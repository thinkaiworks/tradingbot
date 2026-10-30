"""Technical indicators computed over a list of closing prices."""


def sma(values, period):
    """Simple moving average of the last `period` values, or None if too short."""
    if period <= 0:
        raise ValueError("period must be positive")
    if len(values) < period:
        return None
    return sum(values[-period:]) / period


def rsi(values, period=14):
    """Relative Strength Index (simple-average version), or None if too short."""
    if len(values) < period + 1:
        return None
    gains = losses = 0.0
    for prev, cur in zip(values[-period - 1:-1], values[-period:]):
        change = cur - prev
        if change > 0:
            gains += change
        else:
            losses -= change
    if losses == 0:
        return 100.0
    rs = gains / losses
    return 100 - 100 / (1 + rs)
