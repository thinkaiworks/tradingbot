# Trading Bot

A small, dependency-free trading bot in Python. It backtests strategies on historical
price data using a **paper broker** (simulated money only), with fees, position sizing,
stop-loss and take-profit rules.

> ⚠️ For learning and research only. This is not financial advice, and the bot does not
> place real orders.

## Features

- **Strategies:** SMA crossover (`sma`) and RSI mean reversion (`rsi`)
- **Paper broker:** simulated buys and sells with a per-trade fee
- **Risk management:** position sizing, stop-loss, take-profit
- **Metrics:** total return vs. buy-and-hold, max drawdown, Sharpe ratio, win rate
- **Data:** load any OHLCV CSV, or use built-in synthetic data
- No third-party packages; needs Python 3.9+

## Quick start

```bash
git clone https://github.com/thinkaiworks/tradingbot.git
cd tradingbot
python3 -m bot
```

Example output:

```
Strategy:        sma  (500 bars, 2024-01-01 to 2025-05-14)
Start equity:    10,000.00
End equity:      9,863.79
Total return:    -1.36%
Buy and hold:    -20.99%
Max drawdown:    -19.70%
Sharpe ratio:    0.01
Trades:          16
Win rate:        25%
```

## Usage

```bash
# RSI strategy on the sample CSV, with a trade list
python3 -m bot --strategy rsi --data data/sample.csv --show-trades

# Tune the SMA crossover and risk rules
python3 -m bot --strategy sma --fast 5 --slow 20 --stop-loss 0.03 --take-profit 0.10

# All options
python3 -m bot --help
```

Your own CSV needs the columns `date,open,high,low,close,volume`, oldest row first.

## Project layout

```
bot/
  data.py        CSV loading and synthetic price generator
  indicators.py  SMA and RSI
  strategy.py    Trading strategies (buy / sell / hold signals)
  broker.py      Paper broker: cash, position, fees, trade log
  risk.py        Position sizing, stop-loss, take-profit
  backtest.py    Backtest engine and performance metrics
  __main__.py    Command line interface
tests/           Unit tests
data/sample.csv  Sample price data
```

## Adding a strategy

Create a class with a `name` and a `signal(closes)` method that returns `"buy"`,
`"sell"` or `"hold"`, then register it in `STRATEGIES` in `bot/strategy.py`.

## Tests

```bash
python3 -m unittest -v
```
