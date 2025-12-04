# Detailed Design for `accounts.py`

## Overview
The module `accounts.py` will implement a simple account management system for a trading simulation platform. It will include a main `Account` class to manage user accounts, with methods for deposits, withdrawals, buying and selling shares, and reporting portfolio value, profit/loss, holdings, and transactions. The module will be self-contained, including a test implementation of `get_share_price` for AAPL, TSLA, and GOOGL. Error handling will prevent invalid operations like negative balances, insufficient funds for purchases, or selling non-existent shares.

## Module Structure

### Imports
- `datetime`: To timestamp transactions.
- `typing`: For type hints (Optional, Dict, List, Tuple).

### Global Function
- `get_share_price(symbol: str) -> float`: Returns the current price of a share. Includes a test implementation with fixed prices for AAPL ($150.0), TSLA ($700.0), and GOOGL ($2800.0). Raises a `ValueError` for unknown symbols.

### Classes

#### 1. `Transaction`
A data class to represent a single transaction in the account.

**Attributes:**
- `transaction_id`: `int` - Unique identifier for the transaction.
- `timestamp`: `datetime.datetime` - Time of the transaction.
- `type`: `str` - Type of transaction: "DEPOSIT", "WITHDRAWAL", "BUY", or "SELL".
- `amount`: `float` - Amount of money involved (positive for deposit/buy, negative for withdrawal/sell? Actually, we'll store absolute values and handle signs in logic).
- `symbol`: `Optional[str]` - Stock symbol for buy/sell transactions, `None` for deposits/withdrawals.
- `quantity`: `Optional[int]` - Number of shares for buy/sell, `None` for deposits/withdrawals.
- `price_per_share`: `Optional[float]` - Price per share at time of transaction for buy/sell, `None` for deposits/withdrawals.

**Methods:**
- `__init__(self, transaction_id: int, type: str, amount: float, symbol: Optional[str] = None, quantity: Optional[int] = None, price_per_share: Optional[float] = None)`: Initializes a transaction with a generated timestamp.
- `__repr__(self) -> str`: Returns a string representation for debugging.

#### 2. `Account`
The main class representing a user account.

**Attributes:**
- `account_id`: `str` - Unique identifier for the account.
- `balance`: `float` - Current cash balance in the account.
- `holdings`: `Dict[str, int]` - Dictionary mapping stock symbols to quantities owned.
- `transactions`: `List[Transaction]` - List of all transactions in chronological order.
- `initial_deposit`: `float` - Total amount of deposits made to the account (to calculate profit/loss).

**Methods:**
- `__init__(self, account_id: str)`: Initializes an account with zero balance, empty holdings, empty transactions, and zero initial deposit.
- `deposit(self, amount: float) -> None`: Deposits funds into the account. Validates that amount is positive. Updates balance, initial_deposit, and adds a DEPOSIT transaction.
- `withdraw(self, amount: float) -> None`: Withdraws funds from the account. Validates that amount is positive and does not exceed balance. Updates balance and adds a WITHDRAWAL transaction.
- `buy(self, symbol: str, quantity: int) -> None`: Buys shares. Validates that quantity is positive and that the cost (quantity * current price) does not exceed balance. Uses `get_share_price` to get current price. Updates balance, holdings (increases quantity for symbol), and adds a BUY transaction.
- `sell(self, symbol: str, quantity: int) -> None`: Sells shares. Validates that quantity is positive and that the user owns at least that quantity of the symbol. Uses `get_share_price` to get current price. Updates balance, holdings (decreases quantity, removes symbol if zero), and adds a SELL transaction.
- `get_portfolio_value(self) -> float`: Calculates total portfolio value: cash balance + value of all holdings (using current prices via `get_share_price`).
- `get_holdings(self) -> Dict[str, int]`: Returns a copy of the current holdings.
- `get_profit_loss(self) -> float`: Calculates profit/loss: current portfolio value - initial_deposit.
- `get_transactions(self) -> List[Transaction]`: Returns a copy of the list of transactions.
- `_add_transaction(self, type: str, amount: float, symbol: Optional[str] = None, quantity: Optional[int] = None, price_per_share: Optional[float] = None) -> None`: Helper method to create and add a transaction to the list.

### Error Handling
- `ValueError`: Raised for invalid inputs (e.g., negative amounts, insufficient funds, insufficient shares, unknown stock symbols).
- `TypeError`: Raised for type mismatches.

### Example Usage
A simple test or UI could be built by creating an `Account` instance and calling its methods.

## Detailed Method Signatures

```python
import datetime
from typing import Optional, Dict, List

def get_share_price(symbol: str) -> float:
    """
    Returns the current price of a share.
    Test implementation with fixed prices for AAPL, TSLA, GOOGL.
    """
    pass  # Implementation details

class Transaction:
    def __init__(self, transaction_id: int, type: str, amount: float, 
                 symbol: Optional[str] = None, quantity: Optional[int] = None, 
                 price_per_share: Optional[float] = None):
        pass

    def __repr__(self) -> str:
        pass

class Account:
    def __init__(self, account_id: str):
        pass

    def deposit(self, amount: float) -> None:
        pass

    def withdraw(self, amount: float) -> None:
        pass

    def buy(self, symbol: str, quantity: int) -> None:
        pass

    def sell(self, symbol: str, quantity: int) -> None:
        pass

    def get_portfolio_value(self) -> float:
        pass

    def get_holdings(self) -> Dict[str, int]:
        pass

    def get_profit_loss(self) -> float:
        pass

    def get_transactions(self) -> List[Transaction]:
        pass

    def _add_transaction(self, type: str, amount: float, 
                         symbol: Optional[str] = None, quantity: Optional[int] = None, 
                         price_per_share: Optional[float] = None) -> None:
        pass
```

This design ensures the module is self-contained, testable, and ready for integration with a simple UI or further development.