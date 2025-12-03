import datetime

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

class InsufficientFundsError(Exception):
    """Raised when an operation cannot be completed due to a lack of cash."""
    pass

class InsufficientSharesError(Exception):
    """Raised when a user attempts to sell more shares of a stock than they currently own."""
    pass

class Account:
    """
    Manages a user's trading account, including cash balance, stock holdings,
    and transaction history.
    """

    def __init__(self, account_id: str):
        """
        Constructor for the Account class.
        Initializes a new trading account with a zero balance and no holdings.

        Args:
            account_id (str): The unique identifier for this new account.
        """
        self.account_id: str = account_id
        self.cash_balance: float = 0.0
        self.holdings: dict[str, int] = {}  # {symbol: quantity}
        self.transactions: list[dict] = []

    def _record_transaction(self, transaction_type: str, amount: float, symbol: str = None, quantity: int = None, price_per_share: float = None) -> None:
        """
        Helper method to record a transaction.
        """
        transaction = {
            "type": transaction_type,
            "timestamp": datetime.datetime.now().isoformat(),
            "amount": round(amount, 2), # Amount involved in the transaction (e.g., cash change)
        }
        if symbol:
            transaction["symbol"] = symbol.upper()
        if quantity is not None:
            transaction["quantity"] = quantity
        if price_per_share is not None:
            transaction["price_per_share"] = round(price_per_share, 2)
        
        self.transactions.append(transaction)

    def deposit(self, amount: float) -> None:
        """
        Adds a specified amount of cash to the account balance.
        Records a 'deposit' transaction.

        Args:
            amount (float): The amount of cash to deposit. Must be a positive number.

        Raises:
            ValueError: If the amount is not a positive number.
        """
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise ValueError("Deposit amount must be a positive number.")
        
        self.cash_balance += amount
        self._record_transaction(transaction_type="deposit", amount=amount)

    def withdraw(self, amount: float) -> None:
        """
        Withdraws a specified amount of cash from the account balance.
        Records a 'withdrawal' transaction.

        Args:
            amount (float): The amount of cash to withdraw. Must be a positive number.

        Raises:
            ValueError: If the amount is not a positive number.
            InsufficientFundsError: If the withdrawal amount is greater than the current cash_balance.
        """
        if not isinstance(amount, (int, float)) or amount <= 0:
            raise ValueError("Withdrawal amount must be a positive number.")
        
        if amount > self.cash_balance:
            raise InsufficientFundsError(f"Insufficient funds. Attempted to withdraw {amount}, but only {self.cash_balance} available.")
        
        self.cash_balance -= amount
        self._record_transaction(transaction_type="withdrawal", amount=amount)

    def buy_shares(self, symbol: str, quantity: int) -> None:
        """
        Purchases a specified quantity of shares for a given stock symbol.
        This action decreases the cash balance and increases the quantity of shares in the holdings.
        Records a 'buy' transaction.

        Args:
            symbol (str): The stock symbol to purchase (e.g., 'AAPL').
            quantity (int): The number of shares to purchase. Must be a positive integer.

        Returns:
            None

        Raises:
            ValueError: If quantity is not a positive integer.
            InsufficientFundsError: If the total cost exceeds the cash_balance.
        """
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")
        
        symbol = symbol.upper()
        price_per_share = get_share_price(symbol)
        total_cost = price_per_share * quantity

        if total_cost > self.cash_balance:
            raise InsufficientFundsError(f"Insufficient funds to buy {quantity} shares of {symbol}. "
                                         f"Cost: {total_cost}, Available cash: {self.cash_balance}")
        
        self.cash_balance -= total_cost
        self.holdings[symbol] = self.holdings.get(symbol, 0) + quantity
        self._record_transaction(transaction_type="buy", amount=total_cost, symbol=symbol, quantity=quantity, price_per_share=price_per_share)

    def sell_shares(self, symbol: str, quantity: int) -> None:
        """
        Sells a specified quantity of shares for a given stock symbol.
        This action increases the cash balance and decreases the quantity of shares in the holdings.
        Records a 'sell' transaction.

        Args:
            symbol (str): The stock symbol to sell.
            quantity (int): The number of shares to sell. Must be a positive integer.

        Returns:
            None

        Raises:
            ValueError: If quantity is not a positive integer.
            InsufficientSharesError: If the user does not own the symbol or if the quantity to sell
                                     is greater than the number of shares owned.
        """
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("Quantity must be a positive integer.")
        
        symbol = symbol.upper()
        
        if symbol not in self.holdings or self.holdings[symbol] < quantity:
            current_shares = self.holdings.get(symbol, 0)
            raise InsufficientSharesError(f"Insufficient shares of {symbol} to sell. "
                                          f"Attempted to sell {quantity}, but only {current_shares} owned.")
        
        price_per_share = get_share_price(symbol)
        total_proceeds = price_per_share * quantity

        self.cash_balance += total_proceeds
        self.holdings[symbol] -= quantity
        if self.holdings[symbol] == 0:
            del self.holdings[symbol] # Remove symbol if no shares are left

        self._record_transaction(transaction_type="sell", amount=total_proceeds, symbol=symbol, quantity=quantity, price_per_share=price_per_share)

    def get_holdings(self) -> dict[str, int]:
        """
        Provides a snapshot of the user's current stock holdings.

        Returns:
            dict[str, int]: A copy of the holdings dictionary, mapping symbols to the quantity of shares owned.
                            An empty dictionary is returned if no shares are held.
        """
        return self.holdings.copy()

    def get_portfolio_value(self) -> float:
        """
        Calculates the total current value of the account. This is the sum of the cash balance
        and the current market value of all shares held in the portfolio.

        Returns:
            float: The total value of the portfolio.
        """
        holdings_value = 0.0
        for symbol, quantity in self.holdings.items():
            try:
                holdings_value += get_share_price(symbol) * quantity
            except ValueError:
                # If a symbol in holdings is not recognized by get_share_price, it won't contribute to value
                # In a real system, this might log an error or use a stale price. For now, just skip.
                pass 
        return round(self.cash_balance + holdings_value, 2)

    def get_profit_or_loss(self) -> float:
        """
        Calculates the total profit or loss for the account since its creation.
        This is determined by subtracting the total amount of cash deposited from the current total portfolio value.
        Withdrawals do not affect the P/L calculation.

        Returns:
            float: The profit (positive value) or loss (negative value).
        """
        total_deposits = sum(t["amount"] for t in self.transactions if t["type"] == "deposit")
        current_portfolio_value = self.get_portfolio_value()
        
        # Profit/Loss = Current Portfolio Value - Initial Deposits
        # If there were withdrawals, they reduce cash_balance but shouldn't reduce the "investment" base.
        # So we only consider deposits as the initial capital injected.
        
        return round(current_portfolio_value - total_deposits, 2)

    def get_transaction_history(self) -> list[dict]:
        """
        Provides a complete, chronologically ordered list of all transactions that have occurred in the account.

        Returns:
            list[dict]: A copy of the list of transaction records.
                        Returns an empty list if no transactions have occurred.
        """
        return self.transactions.copy()