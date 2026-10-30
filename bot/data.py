"""Price data: load OHLCV bars from CSV or generate synthetic ones."""

import csv
import math
import random
from dataclasses import dataclass
from datetime import date, timedelta


@dataclass(frozen=True)
class Bar:
    date: str
    open: float
    high: float
    low: float
    close: float
    volume: float


def load_csv(path):
    """Load bars from a CSV with columns: date,open,high,low,close,volume."""
    bars = []
    with open(path, newline="") as f:
        for row in csv.DictReader(f):
            bars.append(
                Bar(
                    date=row["date"],
                    open=float(row["open"]),
                    high=float(row["high"]),
                    low=float(row["low"]),
                    close=float(row["close"]),
                    volume=float(row["volume"]),
                )
            )
    if not bars:
        raise ValueError(f"no bars found in {path}")
    return bars


def save_csv(bars, path):
    with open(path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["date", "open", "high", "low", "close", "volume"])
        for b in bars:
            writer.writerow([b.date, b.open, b.high, b.low, b.close, b.volume])


def synthetic_bars(n=500, start_price=100.0, drift=0.0003, vol=0.015, seed=42):
    """Generate a random-walk price series (geometric Brownian motion)."""
    rng = random.Random(seed)
    day = date(2024, 1, 1)
    price = start_price
    bars = []
    for _ in range(n):
        open_ = price
        close = open_ * math.exp(drift + vol * rng.gauss(0, 1))
        high = max(open_, close) * (1 + abs(rng.gauss(0, vol / 2)))
        low = min(open_, close) * (1 - abs(rng.gauss(0, vol / 2)))
        bars.append(
            Bar(
                date=day.isoformat(),
                open=round(open_, 4),
                high=round(high, 4),
                low=round(low, 4),
                close=round(close, 4),
                volume=float(rng.randint(10_000, 100_000)),
            )
        )
        price = close
        day += timedelta(days=1)
    return bars
