import unittest
from unittest.mock import patch
import datetime

# Assuming accounts.py is in the same directory
import accounts

class TestGetSharePrice(unittest.TestCase):
    def test_get_share_price_valid(self):
        self.assertEqual(accounts.get_share_price('AAPL'), 150.0)
        self.assertEqual(accounts.get_share_price('TSLA'), 700.0)
        self.assertEqual(accounts.get_share_price('GOOGL'), 2800.0)
        # Case insensitive
        self.assertEqual(accounts.get_share_price('aapl'), 150.0)
    
    def test_get_share_price_invalid(self):
        with self.assertRaises(ValueError):
            accounts.get_share_price('INVALID')


class TestTransaction(unittest.TestCase):
    def test_transaction_creation(self):
        with patch('accounts.datetime.datetime') as mock_datetime:
            fixed_time = datetime.datetime(2023, 1, 1, 12, 0, 0)
            mock_datetime.now.return_value = fixed_time
            t = accounts.Transaction(1, 'BUY', 1000.0, 'AAPL', 10, 100.0)
            self.assertEqual(t.transaction_id, 1)
            self.assertEqual(t.timestamp, fixed_time)
            self.assertEqual(t.type, 'BUY')
            self.assertEqual(t.amount, 1000.0)
            self.assertEqual(t.symbol, 'AAPL')
            self.assertEqual(t.quantity, 10)
            self.assertEqual(t.price_per_share, 100.0)
    
    def test_transaction_repr(self):
        with patch('accounts.datetime.datetime') as mock_datetime:
            fixed_time = datetime.datetime(2023, 1, 1, 12, 0, 0)
            mock_datetime.now.return_value = fixed_time
            t = accounts.Transaction(1, 'BUY', 1000.0, 'AAPL', 10, 100.0)
            expected = f'Transaction(id=1, timestamp={fixed_time}, type=BUY, amount=1000.0, symbol=AAPL, quantity=10, price_per_share=100.0)'
            self.assertEqual(repr(t), expected)


class TestAccount(unittest.TestCase):
    def setUp(self):
        self.account = accounts.Account('test123')
    
    def test_initial_state(self):
        self.assertEqual(self.account.account_id, 'test123')
        self.assertEqual(self.account.balance, 0.0)
        self.assertEqual(self.account.holdings, {})
        self.assertEqual(self.account.transactions, [])
        self.assertEqual(self.account.initial_deposit, 0.0)
    
    def test_deposit_positive(self):
        self.account.deposit(100.0)
        self.assertEqual(self.account.balance, 100.0)
        self.assertEqual(self.account.initial_deposit, 100.0)
        self.assertEqual(len(self.account.transactions), 1)
        t = self.account.transactions[0]
        self.assertEqual(t.type, 'DEPOSIT')
        self.assertEqual(t.amount, 100.0)
        self.assertIsNone(t.symbol)
        self.assertIsNone(t.quantity)
        self.assertIsNone(t.price_per_share)
    
    def test_deposit_zero_or_negative(self):
        with self.assertRaises(ValueError):
            self.account.deposit(0.0)
        with self.assertRaises(ValueError):
            self.account.deposit(-50.0)
        self.assertEqual(self.account.balance, 0.0)
    
    def test_withdraw_sufficient(self):
        self.account.deposit(200.0)
        self.account.withdraw(50.0)
        self.assertEqual(self.account.balance, 150.0)
        self.assertEqual(len(self.account.transactions), 2)
        t = self.account.transactions[1]
        self.assertEqual(t.type, 'WITHDRAWAL')
        self.assertEqual(t.amount, 50.0)
    
    def test_withdraw_insufficient(self):
        self.account.deposit(30.0)
        with self.assertRaises(ValueError):
            self.account.withdraw(50.0)
        self.assertEqual(self.account.balance, 30.0)
    
    def test_withdraw_zero_or_negative(self):
        with self.assertRaises(ValueError):
            self.account.withdraw(0.0)
        with self.assertRaises(ValueError):
            self.account.withdraw(-10.0)
    
    @patch('accounts.get_share_price')
    def test_buy_sufficient_funds(self, mock_get_price):
        mock_get_price.return_value = 150.0  # AAPL price
        self.account.deposit(2000.0)
        self.account.buy('AAPL', 10)
        self.assertEqual(self.account.balance, 2000.0 - 1500.0)  # 500.0
        self.assertEqual(self.account.holdings, {'AAPL': 10})
        self.assertEqual(len(self.account.transactions), 2)
        t = self.account.transactions[1]
        self.assertEqual(t.type, 'BUY')
        self.assertEqual(t.amount, 1500.0)
        self.assertEqual(t.symbol, 'AAPL')
        self.assertEqual(t.quantity, 10)
        self.assertEqual(t.price_per_share, 150.0)
    
    @patch('accounts.get_share_price')
    def test_buy_insufficient_funds(self, mock_get_price):
        mock_get_price.return_value = 150.0
        self.account.deposit(100.0)
        with self.assertRaises(ValueError):
            self.account.buy('AAPL', 10)
        self.assertEqual(self.account.balance, 100.0)
        self.assertEqual(self.account.holdings, {})
    
    def test_buy_zero_or_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.account.buy('AAPL', 0)
        with self.assertRaises(ValueError):
            self.account.buy('AAPL', -5)
    
    @patch('accounts.get_share_price')
    def test_sell_sufficient_shares(self, mock_get_price):
        mock_get_price.return_value = 150.0
        self.account.deposit(2000.0)
        self.account.buy('AAPL', 10)
        # After buy, balance is 500.0, holdings AAPL:10
        self.account.sell('AAPL', 4)
        self.assertEqual(self.account.balance, 500.0 + 600.0)  # 1100.0
        self.assertEqual(self.account.holdings, {'AAPL': 6})
        self.assertEqual(len(self.account.transactions), 3)
        t = self.account.transactions[2]
        self.assertEqual(t.type, 'SELL')
        self.assertEqual(t.amount, 600.0)
        self.assertEqual(t.symbol, 'AAPL')
        self.assertEqual(t.quantity, 4)
        self.assertEqual(t.price_per_share, 150.0)
    
    @patch('accounts.get_share_price')
    def test_sell_all_shares(self, mock_get_price):
        mock_get_price.return_value = 150.0
        self.account.deposit(2000.0)
        self.account.buy('AAPL', 10)
        self.account.sell('AAPL', 10)
        self.assertEqual(self.account.balance, 2000.0)  # back to original after buy and sell
        self.assertEqual(self.account.holdings, {})
    
    @patch('accounts.get_share_price')
    def test_sell_insufficient_shares(self, mock_get_price):
        mock_get_price.return_value = 150.0
        self.account.deposit(2000.0)
        self.account.buy('AAPL', 5)
        with self.assertRaises(ValueError):
            self.account.sell('AAPL', 10)
        self.assertEqual(self.account.holdings, {'AAPL': 5})
    
    def test_sell_zero_or_negative_quantity(self):
        with self.assertRaises(ValueError):
            self.account.sell('AAPL', 0)
        with self.assertRaises(ValueError):
            self.account.sell('AAPL', -3)
    
    @patch('accounts.get_share_price')
    def test_get_portfolio_value(self, mock_get_price):
        mock_get_price.return_value = 150.0
        self.account.deposit(1000.0)
        self.account.buy('AAPL', 4)  # cost 600, balance 400
        # portfolio value = balance + holdings value = 400 + 4*150 = 1000
        self.assertEqual(self.account.get_portfolio_value(), 1000.0)
        # Add another holding
        mock_get_price.return_value = 700.0  # TSLA
        self.account.deposit(1400.0)
        self.account.buy('TSLA', 2)  # balance now 400+1400-1400=400
        # portfolio value = 400 + 4*150 + 2*700 = 400 + 600 + 1400 = 2400
        mock_get_price.side_effect = lambda s: 150.0 if s == 'AAPL' else 700.0
        self.assertEqual(self.account.get_portfolio_value(), 2400.0)
    
    def test_get_holdings(self):
        self.account.holdings = {'AAPL': 5, 'TSLA': 2}
        holdings_copy = self.account.get_holdings()
        self.assertEqual(holdings_copy, {'AAPL': 5, 'TSLA': 2})
        # Ensure it's a copy
        holdings_copy['AAPL'] = 10
        self.assertEqual(self.account.holdings['AAPL'], 5)
    
    @patch('accounts.get_share_price')
    def test_get_profit_loss(self, mock_get_price):
        mock_get_price.return_value = 150.0
        self.account.deposit(1000.0)
        self.account.buy('AAPL', 4)  # cost 600, balance 400
        # initial deposit 1000, portfolio value 1000, profit/loss 0
        self.assertEqual(self.account.get_profit_loss(), 0.0)
        # Price changes
        mock_get_price.return_value = 200.0  # AAPL price increase
        # portfolio value = 400 + 4*200 = 1200, profit/loss = 200
        self.assertEqual(self.account.get_profit_loss(), 200.0)
        # Withdraw some money
        self.account.withdraw(200.0)  # balance 200, portfolio value 200 + 800 = 1000
        # initial deposit remains 1000, profit/loss 0 again
        self.assertEqual(self.account.get_profit_loss(), 0.0)
    
    def test_get_transactions(self):
        self.account.deposit(100.0)
        self.account.withdraw(30.0)
        transactions_copy = self.account.get_transactions()
        self.assertEqual(len(transactions_copy), 2)
        # Ensure it's a copy
        transactions_copy.pop()
        self.assertEqual(len(self.account.transactions), 2)


if __name__ == '__main__':
    unittest.main()