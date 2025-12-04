import datetime
from typing import Optional, Dict, List

def get_share_price(symbol: str) -> float:
    """
    Returns the current price of a share.
    Test implementation with fixed prices for AAPL, TSLA, GOOGL.
    """
    prices = {
        "AAPL": 150.0,
        "TSLA": 700.0,
        "GOOGL": 2800.0
    }
    price = prices.get(symbol.upper())
    if price is None:
        raise ValueError(f"Unknown symbol: {symbol}")
    return price


class Transaction:
    def __init__(self, transaction_id: int, type: str, amount: float, 
                 symbol: Optional[str] = None, quantity: Optional[int] = None, 
                 price_per_share: Optional[float] = None):
        self.transaction_id = transaction_id
        self.timestamp = datetime.datetime.now()
        self.type = type  # "DEPOSIT", "WITHDRAWAL", "BUY", "SELL"
        self.amount = amount  # Absolute amount of money involved
        self.symbol = symbol
        self.quantity = quantity
        self.price_per_share = price_per_share
    
    def __repr__(self) -> str:
        return (f"Transaction(id={self.transaction_id}, timestamp={self.timestamp}, "
                f"type={self.type}, amount={self.amount}, symbol={self.symbol}, "
                f"quantity={self.quantity}, price_per_share={self.price_per_share})")


class Account:
    def __init__(self, account_id: str):
        self.account_id = account_id
        self.balance = 0.0
        self.holdings: Dict[str, int] = {}
        self.transactions: List[Transaction] = []
        self.initial_deposit = 0.0
        self._next_transaction_id = 1
    
    def deposit(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Deposit amount must be positive")
        self.balance += amount
        self.initial_deposit += amount
        self._add_transaction("DEPOSIT", amount)
    
    def withdraw(self, amount: float) -> None:
        if amount <= 0:
            raise ValueError("Withdrawal amount must be positive")
        if amount > self.balance:
            raise ValueError("Insufficient funds for withdrawal")
        self.balance -= amount
        self._add_transaction("WITHDRAWAL", amount)
    
    def buy(self, symbol: str, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Buy quantity must be positive")
        price = get_share_price(symbol)
        cost = price * quantity
        if cost > self.balance:
            raise ValueError("Insufficient funds to buy shares")
        self.balance -= cost
        # Update holdings
        current_qty = self.holdings.get(symbol, 0)
        self.holdings[symbol] = current_qty + quantity
        self._add_transaction("BUY", cost, symbol, quantity, price)
    
    def sell(self, symbol: str, quantity: int) -> None:
        if quantity <= 0:
            raise ValueError("Sell quantity must be positive")
        current_qty = self.holdings.get(symbol, 0)
        if current_qty < quantity:
            raise ValueError(f"Insufficient shares of {symbol} to sell")
        price = get_share_price(symbol)
        revenue = price * quantity
        self.balance += revenue
        # Update holdings
        new_qty = current_qty - quantity
        if new_qty == 0:
            del self.holdings[symbol]
        else:
            self.holdings[symbol] = new_qty
        self._add_transaction("SELL", revenue, symbol, quantity, price)
    
    def get_portfolio_value(self) -> float:
        total = self.balance
        for symbol, quantity in self.holdings.items():
            price = get_share_price(symbol)
            total += price * quantity
        return total
    
    def get_holdings(self) -> Dict[str, int]:
        return self.holdings.copy()
    
    def get_profit_loss(self) -> float:
        return self.get_portfolio_value() - self.initial_deposit
    
    def get_transactions(self) -> List[Transaction]:
        return self.transactions.copy()
    
    def _add_transaction(self, type: str, amount: float, 
                         symbol: Optional[str] = None, quantity: Optional[int] = None, 
                         price_per_share: Optional[float] = None) -> None:
        transaction = Transaction(
            transaction_id=self._next_transaction_id,
            type=type,
            amount=amount,
            symbol=symbol,
            quantity=quantity,
            price_per_share=price_per_share
        )
        self.transactions.append(transaction)
        self._next_transaction_id += 1