import gradio as gr
from accounts import Account, get_share_price

# Initialize a single user account
account = Account("demo_user")

def create_account():
    """Initialize the account (already created, just reset for demo)."""
    global account
    account = Account("demo_user")
    return "Account created successfully!"

def deposit(amount):
    try:
        amount_val = float(amount)
        account.deposit(amount_val)
        return f"Deposited ${amount_val:.2f} successfully."
    except ValueError as e:
        return f"Error: {e}"

def withdraw(amount):
    try:
        amount_val = float(amount)
        account.withdraw(amount_val)
        return f"Withdrew ${amount_val:.2f} successfully."
    except ValueError as e:
        return f"Error: {e}"

def buy(symbol, quantity):
    try:
        qty = int(quantity)
        account.buy(symbol, qty)
        return f"Bought {qty} shares of {symbol} successfully."
    except ValueError as e:
        return f"Error: {e}"

def sell(symbol, quantity):
    try:
        qty = int(quantity)
        account.sell(symbol, qty)
        return f"Sold {qty} shares of {symbol} successfully."
    except ValueError as e:
        return f"Error: {e}"

def get_balance():
    return f"Current Balance: ${account.balance:.2f}"

def get_holdings():
    holdings = account.get_holdings()
    if not holdings:
        return "No holdings."
    lines = ["Holdings:"]
    for sym, qty in holdings.items():
        price = get_share_price(sym)
        value = price * qty
        lines.append(f"{sym}: {qty} shares @ ${price:.2f} each = ${value:.2f}")
    return "\n".join(lines)

def get_portfolio_value():
    value = account.get_portfolio_value()
    return f"Total Portfolio Value: ${value:.2f}"

def get_profit_loss():
    pnl = account.get_profit_loss()
    return f"Profit/Loss: ${pnl:.2f}"

def get_transactions():
    transactions = account.get_transactions()
    if not transactions:
        return "No transactions yet."
    lines = ["Transaction History:"]
    for t in transactions:
        lines.append(f"ID {t.transaction_id}: {t.timestamp.strftime('%Y-%m-%d %H:%M:%S')} - {t.type}")
        if t.type in ["BUY", "SELL"]:
            lines.append(f"  {t.symbol}: {t.quantity} shares @ ${t.price_per_share:.2f} = ${t.amount:.2f}")
        else:
            lines.append(f"  Amount: ${t.amount:.2f}")
    return "\n".join(lines)

# Gradio UI
with gr.Blocks(title="Trading Simulation Demo") as demo:
    gr.Markdown("# Trading Simulation Account Management")
    gr.Markdown("Single-user demo. All actions apply to the same account.")
    
    with gr.Row():
        with gr.Column(scale=1):
            gr.Markdown("## Account Actions")
            create_btn = gr.Button("Create/Reset Account")
            create_output = gr.Textbox(label="Account Status", interactive=False)
            create_btn.click(create_account, outputs=create_output)
            
            gr.Markdown("### Deposit/Withdraw")
            deposit_amount = gr.Number(label="Deposit Amount ($)", value=1000)
            deposit_btn = gr.Button("Deposit")
            deposit_output = gr.Textbox(label="Deposit Result", interactive=False)
            deposit_btn.click(deposit, inputs=deposit_amount, outputs=deposit_output)
            
            withdraw_amount = gr.Number(label="Withdraw Amount ($)", value=100)
            withdraw_btn = gr.Button("Withdraw")
            withdraw_output = gr.Textbox(label="Withdraw Result", interactive=False)
            withdraw_btn.click(withdraw, inputs=withdraw_amount, outputs=withdraw_output)
            
            gr.Markdown("### Buy/Sell Shares")
            symbol = gr.Dropdown(label="Stock Symbol", choices=["AAPL", "TSLA", "GOOGL"], value="AAPL")
            quantity = gr.Number(label="Quantity", value=1, precision=0)
            buy_btn = gr.Button("Buy")
            sell_btn = gr.Button("Sell")
            trade_output = gr.Textbox(label="Trade Result", interactive=False)
            buy_btn.click(buy, inputs=[symbol, quantity], outputs=trade_output)
            sell_btn.click(sell, inputs=[symbol, quantity], outputs=trade_output)
        
        with gr.Column(scale=1):
            gr.Markdown("## Account Info")
            balance_btn = gr.Button("Check Balance")
            balance_output = gr.Textbox(label="Balance", interactive=False)
            balance_btn.click(get_balance, outputs=balance_output)
            
            holdings_btn = gr.Button("View Holdings")
            holdings_output = gr.Textbox(label="Holdings", interactive=False, lines=5)
            holdings_btn.click(get_holdings, outputs=holdings_output)
            
            portfolio_btn = gr.Button("Portfolio Value")
            portfolio_output = gr.Textbox(label="Portfolio Value", interactive=False)
            portfolio_btn.click(get_portfolio_value, outputs=portfolio_output)
            
            pnl_btn = gr.Button("Profit/Loss")
            pnl_output = gr.Textbox(label="Profit/Loss", interactive=False)
            pnl_btn.click(get_profit_loss, outputs=pnl_output)
            
            trans_btn = gr.Button("View Transactions")
            trans_output = gr.Textbox(label="Transactions", interactive=False, lines=10)
            trans_btn.click(get_transactions, outputs=trans_output)

if __name__ == "__main__":
    demo.launch()