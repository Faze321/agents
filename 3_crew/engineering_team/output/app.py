import gradio as gr
import datetime
import pandas as pd

# Assume the following classes and functions are defined in accounts.py
# For the purpose of this single-file app.py, I will include them here.
# In a real scenario, you would have:
# from accounts import Account, InsufficientFundsError, InsufficientSharesError, get_share_price

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


# Global instance for a single user (as per requirement)
user_account = Account("user_123")

def get_account_summary():
    """Returns the current account summary for display."""
    cash_balance = user_account.cash_balance
    portfolio_value = user_account.get_portfolio_value()
    profit_loss = user_account.get_profit_or_loss()

    summary_text = f"Cash Balance: ${cash_balance:.2f}\n" \
                   f"Portfolio Value: ${portfolio_value:.2f}\n" \
                   f"Profit/Loss: ${profit_loss:.2f}"
    return summary_text

def get_holdings_df():
    """Returns current holdings as a Pandas DataFrame."""
    holdings_dict = user_account.get_holdings()
    if not holdings_dict:
        return pd.DataFrame(columns=["Symbol", "Quantity", "Current Price", "Value"])
    
    data = []
    for symbol, quantity in holdings_dict.items():
        try:
            price = get_share_price(symbol)
            value = price * quantity
            data.append({"Symbol": symbol, "Quantity": quantity, "Current Price": f"${price:.2f}", "Value": f"${value:.2f}"})
        except ValueError:
            data.append({"Symbol": symbol, "Quantity": quantity, "Current Price": "N/A", "Value": "N/A"})
    return pd.DataFrame(data)

def get_transactions_df():
    """Returns transaction history as a Pandas DataFrame."""
    transactions = user_account.get_transaction_history()
    if not transactions:
        return pd.DataFrame(columns=["Timestamp", "Type", "Symbol", "Quantity", "Price/Share", "Amount"])
    
    # Pre-process for display
    display_transactions = []
    for t in transactions:
        display_t = t.copy()
        display_t["Amount"] = f"${display_t['amount']:.2f}"
        if "price_per_share" in display_t:
            display_t["Price/Share"] = f"${display_t['price_per_share']:.2f}"
        else:
            display_t["Price/Share"] = ""
        
        # Rename/reorder columns for better display
        display_t["Timestamp"] = display_t.pop("timestamp")
        display_t["Type"] = display_t.pop("type").capitalize()
        display_t["Symbol"] = display_t.pop("symbol", "")
        display_t["Quantity"] = display_t.pop("quantity", "")
        display_t.pop("amount") # Remove original amount as it's formatted in "Amount"

        display_transactions.append(display_t)

    return pd.DataFrame(display_transactions).reindex(columns=["Timestamp", "Type", "Symbol", "Quantity", "Price/Share", "Amount"])

# Gradio Interface Functions
def deposit_funds(amount: float):
    try:
        user_account.deposit(amount)
        return f"Deposit of ${amount:.2f} successful.", get_account_summary(), get_holdings_df(), get_transactions_df()
    except ValueError as e:
        return f"Error: {e}", get_account_summary(), get_holdings_df(), get_transactions_df()

def withdraw_funds(amount: float):
    try:
        user_account.withdraw(amount)
        return f"Withdrawal of ${amount:.2f} successful.", get_account_summary(), get_holdings_df(), get_transactions_df()
    except (ValueError, InsufficientFundsError) as e:
        return f"Error: {e}", get_account_summary(), get_holdings_df(), get_transactions_df()

def buy_shares_ui(symbol: str, quantity: int):
    try:
        user_account.buy_shares(symbol, quantity)
        return f"Bought {quantity} shares of {symbol}.", get_account_summary(), get_holdings_df(), get_transactions_df()
    except (ValueError, InsufficientFundsError) as e:
        return f"Error: {e}", get_account_summary(), get_holdings_df(), get_transactions_df()

def sell_shares_ui(symbol: str, quantity: int):
    try:
        user_account.sell_shares(symbol, quantity)
        return f"Sold {quantity} shares of {symbol}.", get_account_summary(), get_holdings_df(), get_transactions_df()
    except (ValueError, InsufficientSharesError) as e:
        return f"Error: {e}", get_account_summary(), get_holdings_df(), get_transactions_df()

# Initialize the UI
with gr.Blocks(title="Trading Account Simulator") as demo:
    gr.Markdown("# Simple Trading Account Simulator")
    gr.Markdown("This is a demo for a single user's trading account.")

    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("## Account Summary")
            account_summary_output = gr.Textbox(
                label="Current Status",
                value=get_account_summary(),
                interactive=False,
                lines=3
            )
            
            gr.Markdown("## Funds Management")
            with gr.Column():
                deposit_amount = gr.Number(label="Deposit Amount", value=1000.0)
                deposit_btn = gr.Button("Deposit Funds")
            with gr.Column():
                withdraw_amount = gr.Number(label="Withdraw Amount", value=100.0)
                withdraw_btn = gr.Button("Withdraw Funds")

        with gr.Column(scale=2):
            gr.Markdown("## Trade Shares")
            with gr.Row():
                with gr.Column():
                    gr.Markdown("### Buy Shares")
                    buy_symbol = gr.Dropdown(
                        choices=["AAPL", "GOOGL", "TSLA"],
                        label="Stock Symbol",
                        value="AAPL"
                    )
                    buy_quantity = gr.Slider(minimum=1, maximum=100, step=1, value=1, label="Quantity")
                    buy_btn = gr.Button("Buy Shares")
                with gr.Column():
                    gr.Markdown("### Sell Shares")
                    sell_symbol = gr.Dropdown(
                        choices=["AAPL", "GOOGL", "TSLA"],
                        label="Stock Symbol",
                        value="AAPL"
                    )
                    sell_quantity = gr.Slider(minimum=1, maximum=100, step=1, value=1, label="Quantity")
                    sell_btn = gr.Button("Sell Shares")
            
            status_output = gr.Textbox(label="Status/Messages", interactive=False)

    gr.Markdown("## Current Holdings")
    holdings_output = gr.DataFrame(
        value=get_holdings_df(),
        headers=["Symbol", "Quantity", "Current Price", "Value"],
        datatype=["str", "number", "str", "str"],
        interactive=False
    )

    gr.Markdown("## Transaction History")
    transactions_output = gr.DataFrame(
        value=get_transactions_df(),
        headers=["Timestamp", "Type", "Symbol", "Quantity", "Price/Share", "Amount"],
        datatype=["str", "str", "str", "str", "str", "str"],
        interactive=False
    )

    # Wire up events
    deposit_btn.click(
        deposit_funds,
        inputs=[deposit_amount],
        outputs=[status_output, account_summary_output, holdings_output, transactions_output]
    )
    withdraw_btn.click(
        withdraw_funds,
        inputs=[withdraw_amount],
        outputs=[status_output, account_summary_output, holdings_output, transactions_output]
    )
    buy_btn.click(
        buy_shares_ui,
        inputs=[buy_symbol, buy_quantity],
        outputs=[status_output, account_summary_output, holdings_output, transactions_output]
    )
    sell_btn.click(
        sell_shares_ui,
        inputs=[sell_symbol, sell_quantity],
        outputs=[status_output, account_summary_output, holdings_output, transactions_output]
    )

if __name__ == "__main__":
    demo.launch()