"""Position sizing and exit rules."""

from dataclasses import dataclass


@dataclass
class RiskManager:
    risk_fraction: float = 0.95  # share of cash to put into each position
    stop_loss: float = 0.05      # exit if price falls 5% below entry
    take_profit: float = 0.15    # exit if price rises 15% above entry

    def position_size(self, cash, price, fee_rate):
        if price <= 0:
            return 0.0
        budget = cash * self.risk_fraction
        return budget / (price * (1 + fee_rate))

    def exit_reason(self, entry_price, price):
        """Return "stop_loss" or "take_profit" if an exit rule is hit, else None."""
        if entry_price <= 0:
            return None
        change = price / entry_price - 1
        if self.stop_loss and change <= -self.stop_loss:
            return "stop_loss"
        if self.take_profit and change >= self.take_profit:
            return "take_profit"
        return None
