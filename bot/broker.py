"""A paper broker: simulates fills, fees and a single long position. No real money."""

from dataclasses import dataclass, field


@dataclass
class Trade:
    date: str
    side: str
    qty: float
    price: float
    fee: float
    reason: str


@dataclass
class PaperBroker:
    cash: float
    fee_rate: float = 0.001  # 0.1% per trade
    qty: float = 0.0
    entry_price: float = 0.0
    trades: list = field(default_factory=list)

    @property
    def in_position(self):
        return self.qty > 0

    def equity(self, price):
        return self.cash + self.qty * price

    def buy(self, date, price, qty, reason="signal"):
        if qty <= 0:
            return None
        cost = qty * price
        fee = cost * self.fee_rate
        if cost + fee > self.cash + 1e-9:
            raise ValueError("insufficient cash")
        self.cash -= cost + fee
        self.entry_price = (self.entry_price * self.qty + cost) / (self.qty + qty)
        self.qty += qty
        trade = Trade(date, "buy", qty, price, fee, reason)
        self.trades.append(trade)
        return trade

    def sell_all(self, date, price, reason="signal"):
        if not self.in_position:
            return None
        proceeds = self.qty * price
        fee = proceeds * self.fee_rate
        self.cash += proceeds - fee
        trade = Trade(date, "sell", self.qty, price, fee, reason)
        self.trades.append(trade)
        self.qty = 0.0
        self.entry_price = 0.0
        return trade
