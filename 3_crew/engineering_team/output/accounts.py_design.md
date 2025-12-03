# Design: `accounts.py` Module

## 1. Module Overview

This document outlines the detailed design for the `accounts.py` module. This module provides a self-contained `Account` class for managing a user's portfolio in a trading simulation platform. It handles account creation, cash transactions (deposits/withdrawals), and share trading (buy/sell), while also providing reporting on holdings, portfolio value, profit/loss, and transaction history.

The module is designed to be self-contained and includes a mock implementation for fetching share prices to facilitate immediate testing and development. The entire implementation will be housed within the `accounts.py` file.

## 2. Dependencies

The module will use the standard Python `datetime` library to timestamp transactions.

```python
import datetime
```

## 3. Helper Functions

### `get_share_price(symbol: str) -> float`

A function to retrieve the current market price of a given stock symbol.

*   **Description:** For the purpose of this self-contained module, this function will be a test implementation that returns a fixed price for a predefined set of symbols. In a production environment, this would be replaced with a call to a real-time market data API.
*   **Parameters:**
    *   `symbol (str)`: The stock symbol (e.g., 'AAPL', 'TSLA'). Case-insensitive.
*   **Returns:**
    *   `float`: The current price of one share of the symbol.
*   **Raises:**
    *   `ValueError`: If the symbol is not recognized by the mock service.
*   **Example Implementation:**
    ```python
    def get_share_price(symbol: str) -> float:
        """A mock function to get the price of a share."""
        prices = {
            "AAPL": 150.00,
            "GOOGL": 2800.00,
            "TSLA": 700.00,
        }
        price = prices.get(symbol.upper())
        if price is None:
            raise ValueError(f"Unknown symbol: {symbol}")
        return price
    ```

## 4. Custom Exceptions

To provide clear error feedback, the module will define the following custom exception classes, which should inherit from `Exception`.

### `InsufficientFundsError(Exception)`

Raised when an operation (e.g., withdrawal, buying shares) cannot be completed due to a lack of cash.

### `InsufficientSharesError(Exception)`

Raised when a user attempts to sell more shares of a stock than they currently own.

## 5. `Account` Class

### Class Overview

The `Account` class represents a single user's trading account. It encapsulates all the data and logic related to managing the user's cash balance, stock holdings, and transaction history.

### Attributes

*   `account_id (str)`: A unique identifier for the account, provided on creation.
*   `cash_balance (float)`: The amount of cash currently available in the account for trading or withdrawal. Initialized to `0.0`.
*   `holdings (dict[str, int])`: A dictionary where keys are stock symbols (e.g., 'AAPL') and values are the integer quantity of shares owned.
*   `transactions (list[dict])`: A chronological list of all transactions that have occurred in the account. Each transaction is a dictionary containing details like `type`, `timestamp`, `amount`, `symbol`, `quantity`, and `price_per_share`.

### Methods

#### `__init__(self, account_id: str)`

*   **Description:** Constructor for the `Account` class. Initializes a new trading account with a zero balance and no holdings.
*   **Parameters:**
    *   `account_id (str)`: The unique identifier for this new account.

---

#### `deposit(self, amount: float) -> None`

*   **Description:** Adds a specified amount of cash to the account balance. Records a 'deposit' transaction.
*   **Parameters:**
    *   `amount (float)`: The amount of cash to deposit. Must be a positive number.
*   **Returns:**
    *   `None`
*   **Raises:**
    *   `ValueError`: If the `amount` is not a positive number.

---

#### `withdraw(self, amount: float) -> None`

*   **Description:** Withdraws a specified amount of cash from the account balance. Records a 'withdrawal' transaction.
*   **Parameters:**
    *   `amount (float)`: The amount of cash to withdraw. Must be a positive number.
*   **Returns:**
    *   `None`
*   **Raises:**
    *   `ValueError`: If the `amount` is not a positive number.
    *   `InsufficientFundsError`: If the withdrawal `amount` is greater than the current `cash_balance`.

---

#### `buy_shares(self, symbol: str, quantity: int) -> None`

*   **Description:** Purchases a specified quantity of shares for a given stock symbol. This action decreases the cash balance and increases the quantity of shares in the holdings. Records a 'buy' transaction.
*   **Parameters:**
    *   `symbol (str)`: The stock symbol to purchase (e.g., 'AAPL').
    *   `quantity (int)`: The number of shares to purchase. Must be a positive integer.
*   **Returns:**
    *   `None`
*   **Raises:**
    *   `ValueError`: If `quantity` is not a positive integer.
    *   `InsufficientFundsError`: If the total cost (`quantity * get_share_price(symbol)`) exceeds the `cash_balance`.

---

#### `sell_shares(self, symbol: str, quantity: int) -> None`

*   **Description:** Sells a specified quantity of shares for a given stock symbol. This action increases the cash balance and decreases the quantity of shares in the holdings. Records a 'sell' transaction.
*   **Parameters:**
    *   `symbol (str)`: The stock symbol to sell.
    *   `quantity (int)`: The number of shares to sell. Must be a positive integer.
*   **Returns:**
    *   `None`
*   **Raises:**
    *   `ValueError`: If `quantity` is not a positive integer.
    *   `InsufficientSharesError`: If the user does not own the symbol or if the `quantity` to sell is greater than the number of shares owned.

---

#### `get_holdings(self) -> dict[str, int]`

*   **Description:** Provides a snapshot of the user's current stock holdings.
*   **Returns:**
    *   `dict[str, int]`: A copy of the holdings dictionary, mapping symbols to the quantity of shares owned. An empty dictionary is returned if no shares are held.

---

#### `get_portfolio_value(self) -> float`

*   **Description:** Calculates the total current value of the account. This is the sum of the cash balance and the current market value of all shares held in the portfolio.
*   **Returns:**
    *   `float`: The total value of the portfolio.

---

#### `get_profit_or_loss(self) -> float`

*   **Description:** Calculates the total profit or loss for the account since its creation. This is determined by subtracting the total amount of cash deposited from the current total portfolio value. Withdrawals do not affect the P/L calculation.
*   **Returns:**
    *   `float`: The profit (positive value) or loss (negative value).

---

#### `get_transaction_history(self) -> list[dict]`

*   **Description:** Provides a complete, chronologically ordered list of all transactions that have occurred in the account.
*   **Returns:**
    *   `list[dict]`: A copy of the list of transaction records. Returns an empty list if no transactions have occurred.